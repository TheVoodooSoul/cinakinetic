#!/bin/bash

# 🎬 CinaKinetic.com - Vercel Deployment (Optimized)
# Lightweight web app + RunPod API for AI generation

set -e

echo "🎬 CinaKinetic.com - Vercel Optimized Deployment"
echo "================================================"
echo "🌐 Domain: cinakinetic.com"
echo "🚀 Stack: Vercel + Supabase + RunPod RTX 6000 Ada"
echo "💰 Cost: Free/Pro Vercel + RunPod usage-based"
echo ""

# Create Vercel-optimized structure
echo "📁 Creating Vercel-optimized structure..."

# Create lightweight requirements.txt for Vercel
cat > requirements.txt << EOF
streamlit==1.39.0
fastapi==0.104.1
requests==2.31.0
pillow==10.1.0
numpy==1.24.3
pydantic==2.5.0
supabase==2.0.3
stripe==7.8.0
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
streamlit-drawable-canvas==0.9.3
aiohttp==3.9.1
python-multipart==0.0.6
pydantic-settings==2.1.0
python-dotenv==1.0.0
EOF

# Create Vercel configuration
cat > vercel.json << 'EOF'
{
  "version": 2,
  "builds": [
    {
      "src": "streamlit_app.py",
      "use": "@vercel/python",
      "config": { 
        "maxLambdaSize": "50mb",
        "runtime": "python3.11"
      }
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "streamlit_app.py"
    }
  ],
  "env": {
    "PRODUCTION": "true"
  },
  "functions": {
    "streamlit_app.py": {
      "maxDuration": 30
    }
  }
}
EOF

# Create Vercel-optimized Streamlit app
cat > streamlit_app_vercel.py << 'EOF'
"""
🎬 CinaKinetic.com - Cinema Action Scene Generator
Vercel-optimized version with RunPod API integration
"""

import streamlit as st
import requests
import json
import os
from datetime import datetime
import time

# Page config
st.set_page_config(
    page_title="CinaKinetic - Cinema Action Scene Generator",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for CinaKinetic branding
st.markdown("""
<style>
.main-header {
    background: linear-gradient(135deg, #1e3c72, #2a5298);
    padding: 2rem;
    border-radius: 10px;
    margin-bottom: 2rem;
    text-align: center;
}
.main-header h1 {
    color: white;
    font-size: 3rem;
    margin: 0;
    text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
}
.main-header p {
    color: #e0e0e0;
    font-size: 1.2rem;
    margin: 0.5rem 0 0 0;
}
.feature-card {
    background: #f8f9fa;
    padding: 1.5rem;
    border-radius: 8px;
    border: 1px solid #dee2e6;
    margin: 1rem 0;
}
.pricing-card {
    background: linear-gradient(135deg, #667eea, #764ba2);
    color: white;
    padding: 2rem;
    border-radius: 10px;
    text-align: center;
    margin: 1rem;
}
.status-running { color: #28a745; }
.status-stopped { color: #dc3545; }
.status-pending { color: #ffc107; }
</style>
""", unsafe_allow_html=True)

# Environment variables
RUNPOD_API_KEY = os.getenv("RUNPOD_API_KEY", "")
RUNPOD_ENDPOINT = os.getenv("RUNPOD_ENDPOINT", "")
SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY", "")

def check_runpod_status():
    """Check if RunPod endpoint is available"""
    if not RUNPOD_ENDPOINT:
        return False, "Endpoint not configured"
    
    try:
        response = requests.get(f"{RUNPOD_ENDPOINT}/system_stats", timeout=5)
        return response.status_code == 200, "Connected"
    except:
        return False, "Disconnected"

def generate_image_runpod(prompt, style="cinematic", resolution="1024x1024"):
    """Generate image via RunPod API"""
    if not RUNPOD_ENDPOINT or not RUNPOD_API_KEY:
        return None, "RunPod not configured"
    
    payload = {
        "input": {
            "prompt": prompt,
            "style": style,
            "width": int(resolution.split('x')[0]),
            "height": int(resolution.split('x')[1]),
            "steps": 20,
            "cfg_scale": 7
        }
    }
    
    try:
        response = requests.post(
            f"{RUNPOD_ENDPOINT}/runsync", 
            json=payload,
            headers={"Authorization": f"Bearer {RUNPOD_API_KEY}"},
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            return result.get("output", {}).get("image_url"), "Success"
        else:
            return None, f"API Error: {response.status_code}"
    except Exception as e:
        return None, f"Connection Error: {str(e)}"

def main():
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🎬 CinaKinetic</h1>
        <p>Cinema Action Scene Generator</p>
        <p><em>Professional R-rated action sequences with AI</em></p>
    </div>
    """, unsafe_allow_html=True)

    # Sidebar
    with st.sidebar:
        st.markdown("## 🎬 CinaKinetic")
        
        # RunPod Status
        st.markdown("### 🔥 AI Status")
        is_connected, status_msg = check_runpod_status()
        status_class = "status-running" if is_connected else "status-stopped"
        st.markdown(f'<p class="{status_class}">● {status_msg}</p>', unsafe_allow_html=True)
        
        if not is_connected:
            st.warning("⚠️ Configure RunPod API in environment variables")
        
        # Navigation
        st.markdown("### 🎯 Features")
        page = st.radio("Navigate", [
            "🏠 Home",
            "🎨 Generate",
            "🧬 LoRA Training", 
            "🎥 Video Generation",
            "📊 Storyboard",
            "👤 Characters",
            "💳 Pricing"
        ])
        
        # User info
        st.markdown("### 👤 Account")
        if st.button("🔐 Login"):
            st.info("Login with Supabase Auth")
        
        st.markdown("**Credits:** 25 remaining")
        st.progress(0.8)

    # Main content based on page selection
    if page == "🏠 Home":
        show_home_page()
    elif page == "🎨 Generate":
        show_generation_page()
    elif page == "🧬 LoRA Training":
        show_lora_page()
    elif page == "🎥 Video Generation":
        show_video_page()
    elif page == "📊 Storyboard":
        show_storyboard_page()
    elif page == "👤 Characters":
        show_characters_page()
    elif page == "💳 Pricing":
        show_pricing_page()

def show_home_page():
    st.markdown("## 🚀 Welcome to CinaKinetic")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="feature-card">
            <h3>🎨 AI Generation</h3>
            <p>Create stunning R-rated action scenes with state-of-the-art AI models</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="feature-card">
            <h3>🧬 LoRA Training</h3>
            <p>Train custom character models for consistent appearance across scenes</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="feature-card">
            <h3>🎥 Video Generation</h3>
            <p>Transform static images into dynamic action sequences</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Recent generations placeholder
    st.markdown("## 📸 Recent Generations")
    col1, col2, col3, col4 = st.columns(4)
    
    for i, col in enumerate([col1, col2, col3, col4]):
        with col:
            st.image("https://picsum.photos/300/400", caption=f"Action Scene {i+1}")

def show_generation_page():
    st.markdown("## 🎨 Generate Action Scene")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Prompt input
        prompt = st.text_area(
            "🎬 Scene Description", 
            "A martial artist in a dark alley, dramatic lighting, cinematic composition",
            height=100
        )
        
        # Style options
        style = st.selectbox("🎭 Style", [
            "cinematic", "dark", "gritty", "noir", "action", "thriller"
        ])
        
        # Resolution
        resolution = st.selectbox("📐 Resolution", [
            "768x768", "1024x1024", "1024x1536", "1536x1024"
        ])
        
        # LoRA selection
        lora = st.selectbox("🧬 Character LoRA", [
            "None", "Action Hero Male", "Femme Fatale", "Martial Artist"
        ])
        
        # Generate button
        if st.button("🚀 Generate Scene", type="primary"):
            if prompt:
                with st.spinner("🎬 Generating your action scene..."):
                    image_url, status = generate_image_runpod(prompt, style, resolution)
                    
                    if image_url:
                        st.success("✅ Scene generated successfully!")
                        st.image(image_url, caption="Generated Action Scene")
                        
                        # Download button
                        if st.button("💾 Download"):
                            st.info("Download functionality ready")
                    else:
                        st.error(f"❌ Generation failed: {status}")
            else:
                st.warning("⚠️ Please enter a scene description")
    
    with col2:
        st.markdown("### 🎯 Quick Prompts")
        quick_prompts = [
            "Intense fight scene in a warehouse",
            "Car chase through city streets", 
            "Rooftop confrontation at night",
            "Underground fight club",
            "Tactical team breach",
            "Motorcycle pursuit"
        ]
        
        for quick_prompt in quick_prompts:
            if st.button(quick_prompt, key=quick_prompt):
                st.rerun()

def show_lora_page():
    st.markdown("## 🧬 LoRA Character Training")
    
    st.info("💡 Train custom character models for consistent appearance across multiple scenes")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📸 Upload Training Images")
        uploaded_files = st.file_uploader(
            "Choose images (15-25 recommended)", 
            accept_multiple_files=True,
            type=['png', 'jpg', 'jpeg']
        )
        
        if uploaded_files:
            st.success(f"📁 {len(uploaded_files)} images uploaded")
            
            # Show preview
            cols = st.columns(3)
            for i, file in enumerate(uploaded_files[:6]):  # Show first 6
                with cols[i % 3]:
                    st.image(file, caption=f"Image {i+1}")
        
        # Training parameters
        st.markdown("### ⚙️ Training Settings")
        char_name = st.text_input("Character Name", "Action Hero")
        training_steps = st.slider("Training Steps", 500, 2000, 1000)
        learning_rate = st.selectbox("Learning Rate", ["1e-4", "5e-5", "1e-5"])
        
        # Cost calculation
        estimated_cost = len(uploaded_files) * 3 if uploaded_files else 75
        st.markdown(f"💰 **Estimated Cost:** {estimated_cost} credits (~20 minutes)")
        
        if st.button("🚀 Start Training", type="primary", disabled=not uploaded_files):
            st.info("🔄 Training would start on RunPod RTX 6000 Ada...")
    
    with col2:
        st.markdown("### 🎭 Existing Characters")
        
        characters = [
            {"name": "Action Hero Male", "status": "Ready", "usage": 45},
            {"name": "Femme Fatale", "status": "Training", "usage": 12},
            {"name": "Martial Artist", "status": "Ready", "usage": 78}
        ]
        
        for char in characters:
            with st.expander(f"{char['name']} - {char['status']}"):
                st.write(f"**Usage:** {char['usage']} generations")
                if char['status'] == "Ready":
                    if st.button(f"Use {char['name']}", key=char['name']):
                        st.success(f"Selected {char['name']} for generation")

def show_video_page():
    st.markdown("## 🎥 Video Generation")
    
    tab1, tab2, tab3 = st.tabs(["📝 Text-to-Video", "🖼️ Image-to-Video", "🎬 Video-to-Video"])
    
    with tab1:
        st.markdown("### 📝 Text-to-Video")
        video_prompt = st.text_area("Video Description", "Fighter throwing punches in slow motion")
        duration = st.slider("Duration (seconds)", 2, 10, 4)
        fps = st.selectbox("Frame Rate", [24, 30, 60])
        
        if st.button("🎬 Generate Video"):
            st.info("🎥 Video generation would process on RunPod...")
    
    with tab2:
        st.markdown("### 🖼️ Image-to-Video")
        uploaded_image = st.file_uploader("Upload Image", type=['png', 'jpg', 'jpeg'])
        if uploaded_image:
            st.image(uploaded_image, caption="Source Image")
        
        motion_prompt = st.text_input("Motion Description", "Add dynamic fighting movements")
        
        if st.button("🎬 Animate Image"):
            st.info("🎥 Image animation would process on RunPod...")
    
    with tab3:
        st.markdown("### 🎬 Video-to-Video")
        st.info("Transform existing videos with new styles and effects")

def show_storyboard_page():
    st.markdown("## 📊 Professional Storyboard")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### 🎬 Scene Sequence")
        
        # Storyboard panels
        for i in range(3):
            with st.expander(f"Scene {i+1}", expanded=i==0):
                scene_col1, scene_col2 = st.columns([1, 2])
                
                with scene_col1:
                    st.image("https://picsum.photos/200/150", caption=f"Scene {i+1}")
                
                with scene_col2:
                    st.text_area(f"Description {i+1}", f"Action sequence {i+1}", key=f"desc_{i}")
                    st.text_input(f"Duration", "3 seconds", key=f"dur_{i}")
    
    with col2:
        st.markdown("### 📋 Export Options")
        
        export_format = st.radio("Format", ["PDF", "PNG Sequence", "JSON"])
        
        if st.button("📄 Export Storyboard"):
            st.success("✅ Storyboard exported!")
        
        st.markdown("### 📊 Project Stats")
        st.metric("Total Scenes", "8")
        st.metric("Total Duration", "24 seconds")
        st.metric("Credits Used", "156")

def show_characters_page():
    st.markdown("## 👤 Character Library")
    
    # Character grid
    cols = st.columns(3)
    
    characters = [
        {"name": "Action Hero", "image": "https://picsum.photos/200/250", "scenes": 24},
        {"name": "Femme Fatale", "image": "https://picsum.photos/200/250", "scenes": 18}, 
        {"name": "Martial Artist", "image": "https://picsum.photos/200/250", "scenes": 31}
    ]
    
    for i, char in enumerate(characters):
        with cols[i % 3]:
            st.image(char["image"], caption=char["name"])
            st.write(f"**Scenes:** {char['scenes']}")
            if st.button(f"Edit {char['name']}", key=char["name"]):
                st.info(f"Editing {char['name']}")

def show_pricing_page():
    st.markdown("## 💳 Pricing Plans")
    
    col1, col2, col3, col4 = st.columns(4)
    
    plans = [
        {"name": "Starter", "price": "$5", "credits": 100, "features": ["Basic Generation", "768x768 Images", "Email Support"]},
        {"name": "Pro", "price": "$15", "credits": 500, "features": ["HD Generation", "Video Creation", "LoRA Training", "Priority Support"]},
        {"name": "Studio", "price": "$40", "credits": 2000, "features": ["Ultra HD", "Batch Processing", "Multi-ControlNet", "Phone Support"]},
        {"name": "Enterprise", "price": "$150", "credits": 10000, "features": ["Unlimited Features", "Custom Models", "Dedicated Support", "SLA"]}
    ]
    
    for i, plan in enumerate(plans):
        with [col1, col2, col3, col4][i]:
            st.markdown(f"""
            <div class="pricing-card">
                <h3>{plan['name']}</h3>
                <h2>{plan['price']}/month</h2>
                <p>{plan['credits']} credits</p>
                <ul>
                    {''.join([f'<li>{feature}</li>' for feature in plan['features']])}
                </ul>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button(f"Choose {plan['name']}", key=plan['name']):
                st.success(f"Selected {plan['name']} plan!")

if __name__ == "__main__":
    main()
EOF

# Copy optimized app over main app
cp streamlit_app_vercel.py streamlit_app.py

echo "✅ Vercel-optimized structure created!"
echo ""
echo "📝 Next steps:"
echo "1. Install Vercel CLI: npm install -g vercel"
echo "2. Login to Vercel: vercel login"  
echo "3. Deploy: vercel --prod"
echo ""
echo "🔑 Required environment variables in Vercel:"
echo "   - RUNPOD_API_KEY"
echo "   - RUNPOD_ENDPOINT"
echo "   - SUPABASE_URL"
echo "   - SUPABASE_ANON_KEY"
echo "   - STRIPE_PUBLISHABLE_KEY"
echo "   - STRIPE_SECRET_KEY"
echo ""
echo "💰 Expected costs:"
echo "   - Vercel: Free tier (or $20/month Pro)"
echo "   - RunPod: $2/hour when generating"
echo "   - Supabase: Free tier"
echo "   - Domain: $12/year"
echo ""
echo "🎬 Total: ~$0-20/month + usage-based RunPod!"
EOF