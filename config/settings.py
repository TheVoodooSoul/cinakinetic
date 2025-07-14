from pydantic_settings import BaseSettings
from typing import List, Optional

class Settings(BaseSettings):
    # API Settings
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    debug: bool = True
    
    # ComfyUI Settings
    comfyui_url: str = "http://localhost:8188"
    comfyui_timeout: int = 300
    
    # Database Settings
    data_directory: str = "data"
    
    # AI Model Settings
    default_model: str = "sd_xl"
    max_image_size: int = 2048
    default_steps: int = 30
    default_cfg_scale: float = 7.5
    
    # Content Safety Settings
    enable_safety_filter: bool = True
    max_violence_level: str = "r_rated"  # pg13, r_rated, cinematic
    
    # Supported scene types
    supported_scene_types: List[str] = [
        "car_chase", "fight_scene", "explosion", "shootout",
        "aerial_combat", "space_battle", "boxing_match", "martial_arts",
        "chase_foot", "vehicle_crash"
    ]
    
    # Available models for different scene types
    scene_model_mapping: dict = {
        "car_chase": "realisticVisionV60_v60B1.safetensors",
        "fight_scene": "epicrealismXL_v10.safetensors",
        "explosion": "juggernautXL_v8Rundiffusion.safetensors",
        "aerial_combat": "dreamshaper_8.safetensors",
        "space_battle": "scientificDiffusion_v10.safetensors",
        "boxing_match": "epicrealismXL_v10.safetensors",
        "martial_arts": "epicrealismXL_v10.safetensors"
    }
    
    class Config:
        env_file = ".env"

# Global settings instance
settings = Settings()