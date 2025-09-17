#!/usr/bin/env python3
"""
WhatsApp Bot Management System - Main Entry Point
Execute este arquivo para instalar e iniciar tudo automaticamente
"""

import os
import sys
import subprocess
import time
import signal
import threading
from pathlib import Path

# Cores para output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_banner():
    banner = f"""
{Colors.HEADER}
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║          🤖 WhatsApp Bot Management System 🤖                ║
║                                                               ║
║          🌐 Domain: chatbot.auto-atendimento.digital         ║
║          🚀 Auto-Install & Auto-Start System                 ║
║                                                               ║
║          FastAPI + PostgreSQL + Baileys + React              ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
{Colors.ENDC}
"""
    print(banner)

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

def run_command(command, cwd=None, shell=True):
    """Executa comando de forma segura"""
    try:
        process = subprocess.Popen(
            command,
            shell=shell,
            cwd=cwd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        return process
    except Exception as e:
        print_status(f"Erro executando comando: {e}", "ERROR")
        return None

def check_installation_needed():
    """Verifica se precisa instalar dependências"""
    checks = [
        ("requirements.txt installed", "python -c 'import fastapi, sqlalchemy, psycopg2'"),
        ("Node.js baileys deps", "ls baileys_service/node_modules"),
        ("PostgreSQL running", "sudo systemctl is-active postgresql"),
        ("Redis running", "sudo systemctl is-active redis-server")
    ]
    
    need_install = False
    
    for check_name, command in checks:
        try:
            result = subprocess.run(command, shell=True, capture_output=True, text=True)
            if result.returncode != 0:
                print_status(f"❌ {check_name}", "WARNING")
                need_install = True
            else:
                print_status(f"✅ {check_name}", "SUCCESS")
        except:
            print_status(f"❌ {check_name}", "WARNING")
            need_install = True
    
    return need_install

def auto_install():
    """Executa instalação automática"""
    print_status("🔧 Executando instalação automática...", "HEADER")
    
    try:
        # Executar auto_install.py
        process = subprocess.run([sys.executable, "auto_install.py"], 
                               capture_output=False, text=True)
        
        if process.returncode == 0:
            print_status("✅ Instalação concluída com sucesso!", "SUCCESS")
            return True
        else:
            print_status("❌ Falha na instalação", "ERROR")
            return False
            
    except Exception as e:
        print_status(f"❌ Erro na instalação: {e}", "ERROR")
        return False

def start_services():
    """Inicia todos os serviços"""
    print_status("🚀 Iniciando serviços...", "HEADER")
    
    processes = []
    
    try:
        # 1. Iniciar PostgreSQL e Redis
        print_status("📊 Iniciando PostgreSQL e Redis...")
        subprocess.run("sudo systemctl start postgresql redis-server", shell=True, check=False)
        time.sleep(3)
        
        # 2. Executar migrações se necessário
        print_status("🗄️  Verificando migrações do banco...")
        subprocess.run("alembic upgrade head", shell=True, check=False)
        time.sleep(1)
        
        # 3. Inicializar dados se necessário
        print_status("👤 Verificando usuário admin...")
        subprocess.run(f"{sys.executable} scripts/init_db.py", shell=True, check=False)
        time.sleep(1)
        
        # 4. Iniciar Baileys Service
        print_status("🤖 Iniciando Baileys Service...")
        baileys_process = run_command(
            "npm start", 
            cwd="baileys_service"
        )
        if baileys_process:
            processes.append(("Baileys", baileys_process))
            time.sleep(3)
        
        # 5. Iniciar FastAPI
        print_status("🌐 Iniciando FastAPI Server...")
        
        # Configurar ambiente
        os.environ["HOST"] = "0.0.0.0"
        os.environ["PORT"] = "8000"
        
        # Iniciar FastAPI usando uvicorn
        api_process = run_command([
            sys.executable, "-m", "uvicorn", "main:app",
            "--host", "0.0.0.0", 
            "--port", "8000",
            "--reload"
        ], shell=False)
        
        if api_process:
            processes.append(("FastAPI", api_process))
        
        # Aguardar um pouco para inicialização
        time.sleep(5)
        
        # Verificar se serviços estão rodando
        print_status("🔍 Verificando serviços...", "HEADER")
        
        # Testar API
        try:
            import requests
            response = requests.get("http://localhost:8000/health", timeout=5)
            if response.status_code == 200:
                print_status("✅ FastAPI está funcionando!", "SUCCESS")
            else:
                print_status("⚠️  FastAPI respondeu mas com erro", "WARNING")
        except:
            print_status("⚠️  FastAPI pode estar iniciando...", "WARNING")
        
        # Testar Baileys
        try:
            import requests
            response = requests.get("http://localhost:3001/health", timeout=5)
            if response.status_code == 200:
                print_status("✅ Baileys Service está funcionando!", "SUCCESS")
            else:
                print_status("⚠️  Baileys respondeu mas com erro", "WARNING")
        except:
            print_status("⚠️  Baileys pode estar iniciando...", "WARNING")
        
        print_status("=" * 60, "SUCCESS")
        print_status("🎉 SISTEMA INICIADO COM SUCESSO!", "SUCCESS")
        print_status("=" * 60, "SUCCESS")
        print_status("🌐 URL Principal: http://chatbot.auto-atendimento.digital:8000", "SUCCESS")
        print_status("📚 API Docs: http://chatbot.auto-atendimento.digital:8000/api/docs", "SUCCESS")
        print_status("🤖 Baileys API: http://chatbot.auto-atendimento.digital:3001", "SUCCESS")
        print_status("👤 Login Padrão: admin / admin123", "SUCCESS")
        print_status("⚠️  ALTERE A SENHA APÓS PRIMEIRO LOGIN!", "WARNING")
        print_status("=" * 60, "SUCCESS")
        print_status("🛑 Pressione Ctrl+C para parar o sistema", "INFO")
        
        # Função para cleanup
        def cleanup():
            print_status("\n🛑 Parando serviços...", "WARNING")
            for name, process in processes:
                try:
                    print_status(f"Parando {name}...")
                    process.terminate()
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
                except:
                    pass
            print_status("✅ Todos os serviços foram parados!", "SUCCESS")
        
        # Handler para Ctrl+C
        def signal_handler(sig, frame):
            cleanup()
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        # Aguardar indefinidamente
        try:
            while True:
                time.sleep(1)
                # Verificar se processos ainda estão vivos
                for name, process in processes:
                    if process.poll() is not None:
                        print_status(f"⚠️  {name} parou inesperadamente!", "WARNING")
        except KeyboardInterrupt:
            pass
        finally:
            cleanup()
            
    except Exception as e:
        print_status(f"❌ Erro iniciando serviços: {e}", "ERROR")
        return False

# FastAPI App (importado quando necessário)
def create_app():
    """Cria aplicação FastAPI"""
    try:
        from fastapi import FastAPI, Request
        from fastapi.staticfiles import StaticFiles
        from fastapi.templating import Jinja2Templates
        from fastapi.middleware.cors import CORSMiddleware
        from fastapi.responses import HTMLResponse
        
        # Import routers
        from routers import auth, dashboard, instances, messages, campaigns, finances, groups, webhooks
        
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
        
        # Include routers
        app.include_router(auth.router)
        app.include_router(dashboard.router)
        app.include_router(instances.router)
        app.include_router(messages.router)
        app.include_router(campaigns.router)
        app.include_router(finances.router)
        app.include_router(groups.router)
        app.include_router(webhooks.router)
        
        # Static files and templates
        templates = Jinja2Templates(directory="templates")
        
        # Serve static files
        if os.path.exists("static"):
            app.mount("/static", StaticFiles(directory="static"), name="static")
        
        @app.get("/", response_class=HTMLResponse)
        async def read_root(request: Request):
            """Serve the main application"""
            return templates.TemplateResponse("index.html", {"request": request})
        
        @app.get("/health")
        async def health_check():
            """Health check endpoint"""
            return {
                "status": "healthy",
                "service": "whatsapp-bot-api",
                "version": "1.0.0",
                "domain": "chatbot.auto-atendimento.digital"
            }
        
        return app
        
    except ImportError as e:
        print_status(f"❌ Erro importando módulos: {e}", "ERROR")
        print_status("🔧 Executando instalação automática...", "INFO")
        return None

def main():
    """Função principal"""
    print_banner()
    
    # Verificar se precisa instalar
    print_status("🔍 Verificando instalação...", "HEADER")
    
    if check_installation_needed():
        print_status("🔧 Instalação necessária! Iniciando auto-install...", "WARNING")
        
        if not auto_install():
            print_status("❌ Falha na instalação automática!", "ERROR")
            sys.exit(1)
        
        print_status("✅ Instalação concluída! Iniciando sistema...", "SUCCESS")
    else:
        print_status("✅ Sistema já está instalado!", "SUCCESS")
    
    # Criar app FastAPI
    global app
    app = create_app()
    
    if app is None:
        print_status("❌ Falha ao criar aplicação FastAPI", "ERROR")
        sys.exit(1)
    
    # Iniciar todos os serviços
    start_services()

# Criar instância global da app
app = None

if __name__ == "__main__":
    main()
else:
    # Se importado como módulo, criar app
    app = create_app()