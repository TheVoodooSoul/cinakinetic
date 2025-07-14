import streamlit as st
import asyncio
import json
from typing import Dict, Any, Optional
import uuid
import time
from datetime import datetime

from ..workflows.workflow_templates import (
    ActionWorkflowTemplate, 
    WorkflowType, 
    ACTION_SCENE_TEMPLATES
)
from .pricing_interface import (
    PricingManager, 
    check_generation_permissions,
    create_pricing_interface
)
from ..ai_pipeline.runpod_client import RunPodClient

def create_production_interface():
    """Main production interface for action scene generation"""
    
    st.title("🎬 Cinema Action Scene Generator - Production")
    
    # Initialize session state
    if 'workflow_template' not in st.session_state:
        st.session_state.workflow_template = ActionWorkflowTemplate(rtx6000_optimized=True)
    if 'pricing_manager' not in st.session_state:
        st.session_state.pricing_manager = PricingManager()
    if 'user_credits' not in st.session_state:
        st.session_state.user_credits = 100  # Default starter credits
    if 'user_tier' not in st.session_state:
        st.session_state.user_tier = 'starter'
    
    # Sidebar - Quick status and credits
    with st.sidebar:
        st.header("⚡ Quick Status")
        
        # Credits and tier
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Credits", st.session_state.user_credits)
        with col2:
            st.metric("Plan", st.session_state.user_tier.title())
        
        # RunPod status
        runpod_url = st.session_state.get('runpod_url')
        if runpod_url:
            st.success("🚀 RTX 6000 Ada Connected")
            
            if st.button("📊 Pod Status"):
                show_pod_status(runpod_url)
        else:
            st.warning("⚠️ RunPod not connected")
            if st.button("🔗 Connect Pod"):
                show_pod_connection()
        
        # Quick templates
        st.subheader("🎯 Quick Templates")
        for template_name in ["fight_sequence_hq", "sketch_to_fight", "car_chase_sequence"]:
            if st.button(template_name.replace("_", " ").title(), key=f"quick_{template_name}"):
                st.session_state['selected_template'] = template_name
                st.rerun()
    
    # Main tabs
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "🎨 Studio", 
        "⚡ Templates", 
        "🎬 Video Suite",
        "🎯 LoRA Studio",
        "💳 Billing",
        "📊 Analytics"
    ])
    
    with tab1:
        create_studio_interface()
    
    with tab2:
        create_template_interface()
    
    with tab3:
        create_video_suite_interface()
    
    with tab4:
        # LoRA Studio
        from ..lora.lora_trainer import LoRATrainer
        lora_trainer = LoRATrainer()
        lora_trainer.create_lora_interface()
    
    with tab5:
        create_pricing_interface()
    
    with tab6:
        create_analytics_interface()

def create_studio_interface():
    """Advanced studio interface for custom workflows"""
    
    st.header("🎨 Production Studio")
    st.write("Create custom action scenes with full control")
    
    # Workflow type selection
    col1, col2 = st.columns([2, 1])
    
    with col1:
        workflow_type = st.selectbox(
            "Generation Type",
            [
                ("Image Generation", WorkflowType.IMAGE_GENERATION),
                ("Sketch to Image", WorkflowType.SKETCH_TO_IMAGE),
                ("Text to Video", WorkflowType.TEXT_TO_VIDEO),
                ("Image to Video", WorkflowType.IMAGE_TO_VIDEO),
                ("Video to Video", WorkflowType.VIDEO_TO_VIDEO),
                ("Batch Generation", WorkflowType.BATCH_GENERATION),
                ("Multi-ControlNet", WorkflowType.CONTROLNET_MULTI)
            ],
            format_func=lambda x: x[0]
        )[1]
    
    with col2:
        # Show credit cost
        resolution = st.selectbox("Resolution", ["768x768", "1024x1024", "1536x1536", "2048x1536"])
        batch_size = st.number_input("Batch Size", 1, 8, 1)
        
        pricing_manager = st.session_state.pricing_manager
        credits_needed = pricing_manager.calculate_credits_needed(workflow_type, resolution, batch_size)
        
        st.metric("Credits Required", credits_needed)
        
        # Permission check
        permissions = check_generation_permissions(workflow_type, resolution, batch_size)
        
        if permissions["allowed"]:
            st.success("✅ Ready to generate")
        else:
            if not permissions["credits_ok"]:
                st.error("❌ Insufficient credits")
            if not permissions["resolution_ok"]:
                st.error("❌ Resolution exceeds plan limit")
            if not permissions["video_ok"]:
                st.error("❌ Video generation requires Pro+ plan")
            if not permissions["batch_ok"]:
                st.error("❌ Batch size exceeds plan limit")
    
    # Workflow-specific parameters
    params = {}
    
    if workflow_type == WorkflowType.IMAGE_GENERATION:
        params = create_image_params_ui(resolution)
    elif workflow_type == WorkflowType.SKETCH_TO_IMAGE:
        params = create_sketch_params_ui(resolution)
    elif workflow_type in [WorkflowType.TEXT_TO_VIDEO, WorkflowType.IMAGE_TO_VIDEO, WorkflowType.VIDEO_TO_VIDEO]:
        params = create_video_params_ui(workflow_type, resolution)
    elif workflow_type == WorkflowType.BATCH_GENERATION:
        params = create_batch_params_ui(resolution, batch_size)
    elif workflow_type == WorkflowType.CONTROLNET_MULTI:
        params = create_multi_controlnet_ui(resolution)
    
    # Generation button
    if st.button("🚀 Generate", type="primary", disabled=not permissions["allowed"]):
        generate_with_workflow(workflow_type, params, permissions["credits_needed"])

def create_image_params_ui(resolution: str) -> Dict[str, Any]:
    """UI for image generation parameters"""
    
    col1, col2 = st.columns(2)
    
    with col1:
        prompt = st.text_area(
            "Action Scene Prompt",
            placeholder="Epic martial arts fight scene, two fighters in dynamic combat poses, cinematic lighting, professional choreography",
            height=100
        )
        
        scene_type = st.selectbox(
            "Scene Type",
            ["Fight Scene", "Car Chase", "Explosion", "Aerial Combat", "Gun Fight"]
        )
    
    with col2:
        negative_prompt = st.text_area(
            "Negative Prompt",
            value="low quality, blurry, amateur, static poses, bad anatomy",
            height=100
        )
        
        style = st.selectbox(
            "Style",
            ["Cinematic", "Realistic", "Dramatic", "High Contrast", "Film Noir"]
        )
    
    # LoRA selection
    with st.expander("🎯 LoRA Selection", expanded=True):
        from ..lora.lora_trainer import integrate_lora_with_generation
        lora_selection = integrate_lora_with_generation()
    
    # Advanced settings
    with st.expander("Advanced Settings"):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            seed = st.number_input("Seed", value=-1, help="-1 for random")
            wan_model = st.selectbox("WAN Model", ["Auto", "wan.safetensors", "wan2_114b.safetensors"])
        
        with col2:
            steps = st.slider("Steps", 15, 40, 25)
            cfg_scale = st.slider("CFG Scale", 4.0, 12.0, 6.5, 0.5)
        
        with col3:
            sampler = st.selectbox("Sampler", ["dpmpp_2m_karras", "euler_a", "dpm_fast"])
            scheduler = st.selectbox("Scheduler", ["karras", "normal", "exponential"])
    
    width, height = map(int, resolution.split('x'))
    
    # Build LoRA list
    loras = []
    if 'lora_selection' in locals() and lora_selection:
        if lora_selection.get('character_lora'):
            char = st.session_state.characters[lora_selection['character_lora']]
            if char.get('lora_name'):
                loras.append({"name": char['lora_name'], "strength": 0.8})
        
        if lora_selection.get('fighting_style'):
            loras.append({"name": f"{lora_selection['fighting_style']}.safetensors", "strength": 0.7})
        
        for additional_lora in lora_selection.get('additional_loras', []):
            loras.append({"name": f"{additional_lora}.safetensors", "strength": 0.6})
    
    # Build enhanced prompt with LoRA triggers
    enhanced_prompt = f"{prompt}, {scene_type.lower()}, {style.lower()} style"
    
    if loras:
        triggers = []
        if lora_selection.get('character_lora'):
            char = st.session_state.characters[lora_selection['character_lora']]
            triggers.append(char.get('trigger_word', ''))
        if lora_selection.get('fighting_style'):
            triggers.append(lora_selection['fighting_style'])
        for lora in lora_selection.get('additional_loras', []):
            triggers.append(lora)
        
        if triggers:
            enhanced_prompt += f", {', '.join(filter(None, triggers))}"
    
    return {
        "prompt": enhanced_prompt,
        "negative_prompt": negative_prompt,
        "width": width,
        "height": height,
        "seed": seed if seed != -1 else None,
        "model_name": wan_model if wan_model != "Auto" else "wan.safetensors",
        "filename_prefix": f"{scene_type.lower().replace(' ', '_')}_{int(time.time())}",
        "loras": loras
    }

def create_sketch_params_ui(resolution: str) -> Dict[str, Any]:
    """UI for sketch-to-image parameters"""
    
    from .sketch_interface import SketchInterface
    
    st.subheader("Sketch Input")
    
    sketch_ui = SketchInterface()
    sketch_result = sketch_ui.create_drawing_canvas("studio")
    
    if sketch_result:
        st.success("✅ Sketch captured!")
        
        col1, col2 = st.columns(2)
        
        with col1:
            prompt = st.text_area(
                "Enhancement Prompt",
                placeholder="Professional fight choreography, cinematic lighting, high detail",
                height=80
            )
            
            controlnet_strength = st.slider("ControlNet Strength", 0.1, 1.0, 0.8, 0.1)
        
        with col2:
            controlnet_type = st.selectbox(
                "ControlNet Type",
                ["openpose", "canny", "depth", "lineart"]
            )
            
            enhancement_level = st.selectbox(
                "Enhancement Level",
                ["Subtle", "Moderate", "Strong", "Dramatic"]
            )
        
        width, height = sketch_result["canvas_size"]
        
        return {
            "prompt": prompt,
            "control_image": sketch_result["processed_image"],
            "controlnet_type": controlnet_type,
            "controlnet_strength": controlnet_strength,
            "width": width,
            "height": height,
            "model_name": "wan.safetensors"
        }
    
    else:
        st.info("👆 Draw your action scene above to continue")
        return {}

def create_video_params_ui(workflow_type: WorkflowType, resolution: str) -> Dict[str, Any]:
    """UI for video generation parameters"""
    
    st.subheader("🎬 Video Generation")
    
    if workflow_type == WorkflowType.TEXT_TO_VIDEO:
        col1, col2 = st.columns(2)
        
        with col1:
            prompt = st.text_area(
                "Video Prompt",
                placeholder="High-speed car chase through city streets, vehicles racing, cinematic action sequence",
                height=100
            )
            
            motion_strength = st.slider("Motion Intensity", 0.1, 1.0, 0.8, 0.1)
        
        with col2:
            video_length = st.selectbox("Video Length", ["1 second (24 frames)", "2 seconds (48 frames)", "3 seconds (72 frames)"])
            frame_count = int(video_length.split("(")[1].split(" ")[0])
            
            fps = st.selectbox("Frame Rate", [24, 30, 60])
        
        width, height = map(int, resolution.split('x'))
        
        return {
            "prompt": prompt,
            "width": width,
            "height": height,
            "frame_count": frame_count,
            "motion_strength": motion_strength,
            "fps": fps,
            "model_name": "wan.safetensors"
        }
    
    elif workflow_type == WorkflowType.IMAGE_TO_VIDEO:
        uploaded_file = st.file_uploader(
            "Upload Starting Image",
            type=['png', 'jpg', 'jpeg'],
            help="Upload the image you want to animate"
        )
        
        if uploaded_file:
            st.image(uploaded_file, caption="Starting Image", width=300)
            
            col1, col2 = st.columns(2)
            
            with col1:
                motion_prompt = st.text_area(
                    "Motion Description",
                    placeholder="Punch sequence, fighting motion, dynamic movement",
                    height=80
                )
                
                motion_strength = st.slider("Motion Strength", 0.1, 1.0, 0.8, 0.1)
            
            with col2:
                motion_type = st.selectbox(
                    "Motion Type",
                    ["Fight Sequence", "Action Movement", "Camera Pan", "Zoom Effect"]
                )
                
                frame_count = st.selectbox("Frames", [12, 24, 36, 48])
            
            return {
                "input_image": uploaded_file,
                "motion_prompt": motion_prompt,
                "motion_strength": motion_strength,
                "frame_count": frame_count,
                "model_name": "wan.safetensors"
            }
        
        else:
            st.info("📤 Upload an image to animate")
            return {}
    
    elif workflow_type == WorkflowType.VIDEO_TO_VIDEO:
        uploaded_video = st.file_uploader(
            "Upload Source Video",
            type=['mp4', 'mov', 'avi'],
            help="Upload the video you want to transform"
        )
        
        if uploaded_video:
            st.video(uploaded_video)
            
            col1, col2 = st.columns(2)
            
            with col1:
                style_prompt = st.text_area(
                    "Style Transformation",
                    placeholder="Convert to cinematic action style, enhance lighting, add dramatic effects",
                    height=100
                )
            
            with col2:
                strength = st.slider("Transformation Strength", 0.1, 1.0, 0.6, 0.1)
                preserve_motion = st.checkbox("Preserve Original Motion", value=True)
            
            return {
                "input_video": uploaded_video,
                "style_prompt": style_prompt,
                "strength": strength,
                "preserve_motion": preserve_motion,
                "model_name": "wan.safetensors"
            }
        
        else:
            st.info("📤 Upload a video to transform")
            return {}

def create_batch_params_ui(resolution: str, batch_size: int) -> Dict[str, Any]:
    """UI for batch generation parameters"""
    
    st.subheader(f"🔄 Batch Generation ({batch_size} images)")
    
    # Batch prompts
    prompts = []
    for i in range(batch_size):
        prompt = st.text_area(
            f"Prompt {i+1}",
            placeholder=f"Action scene variation {i+1}",
            height=60,
            key=f"batch_prompt_{i}"
        )
        prompts.append(prompt)
    
    # Common settings
    col1, col2 = st.columns(2)
    
    with col1:
        common_negative = st.text_area(
            "Common Negative Prompt",
            value="low quality, blurry, amateur",
            height=60
        )
    
    with col2:
        variation_strength = st.slider("Variation Strength", 0.1, 1.0, 0.8, 0.1)
        shared_composition = st.checkbox("Shared Composition", value=False)
    
    width, height = map(int, resolution.split('x'))
    
    return {
        "batch_prompts": prompts,
        "negative_prompt": common_negative,
        "width": width,
        "height": height,
        "batch_size": batch_size,
        "model_name": "wan.safetensors"
    }

def create_multi_controlnet_ui(resolution: str) -> Dict[str, Any]:
    """UI for multi-ControlNet generation"""
    
    st.subheader("🎯 Multi-ControlNet Generation")
    st.write("Use multiple control inputs for precise scene composition")
    
    controlnets = []
    
    num_controlnets = st.selectbox("Number of ControlNets", [1, 2, 3, 4])
    
    for i in range(num_controlnets):
        with st.expander(f"ControlNet {i+1}"):
            col1, col2 = st.columns(2)
            
            with col1:
                cn_type = st.selectbox(
                    "Type",
                    ["openpose", "canny", "depth", "lineart"],
                    key=f"cn_type_{i}"
                )
                
                strength = st.slider(
                    "Strength",
                    0.1, 1.0, 0.8, 0.1,
                    key=f"cn_strength_{i}"
                )
            
            with col2:
                uploaded_file = st.file_uploader(
                    "Control Image",
                    type=['png', 'jpg', 'jpeg'],
                    key=f"cn_image_{i}"
                )
            
            if uploaded_file:
                st.image(uploaded_file, caption=f"ControlNet {i+1} Input", width=200)
                
                controlnets.append({
                    "type": cn_type,
                    "strength": strength,
                    "image": uploaded_file
                })
    
    if controlnets:
        main_prompt = st.text_area(
            "Main Prompt",
            placeholder="Epic action scene guided by multiple control inputs",
            height=100
        )
        
        width, height = map(int, resolution.split('x'))
        
        return {
            "prompt": main_prompt,
            "controlnets": controlnets,
            "width": width,
            "height": height,
            "model_name": "wan.safetensors"
        }
    
    else:
        st.info("👆 Upload control images to continue")
        return {}

def create_template_interface():
    """Interface for pre-built templates"""
    
    st.header("⚡ Template Library")
    st.write("Pre-configured workflows for common action scenes")
    
    # Template categories
    categories = {
        "Fight Scenes": ["fight_sequence_hq", "sketch_to_fight", "fight_motion_video"],
        "Vehicle Action": ["car_chase_sequence"],
        "Explosions": ["explosion_batch"],
        "Custom": []
    }
    
    selected_category = st.selectbox("Category", list(categories.keys()))
    
    # Show templates in category
    templates_in_category = categories[selected_category]
    
    if templates_in_category:
        cols = st.columns(min(len(templates_in_category), 3))
        
        for i, template_name in enumerate(templates_in_category):
            template = ACTION_SCENE_TEMPLATES[template_name]
            
            with cols[i % 3]:
                st.subheader(template_name.replace("_", " ").title())
                
                # Show template preview
                workflow_type = template["type"]
                params = template["params"]
                
                st.write(f"**Type:** {workflow_type.value.replace('_', ' ').title()}")
                
                if "prompt" in params:
                    st.write(f"**Prompt:** {params['prompt'][:50]}...")
                
                if "width" in params and "height" in params:
                    st.write(f"**Resolution:** {params['width']}x{params['height']}")
                
                # Check permissions
                resolution = f"{params.get('width', 768)}x{params.get('height', 768)}"
                batch_size = params.get('batch_size', 1)
                
                permissions = check_generation_permissions(workflow_type, resolution, batch_size)
                credits_needed = permissions["credits_needed"]
                
                st.write(f"**Credits:** {credits_needed}")
                
                if permissions["allowed"]:
                    if st.button(f"Generate", key=f"template_{template_name}"):
                        generate_from_template(template_name, template)
                else:
                    st.button("🔒 Upgrade Required", disabled=True, key=f"locked_{template_name}")
    
    else:
        st.info("No templates in this category yet. Check back soon!")

def create_video_suite_interface():
    """Advanced video generation interface"""
    
    st.header("🎬 Video Production Suite")
    st.write("Professional video generation with t2v, i2v, and v2v")
    
    # Check video permissions
    user_tier = st.session_state.get('user_tier', 'starter')
    pricing_manager = st.session_state.pricing_manager
    tier_info = pricing_manager.pricing_tiers[user_tier]
    
    if not tier_info.video_enabled:
        st.warning("🔒 Video generation requires Pro plan or higher")
        
        if st.button("🚀 Upgrade to Pro"):
            st.session_state['user_tier'] = 'pro'
            st.session_state['user_credits'] += 500
            st.success("✅ Upgraded to Pro! Video features unlocked.")
            st.rerun()
        
        return
    
    # Video workflow selection
    video_workflow = st.selectbox(
        "Video Workflow",
        [
            "Text to Video (t2v)",
            "Image to Video (i2v)", 
            "Video to Video (v2v)",
            "Fight Sequence Generator"
        ]
    )
    
    if video_workflow == "Text to Video (t2v)":
        create_t2v_interface()
    elif video_workflow == "Image to Video (i2v)":
        create_i2v_interface()
    elif video_workflow == "Video to Video (v2v)":
        create_v2v_interface()
    elif video_workflow == "Fight Sequence Generator":
        create_fight_sequence_interface()

def create_t2v_interface():
    """Text-to-Video interface"""
    
    st.subheader("📝 Text to Video Generation")
    
    col1, col2 = st.columns(2)
    
    with col1:
        prompt = st.text_area(
            "Video Prompt",
            placeholder="Epic fight scene: two martial artists exchanging powerful punches and kicks in dynamic sequence",
            height=120
        )
        
        duration = st.selectbox("Duration", ["1 second", "2 seconds", "3 seconds"])
    
    with col2:
        style = st.selectbox(
            "Video Style",
            ["Cinematic", "Slow Motion", "Fast Action", "Dramatic"]
        )
        
        quality = st.selectbox("Quality", ["Standard (768p)", "High (1080p)"])
    
    if st.button("🎬 Generate Video", type="primary"):
        st.info("🎬 Generating video... This may take 60-90 seconds on RTX 6000")
        # Would call video generation

def create_i2v_interface():
    """Image-to-Video interface"""
    
    st.subheader("🖼️ Image to Video Animation")
    
    uploaded_image = st.file_uploader(
        "Upload Starting Image",
        type=['png', 'jpg', 'jpeg']
    )
    
    if uploaded_image:
        col1, col2 = st.columns(2)
        
        with col1:
            st.image(uploaded_image, caption="Starting Frame", width=300)
        
        with col2:
            motion_type = st.selectbox(
                "Motion Type",
                ["Fight Motion", "Camera Movement", "Object Animation", "Background Action"]
            )
            
            motion_prompt = st.text_area(
                "Motion Description",
                placeholder="Character throws a powerful punch, dynamic fighting motion",
                height=80
            )
            
            intensity = st.slider("Motion Intensity", 0.1, 1.0, 0.8)
        
        if st.button("🎬 Animate Image"):
            st.info("🎬 Creating animation... RTX 6000 processing...")

def create_v2v_interface():
    """Video-to-Video interface"""
    
    st.subheader("🎞️ Video to Video Transformation")
    
    uploaded_video = st.file_uploader(
        "Upload Source Video",
        type=['mp4', 'mov', 'avi']
    )
    
    if uploaded_video:
        st.video(uploaded_video)
        
        transformation = st.selectbox(
            "Transformation Type",
            ["Style Transfer", "Quality Enhancement", "Effect Addition", "Cinematography"]
        )
        
        style_prompt = st.text_area(
            "Transformation Prompt",
            placeholder="Transform to cinematic action movie style with dramatic lighting and effects",
            height=80
        )
        
        strength = st.slider("Transformation Strength", 0.1, 1.0, 0.6)
        
        if st.button("🎬 Transform Video"):
            st.info("🎬 Transforming video... Processing on RTX 6000...")

def create_fight_sequence_interface():
    """Specialized fight sequence generator"""
    
    st.subheader("🥊 Fight Sequence Generator")
    st.write("Generate complete fight choreography sequences")
    
    col1, col2 = st.columns(2)
    
    with col1:
        fight_style = st.selectbox(
            "Fighting Style",
            ["Boxing", "Martial Arts", "MMA", "Street Fight", "Sword Combat"]
        )
        
        sequence_length = st.selectbox(
            "Sequence Length",
            ["Short (3 seconds)", "Medium (5 seconds)", "Long (8 seconds)"]
        )
    
    with col2:
        fighters = st.number_input("Number of Fighters", 2, 4, 2)
        
        environment = st.selectbox(
            "Environment",
            ["Boxing Ring", "Rooftop", "Warehouse", "Street", "Dojo"]
        )
    
    choreography = st.text_area(
        "Fight Choreography",
        placeholder="Fighter 1 throws jab, Fighter 2 blocks and counters with hook, Fighter 1 ducks and uppercuts...",
        height=100
    )
    
    if st.button("🥊 Generate Fight Sequence", type="primary"):
        st.info(f"🥊 Generating {fight_style.lower()} sequence... This is a complex generation that may take 2-3 minutes")

def create_analytics_interface():
    """Analytics and usage dashboard"""
    
    st.header("📊 Analytics Dashboard")
    
    # Mock analytics data
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Generations", 47, "+12 this week")
    
    with col2:
        st.metric("Credits Used", 234, "+56 this week")
    
    with col3:
        st.metric("Success Rate", "94%", "+2%")
    
    with col4:
        st.metric("Avg Quality", "8.7/10", "+0.3")
    
    # Usage charts would go here
    st.info("📊 Detailed analytics coming soon!")

def generate_with_workflow(workflow_type: WorkflowType, params: Dict[str, Any], credits_needed: int):
    """Generate using workflow template"""
    
    if not params:
        st.error("❌ Please complete all required parameters")
        return
    
    # Deduct credits
    pricing_manager = st.session_state.pricing_manager
    
    with st.spinner(f"🚀 Generating on RTX 6000 Ada... ({credits_needed} credits)"):
        # Simulate generation time
        progress_bar = st.progress(0)
        for i in range(100):
            time.sleep(0.05)  # RTX 6000 is fast!
            progress_bar.progress((i + 1) / 100)
        
        # Deduct credits
        success = True  # Would be actual generation result
        pricing_manager.deduct_credits("user123", workflow_type, f"{params.get('width', 768)}x{params.get('height', 768)}", params.get('batch_size', 1), success)
        
        if success:
            st.success("✅ Generation completed!")
            
            # Show result placeholder
            if workflow_type in [WorkflowType.TEXT_TO_VIDEO, WorkflowType.IMAGE_TO_VIDEO, WorkflowType.VIDEO_TO_VIDEO]:
                st.video("https://sample-videos.com/zip/10/mp4/SampleVideo_1280x720_1mb.mp4")
                st.caption("Generated Action Sequence")
            else:
                st.image("https://via.placeholder.com/1024x1024/333/FFF?text=Generated+Action+Scene", caption="Generated Image")
            
            # Generation info
            col1, col2, col3 = st.columns(3)
            with col1:
                st.write(f"**Type:** {workflow_type.value.replace('_', ' ').title()}")
            with col2:
                st.write(f"**Credits Used:** {credits_needed}")
            with col3:
                st.write("**Generation Time:** 12.3s")
            
            # Download button
            st.download_button(
                "💾 Download Result",
                data=b"placeholder_image_data",
                file_name=f"action_scene_{int(time.time())}.png",
                mime="image/png"
            )
        
        else:
            st.error("❌ Generation failed - no credits charged")

def generate_from_template(template_name: str, template: Dict[str, Any]):
    """Generate from pre-built template"""
    
    workflow_type = template["type"]
    params = template["params"]
    
    # Calculate credits
    pricing_manager = st.session_state.pricing_manager
    resolution = f"{params.get('width', 768)}x{params.get('height', 768)}"
    batch_size = params.get('batch_size', 1)
    credits_needed = pricing_manager.calculate_credits_needed(workflow_type, resolution, batch_size)
    
    st.info(f"🎬 Generating {template_name.replace('_', ' ').title()}...")
    
    generate_with_workflow(workflow_type, params, credits_needed)

def show_pod_status(pod_url: str):
    """Show RunPod status"""
    
    try:
        import requests
        response = requests.get(f"{pod_url}/system_stats", timeout=5)
        
        if response.status_code == 200:
            stats = response.json()
            
            st.subheader("🚀 RTX 6000 Ada Status")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**GPU Status:** Online ✅")
                st.write(f"**VRAM:** {stats.get('devices', [{}])[0].get('vram_total', 'Unknown')} MB")
            
            with col2:
                st.write("**Queue:** Empty ⚡")
                st.write("**Performance:** Optimal 🔥")
        
        else:
            st.error("❌ Pod connection error")
    
    except Exception:
        st.error("❌ Cannot reach pod")

def show_pod_connection():
    """Show pod connection dialog"""
    
    pod_url = st.text_input(
        "RunPod ComfyUI URL",
        placeholder="https://[pod-id]-8188.proxy.runpod.net"
    )
    
    if pod_url and st.button("Connect"):
        st.session_state['runpod_url'] = pod_url
        st.success("✅ Connected to RTX 6000 Ada pod!")
        st.rerun()