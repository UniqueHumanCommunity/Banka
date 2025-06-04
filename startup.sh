#!/bin/bash
set -e

echo "🚀 Starting BanKa MVP..."

# Create necessary directories
mkdir -p /app/logs /var/log/supervisor

# Check backend environment
echo "📋 Checking backend environment..."
cd /app/backend

# Create .env if not exists
if [ ! -f .env ]; then
    echo "⚠️ Creating default .env file..."
    cat > .env << 'EOF'
WEB3_PROVIDER_URL=https://bsc-testnet.nodereal.io/v1/e9a36765eb8a40b9bd12e680a1fd2bc5
WALLET_MNEMONIC=flee cluster north scissors random attitude mutual strategy excuse debris consider uniform
EVENT_FACTORY_ADDRESS=0xB03c97E3357f1D4D33E421164a5205E36bACD779
MONGO_URL=mongodb://localhost:27017
JWT_SECRET=banka-secret-key-2024-production
EOF
fi

# Test Python imports
echo "🐍 Testing Python dependencies..."
python3 -c "
try:
    import fastapi, uvicorn, motor, web3, eth_account
    print('✅ All Python dependencies available')
except ImportError as e:
    print(f'❌ Missing dependency: {e}')
    exit(1)
"

# Configure nginx
echo "🔧 Configuring nginx..."
nginx -t

echo "✅ All checks passed!"
echo "🎯 Starting services with supervisor..."

# Start supervisor
exec supervisord -c /etc/supervisor/conf.d/banka.conf
