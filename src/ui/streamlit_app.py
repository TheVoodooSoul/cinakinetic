import streamlit as st
import requests
import json
import uuid
from typing import Dict, List
import time
from datetime import datetime

# Page config
st.set_page_config(
    page_title="Cinema Action Scene Generator",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Constants
API_BASE_URL = "http://localhost:8000"

# Custom CSS for dark theme and action aesthetics
st.markdown("""
<style>
    .stApp {
        background-color: #0E0E0E;
    }
    
    .action-header {
        background: linear-gradient(45deg, #FF4B4B, #FF8E53);
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        margin-bottom: 30px;
    }
    
    .action-header h1 {
        color: white;
        margin: 0;
        font-size: 2.5em;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
    }
    
    .scene-node {
        border: 2px solid #FF4B4B;
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
        background-color: #1E1E1E;
    }
    
    .scene-preview {
        border-radius: 8px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.3);
    }
    
    .stSelectbox > div > div {
        background-color: #2D2D2D;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'storyboard' not in st.session_state:
    st.session_state.storyboard = None
if 'current_node' not in st.session_state:
    st.session_state.current_node = None
if 'scene_templates' not in st.session_state:
    st.session_state.scene_templates = {}

def load_scene_templates():
    """Load scene templates from API"""
    try:
        response = requests.get(f"{API_BASE_URL}/scene-templates/")
        if response.status_code == 200:
            st.session_state.scene_templates = response.json()
    except requests.RequestException:
        st.error("Failed to load scene templates. Make sure the API server is running.")

def create_new_storyboard(title: str, description: str = ""):
    """Create a new storyboard"""
    try:
        response = requests.post(
            f"{API_BASE_URL}/storyboards/",
            params={"title": title, "description": description}
        )
        if response.status_code == 200:
            st.session_state.storyboard = response.json()
            st.success(f"Created storyboard: {title}")
        else:
            st.error("Failed to create storyboard")
    except requests.RequestException:
        st.error("Failed to connect to API server")

def load_storyboards():
    """Load all storyboards"""
    try:
        response = requests.get(f"{API_BASE_URL}/storyboards/")
        if response.status_code == 200:
            return response.json()
        return []
    except requests.RequestException:
        st.error("Failed to load storyboards")
        return []

def generate_scene(node_data: Dict):
    """Generate a scene using the API"""
    try:
        with st.spinner("Generating action scene..."):
            response = requests.post(
                f"{API_BASE_URL}/generate-scene/",
                json=node_data
            )
            
            if response.status_code == 200:
                result = response.json()
                if result["success"]:
                    return result
                else:
                    st.error(f"Generation failed: {result.get('error', 'Unknown error')}")
            else:
                st.error("Failed to generate scene")
                
    except requests.RequestException:
        st.error("Failed to connect to generation service")
    
    return None

def main():
    # Header
    st.markdown("""
    <div class="action-header">
        <h1>🎬 Cinema Action Scene Generator</h1>
        <p style="color: white; margin: 0;">Create cinematic action sequences with AI</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Load templates
    if not st.session_state.scene_templates:
        load_scene_templates()
    
    # Sidebar for storyboard management
    with st.sidebar:
        # Navigation
        page = st.selectbox(
            "Navigate",
            ["🎬 Storyboard Editor", "🚀 Production Studio", "🎯 LoRA Studio", "🛠️ Setup & Config"],
            index=0
        )
        
        if page == "🛠️ Setup & Config":
            from .setup_page import create_setup_page
            create_setup_page()
            return
        elif page == "🚀 Production Studio":
            from .production_interface import create_production_interface
            create_production_interface()
            return
        elif page == "🎯 LoRA Studio":
            from ..lora.lora_trainer import LoRATrainer
            lora_trainer = LoRATrainer()
            lora_trainer.create_lora_interface()
            return
        
        st.header("🎯 Storyboard Manager")
        
        # Create new storyboard
        with st.expander("Create New Storyboard", expanded=True):
            new_title = st.text_input("Storyboard Title", placeholder="e.g., Epic Car Chase Sequence")
            new_description = st.text_area("Description", placeholder="Describe your action sequence...")
            
            if st.button("Create Storyboard", type="primary"):
                if new_title:
                    create_new_storyboard(new_title, new_description)
                else:
                    st.error("Please enter a title")
        
        # Load existing storyboards
        st.subheader("Load Storyboard")
        storyboards = load_storyboards()
        
        if storyboards:
            storyboard_options = {sb["title"]: sb for sb in storyboards}
            selected_title = st.selectbox(
                "Select Storyboard",
                options=list(storyboard_options.keys()),
                index=None,
                placeholder="Choose a storyboard..."
            )
            
            if selected_title and st.button("Load Selected"):
                st.session_state.storyboard = storyboard_options[selected_title]
                st.success(f"Loaded: {selected_title}")
        else:
            st.info("No storyboards found. Create your first one!")
    
    # Main content area
    if st.session_state.storyboard is None:
        # Welcome screen
        st.markdown("## 🚀 Get Started")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 🎬 Action Scene Types")
            if st.session_state.scene_templates:
                for template_name, template_data in st.session_state.scene_templates.items():
                    with st.expander(template_data["name"]):
                        st.write(template_data["description"])
                        st.code(template_data["default_prompt"])
        
        with col2:
            st.markdown("### 🛠️ Features")
            st.write("""
            - **Node-based Editor**: Visual workflow for scene sequencing
            - **AI Generation**: Multiple models for different action types
            - **ControlNet Support**: Precise pose and composition control
            - **Violence Levels**: PG-13 to R-rated cinematic action
            - **Professional Output**: Storyboard and image sequence export
            """)
            
            st.markdown("### 🎯 Supported Action Scenes")
            st.write("""
            - Car chases and vehicle pursuits
            - Hand-to-hand combat and martial arts
            - Explosions and demolitions
            - Shootouts and tactical combat
            - Aerial and space battles
            - Boxing and sports combat
            """)
    
    else:
        # Storyboard editor
        storyboard = st.session_state.storyboard
        
        st.markdown(f"## 🎬 {storyboard['title']}")
        if storyboard.get('description'):
            st.write(storyboard['description'])
        
        # Scene editor tabs
        tab1, tab2, tab3, tab4, tab5 = st.tabs(["🎯 Scene Editor", "🎨 Sketch to Image", "⚡ Iterative Workflow", "🎬 Storyboard View", "⚙️ Export"])
        
        with tab1:
            # Scene creation interface
            st.subheader("Create New Scene")
            
            col1, col2 = st.columns([1, 1])
            
            with col1:
                # Scene parameters
                st.markdown("### Scene Parameters")
                
                scene_type = st.selectbox(
                    "Scene Type",
                    options=["car_chase", "fight_scene", "explosion", "shootout", 
                            "aerial_combat", "space_battle", "boxing_match", "martial_arts"],
                    format_func=lambda x: x.replace("_", " ").title()
                )
                
                violence_level = st.selectbox(
                    "Violence Level",
                    options=["pg13", "r_rated", "cinematic"],
                    index=1,
                    format_func=lambda x: x.replace("_", "-").upper()
                )
                
                camera_angle = st.selectbox(
                    "Camera Angle",
                    options=["wide_shot", "medium_shot", "close_up", "low_angle", 
                            "high_angle", "dutch_angle", "pov"],
                    index=1,
                    format_func=lambda x: x.replace("_", " ").title()
                )
                
                setting = st.text_input("Setting", placeholder="e.g., busy city streets, warehouse, rooftop")
                lighting = st.text_input("Lighting", value="dramatic", placeholder="e.g., dramatic, cinematic, neon")
                
                motion_blur = st.checkbox("Motion Blur", value=True)
                
            with col2:
                # Generation parameters
                st.markdown("### Generation Settings")
                
                width = st.selectbox("Width", options=[512, 768, 1024, 1536], index=2)
                height = st.selectbox("Height", options=[512, 768, 1024, 1536], index=2)
                steps = st.slider("Steps", min_value=10, max_value=50, value=30)
                cfg_scale = st.slider("CFG Scale", min_value=1.0, max_value=20.0, value=7.5, step=0.5)
                
                # ControlNet settings
                use_controlnet = st.checkbox("Use ControlNet")
                if use_controlnet:
                    controlnet_type = st.selectbox(
                        "ControlNet Type",
                        options=["openpose", "depth", "canny", "lineart"],
                        index=0
                    )
                    controlnet_strength = st.slider("ControlNet Strength", 0.0, 1.0, 0.8, 0.1)
            
            # Prompt input
            st.markdown("### Scene Prompt")
            
            # Template selector
            if st.session_state.scene_templates and scene_type in st.session_state.scene_templates:
                template = st.session_state.scene_templates[scene_type]
                if st.button(f"Use {template['name']} Template"):
                    st.session_state.current_prompt = template["default_prompt"]
            
            prompt = st.text_area(
                "Describe your action scene",
                value=st.session_state.get('current_prompt', ''),
                height=100,
                placeholder="Describe the action scene in detail..."
            )
            
            # Generate button
            if st.button("🎬 Generate Scene", type="primary", use_container_width=True):
                if prompt:
                    # Prepare generation request
                    node_id = str(uuid.uuid4())
                    
                    generation_request = {
                        "node_id": node_id,
                        "prompt": prompt,
                        "scene_params": {
                            "scene_type": scene_type,
                            "violence_level": violence_level,
                            "camera_angle": camera_angle,
                            "setting": setting,
                            "lighting": lighting,
                            "motion_blur": motion_blur,
                            "characters": [],
                            "props": []
                        },
                        "generation_config": {
                            "width": width,
                            "height": height,
                            "steps": steps,
                            "cfg_scale": cfg_scale,
                            "controlnet": {
                                "type": controlnet_type,
                                "enabled": use_controlnet,
                                "strength": controlnet_strength
                            } if use_controlnet else None
                        }
                    }
                    
                    # Generate scene
                    result = generate_scene(generation_request)
                    
                    if result:
                        st.success("Scene generated successfully!")
                        
                        # Display result
                        col1, col2 = st.columns([1, 1])
                        with col1:
                            st.image(
                                "https://via.placeholder.com/512x512/333/FFF?text=Generated+Scene",
                                caption=f"Generated Scene: {scene_type.replace('_', ' ').title()}",
                                use_container_width=True
                            )
                        
                        with col2:
                            st.write("**Generation Details:**")
                            st.write(f"- Scene Type: {scene_type.replace('_', ' ').title()}")
                            st.write(f"- Violence Level: {violence_level.replace('_', '-').upper()}")
                            st.write(f"- Camera Angle: {camera_angle.replace('_', ' ').title()}")
                            st.write(f"- Generation Time: {result.get('generation_time', 0):.2f}s")
                            
                            if st.button("Add to Storyboard"):
                                st.info("Scene added to storyboard!")
                else:
                    st.error("Please enter a scene prompt")
        
        with tab2:
            # Sketch to Image interface
            from .sketch_interface import SketchInterface
            
            sketch_ui = SketchInterface()
            
            st.markdown("### 🎨 Sketch to Action Scene")
            st.write("Draw your action scene composition and generate AI images from your sketches.")
            
            # Generation method selection
            col1, col2 = st.columns([1, 1])
            
            with col1:
                generation_method = st.selectbox(
                    "Generation Method",
                    ["ComfyUI (Local)", "Replicate API (Cloud)"],
                    help="ComfyUI gives full control, Replicate is faster but has content restrictions"
                )
                
                if generation_method == "Replicate API (Cloud)":
                    replicate_token = st.text_input(
                        "Replicate API Token",
                        type="password",
                        help="Get your token from https://replicate.com/account/api-tokens"
                    )
                    
                    if replicate_token:
                        st.success("✅ Replicate token configured")
                    else:
                        st.warning("⚠️ Enter Replicate token to use cloud generation")
            
            with col2:
                # WAN model selection
                wan_model = st.selectbox(
                    "WAN Model",
                    ["WAN safetensors", "WAN2.114b", "Auto-select"],
                    help="Choose your WAN model for generation"
                )
                
                if wan_model != "Auto-select":
                    wan_path = st.text_input(
                        f"Path to {wan_model}",
                        placeholder=f"/path/to/{wan_model.lower().replace(' ', '_')}"
                    )
            
            # Main sketch interface
            sketch_result = sketch_ui.create_drawing_canvas("main")
            
            if sketch_result:
                st.success("🎨 Sketch captured! Generating action scene...")
                
                # Prepare generation parameters
                generation_params = {
                    "sketch_data": sketch_result,
                    "scene_params": {
                        "scene_type": scene_type,
                        "violence_level": violence_level,
                        "camera_angle": camera_angle,
                        "setting": setting,
                        "lighting": lighting,
                        "motion_blur": motion_blur
                    },
                    "generation_config": {
                        "width": sketch_result["canvas_size"][0],
                        "height": sketch_result["canvas_size"][1],
                        "steps": steps,
                        "cfg_scale": cfg_scale,
                        "controlnet": {
                            "type": sketch_result["control_type"],
                            "enabled": True,
                            "strength": sketch_result["control_strength"]
                        }
                    },
                    "method": generation_method,
                    "wan_model": wan_model if wan_model != "Auto-select" else None
                }
                
                # Generate with selected method
                if generation_method == "ComfyUI (Local)":
                    # Use ComfyUI generation
                    generation_request = {
                        "node_id": str(uuid.uuid4()),
                        "prompt": prompt or "action scene from sketch",
                        "scene_params": generation_params["scene_params"],
                        "generation_config": generation_params["generation_config"]
                    }
                    
                    result = generate_scene(generation_request)
                    
                else:
                    # Use Replicate API
                    if replicate_token:
                        st.info("🌐 Generating with Replicate API...")
                        # This would call the Replicate client
                        st.info("Replicate generation will be implemented when you provide the API token")
                        result = None
                    else:
                        st.error("Please provide Replicate API token")
                        result = None
                
                if result and result.get("success"):
                    col1, col2, col3 = st.columns([1, 1, 1])
                    
                    with col1:
                        st.write("**Original Sketch**")
                        st.image(sketch_result["processed_image"], caption="Your Sketch")
                    
                    with col2:
                        st.write("**Generated Scene**")
                        st.image(
                            "https://via.placeholder.com/512x512/333/FFF?text=Generated+Action+Scene",
                            caption="AI Generated Result"
                        )
                    
                    with col3:
                        st.write("**Generation Info**")
                        st.write(f"Method: {generation_method}")
                        st.write(f"Control: {sketch_result['control_type']}")
                        st.write(f"Strength: {sketch_result['control_strength']}")
                        st.write(f"Time: {result.get('generation_time', 0):.1f}s")
                        
                        if st.button("🔄 Refine Result"):
                            st.session_state['refine_image'] = result["image_url"]
                    
                    # Iterative refinement
                    if 'refine_image' in st.session_state:
                        st.markdown("---")
                        refinement_result = sketch_ui.create_refinement_workflow(st.session_state['refine_image'])
                        
                        if refinement_result:
                            st.success("🔄 Applying refinement...")
                            # This would apply the refinement
                            st.info("Refinement processing...")
            
            # ControlNet comparison section
            st.markdown("---")
            st.markdown("### 🎯 ControlNet Comparison")
            
            if st.button("🧪 Generate Multiple ControlNet Versions"):
                st.info("This will generate the same scene with different ControlNet approaches")
                
                # Show comparison grid
                control_types = ["openpose", "canny", "depth", "lineart"]
                cols = st.columns(len(control_types))
                
                for i, control_type in enumerate(control_types):
                    with cols[i]:
                        st.image(
                            f"https://via.placeholder.com/256x256/333/FFF?text={control_type.title()}",
                            caption=f"{control_type.title()} Control"
                        )
                        st.write(f"Strength: 0.8")
                        if st.button(f"Use {control_type}", key=f"use_{control_type}"):
                            st.success(f"Using {control_type} ControlNet")
        
        with tab3:
            # Iterative Workflow interface
            from .iterative_workflow import IterativeWorkflow
            
            workflow = IterativeWorkflow()
            workflow.create_workflow_interface()
        
        with tab5:
            # Storyboard view
            st.subheader("Storyboard Timeline")
            
            nodes = storyboard.get('nodes', [])
            
            if nodes:
                for i, node in enumerate(nodes):
                    with st.container():
                        col1, col2, col3 = st.columns([1, 2, 1])
                        
                        with col1:
                            st.image(
                                "https://via.placeholder.com/200x150/333/FFF?text=Scene+" + str(i+1),
                                caption=f"Scene {i+1}"
                            )
                        
                        with col2:
                            st.write(f"**Scene {i+1}**")
                            st.write(node.get('prompt', 'No prompt available'))
                            st.write(f"Type: {node.get('scene_params', {}).get('scene_type', 'Unknown').replace('_', ' ').title()}")
                        
                        with col3:
                            if st.button(f"Edit Scene {i+1}", key=f"edit_{i}"):
                                st.info(f"Editing scene {i+1}")
                            if st.button(f"Delete Scene {i+1}", key=f"delete_{i}"):
                                st.warning(f"Scene {i+1} deleted")
            else:
                st.info("No scenes in this storyboard yet. Create your first scene in the Scene Editor tab!")
        
        with tab3:
            # Export options
            st.subheader("Export Storyboard")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### Export Formats")
                export_pdf = st.checkbox("PDF Storyboard", value=True)
                export_images = st.checkbox("Image Sequence", value=True)
                export_json = st.checkbox("JSON Data", value=False)
                
                if st.button("📄 Generate Exports", type="primary"):
                    with st.spinner("Generating exports..."):
                        time.sleep(2)  # Simulate export process
                        st.success("Exports generated!")
                        
                        if export_pdf:
                            st.download_button(
                                "📄 Download PDF Storyboard",
                                data="placeholder pdf data",
                                file_name=f"{storyboard['title']}_storyboard.pdf",
                                mime="application/pdf"
                            )
                        
                        if export_images:
                            st.download_button(
                                "🖼️ Download Image Sequence",
                                data="placeholder zip data",
                                file_name=f"{storyboard['title']}_images.zip",
                                mime="application/zip"
                            )
                        
                        if export_json:
                            st.download_button(
                                "📋 Download JSON Data",
                                data=json.dumps(storyboard, indent=2),
                                file_name=f"{storyboard['title']}_data.json",
                                mime="application/json"
                            )
            
            with col2:
                st.markdown("### Storyboard Stats")
                st.metric("Total Scenes", len(storyboard.get('nodes', [])))
                st.metric("Scene Types", len(set(node.get('scene_params', {}).get('scene_type', '') for node in storyboard.get('nodes', []))))
                st.metric("Created", storyboard.get('created_at', 'Unknown')[:10])

if __name__ == "__main__":
    main()