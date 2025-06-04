#!/bin/bash
# Production deployment script for BanKa MVP

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🎪 BanKa MVP Production Deployment Script${NC}"
echo -e "${BLUE}=========================================${NC}"

# Configuration
IMAGE_NAME="banka-mvp"
CONTAINER_NAME="banka-production"
PRODUCTION_PORT="8080"
MONGO_PORT="27017"

# Parse command line arguments
COMMAND=${1:-"deploy"}
ENVIRONMENT=${2:-"production"}

show_help() {
    echo -e "${YELLOW}Usage: ./deploy.sh [COMMAND] [ENVIRONMENT]${NC}"
    echo ""
    echo "Commands:"
    echo "  deploy     - Build and deploy the application (default)"
    echo "  build      - Build Docker image only"
    echo "  start      - Start existing containers"
    echo "  stop       - Stop running containers"
    echo "  restart    - Restart containers"
    echo "  logs       - Show application logs"
    echo "  cleanup    - Remove containers and images"
    echo "  health     - Check application health"
    echo "  help       - Show this help message"
    echo ""
    echo "Environments:"
    echo "  production - Production deployment (default)"
    echo "  staging    - Staging deployment"
}

check_prerequisites() {
    echo -e "${BLUE}🔍 Checking prerequisites...${NC}"
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        echo -e "${RED}❌ Docker is not installed${NC}"
        exit 1
    fi
    
    # Check if Docker is running
    if ! docker info &> /dev/null; then
        echo -e "${RED}❌ Docker is not running${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}✅ Prerequisites checked${NC}"
}

build_image() {
    echo -e "${BLUE}🏗️ Building production Docker image...${NC}"
    
    # Build the image
    docker build \
        -f production.Dockerfile \
        -t ${IMAGE_NAME}:latest \
        -t ${IMAGE_NAME}:$(date +%Y%m%d-%H%M%S) \
        .
    
    echo -e "${GREEN}✅ Docker image built successfully${NC}"
}

start_mongodb() {
    echo -e "${BLUE}🍃 Starting MongoDB...${NC}"
    
    # Check if MongoDB container exists
    if [ ! "$(docker ps -aq -f name=banka-mongodb)" ]; then
        docker run -d \
            --name banka-mongodb \
            --restart unless-stopped \
            -p ${MONGO_PORT}:27017 \
            -v banka-mongodb-data:/data/db \
            mongo:7
    else
        docker start banka-mongodb || true
    fi
    
    echo -e "${GREEN}✅ MongoDB started${NC}"
}

deploy_application() {
    echo -e "${BLUE}🚀 Deploying BanKa MVP...${NC}"
    
    # Stop existing container if running
    docker stop ${CONTAINER_NAME} 2>/dev/null || true
    docker rm ${CONTAINER_NAME} 2>/dev/null || true
    
    # Start MongoDB
    start_mongodb
    
    # Wait for MongoDB to be ready
    echo -e "${YELLOW}⏳ Waiting for MongoDB to be ready...${NC}"
    sleep 10
    
    # Run the application container
    docker run -d \
        --name ${CONTAINER_NAME} \
        --restart unless-stopped \
        -p ${PRODUCTION_PORT}:8080 \
        --link banka-mongodb:mongodb \
        -e MONGO_URL="mongodb://mongodb:27017" \
        -e WEB3_PROVIDER_URL="https://bsc-testnet.nodereal.io/v1/e9a36765eb8a40b9bd12e680a1fd2bc5" \
        -e WALLET_MNEMONIC="flee cluster north scissors random attitude mutual strategy excuse debris consider uniform" \
        -e EVENT_FACTORY_ADDRESS="0xB03c97E3357f1D4D33E421164a5205E36bACD779" \
        -e JWT_SECRET="$(openssl rand -base64 32)" \
        ${IMAGE_NAME}:latest
    
    echo -e "${GREEN}✅ BanKa MVP deployed successfully${NC}"
    echo -e "${YELLOW}📡 Application URL: http://localhost:${PRODUCTION_PORT}${NC}"
}

check_health() {
    echo -e "${BLUE}🏥 Checking application health...${NC}"
    
    # Wait a moment for the application to start
    sleep 5
    
    # Check if containers are running
    if [ "$(docker ps -q -f name=${CONTAINER_NAME})" ]; then
        echo -e "${GREEN}✅ Application container is running${NC}"
    else
        echo -e "${RED}❌ Application container is not running${NC}"
        return 1
    fi
    
    if [ "$(docker ps -q -f name=banka-mongodb)" ]; then
        echo -e "${GREEN}✅ MongoDB container is running${NC}"
    else
        echo -e "${RED}❌ MongoDB container is not running${NC}"
        return 1
    fi
    
    # Check API health endpoint
    echo -e "${YELLOW}🔍 Testing API health endpoint...${NC}"
    if curl -f http://localhost:${PRODUCTION_PORT}/api/health &> /dev/null; then
        echo -e "${GREEN}✅ API health check passed${NC}"
    else
        echo -e "${RED}❌ API health check failed${NC}"
        echo -e "${YELLOW}ℹ️ Application might still be starting up...${NC}"
    fi
}

show_logs() {
    echo -e "${BLUE}📋 Showing application logs...${NC}"
    docker logs -f ${CONTAINER_NAME}
}

stop_application() {
    echo -e "${BLUE}🛑 Stopping BanKa MVP...${NC}"
    docker stop ${CONTAINER_NAME} banka-mongodb 2>/dev/null || true
    echo -e "${GREEN}✅ Application stopped${NC}"
}

start_application() {
    echo -e "${BLUE}▶️ Starting BanKa MVP...${NC}"
    docker start banka-mongodb ${CONTAINER_NAME} 2>/dev/null || true
    echo -e "${GREEN}✅ Application started${NC}"
}

restart_application() {
    stop_application
    sleep 2
    start_application
}

cleanup() {
    echo -e "${BLUE}🧹 Cleaning up containers and images...${NC}"
    
    # Stop and remove containers
    docker stop ${CONTAINER_NAME} banka-mongodb 2>/dev/null || true
    docker rm ${CONTAINER_NAME} banka-mongodb 2>/dev/null || true
    
    # Remove images
    docker rmi ${IMAGE_NAME}:latest 2>/dev/null || true
    
    # Remove volumes (uncomment if you want to delete data)
    # docker volume rm banka-mongodb-data 2>/dev/null || true
    
    echo -e "${GREEN}✅ Cleanup completed${NC}"
}

# Main command processing
case $COMMAND in
    "help")
        show_help
        ;;
    "build")
        check_prerequisites
        build_image
        ;;
    "deploy")
        check_prerequisites
        build_image
        deploy_application
        sleep 10
        check_health
        echo -e "${GREEN}🎉 BanKa MVP deployment completed!${NC}"
        echo -e "${YELLOW}🌐 Access your application at: http://localhost:${PRODUCTION_PORT}${NC}"
        ;;
    "start")
        start_application
        ;;
    "stop")
        stop_application
        ;;
    "restart")
        restart_application
        ;;
    "logs")
        show_logs
        ;;
    "health")
        check_health
        ;;
    "cleanup")
        cleanup
        ;;
    *)
        echo -e "${RED}❌ Unknown command: $COMMAND${NC}"
        show_help
        exit 1
        ;;
esac
