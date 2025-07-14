"""
Programmatic ComfyUI workflow templates for action scene generation
No manual node setup required - pure code generation
"""

from typing import Dict, Any, Optional, List
from enum import Enum
import json

class WorkflowType(str, Enum):
    IMAGE_GENERATION = "image_generation"
    SKETCH_TO_IMAGE = "sketch_to_image" 
    TEXT_TO_VIDEO = "text_to_video"
    IMAGE_TO_VIDEO = "image_to_video"
    VIDEO_TO_VIDEO = "video_to_video"
    BATCH_GENERATION = "batch_generation"
    CONTROLNET_MULTI = "controlnet_multi"

class ActionWorkflowTemplate:
    """Generate ComfyUI workflows programmatically"""
    
    def __init__(self, rtx6000_optimized: bool = True):
        self.rtx6000_optimized = rtx6000_optimized
        self.base_settings = self._get_base_settings()
    
    def _get_base_settings(self) -> Dict[str, Any]:
        """RTX 6000 Ada optimized settings"""
        return {
            "wan_settings": {
                "sampler": "dpmpp_2m_karras",
                "scheduler": "karras", 
                "steps": 25,
                "cfg_scale": 6.5,
                "clip_skip": 2
            },
            "video_settings": {
                "frame_count": 24,
                "fps": 24,
                "motion_strength": 0.8,
                "interpolation": "film"
            },
            "batch_settings": {
                "max_batch": 4,
                "parallel_controlnet": True
            }
        }
    
    def generate_workflow(
        self, 
        workflow_type: WorkflowType,
        params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate complete workflow JSON"""
        
        if workflow_type == WorkflowType.IMAGE_GENERATION:
            return self._create_image_workflow(params)
        elif workflow_type == WorkflowType.SKETCH_TO_IMAGE:
            return self._create_sketch_to_image_workflow(params)
        elif workflow_type == WorkflowType.TEXT_TO_VIDEO:
            return self._create_text_to_video_workflow(params)
        elif workflow_type == WorkflowType.IMAGE_TO_VIDEO:
            return self._create_image_to_video_workflow(params)
        elif workflow_type == WorkflowType.VIDEO_TO_VIDEO:
            return self._create_video_to_video_workflow(params)
        elif workflow_type == WorkflowType.BATCH_GENERATION:
            return self._create_batch_workflow(params)
        elif workflow_type == WorkflowType.CONTROLNET_MULTI:
            return self._create_multi_controlnet_workflow(params)
        
        raise ValueError(f"Unknown workflow type: {workflow_type}")
    
    def _create_image_workflow(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Standard high-quality image generation"""
        
        settings = self.base_settings["wan_settings"]
        
        return {
            "1": {
                "inputs": {
                    "text": params["prompt"],
                    "clip": ["4", 1]
                },
                "class_type": "CLIPTextEncode"
            },
            "2": {
                "inputs": {
                    "text": params.get("negative_prompt", "low quality, blurry"),
                    "clip": ["4", 1]
                },
                "class_type": "CLIPTextEncode"
            },
            "3": {
                "inputs": {
                    "seed": params.get("seed", 42),
                    "steps": settings["steps"],
                    "cfg": settings["cfg_scale"],
                    "sampler_name": settings["sampler"],
                    "scheduler": settings["scheduler"],
                    "denoise": 1,
                    "model": ["4", 0],
                    "positive": ["1", 0],
                    "negative": ["2", 0],
                    "latent_image": ["5", 0]
                },
                "class_type": "KSampler"
            },
            "4": {
                "inputs": {
                    "ckpt_name": params["model_name"]
                },
                "class_type": "CheckpointLoaderSimple"
            },
            "5": {
                "inputs": {
                    "width": params.get("width", 1024),
                    "height": params.get("height", 1024),
                    "batch_size": params.get("batch_size", 1)
                },
                "class_type": "EmptyLatentImage"
            },
            "8": {
                "inputs": {
                    "samples": ["3", 0],
                    "vae": ["4", 2]
                },
                "class_type": "VAEDecode"
            },
            "9": {
                "inputs": {
                    "filename_prefix": params.get("filename_prefix", "action_scene"),
                    "images": ["8", 0]
                },
                "class_type": "SaveImage"
            }
        }
    
    def _create_sketch_to_image_workflow(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Sketch/ControlNet to image workflow"""
        
        base_workflow = self._create_image_workflow(params)
        
        # Add ControlNet nodes
        controlnet_nodes = {
            "10": {
                "inputs": {
                    "control_net_name": f"control_{params['controlnet_type']}_sd15.pth"
                },
                "class_type": "ControlNetLoader"
            },
            "11": {
                "inputs": {
                    "image": params["control_image"]  # Base64 or file path
                },
                "class_type": "LoadImage"
            },
            "12": {
                "inputs": {
                    "image": ["11", 0]
                },
                "class_type": self._get_preprocessor_class(params['controlnet_type'])
            },
            "13": {
                "inputs": {
                    "conditioning": ["1", 0],
                    "control_net": ["10", 0], 
                    "image": ["12", 0],
                    "strength": params.get("controlnet_strength", 0.8)
                },
                "class_type": "ControlNetApply"
            }
        }
        
        # Merge and update connections
        base_workflow.update(controlnet_nodes)
        base_workflow["3"]["inputs"]["positive"] = ["13", 0]
        
        return base_workflow
    
    def _create_text_to_video_workflow(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Text-to-Video generation workflow"""
        
        video_settings = self.base_settings["video_settings"]
        
        return {
            "1": {
                "inputs": {
                    "text": params["prompt"],
                    "clip": ["4", 1]
                },
                "class_type": "CLIPTextEncode"
            },
            "2": {
                "inputs": {
                    "text": params.get("negative_prompt", "low quality, static"),
                    "clip": ["4", 1]
                },
                "class_type": "CLIPTextEncode"
            },
            "3": {
                "inputs": {
                    "ckpt_name": params["model_name"]
                },
                "class_type": "CheckpointLoaderSimple"
            },
            "4": {
                "inputs": {
                    "width": params.get("width", 768),
                    "height": params.get("height", 768),
                    "length": video_settings["frame_count"],
                    "batch_size": 1
                },
                "class_type": "EmptyLatentVideo"  # Assuming video node
            },
            "5": {
                "inputs": {
                    "model": ["3", 0],
                    "positive": ["1", 0],
                    "negative": ["2", 0],
                    "latent": ["4", 0],
                    "seed": params.get("seed", 42),
                    "steps": 20,
                    "cfg": 7.0,
                    "motion_strength": video_settings["motion_strength"]
                },
                "class_type": "VideoKSampler"  # Video-specific sampler
            },
            "6": {
                "inputs": {
                    "samples": ["5", 0],
                    "vae": ["3", 2]
                },
                "class_type": "VAEDecodeVideo"
            },
            "7": {
                "inputs": {
                    "images": ["6", 0],
                    "fps": video_settings["fps"],
                    "filename_prefix": params.get("filename_prefix", "action_video")
                },
                "class_type": "SaveVideo"
            }
        }
    
    def _create_image_to_video_workflow(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Image-to-Video (perfect for fight sequences)"""
        
        video_settings = self.base_settings["video_settings"]
        
        return {
            "1": {
                "inputs": {
                    "image": params["input_image"]  # Base64 or path
                },
                "class_type": "LoadImage"
            },
            "2": {
                "inputs": {
                    "text": params["motion_prompt"],
                    "clip": ["5", 1]
                },
                "class_type": "CLIPTextEncode"
            },
            "3": {
                "inputs": {
                    "text": params.get("negative_prompt", "static, no motion"),
                    "clip": ["5", 1]
                },
                "class_type": "CLIPTextEncode"
            },
            "4": {
                "inputs": {
                    "pixels": ["1", 0],
                    "vae": ["5", 2]
                },
                "class_type": "VAEEncode"
            },
            "5": {
                "inputs": {
                    "ckpt_name": params["model_name"]
                },
                "class_type": "CheckpointLoaderSimple"
            },
            "6": {
                "inputs": {
                    "samples": ["4", 0],
                    "frame_count": video_settings["frame_count"],
                    "motion_strength": params.get("motion_strength", 0.8)
                },
                "class_type": "ImageToVideoLatent"
            },
            "7": {
                "inputs": {
                    "model": ["5", 0],
                    "positive": ["2", 0],
                    "negative": ["3", 0],
                    "latent_video": ["6", 0],
                    "seed": params.get("seed", 42),
                    "steps": 15,  # Fewer steps for i2v
                    "cfg": 6.0
                },
                "class_type": "VideoKSampler"
            },
            "8": {
                "inputs": {
                    "samples": ["7", 0],
                    "vae": ["5", 2]
                },
                "class_type": "VAEDecodeVideo"
            },
            "9": {
                "inputs": {
                    "images": ["8", 0],
                    "fps": video_settings["fps"],
                    "filename_prefix": params.get("filename_prefix", "fight_sequence")
                },
                "class_type": "SaveVideo"
            }
        }
    
    def _create_video_to_video_workflow(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Video-to-Video transformation (style transfer, enhancement)"""
        
        return {
            "1": {
                "inputs": {
                    "video": params["input_video"]  # Video file path
                },
                "class_type": "LoadVideo"
            },
            "2": {
                "inputs": {
                    "text": params["style_prompt"],
                    "clip": ["6", 1]
                },
                "class_type": "CLIPTextEncode"
            },
            "3": {
                "inputs": {
                    "text": params.get("negative_prompt", "low quality"),
                    "clip": ["6", 1]
                },
                "class_type": "CLIPTextEncode"
            },
            "4": {
                "inputs": {
                    "images": ["1", 0],
                    "vae": ["6", 2]
                },
                "class_type": "VAEEncodeVideo"
            },
            "5": {
                "inputs": {
                    "model": ["6", 0],
                    "positive": ["2", 0],
                    "negative": ["3", 0],
                    "latent_video": ["4", 0],
                    "seed": params.get("seed", 42),
                    "steps": 12,
                    "cfg": 5.5,
                    "denoise": params.get("strength", 0.6)  # How much to change
                },
                "class_type": "VideoKSampler"
            },
            "6": {
                "inputs": {
                    "ckpt_name": params["model_name"]
                },
                "class_type": "CheckpointLoaderSimple"
            },
            "7": {
                "inputs": {
                    "samples": ["5", 0],
                    "vae": ["6", 2]
                },
                "class_type": "VAEDecodeVideo"
            },
            "8": {
                "inputs": {
                    "images": ["7", 0],
                    "fps": params.get("fps", 24),
                    "filename_prefix": params.get("filename_prefix", "v2v_action")
                },
                "class_type": "SaveVideo"
            }
        }
    
    def _create_batch_workflow(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Batch generation for multiple action scenes"""
        
        base = self._create_image_workflow(params)
        
        # Modify for batch processing
        base["5"]["inputs"]["batch_size"] = params.get("batch_size", 4)
        
        # Add batch prompts if provided
        if "batch_prompts" in params:
            for i, prompt in enumerate(params["batch_prompts"][:4]):
                base[f"1_{i}"] = {
                    "inputs": {
                        "text": prompt,
                        "clip": ["4", 1]
                    },
                    "class_type": "CLIPTextEncode"
                }
        
        return base
    
    def _create_multi_controlnet_workflow(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Multiple ControlNets for precise control"""
        
        base = self._create_image_workflow(params)
        
        controlnets = params.get("controlnets", [])
        
        for i, cn in enumerate(controlnets):
            cn_id = 10 + (i * 4)
            
            # ControlNet loader
            base[str(cn_id)] = {
                "inputs": {
                    "control_net_name": f"control_{cn['type']}_sd15.pth"
                },
                "class_type": "ControlNetLoader"
            }
            
            # Image loader
            base[str(cn_id + 1)] = {
                "inputs": {
                    "image": cn["image"]
                },
                "class_type": "LoadImage"
            }
            
            # Preprocessor
            base[str(cn_id + 2)] = {
                "inputs": {
                    "image": [str(cn_id + 1), 0]
                },
                "class_type": self._get_preprocessor_class(cn['type'])
            }
            
            # Apply ControlNet
            input_conditioning = ["1", 0] if i == 0 else [str(cn_id - 1), 0]
            base[str(cn_id + 3)] = {
                "inputs": {
                    "conditioning": input_conditioning,
                    "control_net": [str(cn_id), 0],
                    "image": [str(cn_id + 2), 0],
                    "strength": cn.get("strength", 0.8)
                },
                "class_type": "ControlNetApply"
            }
        
        # Update final connection
        final_cn = len(controlnets) * 4 + 9
        base["3"]["inputs"]["positive"] = [str(final_cn), 0]
        
        return base
    
    def _get_preprocessor_class(self, controlnet_type: str) -> str:
        """Get preprocessor class name for ControlNet type"""
        
        preprocessors = {
            "openpose": "OpenposePreprocessor",
            "canny": "CannyEdgePreprocessor", 
            "depth": "MiDaS-DepthMapPreprocessor",
            "lineart": "LineArtPreprocessor",
            "normal": "BAE-NormalMapPreprocessor",
            "seg": "SemSegPreprocessor"
        }
        
        return preprocessors.get(controlnet_type, "OpenposePreprocessor")

# Pre-built templates for common action scenes
ACTION_SCENE_TEMPLATES = {
    "fight_sequence_hq": {
        "type": WorkflowType.IMAGE_GENERATION,
        "params": {
            "prompt": "epic martial arts fight scene, two fighters, dynamic poses, cinematic lighting, professional choreography, 8k quality",
            "negative_prompt": "low quality, static poses, amateur, blurry",
            "width": 1024,
            "height": 1024,
            "filename_prefix": "fight_hq"
        }
    },
    
    "sketch_to_fight": {
        "type": WorkflowType.SKETCH_TO_IMAGE,
        "params": {
            "prompt": "professional fight choreography based on sketch, cinematic quality",
            "controlnet_type": "openpose",
            "controlnet_strength": 0.8,
            "width": 1024,
            "height": 1024
        }
    },
    
    "fight_motion_video": {
        "type": WorkflowType.IMAGE_TO_VIDEO,
        "params": {
            "motion_prompt": "smooth fighting motion, punch sequence, dynamic movement",
            "motion_strength": 0.8,
            "filename_prefix": "fight_motion"
        }
    },
    
    "car_chase_sequence": {
        "type": WorkflowType.TEXT_TO_VIDEO,
        "params": {
            "prompt": "high-speed car chase, vehicles racing through city streets, cinematic action",
            "width": 1024,
            "height": 576,  # Cinematic aspect
            "filename_prefix": "car_chase"
        }
    },
    
    "explosion_batch": {
        "type": WorkflowType.BATCH_GENERATION,
        "params": {
            "batch_prompts": [
                "massive explosion, debris flying, dramatic lighting",
                "building demolition, smoke and fire, cinematic angle",
                "car explosion, action movie style, high detail",
                "industrial explosion, sparks and flames, wide shot"
            ],
            "batch_size": 4,
            "width": 768,
            "height": 768
        }
    }
}