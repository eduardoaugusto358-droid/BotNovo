# 🚀 COMO EXECUTAR O SISTEMA

## ⚡ EXECUÇÃO SIMPLES - UM COMANDO APENAS

```bash
python3 main.py
```

**Isso fará TUDO automaticamente:**

1. ✅ **Verificar e instalar** todas as dependências:
   - Python packages (FastAPI, SQLAlchemy, etc.)
   - Node.js packages (Baileys, Express, etc.)
   - PostgreSQL e Redis
   - Nginx (proxy reverso)

2. ✅ **Configurar sistema**:
   - Criar banco de dados
   - Executar migrações
   - Criar usuário admin
   - Configurar firewall

3. ✅ **Iniciar todos os serviços**:
   - FastAPI (port 8000)
   - Baileys Service (port 3001)
   - PostgreSQL (port 5432)
   - Redis (port 6379)

## 🌐 ACESSOS

- **🖥️ Interface Principal**: http://chatbot.auto-atendimento.digital:8000
- **📚 Documentação da API**: http://chatbot.auto-atendimento.digital:8000/api/docs
- **🤖 Baileys API**: http://chatbot.auto-atendimento.digital:3001

## 👤 LOGIN PADRÃO

- **Usuário**: `admin`
- **Senha**: `admin123`

⚠️ **IMPORTANTE**: Altere a senha após o primeiro login!

## 📱 CONECTAR WHATSAPP

1. Acesse http://chatbot.auto-atendimento.digital:8000
2. Faça login com admin/admin123
3. Vá em **"Números Conectados"**
4. Clique **"Conectar Número"**
5. Preencha nome da instância
6. Clique **"QR Code"**
7. **Escaneie com seu WhatsApp**
8. Aguarde conexão ser estabelecida ✅

## 🛑 PARAR O SISTEMA

Se executado via `python3 main.py`, simplesmente pressione:
```
Ctrl + C
```

## 🔍 VERIFICAR STATUS

```bash
# Ver processos rodando
ps aux | grep -E "(uvicorn|node)"

# Ver logs
tail -f /var/log/syslog | grep whatsapp

# Testar API
curl http://chatbot.auto-atendimento.digital:8000/health
```

## 🚨 TROUBLESHOOTING

### Problema: "Permission denied"
```bash
sudo chmod +x main.py auto_install.py
sudo python3 main.py
```

### Problema: "Port already in use"
```bash
# Matar processos nas portas
sudo lsof -ti:8000 | xargs kill -9
sudo lsof -ti:3001 | xargs kill -9
```

### Problema: PostgreSQL não conecta
```bash
sudo systemctl restart postgresql
sudo systemctl status postgresql
```

### Problema: Baileys não inicia
```bash
cd baileys_service
npm install
node server.js
```

## 📊 ARQUIVOS IMPORTANTES

- `main.py` - Ponto de entrada principal
- `auto_install.py` - Script de instalação automática
- `.env` - Configurações (já configurado para o domínio)
- `requirements.txt` - Dependencies Python
- `baileys_service/package.json` - Dependencies Node.js

## 🎯 FUNCIONALIDADES DISPONÍVEIS

✅ **Dashboard** - Estatísticas em tempo real  
✅ **Números WhatsApp** - Conectar/desconectar via QR Code  
✅ **Mensagens** - Envio e recebimento em tempo real  
✅ **Campanhas** - Marketing em massa  
✅ **Finanças** - Controle de receitas/despesas  
✅ **Grupos** - Organização de contatos  
✅ **API REST** - Integração com outros sistemas  

## 💡 DICAS

- O sistema detecta automaticamente se precisa instalar dependências
- Todos os serviços são iniciados automaticamente
- Logs são exibidos em tempo real no terminal
- Use Ctrl+C para parar tudo de forma segura
- O sistema é reiniciado automaticamente em caso de falhas

## 🔗 PRÓXIMOS PASSOS

1. **Faça login** e altere a senha
2. **Conecte seu WhatsApp** via QR Code
3. **Teste envio de mensagens**
4. **Configure campanhas** se necessário
5. **Explore a API** em `/api/docs`

---

**🎉 Divirta-se automatizando seu WhatsApp!**