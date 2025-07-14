import streamlit as st
from typing import Dict, Any

def create_production_interface_lite():
    """Lightweight production interface for Vercel deployment"""
    
    st.markdown("### 🎬 CinaKinetic Studio")
    
    # Sidebar - User info
    with st.sidebar:
        st.header("⚡ Account")
        
        if 'user' not in st.session_state:
            st.session_state.user = {
                'name': 'Demo User',
                'tier': 'pro',
                'credits': 500
            }
        
        user = st.session_state.user
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Credits", user['credits'])
        with col2:
            st.metric("Plan", user['tier'].title())
        
        st.success("🔥 RunPod RTX 6000 Ada Ready")
    
    # Main tabs
    tab1, tab2, tab3 = st.tabs(["🎨 Generate", "🎯 LoRA Studio", "📊 Gallery"])
    
    with tab1:
        create_generation_interface()
    
    with tab2:
        create_lora_interface_lite()
    
    with tab3:
        create_gallery_interface()

def create_generation_interface():
    """Main generation interface"""
    
    st.header("🎨 Action Scene Generation")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Scene parameters
        scene_type = st.selectbox(
            "Scene Type",
            ["Fight Scene", "Car Chase", "Explosion", "Gun Fight", "Martial Arts"]
        )
        
        prompt = st.text_area(
            "Scene Description",
            placeholder="Epic martial arts fight scene, two fighters in dynamic combat...",
            height=100
        )
        
        # Style options
        style = st.selectbox(
            "Visual Style",
            ["Cinematic", "Realistic", "Dramatic", "Film Noir", "High Contrast"]
        )
    
    with col2:
        # Generation settings
        resolution = st.selectbox("Resolution", ["768x768", "1024x1024", "1536x1536"])
        violence_level = st.selectbox("Content Level", ["PG-13", "R-Rated", "Cinematic"])
        
        # LoRA selection
        st.subheader("🎯 LoRA Selection")
        character_lora = st.selectbox("Character", ["None", "ActionHero_John", "Villain_Kane"])
        fighting_style = st.selectbox("Fighting Style", ["None", "bjjstyle", "kungfustyle", "boxingstyle"])
        
        # Cost calculation
        credits_needed = calculate_credits(resolution, character_lora != "None", fighting_style != "None")
        st.metric("Credits Required", credits_needed)
    
    # Enhanced prompt preview
    if prompt:
        enhanced_prompt = build_enhanced_prompt(prompt, scene_type, style, character_lora, fighting_style)
        with st.expander("📝 Enhanced Prompt Preview"):
            st.code(enhanced_prompt)
    
    # Generate button
    if st.button("🚀 Generate Scene", type="primary", use_container_width=True):
        if prompt:
            generate_scene_lite(prompt, scene_type, resolution, character_lora, fighting_style, credits_needed)
        else:
            st.error("Please enter a scene description")

def create_lora_interface_lite():
    """Simplified LoRA interface"""
    
    st.header("🎯 LoRA Training Studio")
    
    # LoRA types
    lora_type = st.selectbox(
        "LoRA Type",
        ["Character Consistency", "Fighting Style", "Action Poses", "Visual Style"]
    )
    
    if lora_type == "Character Consistency":
        st.markdown("""
        ### 👤 Character LoRA Training
        
        Create consistent characters across action scenes:
        - Upload 15-25 images of the same character
        - Different poses, angles, and lighting
        - Training time: ~20 minutes on RTX 6000 Ada
        - Cost: ~75 credits
        """)
        
        character_name = st.text_input("Character Name", placeholder="ActionHero_John")
        trigger_word = st.text_input("Trigger Word", placeholder="johnhero")
        
        uploaded_files = st.file_uploader(
            "Training Images",
            type=['png', 'jpg', 'jpeg'],
            accept_multiple_files=True,
            help="Upload 15-25 high-quality images"
        )
        
        if uploaded_files and len(uploaded_files) >= 15:
            st.success(f"✅ {len(uploaded_files)} images uploaded - ready to train!")
            
            if st.button("🚀 Start Character Training", type="primary"):
                start_lora_training_lite(character_name, "character", len(uploaded_files))
    
    elif lora_type == "Fighting Style":
        st.markdown("""
        ### 🥋 Fighting Style LoRA Training
        
        Train consistent fighting techniques:
        - Upload 20-40 images of specific martial art
        - Various practitioners showing same techniques
        - Training time: ~25 minutes on RTX 6000 Ada  
        - Cost: ~90 credits
        """)
        
        # Pre-built options
        st.subheader("Quick Start Templates")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🥋 Train BJJ/Grappling LoRA"):
                st.info("Upload 25-40 BJJ grappling images to train your custom bjjstyle LoRA")
        
        with col2:
            if st.button("🥊 Train Boxing LoRA"):
                st.info("Upload 20-35 boxing images for boxingstyle LoRA training")

def create_gallery_interface():
    """Generation gallery and history"""
    
    st.header("📊 Generation Gallery")
    
    # Mock gallery data
    generations = [
        {
            "prompt": "Epic fight scene, johnhero vs villain, kungfustyle",
            "timestamp": "2024-01-15 14:30",
            "resolution": "1024x1024",
            "credits": 3,
            "loras": ["johnhero", "kungfustyle"]
        },
        {
            "prompt": "Car chase through city streets, cinematic angle",
            "timestamp": "2024-01-15 14:15",
            "resolution": "768x768", 
            "credits": 2,
            "loras": []
        },
        {
            "prompt": "Explosion sequence, dramatic lighting",
            "timestamp": "2024-01-15 14:00",
            "resolution": "1024x1024",
            "credits": 2,
            "loras": []
        }
    ]
    
    # Stats
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Generated", len(generations))
    with col2:
        st.metric("Credits Used", sum(g["credits"] for g in generations))
    with col3:
        st.metric("This Month", len(generations))
    with col4:
        st.metric("Success Rate", "96%")
    
    # Gallery grid
    st.subheader("Recent Generations")
    
    for i, gen in enumerate(generations):
        with st.expander(f"🎬 Generation {i+1} - {gen['timestamp']}"):
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.image(
                    f"https://via.placeholder.com/400x400/333/FFF?text=Generated+Scene+{i+1}",
                    caption=gen['prompt'][:50] + "..."
                )
            
            with col2:
                st.write(f"**Prompt:** {gen['prompt']}")
                st.write(f"**Resolution:** {gen['resolution']}")
                st.write(f"**Credits:** {gen['credits']}")
                if gen['loras']:
                    st.write(f"**LoRAs:** {', '.join(gen['loras'])}")
                
                if st.button(f"🔄 Regenerate", key=f"regen_{i}"):
                    st.info("Regenerating with same settings...")

def calculate_credits(resolution: str, has_character: bool, has_fighting_style: bool) -> int:
    """Calculate credits needed for generation"""
    
    base_credits = {
        "768x768": 1,
        "1024x1024": 2,
        "1536x1536": 4
    }.get(resolution, 2)
    
    # LoRA usage adds credits
    if has_character:
        base_credits += 1
    if has_fighting_style:
        base_credits += 1
    
    return base_credits

def build_enhanced_prompt(prompt: str, scene_type: str, style: str, character_lora: str, fighting_style: str) -> str:
    """Build enhanced prompt with LoRA triggers"""
    
    enhanced = f"{prompt}, {scene_type.lower()}, {style.lower()} style"
    
    # Add LoRA triggers
    if character_lora != "None":
        trigger = character_lora.lower().replace("_", "").replace("actionhero", "").replace("villain", "")
        enhanced += f", {trigger}"
    
    if fighting_style != "None":
        enhanced += f", {fighting_style}"
    
    # Add quality enhancers
    enhanced += ", cinematic composition, professional choreography, high detail, 8k quality"
    
    return enhanced

def generate_scene_lite(prompt: str, scene_type: str, resolution: str, character_lora: str, fighting_style: str, credits: int):
    """Simulate scene generation"""
    
    enhanced_prompt = build_enhanced_prompt(prompt, scene_type, "cinematic", character_lora, fighting_style)
    
    with st.spinner(f"🔥 Generating on RTX 6000 Ada... ({credits} credits)"):
        # Simulate generation progress
        progress_bar = st.progress(0)
        import time
        
        for i in range(100):
            time.sleep(0.1)  # Fast simulation
            progress_bar.progress((i + 1) / 100)
    
    st.success("✅ Scene generated successfully!")
    
    # Show result
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.image(
            f"https://via.placeholder.com/512x512/333/FFF?text={scene_type.replace(' ', '+')}+Scene",
            caption="Generated Action Scene"
        )
    
    with col2:
        st.write("**Generation Details:**")
        st.write(f"Scene Type: {scene_type}")
        st.write(f"Resolution: {resolution}")
        st.write(f"Credits Used: {credits}")
        if character_lora != "None":
            st.write(f"Character: {character_lora}")
        if fighting_style != "None":
            st.write(f"Fighting Style: {fighting_style}")
        
        st.write("**Generation Time:** 12.3 seconds")
        
        if st.button("💾 Save to Gallery"):
            st.success("Saved to your gallery!")
        
        if st.button("🔄 Generate Variation"):
            st.info("Generating variation with same settings...")

def start_lora_training_lite(name: str, lora_type: str, num_images: int):
    """Simulate LoRA training"""
    
    credits_needed = 75 if lora_type == "character" else 90
    
    with st.spinner(f"🚀 Training {name} LoRA on RTX 6000 Ada... ({credits_needed} credits)"):
        import time
        progress_bar = st.progress(0)
        
        phases = [
            "Preprocessing images...",
            "Setting up training environment...",
            "Training LoRA model...", 
            "Validation and testing...",
            "Finalizing model..."
        ]
        
        for i, phase in enumerate(phases):
            st.text(phase)
            for j in range(20):
                progress_bar.progress(((i * 20) + j + 1) / 100)
                time.sleep(0.1)
    
    st.success(f"🎉 LoRA '{name}' training completed!")
    st.balloons()
    
    trigger_word = name.lower().replace(" ", "").replace("_", "")
    st.info(f"💡 Use trigger word `{trigger_word}` in your prompts to activate this LoRA!")