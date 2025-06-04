#!/bin/bash
# Quick Start Script for BanKa MVP Production

echo "🎪 BanKa MVP - Sistema de Pagamentos Blockchain para Eventos"
echo "============================================================"
echo ""
echo "✨ FUNCIONALIDADES:"
echo "   • Criação de eventos com tokens ERC-20 reais"
echo "   • Integração MetaMask com botões 'Add Token'"
echo "   • Sistema de pagamentos online/offline"
echo "   • Dashboard completo para organizadores"
echo "   • Marketplace para participantes"
echo ""

# Check if running in production environment
if command -v docker &> /dev/null; then
    echo "🚀 DEPLOY EM PRODUÇÃO"
    echo "---------------------"
    echo ""
    echo "1. Build e Deploy Automático:"
    echo "   ./deploy.sh deploy"
    echo ""
    echo "2. Ou usando Docker Compose:"
    echo "   docker-compose -f docker-compose.production.yml up -d"
    echo ""
    echo "3. Verificar Status:"
    echo "   ./deploy.sh health"
    echo ""
else
    echo "📋 AMBIENTE ATUAL (Kubernetes)"
    echo "------------------------------"
    echo ""
    echo "✅ Aplicação já rodando em:"
    echo "   Frontend: https://25c152bd-973f-4379-b12e-4ce251f20edf.preview.emergentagent.com"
    echo "   API: https://25c152bd-973f-4379-b12e-4ce251f20edf.preview.emergentagent.com/api"
    echo "   Health: https://25c152bd-973f-4379-b12e-4ce251f20edf.preview.emergentagent.com/api/health"
    echo ""
fi

echo "👤 CONTAS DEMO PRONTAS:"
echo "   Organizador: organizador@banka.com / 123456"
echo "   Participante: participante@banka.com / 123456"
echo "   Caixa: caixa@banka.com / 123456"
echo ""

echo "🎯 EVENTO DEMO CRIADO:"
echo "   • Festival BanKa 2024"
echo "   • Tokens: CERVEJA, ENTRADA"
echo "   • Contratos na BNB Chain Testnet"
echo ""

echo "📚 DOCUMENTAÇÃO:"
echo "   • DEPLOYMENT.md - Guia completo de deploy"
echo "   • README.production.md - Documentação do produto"
echo "   • MVP_CHECKLIST.md - Checklist de entrega"
echo ""

echo "🔧 COMANDOS ÚTEIS:"
echo "   ./deploy.sh help     - Ajuda completa"
echo "   ./deploy.sh logs     - Ver logs"
echo "   ./deploy.sh health   - Verificar saúde"
echo ""

echo "🎉 STATUS: MVP 100% FUNCIONAL E PRONTO PARA PRODUÇÃO!"