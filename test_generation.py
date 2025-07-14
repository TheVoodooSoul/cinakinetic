#!/usr/bin/env python3
"""
Test AI generation pipeline for Cinema Action Scene Generator
"""

import sys
import os
import asyncio
import json
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

async def test_generation():
    """Test the full generation pipeline"""
    
    print("🎬 Testing Action Scene Generation")
    print("=" * 40)
    
    try:
        from src.ai_pipeline.comfyui_client import ComfyUIClient
        from src.models.scene_models import SceneParameters, GenerationConfig, SceneType, ViolenceLevel, CameraAngle
        
        # Initialize client
        client = ComfyUIClient()
        
        # Test health check
        print("Testing ComfyUI connection...")
        health = await client.health_check()
        
        if not health:
            print("❌ ComfyUI not available - using development mode")
            return False
        
        print("✅ ComfyUI connection successful")
        
        # Create test scene parameters
        scene_params = SceneParameters(
            scene_type=SceneType.CAR_CHASE,
            violence_level=ViolenceLevel.R_RATED,
            camera_angle=CameraAngle.LOW_ANGLE,
            setting="city streets",
            lighting="dramatic"
        )
        
        # Create generation config
        gen_config = GenerationConfig(
            width=512,  # Small size for testing
            height=512,
            steps=20,   # Fewer steps for faster testing
            cfg_scale=7.5
        )
        
        # Test prompt
        prompt = "high-speed car chase through city streets"
        
        print(f"Generating scene: {prompt}")
        print("This may take 1-3 minutes on M2 Max...")
        
        # Generate scene
        result = await client.generate_scene(
            prompt=prompt,
            scene_params=scene_params,
            config=gen_config
        )
        
        print("✅ Generation completed!")
        print(f"Result: {json.dumps(result, indent=2)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Generation test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    print("🎬 Cinema Action Scene Generator - Generation Test")
    print("=" * 55)
    
    success = await test_generation()
    
    if success:
        print("\n🎉 Generation pipeline is working!")
        print("You can now run the full application:")
        print("python run_dev.py")
    else:
        print("\n💡 Generation not available - but UI will work in development mode")
        print("The application will use placeholder images for now.")
        print("You can still test the UI and workflow:")
        print("python run_dev.py")

if __name__ == "__main__":
    asyncio.run(main())