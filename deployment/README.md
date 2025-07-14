# 🚀 Production Deployment Guide

## Quick Deployment

**1. Get your domain ready** (e.g., `actionscenes.ai`)

**2. Deploy to your server:**
```bash
# On your production server
git clone https://github.com/your-repo/cinema-action-scene-generator.git
cd cinema-action-scene-generator/deployment
./deploy.sh yourdomain.com
```

**3. Configure API keys in `.env`:**
```bash
sudo nano /opt/cinema-action-generator/.env
# Add your RunPod, Stripe, and other API keys
docker-compose restart
```

**4. Set up DNS:**
```
A Record: yourdomain.com -> Your Server IP
A Record: api.yourdomain.com -> Your Server IP
```

## Production Architecture

```
User → Cloudflare → Traefik → Frontend (Streamlit)
                           → Backend (FastAPI) → RunPod (RTX 6000 Ada)
                                              → PostgreSQL
                                              → Redis
                                              → MinIO (File Storage)
```

## Server Requirements

**Minimum:**
- 4 CPU cores
- 8GB RAM
- 100GB SSD storage
- Ubuntu 20.04+

**Recommended:**
- 8 CPU cores
- 16GB RAM
- 500GB SSD storage
- Load balancer for multiple instances

## Environment Variables

**Required:**
```bash
DOMAIN=yourdomain.com
RUNPOD_API_KEY=your_key
RUNPOD_ENDPOINT=https://your-pod.runpod.net
STRIPE_SECRET_KEY=sk_live_...
ACME_EMAIL=admin@yourdomain.com
```

**Optional:**
```bash
GOOGLE_ANALYTICS_ID=G-...
SENTRY_DSN=https://...
```

## Security Features

- ✅ SSL/TLS with Let's Encrypt
- ✅ Rate limiting
- ✅ JWT authentication
- ✅ Password hashing
- ✅ Input validation
- ✅ CORS protection
- ✅ Firewall configuration

## Monitoring

**Health Checks:**
- Frontend: `https://yourdomain.com/_stcore/health`
- Backend: `https://api.yourdomain.com/health`
- Database: Built-in Docker health checks

**Logs:**
```bash
docker-compose logs -f frontend
docker-compose logs -f backend
docker-compose logs -f database
```

## Scaling

**Horizontal Scaling:**
```bash
docker-compose up -d --scale frontend=3 --scale backend=3
```

**Load Balancer:**
```yaml
# Add to docker-compose.yml
nginx:
  image: nginx:alpine
  ports:
    - "80:80"
  volumes:
    - ./nginx.conf:/etc/nginx/nginx.conf
```

## Backup Strategy

**Database Backup:**
```bash
docker-compose exec database pg_dump -U cinema_user cinema_action_db > backup.sql
```

**File Storage Backup:**
```bash
docker-compose exec storage mc mirror /data /backup
```

**Automated Backups:**
```bash
# Add to crontab
0 2 * * * /opt/cinema-action-generator/backup.sh
```

## Updates

**Update Application:**
```bash
cd /opt/cinema-action-generator
git pull origin main
docker-compose build
docker-compose up -d
```

**Database Migrations:**
```bash
docker-compose exec backend alembic upgrade head
```

## Troubleshooting

**Services won't start:**
```bash
docker-compose logs
docker system prune -f
docker-compose up -d --force-recreate
```

**SSL issues:**
```bash
docker-compose exec traefik cat /letsencrypt/acme.json
# Check DNS propagation
```

**Performance issues:**
```bash
docker stats
htop
# Scale services or upgrade server
```

## Cost Optimization

**Server Costs:**
- DigitalOcean: $40-80/month
- AWS/GCP: $50-100/month
- Hetzner: $30-60/month

**RunPod Costs:**
- RTX 6000 Ada: ~$2/hour
- Only run when generating
- Auto-stop when idle

**Total Monthly:**
- Server: $50-100
- RunPod: $100-500 (usage dependent)
- Domain/SSL: $10-20
- **Total: $160-620/month**

## Production Checklist

**Before Launch:**
- [ ] Domain configured with DNS
- [ ] SSL certificates working
- [ ] All API keys configured
- [ ] Database initialized
- [ ] File storage configured
- [ ] Monitoring set up
- [ ] Backups configured
- [ ] Load testing completed

**After Launch:**
- [ ] Monitor resource usage
- [ ] Set up alerting
- [ ] Configure log rotation
- [ ] Test disaster recovery
- [ ] Monitor security logs

## Support

**Server Issues:**
- Check Docker logs
- Monitor resource usage
- Review nginx/traefik logs

**Application Issues:**
- Check FastAPI logs
- Monitor database connections
- Verify RunPod connectivity

**Performance:**
- Scale services horizontally
- Optimize database queries
- Use CDN for static assets