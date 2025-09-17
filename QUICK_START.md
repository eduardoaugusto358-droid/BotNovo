# 🚀 QUICK START - WhatsApp Bot Management System

## ⚡ Execução Rápida

### Opção 1: Docker (RECOMENDADO)
```bash
# Execute o sistema completo
python run.py
# Escolha opção 1 (Docker)

# OU execute diretamente:
docker-compose up -d
```

### Opção 2: Desenvolvimento Manual
```bash
# 1. Instale PostgreSQL e Redis
# 2. Execute:
python run.py
# Escolha opção 2 (Desenvolvimento)
```

## 🌐 Acessos

- **Interface Web**: http://localhost:8000
- **API Docs**: http://localhost:8000/api/docs  
- **Baileys Service**: http://localhost:3001

## 👤 Login Padrão

- **Usuário**: admin
- **Senha**: admin123
- ⚠️ **ALTERE A SENHA APÓS PRIMEIRO LOGIN!**

## 📱 Como Conectar WhatsApp

1. Acesse http://localhost:8000
2. Faça login com admin/admin123
3. Vá em "Números Conectados"
4. Clique "Conectar Número"
5. Preencha o nome da instância
6. Clique "QR Code"
7. Escaneie com seu WhatsApp
8. Aguarde a conexão!

## 🎯 Funcionalidades Principais

### ✅ Funcionando
- ✅ Dashboard com estatísticas
- ✅ Conexão WhatsApp via QR Code
- ✅ Gestão de usuários e instâncias
- ✅ Sistema de autenticação
- ✅ API REST completa
- ✅ Recebimento de mensagens (webhook)
- ✅ Estrutura para campanhas
- ✅ Controle financeiro
- ✅ Grupos de contatos

### 🔄 Em Desenvolvimento
- 🔄 Interface completa de mensagens
- 🔄 Envio automático de campanhas  
- 🔄 Upload de arquivos
- 🔄 Relatórios avançados

## 🛠️ Arquitetura

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   FastAPI       │    │   PostgreSQL    │
│   (Web)         │◄──►│   Backend       │◄──►│   Database      │
│   Port: 8000    │    │   Port: 8000    │    │   Port: 5432    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │
         │              ┌─────────────────┐    ┌─────────────────┐
         └──────────────►│   Baileys       │◄──►│   WhatsApp      │
                         │   Service       │    │   Web           │
                         │   Port: 3001    │    │                 │
                         └─────────────────┘    └─────────────────┘
```

## 📊 Estrutura do Banco

- **users**: Usuários do sistema
- **whatsapp_instances**: Números WhatsApp conectados
- **conversations**: Conversas ativas
- **messages**: Histórico de mensagens
- **campaigns**: Campanhas de marketing
- **contacts**: Agenda de contatos
- **finance_entries**: Controle financeiro
- **groups**: Grupos de contatos

## 🚨 Troubleshooting

### Problema: "Connection refused" PostgreSQL
```bash
# Verificar se PostgreSQL está rodando
docker-compose ps

# Restartar serviços
docker-compose restart postgres
```

### Problema: QR Code não aparece
```bash
# Verificar logs do Baileys
docker-compose logs baileys

# Restartar Baileys
docker-compose restart baileys
```

### Problema: Login não funciona
```bash
# Recriar usuário admin
docker-compose exec api python scripts/create_user.py admin admin123 "Administrator" admin@test.com admin
```

## 🔧 Comandos Úteis

```bash
# Ver logs em tempo real
docker-compose logs -f

# Entrar no container da API
docker-compose exec api bash

# Backup do banco
docker-compose exec postgres pg_dump -U admin whatsapp_bot > backup.sql

# Criar novo usuário
docker-compose exec api python scripts/create_user.py usuario senha "Nome" email@test.com

# Parar tudo
docker-compose down

# Limpar volumes (CUIDADO - apaga dados!)
docker-compose down -v
```

## 📞 Suporte

Se encontrar problemas:

1. Verifique os logs: `docker-compose logs -f`
2. Consulte a documentação completa: `/app/README.md`
3. Verifique a API: http://localhost:8000/api/docs

## 🎉 Sucesso!

Se chegou até aqui, seu sistema WhatsApp Bot está funcionando! 

Próximos passos:
1. Altere a senha padrão
2. Conecte seu WhatsApp
3. Explore as funcionalidades
4. Integre com seus sistemas

**Divirta-se automatizando seu WhatsApp! 🚀**