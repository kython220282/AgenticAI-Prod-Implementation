# ==================================================
# PHASE 1: PRODUCTION DEPLOYMENT GUIDE
# ==================================================

This guide explains how to deploy the Agentic AI system in production.

## Prerequisites

- Docker & Docker Compose installed
- Domain name (for HTTPS)
- SSL certificates (Let's Encrypt recommended)
- At least 4GB RAM, 2 CPU cores
- API keys for LLM providers

## Quick Start (Development)

1. **Copy environment file:**
```bash
cp .env.example .env
```

2. **Edit .env file:**
- Add your API keys (OpenAI, Anthropic, etc.)
- Set database credentials
- Configure Redis and other services

3. **Start all services:**
```bash
docker-compose up -d
```

4. **Check health:**
```bash
curl http://localhost/health
```

5. **Access services:**
- API: http://localhost (port 80)
- API Docs: http://localhost/docs
- Grafana: http://localhost:3000 (admin/admin)
- Prometheus: http://localhost:9090
- RabbitMQ: http://localhost:15672 (guest/guest)

## Production Deployment

### 1. Environment Configuration

```bash
# Set to production
APP_ENV=production
APP_DEBUG=false

# Generate secure keys
SECRET_KEY=$(openssl rand -hex 32)
JWT_SECRET_KEY=$(openssl rand -hex 32)

# Set real database credentials
POSTGRES_PASSWORD=$(openssl rand -hex 16)

# Add real API keys
OPENAI_API_KEY=sk-your-real-key
ANTHROPIC_API_KEY=sk-ant-your-real-key
```

### 2. SSL/TLS Setup

**Option A: Let's Encrypt (Recommended)**
```bash
# Install certbot
apt-get install certbot python3-certbot-nginx

# Get certificate
certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Auto-renewal
certbot renew --dry-run
```

**Option B: Custom Certificate**
```bash
# Place certificates in nginx/ssl/
mkdir -p nginx/ssl
cp your-cert.pem nginx/ssl/cert.pem
cp your-key.pem nginx/ssl/key.pem

# Update nginx/conf.d/default.conf
# Uncomment SSL configuration lines
```

### 3. Database Setup

```bash
# Initialize database
docker-compose exec api alembic upgrade head

# Create admin user (implement in code)
docker-compose exec api python scripts/create_admin.py
```

### 4. Start Production Stack

```bash
# Build images
docker-compose build --no-cache

# Start services
docker-compose up -d

# View logs
docker-compose logs -f api

# Check status
docker-compose ps
```

### 5. Verify Deployment

```bash
# Health check
curl https://yourdomain.com/health

# Test authentication
curl -X POST https://yourdomain.com/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password"}'

# View metrics
curl https://yourdomain.com/metrics
```

## Service URLs

| Service | URL | Credentials |
|---------|-----|-------------|
| API | https://yourdomain.com | - |
| API Docs | https://yourdomain.com/docs | - |
| Grafana | https://yourdomain.com:3000 | admin/admin |
| Prometheus | https://yourdomain.com:9090 | - |
| RabbitMQ | https://yourdomain.com:15672 | guest/guest |

## Monitoring

### Prometheus Metrics

Access: `http://localhost:9090`

Key metrics:
- `fastapi_requests_total` - Total requests
- `fastapi_request_duration_seconds` - Request latency
- `process_cpu_seconds_total` - CPU usage
- `process_resident_memory_bytes` - Memory usage

### Grafana Dashboards

Access: `http://localhost:3000`

1. Login with admin/admin
2. Add Prometheus datasource: http://prometheus:9090
3. Import dashboards from monitoring/grafana/dashboards/

### Logs

```bash
# View API logs
docker-compose logs -f api

# View Nginx logs
docker-compose logs -f nginx

# View worker logs
docker-compose logs -f worker

# View all logs
docker-compose logs -f
```

## Scaling

### Horizontal Scaling

```yaml
# docker-compose.yml
api:
  deploy:
    replicas: 4  # Multiple API instances
    
worker:
  deploy:
    replicas: 2  # Multiple workers
```

### Resource Limits

```yaml
services:
  api:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 4G
        reservations:
          cpus: '1'
          memory: 2G
```

## Backup & Recovery

### Database Backup

```bash
# Backup
docker-compose exec postgres pg_dump -U agenticai agenticai_db > backup.sql

# Restore
docker-compose exec -T postgres psql -U agenticai agenticai_db < backup.sql
```

### Vector Database Backup

```bash
# Backup ChromaDB
docker cp agenticai-chromadb:/chroma/chroma ./backups/chroma_$(date +%Y%m%d)
```

## Troubleshooting

### Service Won't Start

```bash
# Check logs
docker-compose logs api

# Restart service
docker-compose restart api

# Rebuild
docker-compose up -d --build api
```

### Database Connection Issues

```bash
# Check PostgreSQL
docker-compose exec postgres pg_isready

# Check connection from API
docker-compose exec api python -c "from src.api.database import init_db; import asyncio; asyncio.run(init_db())"
```

### Redis Connection Issues

```bash
# Check Redis
docker-compose exec redis redis-cli ping

# Test connection
docker-compose exec api python -c "import redis; r=redis.from_url('redis://redis:6379/0'); print(r.ping())"
```

## Security Checklist

- [ ] Change default passwords
- [ ] Enable HTTPS
- [ ] Configure firewall
- [ ] Set rate limits
- [ ] Enable CORS restrictions
- [ ] Regular security updates
- [ ] Monitor access logs
- [ ] Backup encryption keys
- [ ] Enable 2FA for admin
- [ ] Set up intrusion detection

## Performance Tuning

1. **Database Connection Pooling:**
   - Adjust POOL_SIZE in .env
   - Monitor connection usage

2. **Redis Memory:**
   - Set maxmemory policy
   - Monitor memory usage

3. **Worker Concurrency:**
   - Adjust Celery concurrency
   - Monitor task queue length

4. **API Workers:**
   - Use multiple Uvicorn workers
   - Enable worker timeout

## Maintenance

### Update Application

```bash
# Pull latest code
git pull

# Rebuild images
docker-compose build --no-cache

# Restart services
docker-compose up -d

# Run migrations
docker-compose exec api alembic upgrade head
```

### Update Dependencies

```bash
# Update requirements.txt
pip-compile requirements.in

# Rebuild images
docker-compose build --no-cache
```

## Support

For issues or questions:
1. Check logs: `docker-compose logs -f`
2. Review documentation
3. Contact support team

---

**Phase 1 Complete! ✅**

Next: Phase 2 - Infrastructure components (CI/CD, Database models, Security hardening)
