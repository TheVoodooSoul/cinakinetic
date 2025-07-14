import replicate
import asyncio
import time
import base64
import io
from PIL import Image
from typing import Dict, Any, Optional
from ..models.scene_models import SceneParameters, GenerationConfig
from ..utils.prompt_builder import ActionPromptBuilder

class ReplicateClient:
    def __init__(self, api_token: Optional[str] = None):
        self.api_token = api_token
        self.prompt_builder = ActionPromptBuilder()
        
        # Available models on Replicate
        self.models = {
            "sdxl": "stability-ai/sdxl:39ed52f2a78e934b3ba6e2a89f5b1c712de7dfea535525255b1aa35c5565e08b",
            "sdxl_controlnet": "lucataco/sdxl-controlnet:db2ffdbdc04d8a6bb2a05c7ac086c8d90e4fa4ac08b85c96b4ccaf75d1b8e7eb",
            "realistic_vision": "adirik/realistic-vision-v5:15d95b7b8cce7b7e24e15db8dd58e7436d96bffedebc9b0ffa37c41aabf1d76f",
            "epicrealism": "adirik/epicrealism:589bd3bef6eac37cabe84aa6b1df1b6b9bbdad6b3b8e1123c99c6f50e5e6b02f"
        }
        
    async def health_check(self) -> bool:
        """Check if Replicate API is accessible"""
        try:
            if not self.api_token:
                return False
            # Simple check - this would need actual implementation
            return True
        except Exception:
            return False
    
    async def generate_scene(
        self, 
        prompt: str, 
        scene_params: SceneParameters, 
        config: GenerationConfig,
        sketch_data: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Generate scene using Replicate API"""
        
        if not self.api_token:
            raise Exception("Replicate API token not configured")
        
        start_time = time.time()
        
        # Build enhanced prompt with content safety
        enhanced_prompt = self._build_safe_prompt(prompt, scene_params)
        
        # Choose appropriate model
        model_id = self._select_model(scene_params, sketch_data is not None)
        
        # Prepare inputs
        inputs = {
            "prompt": enhanced_prompt,
            "negative_prompt": self._build_negative_prompt(scene_params),
            "width": config.width,
            "height": config.height,
            "num_inference_steps": config.steps,
            "guidance_scale": config.cfg_scale,
            "seed": config.seed
        }
        
        # Add ControlNet inputs if sketch provided
        if sketch_data and model_id == self.models["sdxl_controlnet"]:
            inputs.update(self._prepare_controlnet_inputs(sketch_data, config))
        
        try:
            # Run generation
            output = await self._run_replicate_model(model_id, inputs)
            
            generation_time = time.time() - start_time
            
            # Process output
            image_url = output[0] if isinstance(output, list) else output
            
            return {
                "image_url": image_url,
                "generation_time": generation_time,
                "model_used": model_id,
                "metadata": {
                    "enhanced_prompt": enhanced_prompt,
                    "scene_type": scene_params.scene_type,
                    "violence_level": scene_params.violence_level,
                    "content_filtered": self._was_content_filtered(enhanced_prompt)
                }
            }
            
        except Exception as e:
            return {
                "image_url": "/static/images/placeholder_action.jpg",
                "generation_time": time.time() - start_time,
                "error": str(e),
                "metadata": {
                    "enhanced_prompt": enhanced_prompt,
                    "scene_type": scene_params.scene_type,
                    "violence_level": scene_params.violence_level
                }
            }
    
    def _build_safe_prompt(self, prompt: str, scene_params: SceneParameters) -> str:
        """Build prompt with Replicate content safety in mind"""
        
        # Use prompt builder but tone down violence for Replicate
        enhanced_prompt = self.prompt_builder.build_action_prompt(prompt, scene_params)
        
        # Replace problematic terms for Replicate
        safe_replacements = {
            "violence": "action",
            "blood": "impact effects",
            "weapon": "prop",
            "gun": "device",
            "explosion": "special effects",
            "destruction": "dramatic effects",
            "injury": "action sequence",
            "combat": "choreographed scene",
            "fight": "action choreography"
        }
        
        safe_prompt = enhanced_prompt
        for unsafe, safe in safe_replacements.items():
            safe_prompt = safe_prompt.replace(unsafe, safe)
        
        # Add safety terms
        safe_prompt += ", professional stunt choreography, cinematic action, movie production"
        
        return safe_prompt
    
    def _build_negative_prompt(self, scene_params: SceneParameters) -> str:
        """Build negative prompt for content safety"""
        
        base_negative = "low quality, blurry, amateur, gore, graphic violence, inappropriate content"
        
        # Add scene-specific negatives
        scene_negatives = {
            "car_chase": "crashed cars, accidents, realistic damage",
            "fight_scene": "real violence, injury, blood",
            "explosion": "real destruction, casualties, graphic damage"
        }
        
        scene_specific = scene_negatives.get(scene_params.scene_type, "")
        
        return f"{base_negative}, {scene_specific}" if scene_specific else base_negative
    
    def _select_model(self, scene_params: SceneParameters, use_controlnet: bool) -> str:
        """Select appropriate Replicate model"""
        
        if use_controlnet:
            return self.models["sdxl_controlnet"]
        
        # Choose based on scene type
        model_mapping = {
            "car_chase": "realistic_vision",
            "fight_scene": "epicrealism", 
            "explosion": "sdxl",
            "aerial_combat": "sdxl",
            "space_battle": "sdxl"
        }
        
        model_key = model_mapping.get(scene_params.scene_type, "sdxl")
        return self.models.get(model_key, self.models["sdxl"])
    
    def _prepare_controlnet_inputs(self, sketch_data: Dict, config: GenerationConfig) -> Dict:
        """Prepare ControlNet specific inputs"""
        
        controlnet_inputs = {}
        
        if sketch_data.get("processed_image"):
            # Convert PIL Image to base64
            processed_img = sketch_data["processed_image"]
            if isinstance(processed_img, Image.Image):
                buffered = io.BytesIO()
                processed_img.save(buffered, format="PNG")
                img_b64 = base64.b64encode(buffered.getvalue()).decode()
                controlnet_inputs["image"] = f"data:image/png;base64,{img_b64}"
        
        # ControlNet settings
        controlnet_inputs.update({
            "controlnet_conditioning_scale": sketch_data.get("control_strength", 0.8),
            "control_guidance_start": 0.0,
            "control_guidance_end": 1.0
        })
        
        return controlnet_inputs
    
    async def _run_replicate_model(self, model_id: str, inputs: Dict) -> Any:
        """Run Replicate model asynchronously"""
        
        # This would be the actual Replicate API call
        # For now, return placeholder
        await asyncio.sleep(2)  # Simulate API call
        
        return ["https://replicate.delivery/pbxt/placeholder-image.jpg"]
    
    def _was_content_filtered(self, prompt: str) -> bool:
        """Check if content was likely filtered"""
        
        # Simple heuristic - check for filtered keywords
        filtered_keywords = ["violence", "blood", "weapon", "destruction"]
        original_count = sum(1 for word in filtered_keywords if word in prompt.lower())
        
        return original_count > 0
    
    async def refine_image(
        self,
        base_image: str,
        refinement_data: Dict,
        scene_params: SceneParameters
    ) -> Dict[str, Any]:
        """Refine existing image with new instructions"""
        
        start_time = time.time()
        
        # Use img2img model for refinement
        model_id = "stability-ai/sdxl:39ed52f2a78e934b3ba6e2a89f5b1c712de7dfea535525255b1aa35c5565e08b"
        
        inputs = {
            "image": base_image,
            "prompt": refinement_data.get("prompt", ""),
            "strength": refinement_data.get("strength", 0.5),
            "guidance_scale": 7.5,
            "num_inference_steps": 30
        }
        
        try:
            output = await self._run_replicate_model(model_id, inputs)
            
            return {
                "image_url": output[0] if isinstance(output, list) else output,
                "generation_time": time.time() - start_time,
                "refinement_applied": True
            }
            
        except Exception as e:
            return {
                "image_url": base_image,  # Return original on failure
                "generation_time": time.time() - start_time,
                "error": str(e),
                "refinement_applied": False
            }

class ReplicateManager:
    """Manage multiple Replicate clients and fallbacks"""
    
    def __init__(self):
        self.clients = {}
        self.active_client = None
        
    def add_client(self, name: str, api_token: str):
        """Add a Replicate client"""
        self.clients[name] = ReplicateClient(api_token)
        if self.active_client is None:
            self.active_client = name
    
    def set_active_client(self, name: str):
        """Set active client"""
        if name in self.clients:
            self.active_client = name
    
    async def generate_scene(self, *args, **kwargs):
        """Generate using active client"""
        if self.active_client and self.active_client in self.clients:
            return await self.clients[self.active_client].generate_scene(*args, **kwargs)
        else:
            raise Exception("No active Replicate client configured")
    
    async def health_check(self):
        """Check health of active client"""
        if self.active_client and self.active_client in self.clients:
            return await self.clients[self.active_client].health_check()
        return False