#!/usr/bin/env python3
"""
WhatsApp Bot Management System - Main Entry Point
Execute este arquivo para instalar e iniciar tudo automaticamente
"""

import importlib.util
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
║          🌐 Domain: 78.46.250.112         ║
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

PACKAGE_IMPORT_OVERRIDES = {
    "python-jose": "jose",
    "python-dotenv": "dotenv",
    "psycopg2-binary": "psycopg2",
    "python-multipart": "multipart",
    "pillow": "PIL",
}


def read_requirements():
    """Lê requirements.txt e retorna lista de dependências"""
    req_path = Path("requirements.txt")
    if not req_path.exists():
        return []

    requirements = []
    for line in req_path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        requirements.append(line)
    return requirements


def normalize_requirement_name(requirement):
    """Extrai nome base do pacote sem versão ou extras"""
    name = requirement.split(";")[0].strip()
    for separator in ("==", ">=", "<=", "~=", "!=", ">", "<"):
        if separator in name:
            name = name.split(separator, 1)[0].strip()
    if "[" in name:
        name = name.split("[", 1)[0].strip()
    return name


def requirement_to_module(requirement):
    """Mapeia requirement para nome de módulo importável"""
    base_name = normalize_requirement_name(requirement)
    if not base_name:
        return ""
    if base_name in PACKAGE_IMPORT_OVERRIDES:
        return PACKAGE_IMPORT_OVERRIDES[base_name]
    return base_name.replace("-", "_")


def module_available(module_name):
    """Verifica se módulo pode ser importado"""
    if not module_name:
        return True

    try:
        if importlib.util.find_spec(module_name) is not None:
            return True
    except Exception:
        pass

    try:
        result = subprocess.run(
            [sys.executable, "-c", f"import {module_name}"],
            capture_output=True,
            text=True,
        )
        return result.returncode == 0
    except Exception:
        return False


def force_install_critical_deps(missing_requirements=None):
    """Força instalação das dependências informadas ou de requirements.txt"""
    dependencies = missing_requirements or read_requirements()
    if not dependencies:
        print_status("⚠️  Nenhuma dependência para instalar", "WARNING")
        return

    print_status("🔧 Garantindo dependências Python...", "HEADER")

    subprocess.run(
        [sys.executable, "-m", "pip", "install", "--upgrade", "pip"],
        capture_output=True,
    )

    for dep in dependencies:
        print_status(f"📦 Instalando {dep}...")
        try:
            result = subprocess.run(
                [sys.executable, "-m", "pip", "install", dep],
                capture_output=True,
                text=True,
            )
            if result.returncode != 0:
                print_status(
                    f"⚠️  Problema instalando {dep}: {result.stderr}",
                    "WARNING",
                )
        except Exception as e:
            print_status(f"❌ Erro instalando {dep}: {e}", "ERROR")

    if Path("requirements.txt").exists():
        print_status("📄 Sincronizando requirements.txt...")
        subprocess.run(
            [
                sys.executable,
                "-m",
                "pip",
                "install",
                "-r",
                "requirements.txt",
            ],
            capture_output=True,
        )

def check_installation_needed():
    """Verifica se precisa instalar dependências"""
    print_status("🔍 Verificando dependências...", "HEADER")

    requirements = read_requirements()
    missing_requirements = []

    if requirements:
        print_status("📦 Verificando pacotes Python obrigatórios...")
        for requirement in requirements:
            module_name = requirement_to_module(requirement)
            if module_available(module_name):
                print_status(f"✅ {module_name} OK", "SUCCESS")
            else:
                print_status(
                    f"❌ {module_name or requirement} faltando (pacote {requirement})",
                    "WARNING",
                )
                missing_requirements.append(requirement)
    else:
        print_status("⚠️  requirements.txt não encontrado", "WARNING")

    # Verificar serviços do sistema
    services = [
        ("PostgreSQL", "sudo systemctl is-active postgresql"),
        ("Redis", "sudo systemctl is-active redis-server"),
        ("Node.js Baileys", "ls baileys_service/node_modules")
    ]

    services_need_install = False

    for service_name, command in services:
        try:
            result = subprocess.run(command, shell=True, capture_output=True, text=True)
            if result.returncode == 0:
                print_status(f"✅ {service_name} OK", "SUCCESS")
            else:
                print_status(f"❌ {service_name} PRECISA INSTALAR", "WARNING")
                services_need_install = True
        except:
            print_status(f"❌ {service_name} ERRO", "WARNING")
            services_need_install = True

    if missing_requirements:
        unique_missing = sorted(set(missing_requirements))
        print_status(
            f"📦 Dependências faltando: {', '.join(unique_missing)}",
            "WARNING",
        )
        force_install_critical_deps(unique_missing)

        remaining_missing = []
        for requirement in unique_missing:
            module_name = requirement_to_module(requirement)
            if not module_available(module_name):
                remaining_missing.append(requirement)

        if not remaining_missing:
            print_status("✅ Dependências Python corrigidas!", "SUCCESS")

        missing_requirements = remaining_missing

    need_install = len(missing_requirements) > 0 or services_need_install

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
            response = requests.get("http://78.46.250.112:8000/health", timeout=5)
            if response.status_code == 200:
                print_status("✅ FastAPI está funcionando!", "SUCCESS")
            else:
                print_status("⚠️  FastAPI respondeu mas com erro", "WARNING")
        except:
            print_status("⚠️  FastAPI pode estar iniciando...", "WARNING")
        
        # Testar Baileys
        try:
            import requests
            response = requests.get("http://78.46.250.112:3001/health", timeout=5)
            if response.status_code == 200:
                print_status("✅ Baileys Service está funcionando!", "SUCCESS")
            else:
                print_status("⚠️  Baileys respondeu mas com erro", "WARNING")
        except:
            print_status("⚠️  Baileys pode estar iniciando...", "WARNING")
        
        print_status("=" * 60, "SUCCESS")
        print_status("🎉 SISTEMA INICIADO COM SUCESSO!", "SUCCESS")
        print_status("=" * 60, "SUCCESS")
        print_status("🌐 URL Principal: http://78.46.250.112:8000", "SUCCESS")
        print_status("📚 API Docs: http://78.46.250.112:8000/api/docs", "SUCCESS")
        print_status("🤖 Baileys API: http://78.46.250.112:3001", "SUCCESS")
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
                "domain": "78.46.250.112"
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