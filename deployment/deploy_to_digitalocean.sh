#!/bin/bash

# 🎬 CinaKinetic.com - DigitalOcean Production Deployment
# Full feature deployment with LoRA training, video generation, and R-rated content support

set -e

echo "🎬 CinaKinetic.com - DigitalOcean Production Deployment"
echo "======================================================="
echo "🌐 Domain: cinakinetic.com"
echo "🚀 Stack: Streamlit + FastAPI + Supabase + RunPod RTX 6000 Ada"
echo "💰 Cost: ~$24/month DigitalOcean droplet"
echo ""

# Check if domain is provided
DOMAIN=${1:-cinakinetic.com}
echo "🌐 Deploying to: $DOMAIN"

# Check if we're on the server
if [ ! -f "/etc/os-release" ]; then
    echo "❌ This script should be run on your DigitalOcean server"
    echo "📋 Instructions:"
    echo "1. Copy this project to your DigitalOcean server"
    echo "2. SSH into your server"
    echo "3. Run this script"
    exit 1
fi

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    echo "❌ Please don't run as root. Use a sudo user instead."
    exit 1
fi

echo "🔧 Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install required packages
echo "📦 Installing system dependencies..."
sudo apt install -y \
    docker.io \
    docker-compose \
    nginx \
    certbot \
    python3-certbot-nginx \
    git \
    curl \
    ufw \
    htop \
    vim

# Add user to docker group
sudo usermod -aG docker $USER

# Enable and start Docker
sudo systemctl enable docker
sudo systemctl start docker

# Create deployment directory
DEPLOY_DIR="/opt/cinakinetic"
echo "📁 Creating deployment directory: $DEPLOY_DIR"

if [ ! -d "$DEPLOY_DIR" ]; then
    sudo mkdir -p $DEPLOY_DIR
    sudo chown $USER:$USER $DEPLOY_DIR
fi

# Create the application structure
echo "📋 Setting up application structure..."
mkdir -p $DEPLOY_DIR/{src,static,config,data,logs}

# Create environment file
echo "⚙️ Creating environment configuration..."
cat > $DEPLOY_DIR/.env << EOF
# 🎬 CinaKinetic.com Production Environment

# Domain Configuration
DOMAIN=$DOMAIN
PRODUCTION=true

# Database Configuration (PostgreSQL via Supabase)
SUPABASE_URL=your_supabase_project_url
SUPABASE_ANON_KEY=your_supabase_anon_key
SUPABASE_SERVICE_KEY=your_supabase_service_key

# RunPod RTX 6000 Ada Configuration
RUNPOD_API_KEY=your_runpod_api_key
RUNPOD_ENDPOINT=your_runpod_endpoint

# Stripe Payment Configuration
STRIPE_PUBLISHABLE_KEY=your_stripe_publishable_key
STRIPE_SECRET_KEY=your_stripe_secret_key

# Security Keys (Auto-generated)
JWT_SECRET=$(openssl rand -base64 64)
ENCRYPTION_KEY=$(openssl rand -base64 32)

# Email Configuration
ACME_EMAIL=admin@$DOMAIN

# Application Settings
MAX_FILE_SIZE=50MB
MAX_BATCH_SIZE=8
DEFAULT_CREDITS=25

# Feature Flags
ENABLE_LORA_TRAINING=true
ENABLE_VIDEO_GENERATION=true
ENABLE_R_RATED_CONTENT=true
ENABLE_BATCH_PROCESSING=true
ENABLE_MULTI_CONTROLNET=true
EOF

# Create docker-compose for full stack
echo "🐳 Creating Docker Compose configuration..."
cat > $DEPLOY_DIR/docker-compose.yml << 'EOF'
version: '3.8'

services:
  # Main Application - Streamlit
  app:
    build:
      context: .
      dockerfile: Dockerfile
    ports:
      - "8501:8501"
    environment:
      - PRODUCTION=true
    env_file:
      - .env
    volumes:
      - ./data:/app/data
      - ./static:/app/static
      - ./logs:/app/logs
    restart: unless-stopped
    depends_on:
      - redis

  # Redis for caching and sessions
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    restart: unless-stopped

  # Nginx reverse proxy
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - /etc/letsencrypt:/etc/letsencrypt
      - /var/www/certbot:/var/www/certbot
    restart: unless-stopped
    depends_on:
      - app

volumes:
  redis_data:
EOF

# Create Dockerfile
echo "🔨 Creating Dockerfile..."
cat > $DEPLOY_DIR/Dockerfile << 'EOF'
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libffi-dev \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/
COPY static/ ./static/
COPY config/ ./config/
COPY streamlit_app.py .

# Create data directories
RUN mkdir -p data/output logs

# Expose port
EXPOSE 8501

# Run Streamlit
CMD ["streamlit", "run", "streamlit_app.py", "--server.port=8501", "--server.address=0.0.0.0", "--server.headless=true"]
EOF

# Create Nginx configuration
echo "🌐 Creating Nginx configuration..."
cat > $DEPLOY_DIR/nginx.conf << EOF
events {
    worker_connections 1024;
}

http {
    upstream app {
        server app:8501;
    }

    # Rate limiting
    limit_req_zone \$binary_remote_addr zone=api:10m rate=10r/m;
    limit_req_zone \$binary_remote_addr zone=general:10m rate=100r/m;

    server {
        listen 80;
        server_name $DOMAIN www.$DOMAIN;

        # Certbot challenge
        location /.well-known/acme-challenge/ {
            root /var/www/certbot;
        }

        # Redirect HTTP to HTTPS
        location / {
            return 301 https://\$server_name\$request_uri;
        }
    }

    server {
        listen 443 ssl http2;
        server_name $DOMAIN www.$DOMAIN;

        # SSL configuration
        ssl_certificate /etc/letsencrypt/live/$DOMAIN/fullchain.pem;
        ssl_certificate_key /etc/letsencrypt/live/$DOMAIN/privkey.pem;
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
        ssl_prefer_server_ciphers off;

        # Security headers
        add_header X-Frame-Options "SAMEORIGIN" always;
        add_header X-XSS-Protection "1; mode=block" always;
        add_header X-Content-Type-Options "nosniff" always;
        add_header Referrer-Policy "no-referrer-when-downgrade" always;
        add_header Content-Security-Policy "default-src 'self' http: https: data: blob: 'unsafe-inline'" always;

        # File upload limits
        client_max_body_size 50M;

        # Main application
        location / {
            limit_req zone=general burst=20 nodelay;
            proxy_pass http://app;
            proxy_set_header Host \$host;
            proxy_set_header X-Real-IP \$remote_addr;
            proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto \$scheme;
            
            # WebSocket support for Streamlit
            proxy_http_version 1.1;
            proxy_set_header Upgrade \$http_upgrade;
            proxy_set_header Connection "upgrade";
            proxy_read_timeout 86400;
        }

        # API rate limiting
        location /api/ {
            limit_req zone=api burst=5 nodelay;
            proxy_pass http://app;
            proxy_set_header Host \$host;
            proxy_set_header X-Real-IP \$remote_addr;
            proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto \$scheme;
        }

        # Static files caching
        location /static/ {
            expires 30d;
            add_header Cache-Control "public, immutable";
        }
    }
}
EOF

# Copy application files
echo "📁 Copying application files..."
if [ -d "../src" ]; then
    cp -r ../src $DEPLOY_DIR/
    cp -r ../static $DEPLOY_DIR/
    cp -r ../config $DEPLOY_DIR/
    cp ../streamlit_app.py $DEPLOY_DIR/
    cp ../requirements.txt $DEPLOY_DIR/
else
    echo "⚠️ Application files not found. Please copy your project files to $DEPLOY_DIR"
fi

# Set up firewall
echo "🔥 Configuring firewall..."
sudo ufw allow 22/tcp   # SSH
sudo ufw allow 80/tcp   # HTTP
sudo ufw allow 443/tcp  # HTTPS
sudo ufw --force enable

# Create systemd service
echo "🔄 Creating systemd service..."
sudo tee /etc/systemd/system/cinakinetic.service > /dev/null << EOF
[Unit]
Description=CinaKinetic.com - Cinema Action Scene Generator
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=$DEPLOY_DIR
ExecStart=/usr/bin/docker-compose up -d
ExecStop=/usr/bin/docker-compose down
TimeoutStartSec=0
User=$USER
Group=$USER

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable cinakinetic

# Build and start services
echo "🚀 Building and starting services..."
cd $DEPLOY_DIR
docker-compose build
docker-compose up -d

# Get SSL certificate
echo "🔒 Setting up SSL certificate..."
sudo certbot certonly --webroot \
    --webroot-path=/var/www/certbot \
    --email admin@$DOMAIN \
    --agree-tos \
    --no-eff-email \
    -d $DOMAIN \
    -d www.$DOMAIN

# Restart nginx with SSL
docker-compose restart nginx

# Set up auto-renewal for SSL
echo "🔄 Setting up SSL auto-renewal..."
echo "0 12 * * * /usr/bin/certbot renew --quiet" | sudo tee -a /var/spool/cron/crontabs/root

# Wait for services
echo "⏳ Waiting for services to start..."
sleep 30

# Check status
echo "📊 Service Status:"
docker-compose ps

# Get server IP
SERVER_IP=$(curl -s ifconfig.me)

# Display deployment information
echo ""
echo "🎉 CinaKinetic.com Deployment Complete!"
echo "======================================================="
echo "🌐 Domain: https://$DOMAIN"
echo "🖥️ Server IP: $SERVER_IP"
echo "📁 App Directory: $DEPLOY_DIR"
echo ""
echo "📝 IMPORTANT: Complete these steps:"
echo ""
echo "1. 🌐 DNS Configuration:"
echo "   Create A records pointing to $SERVER_IP:"
echo "   • $DOMAIN → $SERVER_IP"
echo "   • www.$DOMAIN → $SERVER_IP"
echo ""
echo "2. 🔑 Environment Variables:"
echo "   Edit $DEPLOY_DIR/.env with your actual keys:"
echo "   • SUPABASE_URL, SUPABASE_ANON_KEY, SUPABASE_SERVICE_KEY"
echo "   • RUNPOD_API_KEY, RUNPOD_ENDPOINT"
echo "   • STRIPE_PUBLISHABLE_KEY, STRIPE_SECRET_KEY"
echo ""
echo "3. 🔄 Restart Services:"
echo "   cd $DEPLOY_DIR && docker-compose restart"
echo ""
echo "🔧 Management Commands:"
echo "   • View logs: cd $DEPLOY_DIR && docker-compose logs -f"
echo "   • Restart: cd $DEPLOY_DIR && docker-compose restart"
echo "   • Stop: cd $DEPLOY_DIR && docker-compose down"
echo "   • Status: cd $DEPLOY_DIR && docker-compose ps"
echo ""
echo "💰 Expected Costs:"
echo "   • DigitalOcean Droplet: $24/month (4GB RAM)"
echo "   • Domain: $12/year"
echo "   • Supabase: Free tier initially"
echo "   • RunPod: ~$2/hour when generating"
echo "   • Stripe: 2.9% + 30¢ per transaction"
echo ""
echo "🚀 Features Available:"
echo "   ✅ LoRA training (character consistency)"
echo "   ✅ Video generation (t2v, i2v, v2v)"
echo "   ✅ R-rated content support"
echo "   ✅ Batch processing (up to 8x)"
echo "   ✅ Multi-ControlNet"
echo "   ✅ Professional storyboard export"
echo "   ✅ Credit-based billing system"
echo ""
echo "🎬 CinaKinetic.com is ready for action!"
echo "======================================================="

# Save deployment info
cat > $DEPLOY_DIR/DEPLOYMENT_INFO.md << EOF
# CinaKinetic.com - Deployment Information

**Deployed:** $(date)
**Domain:** https://$DOMAIN
**Server IP:** $SERVER_IP
**Stack:** Streamlit + Supabase + RunPod RTX 6000 Ada

## Next Steps
1. Configure DNS A records
2. Update environment variables in .env
3. Restart services
4. Test full workflow

## Management
- Logs: \`docker-compose logs -f\`
- Restart: \`docker-compose restart\`
- Config: \`$DEPLOY_DIR/.env\`

## Architecture
- Frontend: Streamlit (Port 8501)
- Database: Supabase (PostgreSQL + Auth)
- Cache: Redis (Port 6379)
- Proxy: Nginx (Ports 80/443)
- AI: RunPod RTX 6000 Ada

## Costs
- DigitalOcean: $24/month
- RunPod: $2/hour when active
- Domain: $12/year
- Supabase: Free tier → $25/month Pro
- Stripe: 2.9% + 30¢ per transaction
EOF

echo "📄 Deployment info saved to $DEPLOY_DIR/DEPLOYMENT_INFO.md"
echo ""
echo "🎬 Welcome to production! Start creating epic action scenes!"