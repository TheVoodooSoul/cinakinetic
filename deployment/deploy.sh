#!/bin/bash

# Cinema Action Scene Generator - Production Deployment Script

set -e

echo "🎬 Cinema Action Scene Generator - Production Deployment"
echo "========================================================"

# Check if domain is provided
if [ -z "$1" ]; then
    echo "❌ Error: Please provide your domain"
    echo "Usage: ./deploy.sh yourdomain.com"
    exit 1
fi

DOMAIN=$1
echo "🌐 Domain: $DOMAIN"

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    echo "❌ Please don't run as root"
    exit 1
fi

# Install Docker if not present
if ! command -v docker &> /dev/null; then
    echo "📦 Installing Docker..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
    sudo usermod -aG docker $USER
    echo "✅ Docker installed. Please log out and back in, then run this script again."
    exit 0
fi

# Install Docker Compose if not present
if ! command -v docker-compose &> /dev/null; then
    echo "📦 Installing Docker Compose..."
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
fi

# Create deployment directory
DEPLOY_DIR="/opt/cinema-action-generator"
echo "📁 Creating deployment directory: $DEPLOY_DIR"

if [ ! -d "$DEPLOY_DIR" ]; then
    sudo mkdir -p $DEPLOY_DIR
    sudo chown $USER:$USER $DEPLOY_DIR
fi

# Copy files
echo "📋 Copying application files..."
cp -r ../src $DEPLOY_DIR/
cp -r ../config $DEPLOY_DIR/
cp -r ../static $DEPLOY_DIR/
cp -r ../docs $DEPLOY_DIR/
cp ../requirements.txt $DEPLOY_DIR/
cp docker-compose.prod.yml $DEPLOY_DIR/docker-compose.yml
cp Dockerfile.* $DEPLOY_DIR/
cp .env.example $DEPLOY_DIR/

cd $DEPLOY_DIR

# Create .env file
if [ ! -f ".env" ]; then
    echo "⚙️ Creating environment configuration..."
    cp .env.example .env
    
    # Generate secure passwords
    DB_PASSWORD=$(openssl rand -base64 32)
    JWT_SECRET=$(openssl rand -base64 64)
    ENCRYPTION_KEY=$(openssl rand -base64 32)
    MINIO_ACCESS_KEY=$(openssl rand -base64 16)
    MINIO_SECRET_KEY=$(openssl rand -base64 32)
    
    # Update .env file
    sed -i "s/yoursite.com/$DOMAIN/g" .env
    sed -i "s/your_secure_password/$DB_PASSWORD/g" .env
    sed -i "s/your_jwt_secret_key_here/$JWT_SECRET/g" .env
    sed -i "s/your_32_character_encryption_key/$ENCRYPTION_KEY/g" .env
    sed -i "s/your_minio_access_key/$MINIO_ACCESS_KEY/g" .env
    sed -i "s/your_minio_secret_key/$MINIO_SECRET_KEY/g" .env
    
    echo "✅ Environment file created"
    echo "⚠️  IMPORTANT: Please edit .env file with your actual API keys:"
    echo "   - RUNPOD_API_KEY"
    echo "   - RUNPOD_ENDPOINT" 
    echo "   - STRIPE_PUBLISHABLE_KEY"
    echo "   - STRIPE_SECRET_KEY"
    echo "   - ACME_EMAIL"
fi

# Create necessary directories
mkdir -p data static/output logs

# Set up firewall
echo "🔥 Configuring firewall..."
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw --force enable

# Create systemd service for auto-restart
echo "🔄 Creating systemd service..."
sudo tee /etc/systemd/system/cinema-action-generator.service > /dev/null <<EOF
[Unit]
Description=Cinema Action Scene Generator
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=$DEPLOY_DIR
ExecStart=/usr/local/bin/docker-compose up -d
ExecStop=/usr/local/bin/docker-compose down
TimeoutStartSec=0

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable cinema-action-generator

# Build and start services
echo "🚀 Building and starting services..."
docker-compose build
docker-compose up -d

# Wait for services to be ready
echo "⏳ Waiting for services to start..."
sleep 30

# Check service status
echo "📊 Service Status:"
docker-compose ps

# Show deployment info
echo ""
echo "🎉 Deployment Complete!"
echo "========================================================"
echo "🌐 Website: https://$DOMAIN"
echo "🔧 API: https://api.$DOMAIN"
echo "📊 Traefik Dashboard: http://$DOMAIN:8080"
echo "💾 MinIO Console: http://$DOMAIN:9001"
echo ""
echo "📝 Next Steps:"
echo "1. Edit $DEPLOY_DIR/.env with your API keys"
echo "2. Run: docker-compose restart"
echo "3. Set up DNS A records:"
echo "   $DOMAIN -> $(curl -s ifconfig.me)"
echo "   api.$DOMAIN -> $(curl -s ifconfig.me)"
echo ""
echo "🔐 Important Files:"
echo "   Environment: $DEPLOY_DIR/.env"
echo "   Logs: docker-compose logs -f"
echo "   Data: $DEPLOY_DIR/data"
echo ""
echo "🚀 Your Cinema Action Scene Generator is now live!"
echo "========================================================"