# 🚀 BanKa MVP - Guia de Deploy Completo

## 📋 Visão Geral

Este guia fornece instruções completas para fazer o deploy do BanKa MVP em produção. O BanKa é um sistema completo de pagamentos para eventos usando blockchain e tokens inteligentes.

## ✨ Funcionalidades Principais

- 🎪 **Criação de Eventos**: Sistema completo de gerenciamento de eventos
- 🎫 **Tokens Inteligentes**: Deploy real de contratos ERC-20 na BNB Chain
- 🦊 **Integração MetaMask**: Botões para adicionar tokens automaticamente
- 💳 **Sistema de Pagamentos**: Online (crypto) e offline (caixa)
- 👤 **Gestão de Usuários**: Autenticação completa com carteiras blockchain
- 📊 **Dashboard**: Interface completa para organizadores

## 🏗️ Arquitetura

```
Frontend (React) → Nginx → FastAPI Backend → MongoDB
                      ↓
               BNB Chain Testnet (Smart Contracts)
```

## 📦 Pré-requisitos

### Sistema
- Docker 20.10+
- Docker Compose 2.0+
- 4GB RAM mínimo
- 10GB espaço em disco

### Serviços Externos
- **BNB Chain Testnet**: Para deploy de smart contracts
- **NodeReal RPC**: Endpoint de blockchain já configurado

## 🚀 Deploy Rápido

### 1. Clone e Prepare

```bash
# Se ainda não fez, clone o repositório
git clone <repository-url>
cd banka

# Torne o script executável
chmod +x deploy.sh
```

### 2. Deploy Completo

```bash
# Deploy completo em um comando
./deploy.sh deploy

# Ou seguir passo a passo:
./deploy.sh build    # Construir imagem
./deploy.sh deploy   # Fazer deploy
./deploy.sh health   # Verificar saúde
```

### 3. Acesso

Após o deploy, acesse:
- **Frontend**: http://localhost:8080
- **API**: http://localhost:8080/api
- **Health Check**: http://localhost:8080/api/health

## 🔧 Comandos de Gerenciamento

```bash
# Visualizar logs em tempo real
./deploy.sh logs

# Parar aplicação
./deploy.sh stop

# Iniciar aplicação
./deploy.sh start

# Reiniciar aplicação
./deploy.sh restart

# Verificar saúde
./deploy.sh health

# Limpeza completa
./deploy.sh cleanup
```

## 🌐 Deploy em Produção

### Variáveis de Ambiente

Para produção, configure as seguintes variáveis:

```bash
# Blockchain (obrigatório)
export WEB3_PROVIDER_URL="sua-url-rpc-bnb-chain"
export WALLET_MNEMONIC="sua-mnemonic-segura"

# Segurança (obrigatório)
export JWT_SECRET="$(openssl rand -base64 32)"

# Database (opcional - usa MongoDB local por padrão)
export MONGO_URL="mongodb://seu-servidor:27017"
```

### Deploy com Configurações Customizadas

```bash
# Deploy com suas próprias configurações
docker run -d \
  --name banka-production \
  -p 8080:8080 \
  -e WEB3_PROVIDER_URL="$WEB3_PROVIDER_URL" \
  -e WALLET_MNEMONIC="$WALLET_MNEMONIC" \
  -e JWT_SECRET="$JWT_SECRET" \
  -e MONGO_URL="$MONGO_URL" \
  banka-mvp:latest
```

## 🔐 Configurações de Segurança

### 1. JWT Secret
```bash
# Gerar JWT secret seguro
openssl rand -base64 32
```

### 2. Mnemonic de Carteira
- Use uma mnemonic única para produção
- Mantenha backup seguro da mnemonic
- Nunca commit a mnemonic no código

### 3. Database
- Configure autenticação no MongoDB
- Use conexão SSL quando possível
- Faça backups regulares

## 📊 Monitoramento

### Health Check Automatizado
O sistema inclui health check que verifica:
- Status da API
- Conexão com blockchain
- Conexão com database

```bash
# Verificar saúde via API
curl http://localhost:8080/api/health
```

### Logs
```bash
# Ver logs do backend
docker logs banka-production

# Ver logs do MongoDB
docker logs banka-mongodb

# Logs em tempo real
./deploy.sh logs
```

## 🔄 Atualização

### Deploy de Nova Versão

```bash
# Parar versão atual
./deploy.sh stop

# Construir nova imagem
./deploy.sh build

# Deploy nova versão
./deploy.sh deploy
```

### Backup Antes da Atualização

```bash
# Backup do MongoDB
docker exec banka-mongodb mongodump --archive=/backup.archive

# Copiar backup
docker cp banka-mongodb:/backup.archive ./backup-$(date +%Y%m%d).archive
```

## 🛠️ Troubleshooting

### Problemas Comuns

1. **Container não inicia**
   ```bash
   # Verificar logs
   docker logs banka-production
   
   # Verificar saúde
   ./deploy.sh health
   ```

2. **Erro de conexão com blockchain**
   - Verificar se o RPC URL está correto
   - Verificar conectividade de rede
   - Consultar logs do backend

3. **Erro de database**
   ```bash
   # Verificar MongoDB
   docker exec -it banka-mongodb mongo
   
   # Reiniciar MongoDB
   docker restart banka-mongodb
   ```

4. **Frontend não carrega**
   - Verificar se nginx está rodando
   - Verificar configuração do proxy
   - Verificar logs do nginx

### Debug Avançado

```bash
# Acessar container
docker exec -it banka-production bash

# Verificar processos
docker exec banka-production supervisorctl status

# Logs específicos
docker exec banka-production tail -f /app/logs/backend.log
```

## 📈 Performance

### Otimizações Incluídas

- **Frontend**: Build otimizado com compressão
- **Backend**: Múltiplos workers do Uvicorn
- **Nginx**: Compressão gzip e cache estático
- **Database**: Índices automáticos
- **Docker**: Multi-stage build para imagem menor

### Métricas

```bash
# Uso de recursos
docker stats banka-production banka-mongodb

# Tamanho da imagem
docker images banka-mvp
```

## 💾 Backup e Restore

### Backup Completo

```bash
# Criar script de backup
cat > backup.sh << 'EOF'
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
mkdir -p backups

# Backup MongoDB
docker exec banka-mongodb mongodump --archive=/tmp/backup.archive
docker cp banka-mongodb:/tmp/backup.archive backups/mongodb_${DATE}.archive

# Backup logs
docker cp banka-production:/app/logs backups/logs_${DATE}

echo "Backup completed: backups/*_${DATE}*"
EOF

chmod +x backup.sh
./backup.sh
```

### Restore

```bash
# Restore MongoDB
docker cp backups/mongodb_YYYYMMDD_HHMMSS.archive banka-mongodb:/tmp/restore.archive
docker exec banka-mongodb mongorestore --archive=/tmp/restore.archive --drop
```

## 🔗 Links Úteis

- **Frontend**: http://localhost:8080
- **API Docs**: http://localhost:8080/api/docs (Swagger)
- **Health Check**: http://localhost:8080/api/health
- **BNB Chain Testnet**: https://testnet.bscscan.com/
- **Faucet BNB**: https://testnet.bnbchain.org/faucet-smart

## 📞 Suporte

Para suporte:
1. Verificar logs com `./deploy.sh logs`
2. Executar health check com `./deploy.sh health`
3. Consultar seção de troubleshooting
4. Verificar documentação da API

---

🎉 **Seu BanKa MVP está pronto para produção!**
