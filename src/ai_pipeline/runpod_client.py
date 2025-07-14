import requests
import asyncio
import time
import json
from typing import Dict, Any, Optional
from ..models.scene_models import SceneParameters, GenerationConfig
from ..utils.prompt_builder import ActionPromptBuilder

class RunPodClient:
    """Client for RunPod ComfyUI instances"""
    
    def __init__(self, pod_url: str, api_key: Optional[str] = None):
        self.pod_url = pod_url.rstrip('/')
        self.api_key = api_key
        self.prompt_builder = ActionPromptBuilder()
        
        # Ensure proper URL format
        if not self.pod_url.startswith('http'):
            self.pod_url = f"https://{self.pod_url}"
    
    async def health_check(self) -> bool:
        """Check if RunPod ComfyUI is accessible"""
        try:
            response = requests.get(f"{self.pod_url}/system_stats", timeout=10)
            return response.status_code == 200
        except Exception:
            return False
    
    async def get_available_models(self) -> list:
        """Get list of available models on the pod"""
        try:
            response = requests.get(f"{self.pod_url}/object_info", timeout=10)
            if response.status_code == 200:
                object_info = response.json()
                checkpoint_loader = object_info.get("CheckpointLoaderSimple", {})
                input_info = checkpoint_loader.get("input", {})
                ckpt_name_info = input_info.get("ckpt_name", {})
                
                if isinstance(ckpt_name_info, list) and len(ckpt_name_info) > 1:
                    return ckpt_name_info[0]
            return []
        except Exception:
            return []
    
    async def generate_scene(
        self, 
        prompt: str, 
        scene_params: SceneParameters, 
        config: GenerationConfig,
        wan_model: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate scene using RunPod ComfyUI"""
        
        start_time = time.time()
        
        # Build enhanced prompt
        enhanced_prompt = self.prompt_builder.build_action_prompt(prompt, scene_params)
        
        # Select model (prefer WAN if available)
        model_name = await self._select_model(wan_model, scene_params.scene_type)
        
        # Create optimized workflow for RunPod
        workflow = self._create_runpod_workflow(
            enhanced_prompt, 
            scene_params, 
            config, 
            model_name
        )
        
        try:
            # Submit to RunPod
            result = await self._submit_workflow(workflow)
            
            generation_time = time.time() - start_time
            
            return {
                "image_url": result["image_url"],
                "generation_time": generation_time,
                "model_used": model_name,
                "pod_url": self.pod_url,
                "metadata": {
                    "enhanced_prompt": enhanced_prompt,
                    "scene_type": scene_params.scene_type,
                    "violence_level": scene_params.violence_level,
                    "runpod_generation": True
                }
            }
            
        except Exception as e:
            return {
                "image_url": "/static/images/placeholder_action.jpg",
                "generation_time": time.time() - start_time,
                "error": str(e),
                "model_used": model_name,
                "metadata": {
                    "enhanced_prompt": enhanced_prompt,
                    "scene_type": scene_params.scene_type,
                    "violence_level": scene_params.violence_level,
                    "runpod_generation": True,
                    "error": True
                }
            }
    
    async def _select_model(self, preferred_wan: Optional[str], scene_type: str) -> str:
        """Select best available model for scene type"""
        
        available_models = await self.get_available_models()
        
        # Look for preferred WAN model first
        if preferred_wan:
            for model in available_models:
                if preferred_wan.lower() in model.lower():
                    return model
        
        # Look for any WAN model
        wan_models = [m for m in available_models if 'wan' in m.lower()]
        if wan_models:
            return wan_models[0]
        
        # Scene-specific model preferences
        scene_preferences = {
            "car_chase": ["realistic", "vision", "epic"],
            "fight_scene": ["epic", "realistic", "dream"], 
            "explosion": ["juggernaut", "epic", "dream"],
            "aerial_combat": ["dream", "epic", "realistic"],
            "space_battle": ["dream", "sci", "epic"]
        }
        
        preferences = scene_preferences.get(scene_type, ["realistic", "epic", "dream"])
        
        for preference in preferences:
            for model in available_models:
                if preference in model.lower():
                    return model
        
        # Default to first available model
        return available_models[0] if available_models else "sd_v1-5.safetensors"
    
    def _create_runpod_workflow(
        self, 
        prompt: str, 
        scene_params: SceneParameters, 
        config: GenerationConfig,
        model_name: str
    ) -> Dict[str, Any]:
        """Create optimized workflow for RunPod RTX 4090"""
        
        # Get WAN-optimized settings
        wan_settings = self._get_wan_optimizations(model_name)
        
        workflow = {
            "1": {
                "inputs": {
                    "text": prompt,
                    "clip": ["4", 1]
                },
                "class_type": "CLIPTextEncode",
                "_meta": {"title": "CLIP Text Encode (Prompt)"}
            },
            "2": {
                "inputs": {
                    "text": self._build_negative_prompt(scene_params),
                    "clip": ["4", 1]
                },
                "class_type": "CLIPTextEncode",
                "_meta": {"title": "CLIP Text Encode (Negative)"}
            },
            "3": {
                "inputs": {
                    "seed": config.seed if config.seed is not None else 42,
                    "steps": wan_settings["steps"],
                    "cfg": wan_settings["cfg_scale"],
                    "sampler_name": wan_settings["sampler"],
                    "scheduler": wan_settings["scheduler"],
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
                    "width": config.width,
                    "height": config.height,
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
                    "filename_prefix": f"action_{scene_params.scene_type}_{int(time.time())}",
                    "images": ["8", 0]
                },
                "class_type": "SaveImage",
                "_meta": {"title": "Save Image"}
            }
        }
        
        # Add CLIP skip for WAN models
        if wan_settings["clip_skip"] > 1:
            workflow["10"] = {
                "inputs": {
                    "stop_at_clip_layer": -wan_settings["clip_skip"],
                    "clip": ["4", 1]
                },
                "class_type": "CLIPSetLastLayer",
                "_meta": {"title": "CLIP Set Last Layer"}
            }
            
            # Update text encoders to use CLIP skip
            workflow["1"]["inputs"]["clip"] = ["10", 0]
            workflow["2"]["inputs"]["clip"] = ["10", 0]
        
        # Add ControlNet if configured
        if config.controlnet and config.controlnet.enabled:
            workflow = self._add_controlnet_nodes(workflow, config.controlnet)
        
        return workflow
    
    def _get_wan_optimizations(self, model_name: str) -> Dict[str, Any]:
        """Get optimized settings for WAN models on RTX 6000 Ada"""
        
        if 'wan' in model_name.lower():
            return {
                "sampler": "dpmpp_2m_karras",  # Full name for better results
                "scheduler": "karras",
                "steps": 25,  # Can afford more steps with 48GB VRAM
                "cfg_scale": 6.5,
                "clip_skip": 2
            }
        else:
            return {
                "sampler": "euler_a", 
                "scheduler": "normal",
                "steps": 28,  # Slightly higher for RTX 6000
                "cfg_scale": 7.5,
                "clip_skip": 1
            }
    
    def _build_negative_prompt(self, scene_params: SceneParameters) -> str:
        """Build negative prompt for action scenes"""
        
        base_negative = "low quality, blurry, distorted, amateur, worst quality, bad anatomy"
        
        # Scene-specific negatives
        scene_negatives = {
            "car_chase": "static cars, parked vehicles, slow motion",
            "fight_scene": "peaceful, sitting, calm poses, static",
            "explosion": "intact buildings, no effects, clean environment"
        }
        
        scene_specific = scene_negatives.get(scene_params.scene_type, "")
        
        return f"{base_negative}, {scene_specific}" if scene_specific else base_negative
    
    def _add_controlnet_nodes(self, workflow: Dict[str, Any], controlnet_config) -> Dict[str, Any]:
        """Add ControlNet nodes for RunPod workflow"""
        
        # ControlNet loader
        workflow["11"] = {
            "inputs": {
                "control_net_name": f"control_{controlnet_config.type}_sd15.pth"
            },
            "class_type": "ControlNetLoader",
            "_meta": {"title": "Load ControlNet"}
        }
        
        # Image input (would be provided by sketch interface)
        workflow["12"] = {
            "inputs": {
                "image": "CONTROLNET_IMAGE_PLACEHOLDER"
            },
            "class_type": "LoadImage",
            "_meta": {"title": "Load Control Image"}
        }
        
        # Preprocessor
        if controlnet_config.type == "openpose":
            workflow["13"] = {
                "inputs": {
                    "image": ["12", 0]
                },
                "class_type": "OpenposePreprocessor",
                "_meta": {"title": "OpenPose Preprocessor"}
            }
        elif controlnet_config.type == "canny":
            workflow["13"] = {
                "inputs": {
                    "image": ["12", 0],
                    "low_threshold": 100,
                    "high_threshold": 200
                },
                "class_type": "CannyEdgePreprocessor",
                "_meta": {"title": "Canny Preprocessor"}
            }
        
        # ControlNet Apply
        workflow["14"] = {
            "inputs": {
                "conditioning": ["1", 0],
                "control_net": ["11", 0],
                "image": ["13", 0],
                "strength": controlnet_config.strength
            },
            "class_type": "ControlNetApply",
            "_meta": {"title": "Apply ControlNet"}
        }
        
        # Update KSampler to use ControlNet conditioning
        workflow["3"]["inputs"]["positive"] = ["14", 0]
        
        return workflow
    
    async def _submit_workflow(self, workflow: Dict[str, Any]) -> Dict[str, Any]:
        """Submit workflow to RunPod and wait for completion"""
        
        try:
            # Submit workflow
            response = requests.post(
                f"{self.pod_url}/prompt",
                json={"prompt": workflow},
                timeout=30
            )
            
            if response.status_code != 200:
                raise Exception(f"Failed to submit workflow: {response.status_code}")
            
            result = response.json()
            prompt_id = result["prompt_id"]
            
            # Poll for completion (RunPod is fast, so shorter polling)
            for attempt in range(120):  # 2 minutes max
                await asyncio.sleep(1)
                
                history_response = requests.get(
                    f"{self.pod_url}/history/{prompt_id}",
                    timeout=10
                )
                
                if history_response.status_code == 200:
                    history = history_response.json()
                    
                    if prompt_id in history:
                        # Get generated image
                        outputs = history[prompt_id]["outputs"]
                        if "9" in outputs and "images" in outputs["9"]:
                            image_info = outputs["9"]["images"][0]
                            
                            # RunPod image URL
                            image_url = f"{self.pod_url}/view?filename={image_info['filename']}&type=output"
                            
                            return {
                                "image_url": image_url,
                                "prompt_id": prompt_id,
                                "filename": image_info['filename']
                            }
            
            raise Exception("Generation timeout")
            
        except Exception as e:
            # Fallback to placeholder
            return {
                "image_url": "/static/images/placeholder_action.jpg", 
                "error": str(e)
            }
    
    async def download_image(self, image_url: str, local_path: str) -> bool:
        """Download generated image from RunPod to local storage"""
        
        try:
            response = requests.get(image_url, timeout=30)
            if response.status_code == 200:
                with open(local_path, 'wb') as f:
                    f.write(response.content)
                return True
        except Exception:
            pass
        return False
    
    def get_pod_info(self) -> Dict[str, Any]:
        """Get information about the RunPod instance"""
        
        try:
            response = requests.get(f"{self.pod_url}/system_stats", timeout=10)
            if response.status_code == 200:
                return response.json()
        except Exception:
            pass
        return {}