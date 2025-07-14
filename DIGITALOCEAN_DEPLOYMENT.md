# 🎬 CinaKinetic.com - DigitalOcean Deployment Guide

## 🚀 Quick Start

### 1. Create DigitalOcean Droplet
```bash
# Create a 4GB RAM droplet (Basic plan - $24/month)
# OS: Ubuntu 22.04 LTS x64
# Size: 4GB RAM / 2 vCPUs / 80GB SSD
# Datacenter: NYC1 or SFO3 (closest to your users)
```

### 2. Get Your Server IP
After creating the droplet, you'll get an IP address like `157.230.123.456`

### 3. Upload Project to Server
```bash
# From your local machine
cd /Users/watson/Workspace/cinema_action_scene_generator

# Option A: Use SCP to upload
scp -r . root@YOUR_SERVER_IP:/tmp/cinema_action_scene_generator

# Option B: Use Git (if you have a repo)
# ssh root@YOUR_SERVER_IP
# git clone https://github.com/yourusername/cinema_action_scene_generator.git /tmp/cinema_action_scene_generator
```

### 4. SSH into Server and Deploy
```bash
# SSH into your server
ssh root@YOUR_SERVER_IP

# Create a user (don't run as root)
adduser cinakinetic
usermod -aG sudo cinakinetic
su - cinakinetic

# Move project to user directory
sudo mv /tmp/cinema_action_scene_generator /home/cinakinetic/
cd /home/cinakinetic/cinema_action_scene_generator

# Run deployment script
cd deployment
./deploy_to_digitalocean.sh cinakinetic.com
```

## 🔑 Required API Keys

Before running the deployment, gather these API keys:

### Supabase (Database)
1. Go to [supabase.com/dashboard](https://supabase.com/dashboard)
2. Create new project: "cinakinetic-production"
3. Copy these values:
   - Project URL
   - Anon (public) key
   - Service role key

### RunPod (AI Generation)
1. Go to [runpod.io/console](https://runpod.io/console)
2. Get your API key from Settings
3. Note your RTX 6000 Ada endpoint URL

### Stripe (Payments)
1. Go to [dashboard.stripe.com](https://dashboard.stripe.com)
2. Get from Developers → API Keys:
   - Publishable key (pk_live_... or pk_test_...)
   - Secret key (sk_live_... or sk_test_...)

## 🌐 DNS Configuration

After deployment, configure your domain:

### At Your Domain Registrar
Create these A records pointing to your server IP:

```
Type: A Record
Name: @
Value: YOUR_SERVER_IP
TTL: 300

Type: A Record  
Name: www
Value: YOUR_SERVER_IP
TTL: 300
```

### For cinakinetic.com specifically:
```
cinakinetic.com → YOUR_SERVER_IP
www.cinakinetic.com → YOUR_SERVER_IP
```

## 📋 Post-Deployment Setup

### 1. Update Environment Variables
```bash
cd /opt/cinakinetic
nano .env

# Update these values:
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your_anon_key
SUPABASE_SERVICE_KEY=your_service_key
RUNPOD_API_KEY=your_runpod_key
RUNPOD_ENDPOINT=https://your-pod.proxy.runpod.net
STRIPE_PUBLISHABLE_KEY=pk_live_or_test_...
STRIPE_SECRET_KEY=sk_live_or_test_...
```

### 2. Set Up Supabase Database
1. Go to Supabase Dashboard → SQL Editor
2. Copy and run the SQL from `deployment/supabase_setup.sql`
3. This creates all tables, policies, and functions

### 3. Restart Services
```bash
cd /opt/cinakinetic
docker-compose restart
```

### 4. Verify Deployment
```bash
# Check all services are running
docker-compose ps

# Check logs
docker-compose logs -f app

# Test the website
curl -I https://cinakinetic.com
```

## 🔧 Management Commands

### Service Management
```bash
cd /opt/cinakinetic

# View status
docker-compose ps

# View logs
docker-compose logs -f
docker-compose logs -f app    # Just the main app

# Restart services
docker-compose restart
docker-compose restart app    # Just the main app

# Stop/Start
docker-compose down
docker-compose up -d

# Rebuild after code changes
docker-compose build
docker-compose up -d
```

### System Management
```bash
# Check system resources
htop
df -h

# Check firewall
sudo ufw status

# Check SSL certificate
sudo certbot certificates

# Renew SSL (automatic via cron)
sudo certbot renew --dry-run
```

## 💰 Cost Breakdown

### Monthly Costs
- **DigitalOcean Droplet**: $24/month (4GB RAM)
- **Domain Registration**: $1/month ($12/year)
- **Supabase**: Free tier → $25/month Pro when needed
- **RunPod**: ~$2/hour when generating (turn off when idle)
- **Stripe**: 2.9% + 30¢ per transaction

### **Total: ~$25-50/month + usage-based RunPod**

## 🚀 Features Available

✅ **LoRA Training** - Character consistency (15-25 images, ~20 min)  
✅ **Video Generation** - Text-to-video, Image-to-video, Video-to-video  
✅ **R-rated Content** - Adult action scenes (major platforms restrict this)  
✅ **Batch Processing** - Generate up to 8 images at once  
✅ **Multi-ControlNet** - OpenPose, Canny, Depth, Lineart  
✅ **Professional Export** - PDF storyboards, image sequences  
✅ **Credit System** - Flexible billing with Stripe  
✅ **Character Library** - Save and reuse character LoRAs  
✅ **Fighting Styles** - BJJ, martial arts, action poses  

## 🔒 Security Features

✅ **SSL/HTTPS** - Automatic Let's Encrypt certificates  
✅ **Rate Limiting** - API protection via Nginx  
✅ **Firewall** - UFW configured for security  
✅ **User Authentication** - Supabase Auth integration  
✅ **Data Encryption** - Secure API keys and user data  

## 🎯 Competitive Advantages

1. **R-rated Content Support** - Major platforms (Runway, Pika) restrict this
2. **Character Consistency** - LoRA training for repeated characters
3. **Fighting Style Specialization** - BJJ, martial arts focus
4. **Video Generation** - Full t2v, i2v, v2v pipeline
5. **RTX 6000 Ada Performance** - 10-25 second generation times
6. **Professional Workflow** - Storyboard management and export

## 🆘 Troubleshooting

### Common Issues

**SSL Certificate Issues**
```bash
# Check certificate status
sudo certbot certificates

# Force renewal
sudo certbot renew --force-renewal
docker-compose restart nginx
```

**Application Won't Start**
```bash
# Check logs
docker-compose logs -f app

# Common fixes
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

**Database Connection Issues**
```bash
# Verify Supabase credentials in .env
# Test connection from server
curl -H "apikey: YOUR_ANON_KEY" "YOUR_SUPABASE_URL/rest/v1/"
```

**RunPod Connection Issues**
```bash
# Test RunPod endpoint
curl -H "Authorization: Bearer YOUR_API_KEY" "YOUR_RUNPOD_ENDPOINT/system_stats"
```

### Support Contacts
- **DigitalOcean**: support.digitalocean.com
- **Supabase**: supabase.com/support  
- **RunPod**: discord.gg/runpod
- **Stripe**: support.stripe.com

---

## 🎬 Ready to Launch!

Once deployed, your users can:
1. Sign up at https://cinakinetic.com
2. Train character LoRAs for consistency
3. Generate R-rated action scenes
4. Create video sequences
5. Export professional storyboards
6. Pay with credits via Stripe

**CinaKinetic.com - Where Epic Action Scenes Come to Life! 🚀**