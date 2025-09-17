#!/usr/bin/env python3
"""
Fix Installation Script
Corrige problemas de instalação das dependências
"""

import subprocess
import sys
import os

def run_cmd(cmd):
    """Executa comando e exibe resultado"""
    print(f"🔧 Executando: {cmd}")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Sucesso")
            if result.stdout:
                print(result.stdout)
        else:
            print(f"⚠️  Aviso/Erro:")
            if result.stderr:
                print(result.stderr)
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

def main():
    print("🚀 Corrigindo instalação das dependências...")
    
    # 1. Atualizar pip
    print("\n1. Atualizando pip...")
    run_cmd(f"{sys.executable} -m pip install --upgrade pip")
    
    # 2. Instalar dependências críticas primeiro
    print("\n2. Instalando dependências críticas...")
    critical_deps = [
        "wheel",
        "setuptools", 
        "fastapi",
        "uvicorn[standard]",
        "sqlalchemy",
        "psycopg2-binary",
        "pydantic",
        "python-dotenv"
    ]
    
    for dep in critical_deps:
        print(f"\n📦 Instalando {dep}...")
        run_cmd(f"{sys.executable} -m pip install '{dep}'")
    
    # 3. Instalar requirements.txt
    print("\n3. Instalando requirements.txt...")
    if os.path.exists("requirements.txt"):
        run_cmd(f"{sys.executable} -m pip install -r requirements.txt")
    
    # 4. Verificar instalação
    print("\n4. Verificando instalação...")
    test_modules = ["fastapi", "sqlalchemy", "psycopg2", "pydantic", "uvicorn"]
    
    all_ok = True
    for module in test_modules:
        try:
            result = subprocess.run([sys.executable, "-c", f"import {module}"], capture_output=True)
            if result.returncode == 0:
                print(f"✅ {module} OK")
            else:
                print(f"❌ {module} FALHOU")
                all_ok = False
        except:
            print(f"❌ {module} ERRO")
            all_ok = False
    
    if all_ok:
        print("\n🎉 Todas as dependências instaladas com sucesso!")
        print("✅ Execute agora: python3 main.py")
    else:
        print("\n⚠️  Algumas dependências falharam.")
        print("🔧 Tente executar manualmente:")
        print("   pip3 install -r requirements.txt")
    
    return all_ok

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)