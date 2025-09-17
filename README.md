# WhatsApp Bot Management System

Sistema completo de gestão de bots WhatsApp com integração Baileys, desenvolvido em Python (FastAPI) + PostgreSQL + React.

## 🚀 Características

- **Backend FastAPI**: API REST completa com autenticação JWT
- **Frontend React**: Interface moderna e responsiva
- **Integração Baileys**: Conexão nativa com WhatsApp Web
- **PostgreSQL**: Banco de dados robusto e escalável
- **Docker**: Containerização completa para fácil deploy
- **Autenticação**: Sistema seguro de login/registro
- **Tempo Real**: Webhooks para mensagens em tempo real

## 📋 Funcionalidades

### ✅ Implementadas
- [x] Sistema de autenticação e usuários
- [x] Dashboard com estatísticas
- [x] Gestão de instâncias WhatsApp
- [x] Conexão via QR Code (Baileys)
- [x] Estrutura de mensagens e conversas
- [x] Sistema de campanhas
- [x] Gestão financeira
- [x] Grupos de contatos
- [x] API REST completa
- [x] Webhooks para recebimento de mensagens

### 🔄 Em Desenvolvimento
- [ ] Interface completa de mensagens
- [ ] Executar campanhas automaticamente
- [ ] Upload de mídia (imagens, documentos)
- [ ] Relatórios avançados
- [ ] Agendamento de mensagens

## 🛠️ Tecnologias

### Backend
- **FastAPI**: Framework web moderno e rápido
- **SQLAlchemy**: ORM para Python
- **PostgreSQL**: Banco de dados principal
- **Redis**: Cache e sessões
- **Celery**: Tarefas em background
- **Alembic**: Migrações de banco

### Frontend
- **HTML5/CSS3/JavaScript**: Interface web nativa
- **Axios**: Cliente HTTP
- **Font Awesome**: Ícones

### WhatsApp Integration
- **Baileys**: Biblioteca Node.js para WhatsApp Web
- **QR Code**: Geração de códigos para conexão
- **Webhooks**: Recebimento de mensagens em tempo real

## 🚀 Instalação e Deploy

### Usando Docker (Recomendado)

1. **Clone o repositório**:
```bash
git clone <repository-url>
cd whatsapp-bot-system
```

2. **Configure as variáveis de ambiente**:
```bash
cp .env.example .env
# Edite o arquivo .env conforme necessário
```

3. **Inicie os serviços**:
```bash
docker-compose up -d
```

4. **Acesse a aplicação**:
- Interface Web: http://localhost:8000
- API Docs: http://localhost:8000/api/docs
- Baileys Service: http://localhost:3001

### Instalação Manual

#### Pré-requisitos
- Python 3.11+
- Node.js 18+
- PostgreSQL 15+
- Redis 7+

#### Backend Setup

1. **Instale as dependências Python**:
```bash
pip install -r requirements.txt
```

2. **Configure o banco de dados**:
```bash
# Crie o banco PostgreSQL
createdb whatsapp_bot

# Execute as migrações
alembic upgrade head

# Inicialize o banco com dados básicos
python scripts/init_db.py
```

3. **Inicie o backend**:
```bash
python main.py
# ou
uvicorn main:app --reload
```

#### Baileys Service Setup

1. **Instale as dependências Node.js**:
```bash
cd baileys_service
npm install
```

2. **Inicie o serviço Baileys**:
```bash
npm start
```

## 📖 Uso

### 1. Primeiro Acesso

Após a instalação, acesse http://localhost:8000 e faça login com:
- **Usuário**: admin
- **Senha**: admin123

**⚠️ IMPORTANTE**: Altere a senha padrão imediatamente!

### 2. Conectar WhatsApp

1. Vá para "Números Conectados"
2. Clique em "Conectar Número"
3. Preencha o nome da instância
4. Clique em "QR Code" e escaneie com seu WhatsApp
5. Aguarde a conexão ser estabelecida

### 3. Gerenciar Mensagens

- Visualize conversas em tempo real
- Envie mensagens através da interface
- Organize contatos em grupos
- Monitore estatísticas no dashboard

### 4. Campanhas

- Crie campanhas de mensagens em massa
- Agende envios para datas específicas
- Monitore taxa de entrega e sucesso
- Gerencie listas de contatos

## 🔧 Configuração

### Variáveis de Ambiente

```env
# Database
DATABASE_URL=postgresql://admin:admin123@localhost:5432/whatsapp_bot

# Redis
REDIS_URL=redis://localhost:6379/0

# Security
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Services
BAILEYS_API_URL=http://localhost:3001
FRONTEND_URL=http://localhost:8000
```

### Banco de Dados

O sistema usa PostgreSQL com as seguintes tabelas principais:
- `users`: Usuários do sistema
- `whatsapp_instances`: Instâncias WhatsApp conectadas
- `conversations`: Conversas ativas
- `messages`: Histórico de mensagens
- `campaigns`: Campanhas de marketing
- `contacts`: Agenda de contatos
- `finance_entries`: Controle financeiro

## 📊 API Endpoints

### Autenticação
- `POST /api/auth/login` - Login
- `POST /api/auth/register` - Registro
- `GET /api/auth/me` - Dados do usuário atual

### Instâncias WhatsApp
- `GET /api/instances` - Listar instâncias
- `POST /api/instances` - Criar instância
- `GET /api/instances/{id}/qr-code` - Obter QR Code
- `DELETE /api/instances/{id}` - Remover instância

### Mensagens
- `GET /api/messages/conversations` - Listar conversas
- `POST /api/messages/send` - Enviar mensagem
- `POST /api/webhook/whatsapp/{instance_id}` - Webhook Baileys

### Campanhas
- `GET /api/campaigns` - Listar campanhas
- `POST /api/campaigns` - Criar campanha
- `POST /api/campaigns/{id}/start` - Iniciar campanha

Documentação completa disponível em `/api/docs`

## 🛡️ Segurança

- Autenticação JWT com tokens seguros
- Hashing de senhas com bcrypt
- Validação de dados com Pydantic
- CORS configurado adequadamente
- Rate limiting (recomendado para produção)

## 📝 Scripts Úteis

### Criar Usuário
```bash
python scripts/create_user.py joao 123456 "João Silva" joao@email.com admin
```

### Inicializar Banco
```bash
python scripts/init_db.py
```

### Migrações
```bash
# Criar migração
alembic revision --autogenerate -m "Description"

# Aplicar migrações
alembic upgrade head
```

## 🐛 Troubleshooting

### Problemas Comuns

1. **Erro de conexão com PostgreSQL**:
   - Verifique se o PostgreSQL está rodando
   - Confirme as credenciais no arquivo `.env`

2. **QR Code não aparece**:
   - Verifique se o serviço Baileys está rodando
   - Confirme a URL do Baileys no `.env`

3. **Mensagens não chegam**:
   - Verifique os logs do serviço Baileys
   - Confirme se o webhook está configurado

### Logs

```bash
# Ver logs da aplicação
tail -f app.log

# Ver logs do Docker
docker-compose logs -f

# Ver logs específicos do Baileys
docker-compose logs -f baileys
```

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está licenciado sob a MIT License - veja o arquivo [LICENSE](LICENSE) para detalhes.

## 📞 Suporte

Para suporte técnico:
- Abra uma issue no GitHub
- Envie email para: suporte@whatsappbot.com

## 🎯 Roadmap

- [ ] Chatbot com IA integrada
- [ ] Integração com CRM
- [ ] App mobile React Native
- [ ] Suporte a múltiplos idiomas
- [ ] Templates de mensagens
- [ ] Analytics avançados
- [ ] Integração com Zapier/Make

---

Desenvolvido com ❤️ para automatizar e otimizar sua comunicação via WhatsApp!