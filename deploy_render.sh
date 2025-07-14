#!/bin/bash

# 🎬 CinaKinetic.com - Render.com Deployment
# Full-featured cinema action scene generator

echo "🎬 CinaKinetic.com - Render.com Deployment"
echo "=========================================="
echo "🚀 Full-stack Streamlit app with real AI generation"
echo "💰 Cost: FREE tier available, then $7/month"
echo "⚡ Faster deployment than Railway"
echo ""

# Prepare for Render
cp requirements_render.txt requirements.txt

# Commit changes
git add .
git status

echo ""
echo "📋 Render.com Deployment Steps:"
echo ""
echo "1. 🌐 Go to https://render.com"
echo "2. 📱 Sign up with GitHub"
echo "3. 🔗 Click 'New Web Service'"
echo "4. 📁 Connect your GitHub repo: cinema_action_scene_generator"
echo "5. ⚙️ Render will auto-detect Python/Streamlit"
echo ""
echo "6. 🔧 Set these in Render dashboard:"
echo "   Build Command: pip install -r requirements.txt"
echo "   Start Command: streamlit run railway_setup.py --server.port \$PORT --server.headless true --server.enableCORS false --server.address 0.0.0.0"
echo ""
echo "7. 🔑 Add environment variables:"
echo "   • RUNPOD_API_KEY = your_runpod_api_key"
echo "   • RUNPOD_ENDPOINT = https://api.runpod.ai/v2/jmskqno8hvy4an/run"
echo ""
echo "8. 🚀 Click 'Create Web Service'"
echo ""
echo "✅ Render Advantages:"
echo "   • FREE tier with 750 hours/month"
echo "   • No complex rules like Railway"
echo "   • Auto-deploys from GitHub"
echo "   • Perfect for Streamlit apps"
echo "   • Real AI generation works perfectly"
echo "   • Custom domains included"
echo ""
echo "🎬 Your CinaKinetic app will be live in ~5 minutes!"
echo "=========================================="