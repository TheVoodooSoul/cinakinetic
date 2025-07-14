# RTX 6000 Ada Optimal Settings for WAN Models

RTX_6000_SETTINGS = {
    "wan_models": {
        "sampler": "dpmpp_2m_karras",
        "steps": 25,  # Can afford more steps with 48GB VRAM
        "cfg_scale": 6.5,
        "clip_skip": 2,
        "scheduler": "karras"
    },
    
    "resolutions": {
        "fast": "768x768",      # 8-12 seconds
        "quality": "1024x1024", # 15-25 seconds  
        "premium": "1536x1536", # 30-45 seconds (possible with 48GB!)
        "ultra": "2048x1024"    # Cinematic aspect ratio
    },
    
    "batch_settings": {
        "max_batch_size": 4,    # Can do multiple images at once
        "sequence_length": 16,  # Longer fight sequences
        "parallel_processing": True
    },
    
    "video_generation": {
        "t2v_enabled": True,    # Text-to-video
        "u2v_enabled": True,    # Image-to-video (perfect for fight sequences!)
        "frame_count": 24,      # 1 second at 24fps
        "motion_strength": 0.8,
        "vace_acceleration": True
    },
    
    "advanced_features": {
        "controlnet_batch": True,
        "multi_controlnet": True,  # Multiple controls at once
        "lora_stacking": True,     # Multiple LoRAs
        "inpainting_resolution": "1024x1024"
    }
}

# Expected Performance on RTX 6000 Ada
PERFORMANCE_ESTIMATES = {
    "768x768": "5-10 seconds",
    "1024x1024": "10-18 seconds", 
    "1536x1536": "20-35 seconds",
    "video_24_frames": "45-90 seconds",
    "batch_4x768": "15-25 seconds total"
}