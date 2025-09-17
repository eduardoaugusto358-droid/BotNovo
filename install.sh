#!/bin/bash

# WhatsApp Bot Management System - Auto Installer
# Domain: chatbot.auto-atendimento.digital

echo "🚀 WhatsApp Bot Management System"
echo "🌐 Domain: chatbot.auto-atendimento.digital"
echo "==============================================="

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    print_error "Please run as root or with sudo"
    exit 1
fi

# Update system
print_status "Updating system packages..."
apt-get update -y

# Install basic dependencies
print_status "Installing system dependencies..."
apt-get install -y \
    curl wget git build-essential \
    python3 python3-pip python3-venv \
    postgresql postgresql-contrib \
    redis-server \
    nodejs npm \
    nginx \
    ufw

# Install Node.js 18
print_status "Installing Node.js 18..."
curl -fsSL https://deb.nodesource.com/setup_18.x | bash -
apt-get install -y nodejs

# Configure PostgreSQL
print_status "Configuring PostgreSQL..."
systemctl start postgresql
systemctl enable postgresql

sudo -u postgres psql -c "CREATE USER admin WITH PASSWORD 'admin123';" 2>/dev/null || true
sudo -u postgres psql -c "ALTER USER admin CREATEDB;" 2>/dev/null || true
sudo -u postgres psql -c "CREATE DATABASE whatsapp_bot OWNER admin;" 2>/dev/null || true
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE whatsapp_bot TO admin;" 2>/dev/null || true

# Configure Redis
print_status "Configuring Redis..."
systemctl start redis-server
systemctl enable redis-server

# Configure Firewall
print_status "Configuring firewall..."
ufw allow 8000/tcp
ufw allow 3001/tcp
ufw allow 80/tcp
ufw allow 443/tcp
ufw allow 22/tcp
ufw --force enable

# Configure Nginx (optional)
print_status "Configuring Nginx reverse proxy..."
cat > /etc/nginx/sites-available/whatsapp-bot << 'EOF'
server {
    listen 80;
    server_name chatbot.auto-atendimento.digital;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /baileys/ {
        proxy_pass http://localhost:3001/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
EOF

# Enable site
ln -sf /etc/nginx/sites-available/whatsapp-bot /etc/nginx/sites-enabled/
systemctl restart nginx
systemctl enable nginx

print_status "✅ System dependencies installed!"
print_status "📁 Navigate to your project directory and run:"
print_status "   python3 main.py"
print_status ""
print_status "🌐 Access: http://chatbot.auto-atendimento.digital"
print_status "👤 Login: admin / admin123"