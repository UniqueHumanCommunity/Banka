# Multi-stage Production Dockerfile for BanKa MVP
# Optimized for production deployment

# Stage 1: Build React App
FROM node:20-alpine AS frontend-build
WORKDIR /app/frontend

# Copy package files first for better caching
COPY frontend/package.json frontend/yarn.lock ./
RUN yarn install --frozen-lockfile --production

# Copy source code and build
COPY frontend/ ./
RUN yarn build

# Stage 2: Build Backend Dependencies
FROM python:3.11-slim AS backend-deps
WORKDIR /app/backend

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY backend/requirements.txt ./
RUN pip install --no-cache-dir --user -r requirements.txt

# Stage 3: Production Runtime
FROM python:3.11-slim AS production
WORKDIR /app

# Install nginx and system dependencies
RUN apt-get update && apt-get install -y \
    nginx \
    supervisor \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Copy Python dependencies from builder stage
COPY --from=backend-deps /root/.local /root/.local

# Copy built frontend
COPY --from=frontend-build /app/frontend/build /var/www/html

# Copy backend code
COPY backend/ /app/backend/

# Copy configuration files
COPY production.nginx.conf /etc/nginx/sites-available/default
COPY production.supervisord.conf /etc/supervisor/conf.d/banka.conf
COPY production.entrypoint.sh /app/entrypoint.sh

# Set permissions
RUN chmod +x /app/entrypoint.sh

# Create necessary directories
RUN mkdir -p /var/log/supervisor /var/log/nginx /app/logs

# Environment variables
ENV PYTHONPATH=/root/.local/lib/python3.11/site-packages:$PYTHONPATH
ENV PATH=/root/.local/bin:$PATH
ENV PYTHONUNBUFFERED=1
ENV NODE_ENV=production

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8080/api/health || exit 1

# Expose port
EXPOSE 8080

# Start application
CMD ["/app/entrypoint.sh"]
