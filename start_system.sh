#!/bin/bash
# WhatsApp Bot Auto Start Script

cd /app

echo "🚀 Iniciando WhatsApp Bot Management System..."

# Start services
sudo systemctl start postgresql redis-server
sleep 2

# Start application services
sudo systemctl start whatsapp-bot-api
sudo systemctl start whatsapp-bot-baileys

echo "✅ Sistema iniciado!"
echo "🌐 Acesse: http://78.46.250.112:8000"
echo "📚 API Docs: http://78.46.250.112:8000/api/docs"
echo "👤 Login: admin / admin123"
