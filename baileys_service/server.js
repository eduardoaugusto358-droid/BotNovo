const express = require('express');
const cors = require('cors');
const { makeWASocket, DisconnectReason, useMultiFileAuthState, makeInMemoryStore } = require('@whiskeysockets/baileys');
const QRCode = require('qrcode');
const axios = require('axios');
const fs = require('fs-extra');
const path = require('path');
const pino = require('pino');
const { v4: uuidv4 } = require('uuid');

const app = express();
const PORT = process.env.PORT || 3001;
const SESSION_PATH = process.env.SESSION_PATH || './sessions';

// Middleware
app.use(cors());
app.use(express.json());

// Logger
const logger = pino({ level: 'info' });

// Store active connections
const connections = new Map();
const qrCodes = new Map();

// Ensure sessions directory exists
fs.ensureDirSync(SESSION_PATH);

// Create WhatsApp connection
async function createConnection(sessionId, webhookUrl = null) {
    try {
        const sessionPath = path.join(SESSION_PATH, sessionId);
        await fs.ensureDir(sessionPath);

        const { state, saveCreds } = await useMultiFileAuthState(sessionPath);
        
        const sock = makeWASocket({
            auth: state,
            logger: pino({ level: 'silent' }),
            printQRInTerminal: false,
            browser: ['WhatsApp Bot', 'Chrome', '1.0.0'],
            generateHighQualityLinkPreview: true,
        });

        // Store connection
        connections.set(sessionId, {
            socket: sock,
            webhookUrl,
            status: 'connecting',
            phone: null,
            lastSeen: new Date(),
        });

        // Handle QR code
        sock.ev.on('connection.update', async (update) => {
            const { connection, lastDisconnect, qr } = update;
            
            if (qr) {
                try {
                    const qrCode = await QRCode.toDataURL(qr);
                    qrCodes.set(sessionId, qrCode);
                    
                    // Notify backend about QR code
                    if (webhookUrl) {
                        try {
                            await axios.post(webhookUrl, {
                                type: 'qr_code',
                                sessionId,
                                qrCode,
                            });
                        } catch (error) {
                            logger.error('Failed to send QR webhook:', error.message);
                        }
                    }
                } catch (error) {
                    logger.error('Failed to generate QR code:', error);
                }
            }

            if (connection === 'close') {
                const shouldReconnect = (lastDisconnect?.error)?.output?.statusCode !== DisconnectReason.loggedOut;
                
                if (shouldReconnect) {
                    logger.info(`Reconnecting session ${sessionId}...`);
                    setTimeout(() => createConnection(sessionId, webhookUrl), 3000);
                } else {
                    logger.info(`Session ${sessionId} logged out`);
                    connections.delete(sessionId);
                    qrCodes.delete(sessionId);
                }
            } else if (connection === 'open') {
                logger.info(`Session ${sessionId} connected successfully`);
                const conn = connections.get(sessionId);
                if (conn) {
                    conn.status = 'connected';
                    conn.phone = sock.user?.id?.split('@')[0] || sock.user?.id;
                    conn.lastSeen = new Date();
                }

                // Remove QR code as it's no longer needed
                qrCodes.delete(sessionId);

                // Notify backend about successful connection
                if (webhookUrl) {
                    try {
                        await axios.post(webhookUrl, {
                            type: 'connected',
                            sessionId,
                            phone: sock.user?.id?.split('@')[0] || sock.user?.id,
                        });
                    } catch (error) {
                        logger.error('Failed to send connection webhook:', error);
                    }
                }
            }
        });

        // Handle credential updates
        sock.ev.on('creds.update', saveCreds);

        // Handle incoming messages
        sock.ev.on('messages.upsert', async (m) => {
            const message = m.messages[0];
            if (!message || message.key.fromMe) return;

            const conn = connections.get(sessionId);
            if (conn && conn.webhookUrl) {
                try {
                    await axios.post(conn.webhookUrl, {
                        type: 'message',
                        sessionId,
                        message: {
                            id: message.key.id,
                            from: message.key.remoteJid,
                            content: message.message?.conversation || 
                                    message.message?.extendedTextMessage?.text || '',
                            timestamp: message.messageTimestamp,
                            messageType: getMessageType(message),
                        }
                    });
                } catch (error) {
                    logger.error('Failed to send message webhook:', error);
                }
            }
        });

        return sock;
    } catch (error) {
        logger.error(`Failed to create connection for ${sessionId}:`, error);
        throw error;
    }
}

// Get message type
function getMessageType(message) {
    if (message.message?.conversation) return 'text';
    if (message.message?.extendedTextMessage) return 'text';
    if (message.message?.imageMessage) return 'image';
    if (message.message?.videoMessage) return 'video';
    if (message.message?.audioMessage) return 'audio';
    if (message.message?.documentMessage) return 'document';
    return 'unknown';
}

// Routes
app.post('/create-session', async (req, res) => {
    try {
        const { sessionId, webhookUrl } = req.body;
        
        if (!sessionId) {
            return res.status(400).json({ error: 'sessionId is required' });
        }

        if (connections.has(sessionId)) {
            return res.status(400).json({ error: 'Session already exists' });
        }

        await createConnection(sessionId, webhookUrl);

        res.json({
            success: true,
            message: 'Session created successfully',
            sessionId,
        });
    } catch (error) {
        logger.error('Create session error:', error);
        res.status(500).json({ error: error.message });
    }
});

app.get('/qr-code/:sessionId', (req, res) => {
    const { sessionId } = req.params;
    const qrCode = qrCodes.get(sessionId);
    
    if (!qrCode) {
        return res.status(404).json({ error: 'QR code not found or session already connected' });
    }

    res.json({ qrCode });
});

app.get('/status/:sessionId', (req, res) => {
    const { sessionId } = req.params;
    const connection = connections.get(sessionId);
    
    if (!connection) {
        return res.status(404).json({ error: 'Session not found' });
    }

    res.json({
        sessionId,
        status: connection.status,
        phone: connection.phone,
        lastSeen: connection.lastSeen,
    });
});

app.post('/send-message', async (req, res) => {
    try {
        const { sessionId, to, message, messageType = 'text' } = req.body;
        
        const connection = connections.get(sessionId);
        if (!connection || connection.status !== 'connected') {
            return res.status(400).json({ error: 'Session not connected' });
        }

        const jid = to.includes('@') ? to : `${to}@s.whatsapp.net`;
        let result;

        switch (messageType) {
            case 'text':
                result = await connection.socket.sendMessage(jid, { text: message });
                break;
            default:
                return res.status(400).json({ error: 'Unsupported message type' });
        }

        res.json({
            success: true,
            messageId: result.key.id,
        });
    } catch (error) {
        logger.error('Send message error:', error);
        res.status(500).json({ error: error.message });
    }
});

app.delete('/session/:sessionId', async (req, res) => {
    try {
        const { sessionId } = req.params;
        const connection = connections.get(sessionId);
        
        if (connection) {
            await connection.socket.logout();
            connections.delete(sessionId);
            qrCodes.delete(sessionId);
        }

        // Remove session files
        const sessionPath = path.join(SESSION_PATH, sessionId);
        await fs.remove(sessionPath);

        res.json({ success: true, message: 'Session deleted successfully' });
    } catch (error) {
        logger.error('Delete session error:', error);
        res.status(500).json({ error: error.message });
    }
});

app.get('/sessions', (req, res) => {
    const sessions = Array.from(connections.entries()).map(([sessionId, conn]) => ({
        sessionId,
        status: conn.status,
        phone: conn.phone,
        lastSeen: conn.lastSeen,
    }));

    res.json({ sessions });
});

// Health check
app.get('/health', (req, res) => {
    res.json({ status: 'ok', timestamp: new Date().toISOString() });
});

app.listen(PORT, () => {
    logger.info(`Baileys service running on port ${PORT}`);
});