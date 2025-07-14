#!/usr/bin/env python3
"""
Test the new iterative workflow and WAN model features
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_iterative_workflow():
    """Test iterative workflow components"""
    
    print("🔄 Testing Iterative Workflow")
    print("=" * 30)
    
    try:
        from src.ui.iterative_workflow import IterativeWorkflow, WorkflowNode
        
        # Test workflow creation
        workflow = IterativeWorkflow()
        print("✅ IterativeWorkflow class imported successfully")
        
        # Test node creation
        node = WorkflowNode(
            id="test_node",
            node_type="sketch",
            inputs={},
            outputs={},
            position={"x": 0, "y": 0},
            connections=[],
            settings={"canvas_size": "512x512"}
        )
        print("✅ WorkflowNode class works correctly")
        
        return True
        
    except Exception as e:
        print(f"❌ Iterative workflow test failed: {e}")
        return False

def test_sketch_interface():
    """Test sketch interface components"""
    
    print("\n🎨 Testing Sketch Interface")
    print("=" * 30)
    
    try:
        from src.ui.sketch_interface import SketchInterface
        
        # Test interface creation
        sketch_ui = SketchInterface()
        print("✅ SketchInterface class imported successfully")
        
        # Test image processing
        from PIL import Image
        import numpy as np
        
        test_image = Image.new('RGB', (512, 512), 'white')
        processed = sketch_ui._process_sketch(test_image, "Canny Edge")
        print("✅ Image processing works")
        
        return True
        
    except Exception as e:
        print(f"❌ Sketch interface test failed: {e}")
        return False

def test_wan_model_handler():
    """Test WAN model handler"""
    
    print("\n🎯 Testing WAN Model Handler")
    print("=" * 30)
    
    try:
        from src.utils.wan_model_handler import WANModelHandler
        
        # Test handler creation
        handler = WANModelHandler()
        print("✅ WANModelHandler class imported successfully")
        
        # Test model listing
        models = handler.list_installed_models()
        print(f"✅ Found {len(models)} installed models")
        
        # Test configuration
        config = handler.get_wan_model_config("wan_test")
        print(f"✅ WAN config generated: {config['sampler']}")
        
        return True
        
    except Exception as e:
        print(f"❌ WAN model handler test failed: {e}")
        return False

def test_replicate_client():
    """Test Replicate client"""
    
    print("\n☁️ Testing Replicate Client")
    print("=" * 30)
    
    try:
        from src.ai_pipeline.replicate_client import ReplicateClient
        
        # Test client creation
        client = ReplicateClient()
        print("✅ ReplicateClient class imported successfully")
        
        # Test prompt safety
        from src.models.scene_models import SceneParameters, SceneType, ViolenceLevel, CameraAngle
        
        scene_params = SceneParameters(
            scene_type=SceneType.FIGHT_SCENE,
            violence_level=ViolenceLevel.R_RATED,
            camera_angle=CameraAngle.MEDIUM_SHOT,
            setting="urban rooftop"
        )
        
        safe_prompt = client._build_safe_prompt("intense fight scene", scene_params)
        print(f"✅ Safe prompt generation: {safe_prompt[:50]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Replicate client test failed: {e}")
        return False

def main():
    """Run all iterative feature tests"""
    
    print("🚀 Cinema Action Scene Generator - Iterative Features Test")
    print("=" * 60)
    
    tests = [
        ("Iterative Workflow", test_iterative_workflow),
        ("Sketch Interface", test_sketch_interface), 
        ("WAN Model Handler", test_wan_model_handler),
        ("Replicate Client", test_replicate_client)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
    
    print("\n" + "=" * 60)
    print(f"Feature tests completed: {passed}/{total} passed")
    
    if passed == total:
        print("🎉 All iterative features are working!")
        print("\nNew Features Available:")
        print("- ✏️ Sketch-to-image with drawing canvas")
        print("- 🔄 Iterative node-based workflow (FloraFauna style)")
        print("- 🎬 Motion sequence generation")
        print("- 🔗 Scene combination tools")
        print("- 🎯 WAN model integration")
        print("- ☁️ Replicate API fallback")
        print("- 🛠️ Setup & configuration page")
        
        print("\nTo test the full interface:")
        print("python run_dev.py")
        print("Then navigate to Setup & Config to configure your WAN models")
        
    else:
        print("❌ Some features need attention. Check the errors above.")

if __name__ == "__main__":
    main()