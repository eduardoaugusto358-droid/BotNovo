#!/usr/bin/env python3
"""
WhatsApp Bot Management System - Main Runner
Execute este arquivo para rodar o sistema completo
"""

import subprocess
import sys
import os
import time
import signal
from pathlib import Path

def print_banner():
    banner = """
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║        WhatsApp Bot Management System                         ║
║        Sistema Completo de Gestão de Bots WhatsApp           ║
║                                                               ║
║        🚀 FastAPI + PostgreSQL + Baileys                     ║
║        🎯 Pronto para Produção                               ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
    """
    print(banner)

def check_requirements():
    """Verifica se todas as dependências estão instaladas"""
    print("🔍 Verificando dependências...")
    
    try:
        import fastapi
        import sqlalchemy
        import psycopg2
        import pydantic
        print("✅ Dependências Python OK")
    except ImportError as e:
        print(f"❌ Erro nas dependências Python: {e}")
        print("Execute: pip install -r requirements.txt")
        return False
    
    return True

def run_with_docker():
    """Executa o sistema usando Docker"""
    print("🐳 Iniciando sistema com Docker...")
    
    try:
        # Build e start dos containers
        subprocess.run(["docker-compose", "build"], check=True)
        subprocess.run(["docker-compose", "up", "-d"], check=True)
        
        print("✅ Sistema iniciado com Docker!")
        print("\n📋 Serviços disponíveis:")
        print("  🌐 Frontend: http://localhost:8000")
        print("  📚 API Docs: http://localhost:8000/api/docs")
        print("  🤖 Baileys: http://localhost:3001")
        print("  🗄️  PostgreSQL: localhost:5432")
        print("  🔴 Redis: localhost:6379")
        
        print("\n👤 Login padrão:")
        print("  Usuário: admin")
        print("  Senha: admin123")
        print("  ⚠️  Altere a senha após o primeiro login!")
        
        print("\n📊 Para monitorar os logs:")
        print("  docker-compose logs -f")
        
        print("\n🛑 Para parar o sistema:")
        print("  docker-compose down")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro ao executar Docker: {e}")
        return False
    except FileNotFoundError:
        print("❌ Docker não encontrado. Instale o Docker e Docker Compose.")
        return False

def run_development():
    """Executa o sistema em modo de desenvolvimento"""
    print("🔧 Iniciando sistema em modo desenvolvimento...")
    
    # Lista de processos para limpar ao sair
    processes = []
    
    def cleanup():
        print("\n🛑 Parando serviços...")
        for proc in processes:
            try:
                proc.terminate()
                proc.wait(timeout=5)
            except (ProcessLookupError, subprocess.TimeoutExpired):
                try:
                    proc.kill()
                except ProcessLookupError:
                    pass
        print("✅ Serviços parados!")
    
    def signal_handler(sig, frame):
        cleanup()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        print("🔥 Iniciando FastAPI...")
        api_proc = subprocess.Popen([
            sys.executable, "-m", "uvicorn", "main:app",
            "--host", "0.0.0.0",
            "--port", "8000",
            "--reload"
        ])
        processes.append(api_proc)
        
        print("🤖 Iniciando serviço Baileys...")
        baileys_proc = subprocess.Popen([
            "npm", "start"
        ], cwd="baileys_service")
        processes.append(baileys_proc)
        
        print("✅ Sistema iniciado em modo desenvolvimento!")
        print("\n📋 Serviços disponíveis:")
        print("  🌐 Frontend: http://localhost:8000")
        print("  📚 API Docs: http://localhost:8000/api/docs")
        print("  🤖 Baileys: http://localhost:3001")
        
        print("\n⚠️  Certifique-se de que PostgreSQL e Redis estão rodando!")
        print("  PostgreSQL: localhost:5432")
        print("  Redis: localhost:6379")
        
        print("\n👤 Login padrão:")
        print("  Usuário: admin")
        print("  Senha: admin123")
        
        print("\n🛑 Pressione Ctrl+C para parar o sistema")
        
        # Aguarda até ser interrompido
        try:
            while True:
                time.sleep(1)
                # Verifica se algum processo morreu
                for proc in processes:
                    if proc.poll() is not None:
                        print(f"⚠️  Processo {proc.pid} terminou inesperadamente")
        except KeyboardInterrupt:
            pass
        
    except Exception as e:
        print(f"❌ Erro ao iniciar sistema: {e}")
    finally:
        cleanup()

def main():
    print_banner()
    
    if not check_requirements():
        sys.exit(1)
    
    print("\n🚀 Como deseja executar o sistema?")
    print("1. Docker (Recomendado - Fácil e completo)")
    print("2. Desenvolvimento (Manual - Requer PostgreSQL e Redis)")
    print("3. Sair")
    
    while True:
        choice = input("\nEscolha uma opção (1/2/3): ").strip()
        
        if choice == "1":
            if not os.path.exists("docker-compose.yml"):
                print("❌ docker-compose.yml não encontrado!")
                sys.exit(1)
            
            success = run_with_docker()
            if success:
                input("\nPressione Enter para parar o sistema...")
                subprocess.run(["docker-compose", "down"])
            break
            
        elif choice == "2":
            run_development()
            break
            
        elif choice == "3":
            print("👋 Até logo!")
            sys.exit(0)
            
        else:
            print("❌ Opção inválida. Digite 1, 2 ou 3.")

if __name__ == "__main__":
    main()