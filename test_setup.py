#!/usr/bin/env python3
"""
Simple test to verify the Cinema Action Scene Generator setup
"""

import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_imports():
    """Test that all modules can be imported"""
    print("Testing imports...")
    
    try:
        from src.models.scene_models import SceneType, Storyboard, GenerationRequest
        print("✅ Scene models imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import scene models: {e}")
        return False
    
    try:
        from src.utils.prompt_builder import ActionPromptBuilder
        print("✅ Prompt builder imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import prompt builder: {e}")
        return False
    
    try:
        from src.database.storyboard_db import StoryboardDatabase
        print("✅ Database module imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import database: {e}")
        return False
    
    try:
        from config.settings import settings
        print("✅ Settings imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import settings: {e}")
        return False
    
    return True

def test_prompt_builder():
    """Test the prompt builder functionality"""
    print("\nTesting prompt builder...")
    
    try:
        from src.utils.prompt_builder import ActionPromptBuilder
        from src.models.scene_models import SceneParameters, SceneType, ViolenceLevel, CameraAngle
        
        builder = ActionPromptBuilder()
        
        # Create test scene parameters
        scene_params = SceneParameters(
            scene_type=SceneType.CAR_CHASE,
            violence_level=ViolenceLevel.R_RATED,
            camera_angle=CameraAngle.LOW_ANGLE,
            setting="busy city streets",
            lighting="dramatic",
            motion_blur=True
        )
        
        # Build prompt
        base_prompt = "high-speed car chase through downtown"
        enhanced_prompt = builder.build_action_prompt(base_prompt, scene_params)
        
        print(f"✅ Enhanced prompt: {enhanced_prompt[:100]}...")
        
        # Test scene suggestions
        suggestions = builder.get_scene_suggestions(SceneType.FIGHT_SCENE)
        print(f"✅ Fight scene suggestions: {len(suggestions['keywords'])} keywords")
        
        return True
        
    except Exception as e:
        print(f"❌ Prompt builder test failed: {e}")
        return False

def test_database():
    """Test database functionality"""
    print("\nTesting database...")
    
    try:
        from src.database.storyboard_db import StoryboardDatabase
        from src.models.scene_models import Storyboard
        import asyncio
        
        async def test_db():
            db = StoryboardDatabase(data_dir="test_data")
            
            # Test health check
            health = await db.health_check()
            print(f"✅ Database health check: {health}")
            
            # Create test storyboard
            test_storyboard = Storyboard(
                id="test-123",
                title="Test Action Sequence",
                description="A test storyboard for validation"
            )
            
            # Save and retrieve
            saved = await db.save_storyboard(test_storyboard)
            retrieved = await db.get_storyboard("test-123")
            
            if retrieved and retrieved.title == "Test Action Sequence":
                print("✅ Database save/retrieve works")
                
                # Clean up
                await db.delete_storyboard("test-123")
                return True
            else:
                print("❌ Database save/retrieve failed")
                return False
        
        return asyncio.run(test_db())
        
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False

def test_models():
    """Test data models"""
    print("\nTesting data models...")
    
    try:
        from src.models.scene_models import (
            SceneParameters, GenerationConfig, SceneNode, 
            SceneType, ViolenceLevel, CameraAngle
        )
        
        # Test scene parameters
        scene_params = SceneParameters(
            scene_type=SceneType.EXPLOSION,
            violence_level=ViolenceLevel.CINEMATIC,
            camera_angle=CameraAngle.WIDE_SHOT,
            setting="industrial facility"
        )
        print("✅ Scene parameters created successfully")
        
        # Test generation config
        gen_config = GenerationConfig(
            width=1024,
            height=1024,
            steps=30,
            cfg_scale=7.5
        )
        print("✅ Generation config created successfully")
        
        # Test scene node
        scene_node = SceneNode(
            id="node-1",
            scene_params=scene_params,
            generation_config=gen_config,
            prompt="Massive explosion at industrial facility"
        )
        print("✅ Scene node created successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Models test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🎬 Cinema Action Scene Generator - Setup Test")
    print("=" * 50)
    
    tests = [
        ("Import Test", test_imports),
        ("Models Test", test_models),
        ("Prompt Builder Test", test_prompt_builder),
        ("Database Test", test_database)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        print("-" * 20)
        
        if test_func():
            passed += 1
        
    print("\n" + "=" * 50)
    print(f"Tests completed: {passed}/{total} passed")
    
    if passed == total:
        print("🎉 All tests passed! The setup is working correctly.")
        print("\nNext steps:")
        print("1. Install ComfyUI (optional for development)")
        print("2. Run: python run_dev.py")
        print("3. Open http://localhost:8501 for the UI")
        print("4. Open http://localhost:8000/docs for API docs")
    else:
        print("❌ Some tests failed. Please check the errors above.")
    
    # Clean up test data
    import shutil
    if os.path.exists("test_data"):
        shutil.rmtree("test_data")

if __name__ == "__main__":
    main()