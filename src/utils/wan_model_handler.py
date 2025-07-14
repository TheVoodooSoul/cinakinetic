import os
import shutil
from pathlib import Path
from typing import Dict, List, Optional

class WANModelHandler:
    """Handle WAN model files and integration"""
    
    def __init__(self, comfyui_models_path: str = "/Users/watson/Workspace/ComfyUI/models"):
        self.comfyui_models_path = Path(comfyui_models_path)
        self.checkpoints_path = self.comfyui_models_path / "checkpoints"
        
        # Ensure directories exist
        self.checkpoints_path.mkdir(parents=True, exist_ok=True)
    
    def find_wan_models(self, search_paths: List[str]) -> Dict[str, str]:
        """Find WAN model files in specified paths"""
        
        wan_models = {}
        
        for search_path in search_paths:
            path = Path(search_path)
            if path.exists():
                # Look for WAN models
                for pattern in ["*wan*.safetensors", "*wan*.ckpt", "*WAN*.safetensors", "*WAN*.ckpt"]:
                    for model_file in path.rglob(pattern):
                        model_name = model_file.stem
                        wan_models[model_name] = str(model_file)
        
        return wan_models
    
    def install_wan_model(self, model_path: str, model_name: Optional[str] = None) -> bool:
        """Install WAN model to ComfyUI models directory"""
        
        source_path = Path(model_path)
        
        if not source_path.exists():
            print(f"❌ Model file not found: {model_path}")
            return False
        
        # Determine destination name
        if model_name is None:
            model_name = source_path.name
        
        dest_path = self.checkpoints_path / model_name
        
        try:
            if dest_path.exists():
                print(f"✅ Model already installed: {model_name}")
                return True
            
            print(f"📦 Installing WAN model: {model_name}")
            shutil.copy2(source_path, dest_path)
            print(f"✅ Successfully installed: {model_name}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to install model: {e}")
            return False
    
    def list_installed_models(self) -> List[str]:
        """List all installed models in ComfyUI"""
        
        models = []
        
        for model_file in self.checkpoints_path.glob("*.safetensors"):
            models.append(model_file.name)
        
        for model_file in self.checkpoints_path.glob("*.ckpt"):
            models.append(model_file.name)
        
        return sorted(models)
    
    def get_wan_model_config(self, model_name: str) -> Dict:
        """Get optimized config for WAN models"""
        
        # WAN model specific optimizations
        if "wan" in model_name.lower():
            return {
                "sampler": "dpmpp_2m",
                "scheduler": "karras",
                "steps": 25,  # WAN models work well with fewer steps
                "cfg_scale": 6.0,  # Lower CFG for WAN
                "clip_skip": 2
            }
        
        # Default config
        return {
            "sampler": "euler_a",
            "scheduler": "normal", 
            "steps": 30,
            "cfg_scale": 7.5,
            "clip_skip": 1
        }
    
    def setup_wan_environment(self) -> Dict[str, str]:
        """Set up environment for WAN model usage"""
        
        setup_status = {}
        
        # Check if ComfyUI is available
        if self.comfyui_models_path.exists():
            setup_status["comfyui"] = "✅ ComfyUI models directory found"
        else:
            setup_status["comfyui"] = "❌ ComfyUI models directory not found"
        
        # Check for installed models
        models = self.list_installed_models()
        wan_models = [m for m in models if "wan" in m.lower()]
        
        if wan_models:
            setup_status["wan_models"] = f"✅ Found {len(wan_models)} WAN models: {', '.join(wan_models)}"
        else:
            setup_status["wan_models"] = "⚠️ No WAN models found"
        
        # Check for ControlNet models
        controlnet_path = self.comfyui_models_path / "controlnet"
        if controlnet_path.exists():
            controlnet_models = list(controlnet_path.glob("*.pth")) + list(controlnet_path.glob("*.safetensors"))
            if controlnet_models:
                setup_status["controlnet"] = f"✅ Found {len(controlnet_models)} ControlNet models"
            else:
                setup_status["controlnet"] = "⚠️ No ControlNet models found"
        else:
            setup_status["controlnet"] = "❌ ControlNet directory not found"
        
        return setup_status
    
    def create_wan_workflow(self, model_name: str, use_controlnet: bool = False) -> Dict:
        """Create optimized workflow for WAN models"""
        
        config = self.get_wan_model_config(model_name)
        
        # Base workflow optimized for WAN
        workflow = {
            "1": {
                "inputs": {
                    "text": "PROMPT_PLACEHOLDER",
                    "clip": ["4", 1]
                },
                "class_type": "CLIPTextEncode",
                "_meta": {"title": "CLIP Text Encode (Prompt)"}
            },
            "2": {
                "inputs": {
                    "text": "NEGATIVE_PLACEHOLDER", 
                    "clip": ["4", 1]
                },
                "class_type": "CLIPTextEncode",
                "_meta": {"title": "CLIP Text Encode (Negative)"}
            },
            "3": {
                "inputs": {
                    "seed": 42,
                    "steps": config["steps"],
                    "cfg": config["cfg_scale"],
                    "sampler_name": config["sampler"],
                    "scheduler": config["scheduler"],
                    "denoise": 1,
                    "model": ["4", 0],
                    "positive": ["1", 0],
                    "negative": ["2", 0],
                    "latent_image": ["5", 0]
                },
                "class_type": "KSampler",
                "_meta": {"title": "KSampler"}
            },
            "4": {
                "inputs": {
                    "ckpt_name": model_name
                },
                "class_type": "CheckpointLoaderSimple",
                "_meta": {"title": "Load Checkpoint"}
            },
            "5": {
                "inputs": {
                    "width": 512,
                    "height": 512,
                    "batch_size": 1
                },
                "class_type": "EmptyLatentImage",
                "_meta": {"title": "Empty Latent Image"}
            },
            "8": {
                "inputs": {
                    "samples": ["3", 0],
                    "vae": ["4", 2]
                },
                "class_type": "VAEDecode",
                "_meta": {"title": "VAE Decode"}
            },
            "9": {
                "inputs": {
                    "filename_prefix": f"wan_action_{model_name.split('.')[0]}",
                    "images": ["8", 0]
                },
                "class_type": "SaveImage",
                "_meta": {"title": "Save Image"}
            }
        }
        
        # Add CLIP skip if needed
        if config["clip_skip"] > 1:
            workflow["10"] = {
                "inputs": {
                    "stop_at_clip_layer": -config["clip_skip"],
                    "clip": ["4", 1]
                },
                "class_type": "CLIPSetLastLayer",
                "_meta": {"title": "CLIP Set Last Layer"}
            }
            
            # Update text encoders to use CLIP skip
            workflow["1"]["inputs"]["clip"] = ["10", 0]
            workflow["2"]["inputs"]["clip"] = ["10", 0]
        
        return workflow

def setup_user_wan_models(user_model_paths: Dict[str, str]) -> Dict[str, bool]:
    """Setup user-provided WAN models"""
    
    handler = WANModelHandler()
    results = {}
    
    for model_name, model_path in user_model_paths.items():
        if os.path.exists(model_path):
            success = handler.install_wan_model(model_path, f"{model_name}.safetensors")
            results[model_name] = success
        else:
            print(f"❌ Model path not found: {model_path}")
            results[model_name] = False
    
    return results

def get_wan_setup_instructions() -> str:
    """Get instructions for setting up WAN models"""
    
    return """
# WAN Model Setup Instructions

## 1. Locate Your WAN Models
You mentioned having:
- WAN safetensors
- WAN2.114b

## 2. Install to ComfyUI
Run this setup:

```python
from src.utils.wan_model_handler import setup_user_wan_models

# Update these paths to your actual model locations
user_models = {
    "wan_safetensors": "/path/to/your/wan.safetensors",
    "wan2_114b": "/path/to/your/wan2.114b"
}

results = setup_user_wan_models(user_models)
print("Setup results:", results)
```

## 3. Verify Installation
Check the Cinema Action Scene Generator will automatically detect your WAN models.

## 4. Optimized Settings for WAN
- Sampler: DPM++ 2M Karras
- Steps: 20-25 (WAN models are efficient)
- CFG Scale: 6.0-7.0
- CLIP Skip: 2

## 5. Action Scene Prompts for WAN
WAN models excel at:
- Dynamic action poses
- Cinematic compositions  
- Realistic lighting
- Character expressions during action
"""