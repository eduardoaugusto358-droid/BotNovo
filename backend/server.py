#!/usr/bin/env python3
"""
WhatsApp Bot Management System - Backend Server
"""

import sys
import os
from pathlib import Path
from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv
import logging
from datetime import datetime

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="WhatsApp Bot Management System",
    description="Sistema completo de gestão de bots WhatsApp",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# Database configuration for Emergent platform (using MongoDB for now)
try:
    from motor.motor_asyncio import AsyncIOMotorClient
    
    # Use MongoDB from Emergent platform
    MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
    DB_NAME = os.environ.get('DB_NAME', 'whatsapp_bot')
    
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    
    logger.info(f"Connected to MongoDB: {DB_NAME}")
    
except Exception as e:
    logger.error(f"Database connection error: {e}")
    # Fallback to in-memory storage for development
    db = None

# Resolve project directories regardless of the current working directory
BASE_DIR = Path(__file__).resolve().parent.parent
TEMPLATES_DIR = BASE_DIR / "templates"
STATIC_DIR = BASE_DIR / "static"

# Templates and static files
templates = None
if TEMPLATES_DIR.exists():
    templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

# Serve static files if they exist
if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# API Routes
@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "whatsapp-bot-api",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/")
async def root():
    """Root API endpoint"""
    return {"message": "WhatsApp Bot Management System API"}

# Authentication endpoints
@app.post("/api/auth/login")
async def login(credentials: dict):
    """Login endpoint"""
    username = credentials.get('username')
    password = credentials.get('password')
    
    # Simple authentication for demo
    if username == "admin" and password == "admin123":
        return {
            "access_token": "demo-token-12345",
            "token_type": "bearer",
            "user": {
                "id": "1",
                "username": username,
                "name": "Administrator"
            }
        }
    else:
        raise HTTPException(status_code=401, detail="Invalid credentials")

@app.get("/api/auth/me")
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get current user info"""
    return {
        "id": "1",
        "username": "admin",
        "name": "Administrator"
    }

# Dashboard endpoints
@app.get("/api/dashboard/stats")
async def get_dashboard_stats():
    """Get dashboard statistics"""
    return {
        "total_instances": 2,
        "active_instances": 1,
        "total_messages": 156,
        "messages_today": 23,
        "total_campaigns": 5,
        "active_campaigns": 2,
        "total_revenue": 1250.00,
        "monthly_revenue": 340.00
    }

# WhatsApp instances endpoints
@app.get("/api/instances")
async def get_instances():
    """Get WhatsApp instances"""
    return [
        {
            "id": "1",
            "name": "Instância Principal",
            "phone": "+55 11 99999-9999",
            "status": "connected",
            "qr_code": None,
            "created_at": "2024-01-15T10:30:00Z"
        },
        {
            "id": "2", 
            "name": "Instância Suporte",
            "phone": "+55 11 88888-8888",
            "status": "disconnected",
            "qr_code": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==",
            "created_at": "2024-01-16T14:20:00Z"
        }
    ]

@app.post("/api/instances")
async def create_instance(instance_data: dict):
    """Create new WhatsApp instance"""
    return {
        "id": "3",
        "name": instance_data.get("name", "Nova Instância"),
        "phone": None,
        "status": "connecting",
        "qr_code": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==",
        "created_at": datetime.now().isoformat()
    }

# Messages endpoints
@app.get("/api/messages")
async def get_messages():
    """Get messages"""
    return [
        {
            "id": "1",
            "instance_id": "1",
            "contact_name": "João Silva",
            "contact_phone": "+55 11 77777-7777",
            "message": "Olá! Gostaria de saber mais sobre os produtos.",
            "type": "received",
            "timestamp": "2024-01-17T09:15:00Z"
        },
        {
            "id": "2",
            "instance_id": "1", 
            "contact_name": "Maria Santos",
            "contact_phone": "+55 11 66666-6666",
            "message": "Obrigado pelo atendimento!",
            "type": "received",
            "timestamp": "2024-01-17T08:30:00Z"
        }
    ]

@app.post("/api/messages/send")
async def send_message(message_data: dict):
    """Send message"""
    return {
        "id": "3",
        "instance_id": message_data.get("instance_id"),
        "contact_phone": message_data.get("to"),
        "message": message_data.get("message"),
        "type": "sent",
        "status": "sent",
        "timestamp": datetime.now().isoformat()
    }

# Campaigns endpoints
@app.get("/api/campaigns")
async def get_campaigns():
    """Get campaigns"""
    return [
        {
            "id": "1",
            "name": "Promoção Verão 2024",
            "message": "🌞 Aproveite nossa promoção de verão! Descontos de até 50%",
            "status": "active",
            "sent_count": 120,
            "total_contacts": 150,
            "created_at": "2024-01-10T14:00:00Z"
        },
        {
            "id": "2",
            "name": "Lançamento Produto",
            "message": "🚀 Conheça nosso novo produto! Acesse nosso site.",
            "status": "completed",
            "sent_count": 85,
            "total_contacts": 85,
            "created_at": "2024-01-05T10:00:00Z"
        }
    ]

@app.post("/api/campaigns")
async def create_campaign(campaign_data: dict):
    """Create new campaign"""
    return {
        "id": "3",
        "name": campaign_data.get("name"),
        "message": campaign_data.get("message"),
        "status": "draft",
        "sent_count": 0,
        "total_contacts": 0,
        "created_at": datetime.now().isoformat()
    }

# Finance endpoints
@app.get("/api/finances")
async def get_finances():
    """Get financial data"""
    return [
        {
            "id": "1",
            "description": "Assinatura Mensal",
            "amount": 99.90,
            "type": "income",
            "date": "2024-01-15",
            "category": "subscription"
        },
        {
            "id": "2",
            "description": "Mensagens SMS",
            "amount": -25.50,
            "type": "expense", 
            "date": "2024-01-14",
            "category": "messaging"
        }
    ]

# Frontend route
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """Serve the WhatsApp Bot Management frontend"""
    try:
        if templates is not None:
            return templates.TemplateResponse("index.html", {"request": request})
        raise RuntimeError("Templates directory not available")
    except Exception as e:
        logger.error(f"Error rendering template: {e}")
        # Fallback HTML interface
        return HTMLResponse("""
        <!DOCTYPE html>
        <html>
        <head>
            <title>WhatsApp Bot Management System</title>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <style>
                body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }
                .container { max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
                .header { text-align: center; margin-bottom: 30px; }
                .header h1 { color: #2c3e50; margin: 0; }
                .header p { color: #7f8c8d; margin: 10px 0; }
                .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; margin-top: 30px; }
                .card { background: #f8f9fa; padding: 20px; border-radius: 8px; border-left: 4px solid #3498db; }
                .card h3 { margin-top: 0; color: #2c3e50; }
                .status { display: inline-block; padding: 4px 8px; border-radius: 4px; font-size: 12px; font-weight: bold; }
                .status.connected { background: #d4edda; color: #155724; }
                .btn { display: inline-block; padding: 10px 20px; background: #3498db; color: white; text-decoration: none; border-radius: 5px; margin: 5px; }
                .btn:hover { background: #2980b9; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🤖 WhatsApp Bot Management System</h1>
                    <p>Sistema de gestão de bots WhatsApp - Versão 1.0.0</p>
                    <p><strong>Status:</strong> <span class="status connected">Sistema Ativo</span></p>
                </div>
                
                <div class="grid">
                    <div class="card">
                        <h3>📊 Dashboard</h3>
                        <p>Visualize estatísticas e métricas do sistema</p>
                        <a href="/api/dashboard/stats" class="btn">Ver Estatísticas</a>
                    </div>
                    
                    <div class="card">
                        <h3>📱 Instâncias WhatsApp</h3>
                        <p>Gerencie suas conexões WhatsApp</p>
                        <a href="/api/instances" class="btn">Ver Instâncias</a>
                    </div>
                    
                    <div class="card">
                        <h3>💬 Mensagens</h3>
                        <p>Visualize e envie mensagens</p>
                        <a href="/api/messages" class="btn">Ver Mensagens</a>
                    </div>
                    
                    <div class="card">
                        <h3>📢 Campanhas</h3>
                        <p>Gerencie campanhas de marketing</p>
                        <a href="/api/campaigns" class="btn">Ver Campanhas</a>
                    </div>
                    
                    <div class="card">
                        <h3>💰 Finanças</h3>
                        <p>Controle financeiro do sistema</p>
                        <a href="/api/finances" class="btn">Ver Finanças</a>
                    </div>
                    
                    <div class="card">
                        <h3>📚 API Documentation</h3>
                        <p>Documentação completa da API</p>
                        <a href="/api/docs" class="btn">Ver Docs</a>
                    </div>
                </div>
                
                <div style="margin-top: 40px; text-align: center; color: #7f8c8d;">
                    <p>🌐 Domain: 78.46.250.112 | 🚀 Powered by FastAPI</p>
                </div>
            </div>
        </body>
        </html>
        """)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
