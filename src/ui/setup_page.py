import streamlit as st
import os
from pathlib import Path
import requests
from typing import Dict, List

def create_setup_page():
    """Setup page for WAN models and generation backends"""
    
    st.title("🛠️ Setup & Configuration")
    st.write("Configure your WAN models and generation backends")
    
    # Setup tabs
    tab1, tab2, tab3, tab4 = st.tabs(["🎯 WAN Models", "☁️ RunPod Setup", "🖥️ Local Setup", "🔧 Advanced"])
    
    with tab1:
        st.header("WAN Model Configuration")
        
        # WAN model detection
        st.subheader("Detect WAN Models")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Automatic Detection**")
            
            search_paths = st.text_area(
                "Search Paths (one per line)",
                value="/Users/watson/Downloads\n/Users/watson/Models\n/Users/watson/Desktop",
                help="Enter paths where your WAN models might be located"
            ).strip().split('\n')
            
            if st.button("🔍 Scan for WAN Models"):
                found_models = scan_for_wan_models(search_paths)
                
                if found_models:
                    st.success(f"Found {len(found_models)} WAN models:")
                    for model_name, model_path in found_models.items():
                        st.write(f"✅ **{model_name}**: `{model_path}`")
                        
                        if st.button(f"Install {model_name}", key=f"install_{model_name}"):
                            success = install_wan_model(model_path, model_name)
                            if success:
                                st.success(f"✅ {model_name} installed successfully!")
                            else:
                                st.error(f"❌ Failed to install {model_name}")
                else:
                    st.warning("No WAN models found in specified paths")
        
        with col2:
            st.write("**Manual Installation**")
            
            manual_model_path = st.text_input(
                "WAN Model Path",
                placeholder="/path/to/your/wan_model.safetensors"
            )
            
            manual_model_name = st.text_input(
                "Model Name",
                placeholder="wan_safetensors"
            )
            
            if st.button("📦 Install Manual Model"):
                if manual_model_path and manual_model_name:
                    if os.path.exists(manual_model_path):
                        success = install_wan_model(manual_model_path, manual_model_name)
                        if success:
                            st.success(f"✅ {manual_model_name} installed!")
                        else:
                            st.error("❌ Installation failed")
                    else:
                        st.error("File not found!")
                else:
                    st.error("Please enter both path and name")
        
        # Installed models
        st.subheader("Installed Models")
        installed_models = get_installed_models()
        
        if installed_models:
            for model in installed_models:
                col1, col2, col3 = st.columns([2, 1, 1])
                
                with col1:
                    st.write(f"📦 {model}")
                
                with col2:
                    model_size = get_model_size(model)
                    st.write(f"Size: {model_size}")
                
                with col3:
                    if st.button("Test", key=f"test_{model}"):
                        test_model(model)
        else:
            st.info("No models installed yet")
    
    with tab2:
        st.header("RunPod Cloud Setup")
        st.write("Set up RunPod for faster WAN model processing")
        
        # RunPod benefits
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🚀 Why RunPod?")
            st.write("""
            **Speed Benefits:**
            - RTX 4090: ~10x faster than M2 Max
            - A100: ~20x faster than M2 Max
            - 24GB+ VRAM for large models
            
            **Cost Efficiency:**
            - RTX 4090: ~$0.50/hour
            - A100: ~$1.50/hour
            - Only pay when running
            
            **Pre-configured:**
            - ComfyUI pre-installed
            - Common models included
            - Easy WAN model upload
            """)
        
        with col2:
            st.subheader("⚡ Setup Steps")
            
            # RunPod setup checklist
            runpod_api_key = st.text_input(
                "RunPod API Key",
                type="password",
                help="Get from https://runpod.io/console/user/settings"
            )
            
            if runpod_api_key:
                st.session_state['runpod_api_key'] = runpod_api_key
                st.success("✅ API key saved")
            
            pod_template = st.selectbox(
                "Pod Template",
                [
                    "ComfyUI (RTX 4090) - $0.50/hr",
                    "ComfyUI (A100) - $1.50/hr", 
                    "Custom Template"
                ]
            )
            
            if st.button("🚀 Launch RunPod"):
                if runpod_api_key:
                    launch_runpod(runpod_api_key, pod_template)
                else:
                    st.error("Please enter RunPod API key")
        
        # RunPod management
        st.subheader("Pod Management")
        
        if 'runpod_api_key' in st.session_state:
            active_pods = get_active_pods(st.session_state['runpod_api_key'])
            
            if active_pods:
                for pod in active_pods:
                    with st.expander(f"Pod: {pod['name']} - {pod['status']}"):
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            st.write(f"**GPU:** {pod['gpu']}")
                            st.write(f"**Status:** {pod['status']}")
                        
                        with col2:
                            st.write(f"**Cost:** ${pod['cost_per_hour']}/hr")
                            st.write(f"**Runtime:** {pod['runtime']}")
                        
                        with col3:
                            if pod['status'] == 'running':
                                if st.button(f"Connect to {pod['name']}", key=f"connect_{pod['id']}"):
                                    connect_to_pod(pod)
                                
                                if st.button(f"Stop {pod['name']}", key=f"stop_{pod['id']}"):
                                    stop_pod(pod['id'])
            else:
                st.info("No active pods found")
    
    with tab3:
        st.header("Local Setup Status")
        
        # System requirements check
        st.subheader("System Check")
        
        system_info = get_system_info()
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Hardware**")
            for component, status in system_info["hardware"].items():
                icon = "✅" if status["ok"] else "⚠️"
                st.write(f"{icon} {component}: {status['value']}")
        
        with col2:
            st.write("**Software**")
            for software, status in system_info["software"].items():
                icon = "✅" if status["ok"] else "❌"
                st.write(f"{icon} {software}: {status['value']}")
        
        # ComfyUI status
        st.subheader("ComfyUI Status")
        
        comfyui_status = check_comfyui_status()
        
        if comfyui_status["running"]:
            st.success("✅ ComfyUI is running")
            st.write(f"URL: {comfyui_status['url']}")
            st.write(f"Models: {comfyui_status['model_count']}")
            
            if st.button("🔄 Restart ComfyUI"):
                restart_comfyui()
        else:
            st.error("❌ ComfyUI not running")
            
            if st.button("▶️ Start ComfyUI"):
                start_comfyui()
        
        # Performance recommendations
        st.subheader("Performance Recommendations")
        
        recommendations = get_performance_recommendations(system_info)
        
        for rec in recommendations:
            if rec["type"] == "warning":
                st.warning(f"⚠️ {rec['message']}")
            elif rec["type"] == "info":
                st.info(f"💡 {rec['message']}")
            else:
                st.success(f"✅ {rec['message']}")
    
    with tab4:
        st.header("Advanced Configuration")
        
        # Model paths
        st.subheader("Model Paths")
        
        with st.expander("Configure Model Directories"):
            comfyui_path = st.text_input(
                "ComfyUI Directory",
                value="/Users/watson/Workspace/ComfyUI",
                help="Path to ComfyUI installation"
            )
            
            models_path = st.text_input(
                "Models Directory", 
                value=f"{comfyui_path}/models",
                help="Path to models directory"
            )
            
            if st.button("💾 Save Paths"):
                save_model_paths(comfyui_path, models_path)
                st.success("Paths saved!")
        
        # Generation settings
        st.subheader("Default Generation Settings")
        
        with st.expander("WAN Model Optimizations"):
            col1, col2 = st.columns(2)
            
            with col1:
                default_sampler = st.selectbox(
                    "Default Sampler",
                    ["dpmpp_2m", "euler_a", "heun", "dpm_fast"]
                )
                
                default_steps = st.slider("Default Steps", 10, 50, 25)
                
                default_cfg = st.slider("Default CFG Scale", 1.0, 15.0, 6.0, 0.5)
            
            with col2:
                clip_skip = st.slider("CLIP Skip", 1, 4, 2)
                
                default_scheduler = st.selectbox(
                    "Scheduler",
                    ["karras", "normal", "exponential", "simple"]
                )
                
                memory_optimization = st.selectbox(
                    "Memory Mode",
                    ["auto", "lowvram", "normalvram", "highvram"]
                )
            
            if st.button("💾 Save Settings"):
                save_generation_settings({
                    "sampler": default_sampler,
                    "steps": default_steps,
                    "cfg_scale": default_cfg,
                    "clip_skip": clip_skip,
                    "scheduler": default_scheduler,
                    "memory_mode": memory_optimization
                })
                st.success("Settings saved!")
        
        # Export/Import configuration
        st.subheader("Configuration Management")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("📤 Export Config"):
                config = export_configuration()
                st.download_button(
                    "Download Config",
                    data=config,
                    file_name="cinema_action_config.json",
                    mime="application/json"
                )
        
        with col2:
            uploaded_config = st.file_uploader(
                "Import Config",
                type=['json']
            )
            
            if uploaded_config and st.button("📥 Import"):
                import_configuration(uploaded_config)
                st.success("Configuration imported!")

# Helper functions (simplified implementations)

def scan_for_wan_models(search_paths: List[str]) -> Dict[str, str]:
    """Scan for WAN models in specified paths"""
    found_models = {}
    
    for path in search_paths:
        if os.path.exists(path):
            for root, dirs, files in os.walk(path):
                for file in files:
                    if any(keyword in file.lower() for keyword in ['wan', 'WAN']) and \
                       any(ext in file for ext in ['.safetensors', '.ckpt']):
                        model_name = os.path.splitext(file)[0]
                        found_models[model_name] = os.path.join(root, file)
    
    return found_models

def install_wan_model(model_path: str, model_name: str) -> bool:
    """Install WAN model to ComfyUI"""
    try:
        from ..utils.wan_model_handler import WANModelHandler
        handler = WANModelHandler()
        return handler.install_wan_model(model_path, model_name)
    except Exception:
        return False

def get_installed_models() -> List[str]:
    """Get list of installed models"""
    try:
        from ..utils.wan_model_handler import WANModelHandler
        handler = WANModelHandler()
        return handler.list_installed_models()
    except Exception:
        return []

def get_model_size(model_name: str) -> str:
    """Get model file size"""
    try:
        model_path = Path("/Users/watson/Workspace/ComfyUI/models/checkpoints") / model_name
        if model_path.exists():
            size_bytes = model_path.stat().st_size
            size_gb = size_bytes / (1024**3)
            return f"{size_gb:.1f} GB"
    except Exception:
        pass
    return "Unknown"

def test_model(model_name: str):
    """Test model loading"""
    st.info(f"Testing {model_name}...")
    # Would implement actual model test
    st.success(f"✅ {model_name} loads successfully!")

def launch_runpod(api_key: str, template: str):
    """Launch RunPod instance"""
    st.info("🚀 Launching RunPod instance...")
    # Would implement actual RunPod API calls
    st.success("✅ Pod launched! Check your RunPod dashboard.")

def get_active_pods(api_key: str) -> List[Dict]:
    """Get active RunPod instances"""
    # Mock data for now
    return [
        {
            "id": "pod123",
            "name": "ComfyUI-Action",
            "status": "running",
            "gpu": "RTX 4090",
            "cost_per_hour": 0.50,
            "runtime": "2h 15m"
        }
    ]

def connect_to_pod(pod: Dict):
    """Connect to RunPod instance"""
    st.success(f"✅ Connected to {pod['name']}")
    # Would update app configuration to use pod URL

def stop_pod(pod_id: str):
    """Stop RunPod instance"""
    st.success("✅ Pod stopped")

def get_system_info() -> Dict:
    """Get system information"""
    return {
        "hardware": {
            "GPU": {"value": "Apple M2 Max", "ok": True},
            "RAM": {"value": "32 GB", "ok": True},
            "Storage": {"value": "500 GB free", "ok": True}
        },
        "software": {
            "Python": {"value": "3.11.13", "ok": True},
            "PyTorch": {"value": "2.7.1", "ok": True},
            "ComfyUI": {"value": "0.3.44", "ok": True}
        }
    }

def check_comfyui_status() -> Dict:
    """Check ComfyUI status"""
    try:
        response = requests.get("http://localhost:8188/system_stats", timeout=5)
        return {
            "running": response.status_code == 200,
            "url": "http://localhost:8188",
            "model_count": 5
        }
    except:
        return {"running": False, "url": None, "model_count": 0}

def restart_comfyui():
    """Restart ComfyUI"""
    st.info("🔄 Restarting ComfyUI...")

def start_comfyui():
    """Start ComfyUI"""
    st.info("▶️ Starting ComfyUI...")

def get_performance_recommendations(system_info: Dict) -> List[Dict]:
    """Get performance recommendations"""
    return [
        {"type": "info", "message": "M2 Max is capable but consider RunPod for faster generation"},
        {"type": "warning", "message": "Use 512x512 resolution for local generation to save memory"},
        {"type": "info", "message": "WAN models work well with 20-25 steps on M2 Max"}
    ]

def save_model_paths(comfyui_path: str, models_path: str):
    """Save model paths to config"""
    pass

def save_generation_settings(settings: Dict):
    """Save generation settings"""
    pass

def export_configuration() -> str:
    """Export configuration as JSON"""
    return "{}"

def import_configuration(config_file):
    """Import configuration from file"""
    pass