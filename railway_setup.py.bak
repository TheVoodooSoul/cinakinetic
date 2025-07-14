"""
🎬 CinaKinetic.com - Railway Deployment Setup
Full-featured cinema action scene generator with real AI generation
"""

import streamlit as st
import requests
import json
import os
import time
from datetime import datetime
import base64

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
    color: white;
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
    background: linear-gradient(135deg, #667eea, #764ba2);
    color: white;
    padding: 1.5rem;
    border-radius: 10px;
    margin: 1rem 0;
    border: none;
}
.status-card {
    background: rgba(40, 167, 69, 0.1);
    border: 2px solid #28a745;
    border-radius: 10px;
    padding: 1rem;
    margin: 1rem 0;
}
.generation-card {
    background: rgba(255, 255, 255, 0.05);
    border-radius: 15px;
    padding: 2rem;
    margin: 2rem 0;
}
.stButton > button {
    background: linear-gradient(135deg, #ff6b6b, #ee5a5a);
    color: white;
    border: none;
    border-radius: 25px;
    padding: 0.75rem 2rem;
    font-weight: bold;
    font-size: 1.1rem;
    width: 100%;
}
.stSelectbox > div > div {
    background-color: rgba(255, 255, 255, 0.1);
}
.stTextArea > div > div > textarea {
    background-color: rgba(255, 255, 255, 0.1);
    color: white;
}
</style>
""", unsafe_allow_html=True)

# Environment variables
RUNPOD_API_KEY = os.getenv("RUNPOD_API_KEY", "")
RUNPOD_ENDPOINT = os.getenv("RUNPOD_ENDPOINT", "")

def check_runpod_status():
    """Check if RunPod endpoint is available"""
    if not RUNPOD_ENDPOINT or not RUNPOD_API_KEY:
        return False, "Not configured"
    
    try:
        # Test a simple status check
        response = requests.get(f"{RUNPOD_ENDPOINT.replace('/run', '/status')}", timeout=10)
        return True, "Connected"
    except:
        return False, "Unreachable"

def generate_image_runpod(prompt, style="cinematic", resolution="1024x1024"):
    """Generate image via RunPod Serverless API"""
    if not RUNPOD_ENDPOINT or not RUNPOD_API_KEY:
        return None, "RunPod not configured"
    
    try:
        # Parse resolution
        width, height = resolution.split('x')
        
        # Enhanced prompt with style
        enhanced_prompt = f"{prompt}, {style} style, high quality, detailed, professional photography"
        
        # RunPod serverless payload
        payload = {
            "input": {
                "prompt": enhanced_prompt,
                "width": int(width),
                "height": int(height),
                "num_inference_steps": 25,
                "guidance_scale": 7.5,
                "num_outputs": 1,
                "scheduler": "DPMSolverMultistep",
                "safety_checker": False
            }
        }
        
        # Make request to RunPod
        headers = {
            "Authorization": f"Bearer {RUNPOD_API_KEY}",
            "Content-Type": "application/json"
        }
        
        response = requests.post(
            RUNPOD_ENDPOINT, 
            json=payload,
            headers=headers,
            timeout=120
        )
        
        if response.status_code == 200:
            result = response.json()
            
            # Handle different response formats
            if result.get("status") == "COMPLETED":
                output = result.get("output")
                if isinstance(output, list) and len(output) > 0:
                    return output[0], "Success"
                elif isinstance(output, dict):
                    image_url = output.get("image_url") or output.get("images", [None])[0]
                    return image_url, "Success"
                else:
                    return output, "Success"
            elif result.get("status") == "IN_PROGRESS":
                return None, "Generation in progress..."
            else:
                error_msg = result.get("error", "Unknown error")
                return None, f"Generation failed: {error_msg}"
        else:
            return None, f"API Error: {response.status_code}"
            
    except Exception as e:
        return None, f"Error: {str(e)}"

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
        st.markdown("## 🎬 CinaKinetic Control Panel")
        
        # RunPod Status
        st.markdown("### 🔥 AI Backend Status")
        is_connected, status_msg = check_runpod_status()
        
        if is_connected:
            st.markdown(f'<div class="status-card">✅ <strong>RunPod RTX 6000 Ada</strong><br>{status_msg}</div>', unsafe_allow_html=True)
        else:
            st.error(f"⚠️ RunPod Status: {status_msg}")
            if not RUNPOD_ENDPOINT:
                st.info("💡 Configure RUNPOD_ENDPOINT environment variable")
        
        # Navigation
        st.markdown("### 🎯 Navigation")
        page = st.radio("", [
            "🎨 Generate Scene",
            "🧬 LoRA Training", 
            "🎥 Video Generation",
            "📊 Gallery",
            "💳 Credits & Billing"
        ], label_visibility="collapsed")
        
        # Quick stats
        st.markdown("### 📊 Quick Stats")
        st.metric("Credits Remaining", "25", delta="New user bonus")
        st.metric("Generations Today", "0", delta="0")
        st.metric("Total Generations", "0", delta="0")

    # Main content based on page selection
    if page == "🎨 Generate Scene":
        show_generation_page()
    elif page == "🧬 LoRA Training":
        show_lora_page()
    elif page == "🎥 Video Generation":
        show_video_page()
    elif page == "📊 Gallery":
        show_gallery_page()
    elif page == "💳 Credits & Billing":
        show_billing_page()

def show_generation_page():
    st.markdown("## 🎨 Generate Epic Action Scene")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        with st.container():
            st.markdown('<div class="generation-card">', unsafe_allow_html=True)
            
            # Prompt input
            prompt = st.text_area(
                "🎬 Scene Description", 
                placeholder="A martial artist in a dark alley, dramatic lighting, cinematic composition, intense fight scene",
                height=120,
                help="Describe the action scene you want to create. Be specific about characters, setting, lighting, and mood."
            )
            
            # Settings row
            settings_col1, settings_col2 = st.columns(2)
            
            with settings_col1:
                style = st.selectbox("🎭 Style", [
                    "cinematic", "dark", "gritty", "noir", "action", 
                    "thriller", "dramatic", "moody", "high-contrast"
                ])
            
            with settings_col2:
                resolution = st.selectbox("📐 Resolution", [
                    "768x768 (1 credit)",
                    "1024x1024 (2 credits)", 
                    "1024x1536 (3 credits)",
                    "1536x1024 (3 credits)"
                ])
            
            # Advanced settings (expandable)
            with st.expander("⚙️ Advanced Settings"):
                col_a, col_b = st.columns(2)
                with col_a:
                    steps = st.slider("Inference Steps", 15, 30, 25)
                    guidance = st.slider("Guidance Scale", 5.0, 10.0, 7.5)
                with col_b:
                    seed = st.number_input("Seed (0 = random)", 0, 999999, 0)
                    batch_size = st.selectbox("Batch Size", [1, 2, 4])
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Generate button
            if st.button("🚀 Generate Epic Scene", type="primary"):
                if prompt:
                    generate_and_display(prompt, style, resolution, steps, guidance, seed, batch_size)
                else:
                    st.warning("⚠️ Please enter a scene description")
    
    with col2:
        st.markdown("### 🎯 Quick Action Prompts")
        
        quick_prompts = [
            "Intense warehouse fight scene at night",
            "Car chase through narrow city streets", 
            "Rooftop confrontation in the rain",
            "Underground fight club atmosphere",
            "Tactical team building breach",
            "Motorcycle pursuit at sunset",
            "Martial arts duel in ancient temple",
            "Gun fight in abandoned factory"
        ]
        
        for quick_prompt in quick_prompts:
            if st.button(quick_prompt, key=quick_prompt):
                st.rerun()
        
        # Tips
        st.markdown("### 💡 Pro Tips")
        st.info("""
        **Best Results:**
        - Include lighting details
        - Specify camera angles
        - Add mood descriptors
        - Mention specific fighting styles
        """)

def generate_and_display(prompt, style, resolution, steps, guidance, seed, batch_size):
    """Handle the generation process with proper UI feedback"""
    
    # Extract resolution
    res_clean = resolution.split(' ')[0]  # Remove credit info
    
    # Show generation progress
    progress_container = st.container()
    
    with progress_container:
        st.markdown("### 🔄 Generation in Progress...")
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Step 1: Initializing
        status_text.text("🚀 Initializing RunPod RTX 6000 Ada...")
        progress_bar.progress(10)
        time.sleep(1)
        
        # Step 2: Sending request
        status_text.text("📡 Sending generation request...")
        progress_bar.progress(30)
        
        # Actual generation
        image_url, result_status = generate_image_runpod(prompt, style, res_clean)
        
        if image_url:
            # Step 3: Success
            progress_bar.progress(100)
            status_text.text("✅ Generation complete!")
            
            # Clear progress and show result
            progress_container.empty()
            
            # Display result
            st.markdown("### 🎬 Generated Action Scene")
            
            try:
                st.image(image_url, caption=f"Prompt: {prompt[:100]}...", use_column_width=True)
                
                # Generation details
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Style", style)
                with col2:
                    st.metric("Resolution", res_clean)
                with col3:
                    st.metric("Steps", steps)
                
                # Download button
                if st.button("💾 Download Image"):
                    st.info("💡 Download functionality coming soon!")
                
            except Exception as e:
                st.error(f"❌ Error displaying image: {str(e)}")
                st.code(f"Image URL: {image_url}")
        
        else:
            # Generation failed
            progress_bar.progress(0)
            status_text.text("❌ Generation failed")
            progress_container.empty()
            st.error(f"❌ Generation failed: {result_status}")

def show_lora_page():
    st.markdown("## 🧬 LoRA Character Training")
    
    st.info("💡 Train custom character models for consistent appearance across multiple action scenes")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### 📸 Upload Training Images")
        uploaded_files = st.file_uploader(
            "Choose character images (15-25 recommended)", 
            accept_multiple_files=True,
            type=['png', 'jpg', 'jpeg'],
            help="Upload clear, high-quality images of your character from different angles"
        )
        
        if uploaded_files:
            st.success(f"📁 {len(uploaded_files)} images uploaded")
            
            # Show preview grid
            cols = st.columns(4)
            for i, file in enumerate(uploaded_files[:8]):  # Show first 8
                with cols[i % 4]:
                    st.image(file, caption=f"Image {i+1}", use_column_width=True)
            
            if len(uploaded_files) > 8:
                st.info(f"... and {len(uploaded_files) - 8} more images")
        
        # Training parameters
        st.markdown("### ⚙️ Training Configuration")
        char_name = st.text_input("Character Name", "Action Hero", help="Name for your character LoRA")
        
        col_a, col_b = st.columns(2)
        with col_a:
            training_steps = st.slider("Training Steps", 500, 2000, 1000)
            learning_rate = st.selectbox("Learning Rate", ["1e-4", "5e-5", "1e-5"])
        with col_b:
            resolution_train = st.selectbox("Training Resolution", ["512x512", "768x768", "1024x1024"])
            batch_size_train = st.selectbox("Batch Size", [1, 2, 4])
        
        # Cost calculation
        estimated_time = (len(uploaded_files) * training_steps) // 100 if uploaded_files else 20
        estimated_cost = max(50, len(uploaded_files) * 3) if uploaded_files else 75
        
        col_cost1, col_cost2 = st.columns(2)
        with col_cost1:
            st.metric("Estimated Time", f"{estimated_time} minutes")
        with col_cost2:
            st.metric("Estimated Cost", f"{estimated_cost} credits")
        
        if st.button("🚀 Start LoRA Training", type="primary", disabled=not uploaded_files):
            if uploaded_files:
                st.success("🔄 LoRA training would start on RunPod RTX 6000 Ada...")
                st.info("💡 Training integration coming in next update!")
    
    with col2:
        st.markdown("### 🎭 Existing Character LoRAs")
        
        # Mock existing characters
        characters = [
            {"name": "Action Hero Male", "status": "Ready", "usage": 45},
            {"name": "Femme Fatale", "status": "Training", "usage": 12},
            {"name": "Martial Artist", "status": "Ready", "usage": 78}
        ]
        
        for char in characters:
            with st.expander(f"{char['name']} - {char['status']}"):
                st.write(f"**Usage:** {char['usage']} generations")
                st.write(f"**Status:** {char['status']}")
                if char['status'] == "Ready":
                    if st.button(f"Use {char['name']}", key=char['name']):
                        st.success(f"Selected {char['name']} for generation")

def show_video_page():
    st.markdown("## 🎥 Video Generation")
    
    tab1, tab2, tab3 = st.tabs(["📝 Text-to-Video", "🖼️ Image-to-Video", "🎬 Video-to-Video"])
    
    with tab1:
        st.markdown("### 📝 Generate Action Video from Text")
        video_prompt = st.text_area("Video Description", 
            placeholder="Fighter throwing punches in slow motion, dramatic lighting, cinematic camera work")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            duration = st.slider("Duration (seconds)", 2, 10, 4)
        with col2:
            fps = st.selectbox("Frame Rate", [24, 30, 60])
        with col3:
            video_resolution = st.selectbox("Resolution", ["720p", "1080p", "4K"])
        
        cost_estimate = duration * 10  # Rough estimate
        st.metric("Estimated Cost", f"{cost_estimate} credits")
        
        if st.button("🎬 Generate Video", type="primary"):
            st.info("🎥 Video generation integration coming soon!")
    
    with tab2:
        st.markdown("### 🖼️ Animate Image into Action Video")
        uploaded_image = st.file_uploader("Upload Action Scene Image", type=['png', 'jpg', 'jpeg'])
        
        if uploaded_image:
            st.image(uploaded_image, caption="Source Image", use_column_width=True)
        
        motion_prompt = st.text_input("Motion Description", 
            placeholder="Add dynamic fighting movements, camera zoom, dramatic lighting changes")
        
        if st.button("🎬 Animate Image", type="primary"):
            st.info("🎥 Image-to-video animation coming soon!")
    
    with tab3:
        st.markdown("### 🎬 Transform Existing Video")
        st.info("Transform existing action videos with new styles and effects")
        
        uploaded_video = st.file_uploader("Upload Video", type=['mp4', 'mov', 'avi'])
        
        if uploaded_video:
            st.video(uploaded_video)

def show_gallery_page():
    st.markdown("## 📊 Your Action Scene Gallery")
    
    # Gallery stats
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Generations", "0")
    with col2:
        st.metric("This Week", "0")
    with col3:
        st.metric("Favorites", "0")
    with col4:
        st.metric("Downloads", "0")
    
    # Filter options
    filter_col1, filter_col2, filter_col3 = st.columns(3)
    with filter_col1:
        filter_style = st.selectbox("Filter by Style", ["All", "Cinematic", "Dark", "Gritty", "Action"])
    with filter_col2:
        filter_resolution = st.selectbox("Filter by Resolution", ["All", "768x768", "1024x1024", "1536x1024"])
    with filter_col3:
        sort_by = st.selectbox("Sort by", ["Recent", "Favorites", "Most Downloads"])
    
    # Gallery grid (placeholder)
    st.info("🎨 Your generated action scenes will appear here after you create some!")
    
    # Example gallery layout
    cols = st.columns(3)
    for i in range(6):
        with cols[i % 3]:
            st.image("https://picsum.photos/300/400", caption=f"Action Scene {i+1}")

def show_billing_page():
    st.markdown("## 💳 Credits & Billing")
    
    # Current status
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Current Credits", "25", delta="Bonus credits")
    with col2:
        st.metric("Credits Used", "0", delta="0 this month")
    with col3:
        st.metric("Subscription", "Free Trial", delta="New user")
    
    # Pricing plans
    st.markdown("### 🎯 Subscription Plans")
    
    plan_col1, plan_col2, plan_col3, plan_col4 = st.columns(4)
    
    plans = [
        {"name": "Starter", "price": "$5", "credits": 100, "features": ["Basic Generation", "768x768 Images", "Email Support"]},
        {"name": "Pro", "price": "$15", "credits": 500, "features": ["HD Generation", "Video Creation", "LoRA Training", "Priority Support"]},
        {"name": "Studio", "price": "$40", "credits": 2000, "features": ["Ultra HD", "Batch Processing", "Multi-ControlNet", "Phone Support"]},
        {"name": "Enterprise", "price": "$150", "credits": 10000, "features": ["Unlimited Features", "Custom Models", "Dedicated Support", "SLA"]}
    ]
    
    for i, plan in enumerate(plans):
        with [plan_col1, plan_col2, plan_col3, plan_col4][i]:
            st.markdown(f"""
            **{plan['name']}**
            
            **{plan['price']}/month**
            
            {plan['credits']} credits
            """)
            
            for feature in plan['features']:
                st.write(f"• {feature}")
            
            if st.button(f"Choose {plan['name']}", key=plan['name']):
                st.success(f"Selected {plan['name']} plan!")
    
    # Credit usage breakdown
    st.markdown("### 📊 Credit Usage Guide")
    
    usage_data = {
        "Feature": ["768x768 Image", "1024x1024 Image", "1536x1024 Image", "LoRA Training", "Video (4 sec)", "Video (10 sec)"],
        "Credits": [1, 2, 3, 75, 15, 30],
        "Description": [
            "Standard resolution for quick previews",
            "High quality for most use cases", 
            "Ultra-wide for cinematic scenes",
            "Custom character training",
            "Short action sequence",
            "Extended action sequence"
        ]
    }
    
    st.table(usage_data)

if __name__ == "__main__":
    main()