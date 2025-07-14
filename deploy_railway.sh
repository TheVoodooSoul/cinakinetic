#!/bin/bash

# 🎬 CinaKinetic.com - Railway Deployment Script
# Full-featured cinema action scene generator

echo "🎬 CinaKinetic.com - Railway Deployment"
echo "======================================"
echo "🚀 Full-stack Streamlit app with real AI generation"
echo "💰 Cost: ~$5-10/month"
echo ""

# Copy Railway requirements
cp requirements_railway.txt requirements.txt

# Commit changes for Railway deployment
git add .
git status

echo ""
echo "📋 Next Steps:"
echo ""
echo "1. 🌐 Go to https://railway.app"
echo "2. 🔗 Click 'Deploy from GitHub repo'"
echo "3. 📁 Select this repository: cinema_action_scene_generator"
echo "4. ⚙️ Set environment variables:"
echo "   - RUNPOD_API_KEY = your_runpod_api_key"
echo "   - RUNPOD_ENDPOINT = https://api.runpod.ai/v2/jmskqno8hvy4an/run"
echo ""
echo "5. 🚀 Railway will auto-deploy in ~3 minutes"
echo ""
echo "✅ Features you'll get on Railway:"
echo "   • Real AI image generation with RunPod"
echo "   • Full Streamlit interface"
echo "   • All LoRA training features"
echo "   • Video generation capabilities"
echo "   • User gallery and billing"
echo "   • No serverless function limits"
echo ""
echo "🎬 Your full-featured CinaKinetic app will be live!"
echo "======================================"