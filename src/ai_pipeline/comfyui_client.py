import aiohttp
import asyncio
import json
import base64
import time
from typing import Dict, Any, Optional
from ..models.scene_models import SceneParameters, GenerationConfig
from ..utils.prompt_builder import ActionPromptBuilder

class ComfyUIClient:
    def __init__(self, base_url: str = "http://localhost:8188"):
        self.base_url = base_url
        self.prompt_builder = ActionPromptBuilder()
        
    async def health_check(self) -> bool:
        """Check if ComfyUI server is running"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/system_stats") as response:
                    return response.status == 200
        except Exception:
            return False
    
    async def generate_scene(
        self, 
        prompt: str, 
        scene_params: SceneParameters, 
        config: GenerationConfig
    ) -> Dict[str, Any]:
        """Generate an action scene using ComfyUI"""
        
        start_time = time.time()
        
        # Build enhanced prompt
        enhanced_prompt = self.prompt_builder.build_action_prompt(prompt, scene_params)
        
        # Create ComfyUI workflow
        workflow = self._create_workflow(enhanced_prompt, scene_params, config)
        
        # Submit to ComfyUI
        result = await self._submit_workflow(workflow)
        
        generation_time = time.time() - start_time
        
        return {
            "image_url": result["image_url"],
            "generation_time": generation_time,
            "workflow_id": result.get("workflow_id"),
            "metadata": {
                "enhanced_prompt": enhanced_prompt,
                "scene_type": scene_params.scene_type,
                "violence_level": scene_params.violence_level
            }
        }
    
    def _create_workflow(
        self, 
        prompt: str, 
        scene_params: SceneParameters, 
        config: GenerationConfig
    ) -> Dict[str, Any]:
        """Create ComfyUI workflow JSON"""
        
        # Base workflow structure
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
                    "text": self._build_negative_prompt(scene_params, config),
                    "clip": ["4", 1]
                },
                "class_type": "CLIPTextEncode",
                "_meta": {"title": "CLIP Text Encode (Negative)"}
            },
            "3": {
                "inputs": {
                    "seed": config.seed or -1,
                    "steps": config.steps,
                    "cfg": config.cfg_scale,
                    "sampler_name": "euler",
                    "scheduler": "normal",
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
                    "ckpt_name": self._get_model_name(config.model, scene_params.scene_type)
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
                    "filename_prefix": f"action_scene_{scene_params.scene_type}",
                    "images": ["8", 0]
                },
                "class_type": "SaveImage",
                "_meta": {"title": "Save Image"}
            }
        }
        
        # Add ControlNet if configured
        if config.controlnet and config.controlnet.enabled:
            workflow = self._add_controlnet_nodes(workflow, config.controlnet)
        
        # Add LoRA models if specified
        if config.lora_models:
            workflow = self._add_lora_nodes(workflow, config.lora_models)
            
        return workflow
    
    def _add_controlnet_nodes(self, workflow: Dict[str, Any], controlnet_config) -> Dict[str, Any]:
        """Add ControlNet nodes to workflow"""
        
        # Add ControlNet loader
        workflow["10"] = {
            "inputs": {
                "control_net_name": f"control_{controlnet_config.type}_sd15.pth"
            },
            "class_type": "ControlNetLoader",
            "_meta": {"title": "Load ControlNet"}
        }
        
        # Add image preprocessor
        if controlnet_config.type == "openpose":
            workflow["11"] = {
                "inputs": {
                    "image": ["12", 0]  # Input image
                },
                "class_type": "OpenposePreprocessor",
                "_meta": {"title": "OpenPose Preprocessor"}
            }
        
        # Add ControlNet Apply node
        workflow["13"] = {
            "inputs": {
                "conditioning": ["1", 0],
                "control_net": ["10", 0],
                "image": ["11", 0],
                "strength": controlnet_config.strength
            },
            "class_type": "ControlNetApply",
            "_meta": {"title": "Apply ControlNet"}
        }
        
        # Update KSampler to use ControlNet conditioning
        workflow["3"]["inputs"]["positive"] = ["13", 0]
        
        return workflow
    
    def _add_lora_nodes(self, workflow: Dict[str, Any], lora_models: list) -> Dict[str, Any]:
        """Add LoRA model nodes to workflow"""
        
        node_id = 20
        last_model_output = ["4", 0]
        last_clip_output = ["4", 1]
        
        for lora_name in lora_models:
            workflow[str(node_id)] = {
                "inputs": {
                    "lora_name": lora_name,
                    "strength_model": 0.8,
                    "strength_clip": 0.8,
                    "model": last_model_output,
                    "clip": last_clip_output
                },
                "class_type": "LoraLoader",
                "_meta": {"title": f"Load LoRA {lora_name}"}
            }
            
            last_model_output = [str(node_id), 0]
            last_clip_output = [str(node_id), 1]
            node_id += 1
        
        # Update text encoders to use final LoRA output
        workflow["1"]["inputs"]["clip"] = last_clip_output
        workflow["2"]["inputs"]["clip"] = last_clip_output
        workflow["3"]["inputs"]["model"] = last_model_output
        
        return workflow
    
    def _get_model_name(self, model: str, scene_type: str) -> str:
        """Get appropriate model based on scene type"""
        model_mapping = {
            "car_chase": "realisticVisionV60_v60B1.safetensors",
            "fight_scene": "epicrealismXL_v10.safetensors", 
            "explosion": "juggernautXL_v8Rundiffusion.safetensors",
            "aerial_combat": "dreamshaper_8.safetensors",
            "space_battle": "scientificDiffusion_v10.safetensors"
        }
        
        return model_mapping.get(scene_type, "realisticVisionV60_v60B1.safetensors")
    
    def _build_negative_prompt(self, scene_params: SceneParameters, config: GenerationConfig) -> str:
        """Build negative prompt based on scene parameters"""
        base_negative = config.negative_prompt
        
        # Add scene-specific negative prompts
        scene_negatives = {
            "car_chase": "static, parked cars, slow motion",
            "fight_scene": "peaceful, sitting, calm",
            "explosion": "intact buildings, no fire, no smoke"
        }
        
        scene_specific = scene_negatives.get(scene_params.scene_type, "")
        
        return f"{base_negative}, {scene_specific}" if scene_specific else base_negative
    
    async def _submit_workflow(self, workflow: Dict[str, Any]) -> Dict[str, Any]:
        """Submit workflow to ComfyUI and wait for completion"""
        
        try:
            async with aiohttp.ClientSession() as session:
                # Submit workflow
                async with session.post(
                    f"{self.base_url}/prompt",
                    json={"prompt": workflow}
                ) as response:
                    if response.status != 200:
                        raise Exception(f"Failed to submit workflow: {response.status}")
                    
                    result = await response.json()
                    prompt_id = result["prompt_id"]
                
                # Poll for completion
                while True:
                    await asyncio.sleep(1)
                    
                    async with session.get(f"{self.base_url}/history/{prompt_id}") as response:
                        if response.status == 200:
                            history = await response.json()
                            if prompt_id in history:
                                # Get generated image
                                outputs = history[prompt_id]["outputs"]
                                if "9" in outputs and "images" in outputs["9"]:
                                    image_info = outputs["9"]["images"][0]
                                    image_url = f"/static/output/{image_info['filename']}"
                                    
                                    return {
                                        "image_url": image_url,
                                        "workflow_id": prompt_id
                                    }
                
        except Exception as e:
            # Fallback: return placeholder image for development
            return {
                "image_url": "/static/images/placeholder_action.jpg",
                "workflow_id": "dev_fallback"
            }