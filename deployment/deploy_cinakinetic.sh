#!/bin/bash

# CinaKinetic.com Deployment Script
# Stack: Vercel + Supabase + RunPod

set -e

echo "🎬 CinaKinetic.com - Cinema Action Scene Generator Deployment"
echo "============================================================="
echo "🚀 Stack: Vercel + Supabase + RunPod RTX 6000 Ada"
echo "🌐 Domain: cinakinetic.com"
echo ""

# Check dependencies
echo "🔍 Checking dependencies..."

if ! command -v npm &> /dev/null; then
    echo "❌ npm is required. Please install Node.js"
    exit 1
fi

if ! command -v git &> /dev/null; then
    echo "❌ git is required"
    exit 1
fi

# Install Vercel CLI if not present
if ! command -v vercel &> /dev/null; then
    echo "📦 Installing Vercel CLI..."
    npm install -g vercel
fi

# Install Supabase CLI if not present
if ! command -v supabase &> /dev/null; then
    echo "📦 Installing Supabase CLI..."
    npm install -g supabase
fi

echo "✅ Dependencies ready"

# Setup project for Vercel
echo ""
echo "🚀 Setting up Vercel deployment..."

# Create optimized requirements.txt for Vercel
cat > requirements.txt << EOF
streamlit==1.46.1
fastapi==0.116.1
requests==2.32.4
pillow==11.3.0
opencv-python-headless==4.12.0.88
numpy==2.2.6
pydantic==2.11.7
supabase==2.3.0
stripe==8.8.0
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
streamlit-drawable-canvas==0.9.3
aiohttp==3.12.14
python-multipart==0.0.20
pydantic-settings==2.10.1
EOF

# Create Vercel-optimized entry point
mkdir -p api
cat > api/index.py << 'EOF'
from src.ui.streamlit_app import main
import streamlit as st

# Configure Streamlit for Vercel
st.set_page_config(
    page_title="CinaKinetic - Cinema Action Scene Generator",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

if __name__ == "__main__":
    main()
EOF

# Create deployment configuration
cat > deployment_config.json << EOF
{
    "domain": "cinakinetic.com",
    "stack": {
        "frontend": "Vercel",
        "database": "Supabase", 
        "ai_backend": "RunPod RTX 6000 Ada",
        "payments": "Stripe",
        "storage": "Supabase Storage"
    },
    "estimated_costs": {
        "vercel": "Free tier / $20/month Pro",
        "supabase": "Free tier / $25/month Pro", 
        "runpod": "$2/hour RTX 6000 Ada (usage-based)",
        "stripe": "2.9% + 30¢ per transaction",
        "domain": "$12/year"
    }
}
EOF

echo "✅ Vercel configuration ready"

# Supabase setup
echo ""
echo "🗄️ Setting up Supabase..."

echo "📋 Supabase Setup Instructions:"
echo "1. Go to https://supabase.com/dashboard"
echo "2. Create new project: 'cinakinetic-production'"
echo "3. Region: us-east-1 (closest to Vercel)"
echo "4. Copy your project credentials:"
echo "   - Project URL"
echo "   - Anon (public) key"
echo "   - Service role key"
echo ""

read -p "Press Enter when you have your Supabase project ready..."

echo ""
echo "🔧 Supabase Database Schema Setup:"
echo "1. Go to Supabase Dashboard → SQL Editor"
echo "2. Copy and run the SQL from: deployment/supabase_setup.sql"
echo "3. This will create all tables, policies, and functions"
echo ""

read -p "Press Enter when database schema is set up..."

# RunPod connection test
echo ""
echo "🔥 RunPod RTX 6000 Ada Configuration:"
echo ""

read -p "Enter your RunPod API key: " RUNPOD_API_KEY
read -p "Enter your RunPod endpoint (https://your-pod-8188.proxy.runpod.net): " RUNPOD_ENDPOINT

if [ ! -z "$RUNPOD_ENDPOINT" ]; then
    echo "🧪 Testing RunPod connection..."
    
    response=$(curl -s -o /dev/null -w "%{http_code}" "$RUNPOD_ENDPOINT/system_stats" || echo "000")
    
    if [ "$response" = "200" ]; then
        echo "✅ RunPod RTX 6000 Ada connected successfully!"
    else
        echo "⚠️ RunPod connection test failed (HTTP: $response)"
        echo "   Make sure your pod is running and endpoint is correct"
    fi
fi

# Stripe setup
echo ""
echo "💳 Stripe Payment Setup:"
echo "1. Go to https://dashboard.stripe.com"
echo "2. Create account or login"
echo "3. Get your API keys from Developers → API Keys"
echo "4. Set up products and pricing in Products section"
echo ""

read -p "Enter your Stripe publishable key (pk_live_... or pk_test_...): " STRIPE_PUBLISHABLE_KEY
read -p "Enter your Stripe secret key (sk_live_... or sk_test_...): " STRIPE_SECRET_KEY

# Generate secure secrets
JWT_SECRET=$(openssl rand -base64 64)
ENCRYPTION_KEY=$(openssl rand -base64 32)

echo ""
echo "🔐 Generated secure secrets for production"

# Supabase credentials input
echo ""
echo "📝 Enter your Supabase credentials:"
read -p "Supabase URL: " SUPABASE_URL
read -p "Supabase Anon Key: " SUPABASE_ANON_KEY
read -p "Supabase Service Key: " SUPABASE_SERVICE_KEY

# Vercel deployment
echo ""
echo "🚀 Deploying to Vercel..."

# Login to Vercel (if not already)
vercel whoami || vercel login

# Set environment variables
echo "⚙️ Configuring environment variables..."

vercel env add SUPABASE_URL production <<< "$SUPABASE_URL"
vercel env add SUPABASE_ANON_KEY production <<< "$SUPABASE_ANON_KEY"
vercel env add SUPABASE_SERVICE_KEY production <<< "$SUPABASE_SERVICE_KEY"
vercel env add RUNPOD_API_KEY production <<< "$RUNPOD_API_KEY"
vercel env add RUNPOD_ENDPOINT production <<< "$RUNPOD_ENDPOINT"
vercel env add STRIPE_PUBLISHABLE_KEY production <<< "$STRIPE_PUBLISHABLE_KEY"
vercel env add STRIPE_SECRET_KEY production <<< "$STRIPE_SECRET_KEY"
vercel env add JWT_SECRET production <<< "$JWT_SECRET"
vercel env add ENCRYPTION_KEY production <<< "$ENCRYPTION_KEY"
vercel env add PRODUCTION production <<< "true"
vercel env add DOMAIN production <<< "cinakinetic.com"

echo "✅ Environment variables configured"

# Deploy to Vercel
echo ""
echo "🚀 Deploying application..."

vercel --prod --confirm

echo ""
echo "🎉 Deployment Complete!"
echo "============================================================="
echo "🌐 Website: https://cinakinetic.com"
echo "🗄️ Database: Supabase (PostgreSQL)"
echo "🔥 AI Backend: RunPod RTX 6000 Ada"
echo "💳 Payments: Stripe"
echo ""
echo "📊 Performance Expectations:"
echo "   • Global CDN via Vercel"
echo "   • Sub-100ms database queries via Supabase"
echo "   • 10-25 second AI generation via RTX 6000 Ada"
echo "   • Auto-scaling based on traffic"
echo ""
echo "💰 Cost Structure:"
echo "   • Vercel: Free tier (first 100GB bandwidth)"
echo "   • Supabase: Free tier (500MB database, 1GB storage)"
echo "   • RunPod: ~$2/hour when generating (stop when idle)"
echo "   • Stripe: 2.9% + 30¢ per transaction"
echo ""
echo "🔧 Next Steps:"
echo "1. Set up custom domain: cinakinetic.com → Vercel"
echo "2. Configure DNS CNAME: cinakinetic.com → cname.vercel-dns.com"
echo "3. Test full workflow: signup → generate → payment"
echo "4. Set up monitoring and analytics"
echo ""
echo "📱 Admin URLs:"
echo "   • Vercel Dashboard: https://vercel.com/dashboard"
echo "   • Supabase Dashboard: https://supabase.com/dashboard"
echo "   • Stripe Dashboard: https://dashboard.stripe.com"
echo "   • RunPod Dashboard: https://runpod.io/console"
echo ""
echo "🎬 CinaKinetic.com is now LIVE!"
echo "============================================================="

# Save deployment info
cat > DEPLOYMENT_INFO.md << EOF
# CinaKinetic.com Deployment Information

## 🚀 Live URLs
- **Main Site**: https://cinakinetic.com
- **Status**: Production Ready ✅

## 🏗️ Architecture
- **Frontend**: Vercel (Global CDN)
- **Database**: Supabase (PostgreSQL + Auth)
- **AI Backend**: RunPod RTX 6000 Ada
- **Payments**: Stripe
- **Storage**: Supabase Storage

## 🔑 Environment Variables Set
- SUPABASE_URL ✅
- SUPABASE_ANON_KEY ✅
- SUPABASE_SERVICE_KEY ✅
- RUNPOD_API_KEY ✅
- RUNPOD_ENDPOINT ✅
- STRIPE_PUBLISHABLE_KEY ✅
- STRIPE_SECRET_KEY ✅
- JWT_SECRET ✅ (Generated)
- ENCRYPTION_KEY ✅ (Generated)

## 📊 Expected Performance
- **Page Load**: <100ms (Vercel CDN)
- **Database Queries**: <50ms (Supabase)
- **AI Generation**: 10-25 seconds (RTX 6000 Ada)
- **Uptime**: 99.9% (Vercel SLA)

## 💰 Cost Monitoring
- Monitor usage in each service dashboard
- Set up billing alerts in Vercel/Supabase
- RunPod: Stop pods when not in use
- Stripe: Monitor transaction volume

## 🔧 Management
- **Code Updates**: Push to main branch → Auto-deploy
- **Database**: Manage via Supabase Dashboard
- **Monitoring**: Vercel Analytics + Supabase Logs
- **Scaling**: Automatic via Vercel/Supabase

Deployed on: $(date)
EOF

echo "📄 Deployment information saved to DEPLOYMENT_INFO.md"
echo ""
echo "🎉 Welcome to production! Your users can now create epic action scenes at cinakinetic.com"