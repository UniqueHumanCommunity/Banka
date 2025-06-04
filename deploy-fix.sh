#!/bin/bash
# Fixed deployment script for BanKa MVP

set -e

echo "🎪 BanKa MVP - Fixed Deployment Script"
echo "======================================"

# Check prerequisites
check_docker() {
    if ! command -v docker &> /dev/null; then
        echo "❌ Docker not found. Installing Docker..."
        # Add Docker installation for various systems
        if [[ "$OSTYPE" == "linux-gnu"* ]]; then
            curl -fsSL https://get.docker.com -o get-docker.sh
            sh get-docker.sh
            rm get-docker.sh
        else
            echo "Please install Docker manually: https://docs.docker.com/get-docker/"
            exit 1
        fi
    fi
    echo "✅ Docker is available"
}

# Build and deploy
deploy() {
    echo "🏗️ Building BanKa MVP..."
    
    # Stop existing containers
    docker-compose -f docker-compose.fixed.yml down 2>/dev/null || true
    
    # Build and start
    docker-compose -f docker-compose.fixed.yml up --build -d
    
    echo "⏳ Waiting for services to start..."
    sleep 15
    
    # Check health
    for i in {1..30}; do
        if curl -f http://localhost:8080/api/health &>/dev/null; then
            echo "✅ BanKa MVP is running successfully!"
            echo "🌐 Access at: http://localhost:8080"
            return 0
        fi
        echo "Waiting for startup... ($i/30)"
        sleep 2
    done
    
    echo "❌ Failed to start - checking logs..."
    docker-compose -f docker-compose.fixed.yml logs --tail=50
    return 1
}

# Quick test deployment without Docker
test_current() {
    echo "🧪 Testing current environment..."
    
    # Test API
    if curl -f "https://25c152bd-973f-4379-b12e-4ce251f20edf.preview.emergentagent.com/api/health" &>/dev/null; then
        echo "✅ Current deployment is working!"
        echo "🌐 Access at: https://25c152bd-973f-4379-b12e-4ce251f20edf.preview.emergentagent.com"
        return 0
    else
        echo "❌ Current deployment has issues"
        return 1
    fi
}

# Main execution
case "${1:-test}" in
    "deploy")
        check_docker
        deploy
        ;;
    "test")
        test_current
        ;;
    "logs")
        if command -v docker &> /dev/null; then
            docker-compose -f docker-compose.fixed.yml logs -f
        else
            echo "Docker not available - checking supervisor logs..."
            tail -f /var/log/supervisor/*.log
        fi
        ;;
    "stop")
        docker-compose -f docker-compose.fixed.yml down
        ;;
    *)
        echo "Usage: $0 {deploy|test|logs|stop}"
        echo ""
        echo "  deploy - Build and deploy with Docker"
        echo "  test   - Test current environment"
        echo "  logs   - Show application logs"
        echo "  stop   - Stop Docker deployment"
        exit 1
        ;;
esac
