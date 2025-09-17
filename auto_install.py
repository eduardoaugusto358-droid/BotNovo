#!/usr/bin/env python3
"""
Auto Installation Script
Instala todas as dependências automaticamente
"""

import subprocess
import sys
import os
import platform
import time
import urllib.request
import shutil
from pathlib import Path

class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_status(message, status="INFO"):
    colors = {
        "INFO": Colors.OKBLUE,
        "SUCCESS": Colors.OKGREEN,
        "WARNING": Colors.WARNING,
        "ERROR": Colors.FAIL,
        "HEADER": Colors.HEADER
    }
    color = colors.get(status, Colors.OKBLUE)
    print(f"{color}[{status}]{Colors.ENDC} {message}")

def run_command(command, cwd=None, check=True):
    """Executa comando e retorna resultado"""
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            cwd=cwd, 
            check=check,
            capture_output=True,
            text=True
        )
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.CalledProcessError as e:
        return False, e.stdout, e.stderr

def check_and_install_system_deps():
    """Verifica e instala dependências do sistema"""
    print_status("Verificando dependências do sistema...", "HEADER")
    
    system = platform.system().lower()
    
    if system == "linux":
        # Atualizar packages
        print_status("Atualizando packages do sistema...")
        run_command("sudo apt-get update", check=False)
        
        # Instalar dependências básicas
        deps = [
            "curl", "wget", "git", "build-essential", 
            "postgresql", "postgresql-contrib", "redis-server",
            "python3-dev", "python3-pip", "python3-venv",
            "nodejs", "npm"
        ]
        
        for dep in deps:
            print_status(f"Verificando {dep}...")
            success, _, _ = run_command(f"which {dep}", check=False)
            if not success:
                print_status(f"Instalando {dep}...")
                run_command(f"sudo apt-get install -y {dep}", check=False)
        
        # Instalar Node.js atualizado se necessário
        success, stdout, _ = run_command("node --version", check=False)
        if not success or not stdout.strip().startswith("v18"):
            print_status("Instalando Node.js 18...")
            run_command("curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -", check=False)
            run_command("sudo apt-get install -y nodejs", check=False)
        
        print_status("Dependências do sistema verificadas!", "SUCCESS")
    
    elif system == "darwin":  # macOS
        print_status("Sistema macOS detectado")
        # Verificar Homebrew
        success, _, _ = run_command("which brew", check=False)
        if not success:
            print_status("Instalando Homebrew...")
            run_command('/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"')
        
        # Instalar dependências
        deps = ["postgresql", "redis", "node"]
        for dep in deps:
            run_command(f"brew install {dep}", check=False)
    
    else:
        print_status("Sistema Windows detectado - usando WSL ou instale manualmente", "WARNING")

def setup_postgresql():
    """Configura PostgreSQL"""
    print_status("Configurando PostgreSQL...", "HEADER")
    
    try:
        # Iniciar PostgreSQL
        run_command("sudo systemctl start postgresql", check=False)
        run_command("sudo systemctl enable postgresql", check=False)
        
        # Configurar usuário e banco
        commands = [
            "sudo -u postgres psql -c \"CREATE USER admin WITH PASSWORD 'admin123';\"",
            "sudo -u postgres psql -c \"ALTER USER admin CREATEDB;\"",
            "sudo -u postgres psql -c \"CREATE DATABASE whatsapp_bot OWNER admin;\"",
            "sudo -u postgres psql -c \"GRANT ALL PRIVILEGES ON DATABASE whatsapp_bot TO admin;\""
        ]
        
        for cmd in commands:
            run_command(cmd, check=False)
        
        print_status("PostgreSQL configurado!", "SUCCESS")
        
    except Exception as e:
        print_status(f"Erro configurando PostgreSQL: {e}", "WARNING")

def setup_redis():
    """Configura Redis"""
    print_status("Configurando Redis...", "HEADER")
    
    try:
        run_command("sudo systemctl start redis-server", check=False)
        run_command("sudo systemctl enable redis-server", check=False)
        print_status("Redis configurado!", "SUCCESS")
    except Exception as e:
        print_status(f"Erro configurando Redis: {e}", "WARNING")

def install_python_deps():
    """Instala dependências Python"""
    print_status("Instalando dependências Python...", "HEADER")
    
    try:
        # Upgrade pip
        print_status("Atualizando pip...")
        result = run_command(f"{sys.executable} -m pip install --upgrade pip")
        if not result[0]:
            print_status(f"Aviso pip: {result[2]}", "WARNING")
        
        # Instalar requirements individuais para melhor controle
        requirements = [
            "fastapi==0.110.1",
            "uvicorn[standard]==0.25.0", 
            "sqlalchemy==2.0.25",
            "psycopg2-binary==2.9.9",
            "alembic==1.13.1",
            "python-jose[cryptography]==3.3.0",
            "passlib[bcrypt]==1.7.4",
            "python-multipart==0.0.9",
            "python-dotenv==1.0.1",
            "pydantic==2.6.4",
            "pydantic-settings==2.2.1",
            "bcrypt==4.1.2",
            "asyncpg==0.29.0",
            "websockets==12.0",
            "aiofiles==23.2.1",
            "jinja2==3.1.3",
            "redis==5.0.1",
            "requests==2.31.0",
            "qrcode==7.4.2",
            "pillow==10.2.0",
            "httpx==0.26.0"
        ]
        
        for req in requirements:
            print_status(f"Instalando {req}...")
            result = run_command(f"{sys.executable} -m pip install {req}")
            if not result[0]:
                print_status(f"Erro instalando {req}: {result[2]}", "WARNING")
        
        # Instalar requirements.txt como backup
        if os.path.exists("requirements.txt"):
            print_status("Instalando requirements.txt...")
            result = run_command(f"{sys.executable} -m pip install -r requirements.txt")
            if not result[0]:
                print_status(f"Aviso requirements.txt: {result[2]}", "WARNING")
        
        # Verificar se as principais dependências foram instaladas
        test_imports = [
            "fastapi", "sqlalchemy", "psycopg2", "alembic", 
            "pydantic", "uvicorn", "redis", "httpx"
        ]
        
        for module in test_imports:
            result = run_command(f"{sys.executable} -c 'import {module}'")
            if result[0]:
                print_status(f"✅ {module} instalado", "SUCCESS")
            else:
                print_status(f"❌ {module} falhou", "ERROR")
                # Tentar instalar individualmente
                run_command(f"{sys.executable} -m pip install {module}")
        
        print_status("Dependências Python instaladas!", "SUCCESS")
        
    except Exception as e:
        print_status(f"Erro instalando dependências Python: {e}", "ERROR")
        return False
    
    return True

def install_node_deps():
    """Instala dependências Node.js"""
    print_status("Instalando dependências Node.js...", "HEADER")
    
    baileys_dir = "baileys_service"
    if os.path.exists(baileys_dir):
        print_status("Instalando dependências do Baileys...")
        run_command("npm install", cwd=baileys_dir)
        print_status("Dependências Node.js instaladas!", "SUCCESS")
    else:
        print_status("Diretório baileys_service não encontrado", "WARNING")

def setup_database():
    """Configura banco de dados"""
    print_status("Configurando banco de dados...", "HEADER")
    
    try:
        # Executar migrações
        if os.path.exists("alembic.ini"):
            print_status("Executando migrações...")
            run_command("alembic upgrade head", check=False)
        
        # Inicializar dados
        if os.path.exists("scripts/init_db.py"):
            print_status("Inicializando dados...")
            run_command(f"{sys.executable} scripts/init_db.py", check=False)
        
        print_status("Banco de dados configurado!", "SUCCESS")
        
    except Exception as e:
        print_status(f"Erro configurando banco: {e}", "WARNING")

def create_systemd_services():
    """Cria serviços systemd para auto-start"""
    print_status("Criando serviços systemd...", "HEADER")
    
    try:
        current_dir = os.getcwd()
        python_path = sys.executable
        
        # Serviço FastAPI
        fastapi_service = f"""[Unit]
Description=WhatsApp Bot FastAPI
After=network.target postgresql.service redis.service

[Service]
Type=simple
User={os.getenv('USER', 'root')}
WorkingDirectory={current_dir}
Environment=PATH={os.path.dirname(python_path)}
ExecStart={python_path} -m uvicorn main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
"""
        
        # Serviço Baileys
        baileys_service = f"""[Unit]
Description=WhatsApp Bot Baileys Service
After=network.target

[Service]
Type=simple
User={os.getenv('USER', 'root')}
WorkingDirectory={current_dir}/baileys_service
ExecStart=/usr/bin/node server.js
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
"""
        
        # Escrever arquivos de serviço
        with open("/tmp/whatsapp-bot-api.service", "w") as f:
            f.write(fastapi_service)
        
        with open("/tmp/whatsapp-bot-baileys.service", "w") as f:
            f.write(baileys_service)
        
        # Instalar serviços
        commands = [
            "sudo mv /tmp/whatsapp-bot-api.service /etc/systemd/system/",
            "sudo mv /tmp/whatsapp-bot-baileys.service /etc/systemd/system/",
            "sudo systemctl daemon-reload",
            "sudo systemctl enable whatsapp-bot-api",
            "sudo systemctl enable whatsapp-bot-baileys"
        ]
        
        for cmd in commands:
            run_command(cmd, check=False)
        
        print_status("Serviços systemd criados!", "SUCCESS")
        
    except Exception as e:
        print_status(f"Erro criando serviços: {e}", "WARNING")

def configure_firewall():
    """Configura firewall"""
    print_status("Configurando firewall...", "HEADER")
    
    try:
        commands = [
            "sudo ufw allow 8000/tcp",
            "sudo ufw allow 3001/tcp",
            "sudo ufw allow 5432/tcp",
            "sudo ufw allow 6379/tcp",
            "sudo ufw --force enable"
        ]
        
        for cmd in commands:
            run_command(cmd, check=False)
        
        print_status("Firewall configurado!", "SUCCESS")
        
    except Exception as e:
        print_status(f"Erro configurando firewall: {e}", "WARNING")

def create_startup_script():
    """Cria script de inicialização"""
    current_dir = os.getcwd()
    python_path = sys.executable
    
    startup_script = f"""#!/bin/bash
# WhatsApp Bot Auto Start Script

cd {current_dir}

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
"""
    
    with open("start_system.sh", "w") as f:
        f.write(startup_script)
    
    os.chmod("start_system.sh", 0o755)
    print_status("Script de inicialização criado: ./start_system.sh", "SUCCESS")

def main():
    """Função principal de instalação"""
    print_status("🚀 INICIANDO INSTALAÇÃO AUTOMÁTICA", "HEADER")
    print_status("WhatsApp Bot Management System", "HEADER")
    print_status("Domínio: 78.46.250.112", "HEADER")
    print_status("=" * 50, "HEADER")
    
    try:
        # 1. Dependências do sistema
        check_and_install_system_deps()
        time.sleep(1)
        
        # 2. PostgreSQL
        setup_postgresql()
        time.sleep(1)
        
        # 3. Redis
        setup_redis()
        time.sleep(1)
        
        # 4. Python dependencies
        install_python_deps()
        time.sleep(1)
        
        # 5. Node.js dependencies
        install_node_deps()
        time.sleep(1)
        
        # 6. Database setup
        setup_database()
        time.sleep(1)
        
        # 7. Systemd services
        create_systemd_services()
        time.sleep(1)
        
        # 8. Firewall
        configure_firewall()
        time.sleep(1)
        
        # 9. Startup script
        create_startup_script()
        
        print_status("=" * 50, "SUCCESS")
        print_status("🎉 INSTALAÇÃO CONCLUÍDA COM SUCESSO!", "SUCCESS")
        print_status("=" * 50, "SUCCESS")
        print_status("🌐 URL: http://78.46.250.112:8000", "SUCCESS")
        print_status("📚 API: http://78.46.250.112:8000/api/docs", "SUCCESS")
        print_status("👤 Login: admin / admin123", "SUCCESS")
        print_status("🔧 Para iniciar: ./start_system.sh", "SUCCESS")
        print_status("📋 Status: sudo systemctl status whatsapp-bot-*", "SUCCESS")
        
        return True
        
    except Exception as e:
        print_status(f"❌ ERRO NA INSTALAÇÃO: {e}", "ERROR")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)