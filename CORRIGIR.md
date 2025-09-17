# 🔧 COMO CORRIGIR O PROBLEMA

## ⚡ SOLUÇÃO RÁPIDA

Execute estes comandos na ordem:

```bash
# 1. Corrigir instalação
python3 fix_install.py

# 2. Iniciar sistema
python3 start.py
```

## 🔍 DIAGNÓSTICO DO PROBLEMA

O erro "No module named 'sqlalchemy'" indica que as dependências Python não foram instaladas corretamente.

## 📋 COMANDOS ALTERNATIVOS

### Opção 1: Instalação Manual das Dependências
```bash
pip3 install --upgrade pip
pip3 install fastapi uvicorn sqlalchemy psycopg2-binary pydantic python-dotenv jinja2
pip3 install -r requirements.txt
python3 start.py
```

### Opção 2: Usar Script Simplificado
```bash
python3 start.py
# Este script vai instalar tudo e iniciar automaticamente
```

### Opção 3: Instalação Via Sistema
```bash
sudo apt update
sudo apt install python3-pip python3-dev
pip3 install -r requirements.txt
```

## 🚀 DEPOIS DE CORRIGIR

Quando as dependências estiverem instaladas:

```bash
# Iniciar serviços do sistema
sudo systemctl start postgresql redis-server

# Executar migrações
alembic upgrade head

# Inicializar dados
python3 scripts/init_db.py

# Iniciar aplicação
python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

## 🌐 VERIFICAR SE FUNCIONOU

```bash
# Testar API
curl http://chatbot.auto-atendimento.digital:8000/health

# Testar se módulos foram instalados
python3 -c "import fastapi, sqlalchemy, psycopg2; print('✅ Dependências OK')"
```

## 🔄 SE AINDA NÃO FUNCIONAR

1. **Verificar versão Python**:
```bash
python3 --version
# Deve ser 3.8+
```

2. **Verificar pip**:
```bash
pip3 --version
which pip3
```

3. **Instalar via apt** (Ubuntu/Debian):
```bash
sudo apt install python3-fastapi python3-sqlalchemy python3-psycopg2
```

4. **Verificar permissões**:
```bash
sudo chown -R $USER:$USER .
chmod +x *.py
```

## ⚠️ NOTAS IMPORTANTES

- Use `python3` ao invés de `python`
- Use `pip3` ao invés de `pip` 
- Execute com `sudo` se necessário para instalação de sistema
- Verifique se PostgreSQL e Redis estão rodando:
  ```bash
  sudo systemctl status postgresql redis-server
  ```

## 🎯 RESULTADO ESPERADO

Após correção, você deve conseguir:
- ✅ Acessar http://chatbot.auto-atendimento.digital:8000
- ✅ Ver a interface de login
- ✅ Fazer login com admin/admin123
- ✅ Acessar todas as funcionalidades

---

**Se ainda houver problemas, execute `python3 fix_install.py` novamente e depois `python3 start.py`**