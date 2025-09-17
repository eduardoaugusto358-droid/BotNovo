#!/usr/bin/env python3
"""
Comprehensive deployment fix for WhatsApp Bot System
Addresses externally-managed-environment error and other deployment issues
"""

import os
import sys
import subprocess
import json
import time
from pathlib import Path

class DeploymentFixer:
    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.venv_dir = self.base_dir / "venv"
        self.python_exec = self.venv_dir / "bin" / "python"
        self.pip_exec = self.venv_dir / "bin" / "pip"
        self.alembic_exec = self.venv_dir / "bin" / "alembic"
        
    def log(self, message, level="INFO"):
        """Log messages with formatting"""
        levels = {
            "INFO": "ℹ️",
            "SUCCESS": "✅", 
            "ERROR": "❌",
            "WARNING": "⚠️",
            "PROGRESS": "🔧"
        }
        print(f"{levels.get(level, 'ℹ️')} {message}")
        
    def run_command(self, cmd, cwd=None, check=True):
        """Run shell command with proper error handling"""
        self.log(f"Executando: {cmd}", "PROGRESS")
        try:
            result = subprocess.run(
                cmd, shell=True, cwd=cwd or self.base_dir,
                capture_output=True, text=True, check=check
            )
            if result.stdout.strip():
                print(result.stdout.strip())
            return result
        except subprocess.CalledProcessError as e:
            self.log(f"Erro ao executar comando: {e}", "ERROR")
            if e.stderr:
                print(e.stderr)
            if check:
                raise
            return e
            
    def kill_port_processes(self, port):
        """Kill processes using specific port"""
        try:
            result = self.run_command(f"lsof -ti:{port}", check=False)
            if result.returncode == 0 and result.stdout.strip():
                pids = result.stdout.strip().split('\n')
                for pid in pids:
                    self.run_command(f"kill -9 {pid}", check=False)
                self.log(f"Processos mortos na porta {port}", "SUCCESS")
            else:
                self.log(f"Nenhum processo encontrado na porta {port}", "INFO")
        except Exception as e:
            self.log(f"Erro ao matar processos na porta {port}: {e}", "WARNING")
    
    def create_virtual_environment(self):
        """Create Python virtual environment to bypass externally-managed-environment"""
        self.log("Criando ambiente virtual Python...", "PROGRESS")
        
        # Remove existing venv if it exists
        if self.venv_dir.exists():
            self.run_command(f"rm -rf {self.venv_dir}")
            
        # Install python3-venv if not available
        self.run_command("apt update && apt install -y python3-venv python3-dev build-essential", check=False)
        
        # Create virtual environment
        self.run_command(f"python3 -m venv {self.venv_dir}")
        
        # Upgrade pip in virtual environment
        self.run_command(f"{self.pip_exec} install --upgrade pip")
        
        self.log("Ambiente virtual criado com sucesso!", "SUCCESS")
        
    def install_python_dependencies(self):
        """Install all Python dependencies in virtual environment"""
        self.log("Instalando dependências Python...", "PROGRESS")
        
        # Install requirements
        if (self.base_dir / "requirements.txt").exists():
            self.run_command(f"{self.pip_exec} install -r requirements.txt")
        else:
            # Install critical dependencies manually
            critical_deps = [
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
                "jinja2==3.1.3",
                "aiofiles==23.2.1",
                "requests==2.31.0"
            ]
            
            for dep in critical_deps:
                self.run_command(f"{self.pip_exec} install {dep}")
                
        self.log("Dependências Python instaladas!", "SUCCESS")
        
    def install_system_dependencies(self):
        """Install system-level dependencies"""
        self.log("Instalando dependências do sistema...", "PROGRESS")
        
        # Update package list
        self.run_command("apt update")
        
        # Install PostgreSQL and Redis
        self.run_command("apt install -y postgresql postgresql-contrib redis-server")
        
        # Install Node.js and Yarn for Baileys service
        self.run_command("curl -fsSL https://deb.nodesource.com/setup_18.x | bash -", check=False)
        self.run_command("apt install -y nodejs")
        self.run_command("npm install -g yarn", check=False)
        
        self.log("Dependências do sistema instaladas!", "SUCCESS")
        
    def setup_database(self):
        """Setup PostgreSQL database"""
        self.log("Configurando banco de dados PostgreSQL...", "PROGRESS")
        
        # Start PostgreSQL
        self.run_command("systemctl start postgresql")
        self.run_command("systemctl enable postgresql")
        
        # Create database and user
        db_commands = [
            "CREATE DATABASE whatsapp_bot;",
            "CREATE USER bot_user WITH PASSWORD 'bot_password';", 
            "GRANT ALL PRIVILEGES ON DATABASE whatsapp_bot TO bot_user;",
            "ALTER USER bot_user CREATEDB;"
        ]
        
        for cmd in db_commands:
            self.run_command(f'sudo -u postgres psql -c "{cmd}"', check=False)
            
        self.log("Banco de dados configurado!", "SUCCESS")
        
    def setup_environment_file(self):
        """Create or update .env file with proper configuration"""
        self.log("Configurando arquivo de ambiente...", "PROGRESS")
        
        env_content = """# Database Configuration
DATABASE_URL=postgresql://bot_user:bot_password@localhost:5432/whatsapp_bot

# Redis Configuration  
REDIS_URL=redis://localhost:6379

# Application Configuration
SECRET_KEY=your-secret-key-here-change-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=1440
ALGORITHM=HS256

# Frontend Configuration
FRONTEND_URL=http://chatbot.auto-atendimento.digital:8000

# Baileys Service Configuration
BAILEYS_SERVICE_URL=http://localhost:3001

# Server Configuration
HOST=0.0.0.0
PORT=8000
"""
        
        env_file = self.base_dir / ".env"
        with open(env_file, "w") as f:
            f.write(env_content)
            
        self.log("Arquivo .env configurado!", "SUCCESS")
        
    def install_baileys_dependencies(self):
        """Install Node.js dependencies for Baileys service"""
        self.log("Instalando dependências do Baileys...", "PROGRESS")
        
        baileys_dir = self.base_dir / "baileys_service"
        if baileys_dir.exists():
            self.run_command("yarn install", cwd=baileys_dir)
            self.log("Dependências do Baileys instaladas!", "SUCCESS")
        else:
            self.log("Diretório baileys_service não encontrado", "WARNING")
            
    def run_database_migrations(self):
        """Run Alembic database migrations"""
        self.log("Executando migrações do banco de dados...", "PROGRESS")
        
        # Initialize Alembic if not already done
        if not (self.base_dir / "alembic").exists():
            self.run_command(f"{self.alembic_exec} init alembic")
            
        # Run migrations
        self.run_command(f"{self.alembic_exec} upgrade head")
        
        self.log("Migrações executadas!", "SUCCESS")
        
    def create_startup_script(self):
        """Create startup script that uses virtual environment"""
        self.log("Criando script de inicialização...", "PROGRESS")
        
        startup_content = f"""#!/bin/bash

# WhatsApp Bot System Startup Script
# Uses virtual environment to avoid externally-managed-environment issues

set -e

echo "🚀 Iniciando WhatsApp Bot System..."

# Change to app directory
cd {self.base_dir}

# Kill any existing processes on required ports
echo "🔧 Liberando portas..."
lsof -ti:8000 | xargs kill -9 2>/dev/null || echo "Porta 8000 livre"
lsof -ti:3001 | xargs kill -9 2>/dev/null || echo "Porta 3001 livre"

# Start system services
echo "🔧 Iniciando serviços do sistema..."
systemctl start postgresql redis-server

# Start Baileys service in background
echo "🔧 Iniciando serviço Baileys..."
if [ -d "baileys_service" ]; then
    cd baileys_service
    nohup node server.js > ../baileys.log 2>&1 &
    echo $! > ../baileys.pid
    cd ..
    echo "✅ Baileys iniciado (PID: $(cat baileys.pid))"
fi

# Start FastAPI application with virtual environment
echo "🔧 Iniciando aplicação FastAPI..."
{self.python_exec} -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload &
echo $! > fastapi.pid

echo "✅ Sistema iniciado com sucesso!"
echo "🌐 Acesse: http://chatbot.auto-atendimento.digital:8000"
echo "📚 API Docs: http://chatbot.auto-atendimento.digital:8000/docs"

# Keep script running
wait
"""
        
        startup_script = self.base_dir / "start_system.sh"
        with open(startup_script, "w") as f:
            f.write(startup_content)
            
        # Make executable
        self.run_command(f"chmod +x {startup_script}")
        
        self.log("Script de inicialização criado!", "SUCCESS")
        
    def create_simple_startup(self):
        """Create simple Python startup that uses virtual environment"""
        self.log("Criando inicializador Python simples...", "PROGRESS")
        
        simple_startup = f"""#!/usr/bin/env python3
import subprocess
import sys
import os
from pathlib import Path

# Use virtual environment Python
venv_python = Path(__file__).parent / "venv" / "bin" / "python"
if not venv_python.exists():
    print("❌ Ambiente virtual não encontrado. Execute: python3 fix_deployment.py")
    sys.exit(1)

# Change to app directory
os.chdir(Path(__file__).parent)

print("🚀 Iniciando WhatsApp Bot System...")

# Kill existing processes
subprocess.run("lsof -ti:8000 | xargs kill -9 2>/dev/null || true", shell=True)
subprocess.run("lsof -ti:3001 | xargs kill -9 2>/dev/null || true", shell=True)

# Start services
subprocess.run("systemctl start postgresql redis-server", shell=True)

# Start Baileys service
baileys_dir = Path("baileys_service")
if baileys_dir.exists():
    subprocess.Popen(["node", "server.js"], cwd=baileys_dir)
    print("✅ Baileys service iniciado")

# Start FastAPI
print("🔧 Iniciando FastAPI...")
subprocess.run([str(venv_python), "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"])
"""
        
        simple_file = self.base_dir / "run_system.py"
        with open(simple_file, "w") as f:
            f.write(simple_startup)
            
        self.run_command(f"chmod +x {simple_file}")
        
        self.log("Inicializador Python criado!", "SUCCESS")
        
    def test_installation(self):
        """Test if installation was successful"""
        self.log("Testando instalação...", "PROGRESS")
        
        # Test Python imports
        test_script = """
import sys
try:
    import fastapi
    import sqlalchemy
    import psycopg2
    import uvicorn
    import alembic
    print("✅ Todos os módulos Python importados com sucesso!")
    sys.exit(0)
except ImportError as e:
    print(f"❌ Erro ao importar módulo: {e}")
    sys.exit(1)
"""
        
        with open(self.base_dir / "test_imports.py", "w") as f:
            f.write(test_script)
            
        try:
            self.run_command(f"{self.python_exec} test_imports.py")
            self.log("Teste de importação passou!", "SUCCESS")
        except:
            self.log("Teste de importação falhou!", "ERROR")
            
        # Cleanup test file
        (self.base_dir / "test_imports.py").unlink(missing_ok=True)
        
    def fix_all(self):
        """Run complete deployment fix"""
        self.log("=== INICIANDO CORREÇÃO COMPLETA DO DEPLOYMENT ===", "INFO")
        
        try:
            # Kill processes on required ports
            self.kill_port_processes(8000)
            self.kill_port_processes(3001)
            
            # Create virtual environment
            self.create_virtual_environment()
            
            # Install dependencies
            self.install_system_dependencies()
            self.install_python_dependencies()
            self.install_baileys_dependencies()
            
            # Setup configuration
            self.setup_environment_file()
            self.setup_database()
            
            # Database migrations
            self.run_database_migrations()
            
            # Create startup scripts
            self.create_startup_script()
            self.create_simple_startup()
            
            # Test installation
            self.test_installation()
            
            self.log("=== CORREÇÃO COMPLETA FINALIZADA COM SUCESSO! ===", "SUCCESS")
            self.log("", "INFO")
            self.log("🎉 SISTEMA PRONTO PARA USO!", "SUCCESS")
            self.log("", "INFO")
            self.log("Para iniciar o sistema, execute:", "INFO")
            self.log("  python3 run_system.py", "INFO")
            self.log("  OU", "INFO")
            self.log("  ./start_system.sh", "INFO")
            self.log("", "INFO")
            self.log("🌐 URL: http://chatbot.auto-atendimento.digital:8000", "INFO")
            self.log("📚 API: http://chatbot.auto-atendimento.digital:8000/docs", "INFO")
            
        except Exception as e:
            self.log(f"Erro durante correção: {e}", "ERROR")
            raise

if __name__ == "__main__":
    fixer = DeploymentFixer()
    fixer.fix_all()