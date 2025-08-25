# Docker Setup Guide

Complete guide for setting up and deploying the AI Agent system using Docker.

## 🐳 Overview

The AI Agent system uses Docker for consistent deployment across environments. This guide covers development, staging, and production deployments.

## 📁 Docker Configuration Files

### Main Files
- `Dockerfile` - Multi-stage build configuration
- `docker-compose.yml` - Development environment
- `docker-compose.prod.yml` - Production environment
- `.dockerignore` - Docker build exclusions

## 🚀 Quick Start

### Development Environment

1. **Clone and start**
   ```bash
   git clone <repository-url>
   cd Agentic
   docker-compose up --build
   ```

2. **Access services**
   - Frontend: http://localhost:5173
   - Backend API: http://localhost:8000
   - Redis: localhost:6379
   - MongoDB: localhost:27017

### Production Environment

1. **Build and deploy**
   ```bash
   docker-compose -f docker-compose.prod.yml up --build -d
   ```

2. **Monitor services**
   ```bash
   docker-compose -f docker-compose.prod.yml logs -f
   ```

## 🏗️ Docker Architecture

### Services

| Service | Image | Ports | Purpose |
|---------|--------|--------|---------|
| frontend | Node.js 20 | 5173 | Vue.js frontend |
| backend | Python 3.11 | 8000 | FastAPI backend |
| redis | redis:7-alpine | 6379 | Session storage |
| mongodb | mongo:7 | 27017 | Persistent storage |
| nginx | nginx:alpine | 80, 443 | Reverse proxy |

### Volumes

- `redis_data` - Redis persistent storage
- `mongodb_data` - MongoDB data
- `app_logs` - Application logs
- `uploads` - File uploads

## 🔧 Configuration

### Environment Variables

Create `.env` file:
```bash
# Server Configuration
HOST=0.0.0.0
PORT=8000

# Database Configuration
REDIS_URL=redis://redis:6379
MONGODB_URL=mongodb://mongodb:27017

# AI API Keys
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key
GOOGLE_API_KEY=your_google_key

# Security
SECRET_KEY=your-secret-key
JWT_SECRET_KEY=your-jwt-secret

# MCP Configuration
MCP_CONFIG_PATH=/app/mcp-config.json
```

### Docker Compose Overrides

Create `docker-compose.override.yml` for local customizations:
```yaml
version: '3.8'
services:
  backend:
    environment:
      - DEBUG=true
    volumes:
      - ./backend:/app
  frontend:
    volumes:
      - ./frontend:/app
      - /app/node_modules
```

## 🛠️ Development Workflow

### Local Development with Docker

1. **Start development services**
   ```bash
   docker-compose up frontend backend redis mongodb
   ```

2. **Development with hot reload**
   ```bash
   # Frontend development
   docker-compose run --rm frontend npm run dev
   
   # Backend development
   docker-compose run --rm backend python main.py
   ```

3. **Run tests**
   ```bash
   # Frontend tests
   docker-compose run --rm frontend npm run test
   
   # Backend tests
   docker-compose run --rm backend python -m pytest
   ```

### Debugging

1. **View logs**
   ```bash
   docker-compose logs -f [service-name]
   ```

2. **Enter container**
   ```bash
   docker-compose exec backend bash
   docker-compose exec frontend sh
   ```

3. **Check service health**
   ```bash
   docker-compose ps
   docker-compose healthcheck
   ```

## 📦 Production Deployment

### Single Server Deployment

1. **Prepare environment**
   ```bash
   # Copy production compose file
   cp docker-compose.prod.yml docker-compose.yml
   
   # Set production environment variables
   export ENV=production
   ```

2. **Deploy**
   ```bash
   docker-compose up -d
   ```

### Multi-Server Deployment

#### Using Docker Swarm

1. **Initialize swarm**
   ```bash
   docker swarm init
   ```

2. **Deploy stack**
   ```bash
   docker stack deploy -c docker-compose.prod.yml agentic
   ```

#### Using Docker Compose with external services

```yaml
# docker-compose.prod.yml
version: '3.8'
services:
  backend:
    image: agentic-backend:latest
    environment:
      - REDIS_URL=redis://prod-redis:6379
      - MONGODB_URL=mongodb://prod-mongodb:27017
    deploy:
      replicas: 3
      restart_policy:
        condition: on-failure
  
  frontend:
    image: agentic-frontend:latest
    ports:
      - "80:80"
    depends_on:
      - backend
```

## 🔐 Security

### Production Security Checklist

- [ ] Use specific image tags (avoid `latest`)
- [ ] Enable SSL/TLS with nginx
- [ ] Use secrets for sensitive data
- [ ] Configure firewall rules
- [ ] Enable container resource limits
- [ ] Use read-only containers where possible
- [ ] Regular security updates

### SSL Configuration

Create `nginx/nginx.conf`:
```nginx
server {
    listen 443 ssl;
    server_name your-domain.com;
    
    ssl_certificate /etc/ssl/certs/cert.pem;
    ssl_certificate_key /etc/ssl/private/key.pem;
    
    location / {
        proxy_pass http://frontend:80;
    }
    
    location /api/ {
        proxy_pass http://backend:8000;
    }
}
```

## 📊 Monitoring

### Health Checks

Each service includes health checks:

```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
  interval: 30s
  timeout: 10s
  retries: 3
  start_period: 40s
```

### Logging

Centralized logging with Fluentd:
```yaml
logging:
  driver: fluentd
  options:
    fluentd-address: localhost:24224
    tag: agentic.backend
```

### Metrics

Prometheus metrics available at:
- Backend: http://localhost:8000/metrics
- System: http://localhost:9090

## 🔄 Updates and Rollbacks

### Rolling Updates

```bash
# Update service
docker-compose up -d --no-deps backend

# Rollback
docker-compose rollback backend
```

### Blue-Green Deployment

```bash
# Deploy new version
docker-compose -f docker-compose.blue.yml up -d

# Switch traffic
./switch-traffic.sh blue
```

## 🧪 Testing

### Integration Tests

```bash
# Run integration tests
docker-compose -f docker-compose.test.yml up --abort-on-container-exit

# Load testing
docker run --rm -v $(pwd)/tests:/tests loadimpact/k6 run /tests/load-test.js
```

### End-to-End Tests

```bash
# Run E2E tests
docker-compose -f docker-compose.e2e.yml up --abort-on-container-exit
```

## 🐛 Troubleshooting

### Common Issues

1. **Port conflicts**
   ```bash
   # Check used ports
   netstat -tulpn | grep :8000
   
   # Use different ports
   export BACKEND_PORT=8001
   ```

2. **Permission issues**
   ```bash
   # Fix file permissions
   sudo chown -R $USER:$USER .
   ```

3. **Out of disk space**
   ```bash
   # Clean up
   docker system prune -a
   ```

4. **Memory issues**
   ```bash
   # Check memory usage
   docker stats
   
   # Increase memory limits
   export DOCKER_MEMORY=4g
   ```

### Debug Commands

```bash
# Check container logs
docker-compose logs -f [service-name]

# Inspect container
docker inspect [container-id]

# Check resource usage
docker stats

# Network debugging
docker network ls
docker network inspect agentic_default
```

## 📄 License

This Docker configuration is part of the AI Agent system and follows the same MIT license.