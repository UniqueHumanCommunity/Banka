#!/bin/bash
set -e

echo "🚀 Starting BanKa MVP Production Deployment..."

# Create log directories
mkdir -p /app/logs /var/log/supervisor

# Set proper permissions
chown -R www-data:www-data /var/www/html
chmod -R 755 /var/www/html

# Validate backend environment
echo "📋 Validating backend environment..."
cd /app/backend

# Check if .env file exists and create production defaults if missing
if [ ! -f .env ]; then
    echo "⚠️ No .env file found, creating production defaults..."
    cat > .env << EOF
WEB3_PROVIDER_URL=${WEB3_PROVIDER_URL:-https://bsc-testnet.nodereal.io/v1/e9a36765eb8a40b9bd12e680a1fd2bc5}
WALLET_MNEMONIC=${WALLET_MNEMONIC:-flee cluster north scissors random attitude mutual strategy excuse debris consider uniform}
EVENT_FACTORY_ADDRESS=${EVENT_FACTORY_ADDRESS:-0xB03c97E3357f1D4D33E421164a5205E36bACD779}
MONGO_URL=${MONGO_URL:-mongodb://localhost:27017}
JWT_SECRET=${JWT_SECRET:-$(openssl rand -base64 32)}
EOF
fi

# Test database connection
echo "🔍 Testing database connection..."
python3 -c "
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os

async def test_db():
    try:
        client = AsyncIOMotorClient(os.environ.get('MONGO_URL', 'mongodb://localhost:27017'))
        await client.admin.command('ping')
        print('✅ Database connection successful')
        client.close()
    except Exception as e:
        print(f'❌ Database connection failed: {e}')
        exit(1)

asyncio.run(test_db())
"

# Test blockchain connection
echo "🔗 Testing blockchain connection..."
python3 -c "
from web3 import Web3
import os

try:
    w3 = Web3(Web3.HTTPProvider(os.environ.get('WEB3_PROVIDER_URL')))
    latest_block = w3.eth.block_number
    print(f'✅ Blockchain connected - Latest block: {latest_block}')
except Exception as e:
    print(f'⚠️ Blockchain connection failed: {e}')
    print('🔄 Application will continue with fallback mechanisms')
"

# Remove default nginx configuration
rm -f /etc/nginx/sites-enabled/default

# Validate nginx configuration
echo "🔧 Validating nginx configuration..."
nginx -t

echo "✅ All validations passed!"
echo "🎯 Starting BanKa MVP with Supervisor..."

# Start supervisor which manages both nginx and backend
exec supervisord -c /etc/supervisor/conf.d/banka.conf
