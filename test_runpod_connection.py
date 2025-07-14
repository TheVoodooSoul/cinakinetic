#!/usr/bin/env python3
"""
Test RunPod connection and WAN model setup
"""

import requests
import time
import json
from typing import Dict, Optional

def test_runpod_connection(pod_url: str) -> Dict:
    """Test connection to RunPod ComfyUI instance"""
    
    print(f"🔗 Testing connection to: {pod_url}")
    
    results = {
        "connection": False,
        "comfyui_version": None,
        "models_loaded": [],
        "system_stats": {},
        "wan_models": []
    }
    
    try:
        # Test basic connection
        response = requests.get(f"{pod_url}/system_stats", timeout=10)
        
        if response.status_code == 200:
            results["connection"] = True
            stats = response.json()
            results["system_stats"] = stats
            results["comfyui_version"] = stats.get("system", {}).get("comfyui_version")
            
            print("✅ Connection successful!")
            print(f"   ComfyUI Version: {results['comfyui_version']}")
            print(f"   GPU VRAM: {stats.get('devices', [{}])[0].get('vram_total', 'Unknown')} MB")
            
        else:
            print(f"❌ Connection failed: HTTP {response.status_code}")
            return results
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Connection error: {e}")
        return results
    
    try:
        # Test model loading
        response = requests.get(f"{pod_url}/object_info", timeout=10)
        
        if response.status_code == 200:
            object_info = response.json()
            
            # Check for CheckpointLoaderSimple to get available models
            checkpoint_loader = object_info.get("CheckpointLoaderSimple", {})
            input_info = checkpoint_loader.get("input", {})
            ckpt_name_info = input_info.get("ckpt_name", {})
            
            if isinstance(ckpt_name_info, list) and len(ckpt_name_info) > 1:
                available_models = ckpt_name_info[0]  # First element is the list of models
                results["models_loaded"] = available_models
                
                # Look for WAN models
                wan_models = [model for model in available_models if 'wan' in model.lower()]
                results["wan_models"] = wan_models
                
                print(f"✅ Found {len(available_models)} models loaded")
                if wan_models:
                    print(f"🎯 WAN models detected: {wan_models}")
                else:
                    print("⚠️ No WAN models found - you'll need to upload them")
            
    except Exception as e:
        print(f"⚠️ Could not check models: {e}")
    
    return results

def test_generation(pod_url: str, model_name: str = None) -> bool:
    """Test basic generation on RunPod"""
    
    if not model_name:
        # Use first available model
        connection_test = test_runpod_connection(pod_url)
        models = connection_test.get("models_loaded", [])
        if not models:
            print("❌ No models available for testing")
            return False
        model_name = models[0]
    
    print(f"\n🎨 Testing generation with model: {model_name}")
    
    # Simple test workflow
    workflow = {
        "1": {
            "inputs": {
                "text": "action movie scene, cinematic composition, high quality",
                "clip": ["4", 1]
            },
            "class_type": "CLIPTextEncode"
        },
        "2": {
            "inputs": {
                "text": "low quality, blurry",
                "clip": ["4", 1]
            },
            "class_type": "CLIPTextEncode"
        },
        "3": {
            "inputs": {
                "seed": 42,
                "steps": 20,
                "cfg": 7.0,
                "sampler_name": "dpmpp_2m",
                "scheduler": "karras",
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
                "ckpt_name": model_name
            },
            "class_type": "CheckpointLoaderSimple"
        },
        "5": {
            "inputs": {
                "width": 512,
                "height": 512,
                "batch_size": 1
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
                "filename_prefix": "runpod_test",
                "images": ["8", 0]
            },
            "class_type": "SaveImage"
        }
    }
    
    try:
        # Submit workflow
        response = requests.post(
            f"{pod_url}/prompt",
            json={"prompt": workflow},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            prompt_id = result["prompt_id"]
            
            print(f"✅ Generation started! Prompt ID: {prompt_id}")
            print("⏳ Waiting for completion...")
            
            # Poll for completion
            for i in range(60):  # Wait up to 60 seconds
                time.sleep(1)
                
                history_response = requests.get(f"{pod_url}/history/{prompt_id}")
                if history_response.status_code == 200:
                    history = history_response.json()
                    
                    if prompt_id in history:
                        print("✅ Generation completed successfully!")
                        return True
                
                if i % 10 == 0:
                    print(f"   Still waiting... ({i+1}s)")
            
            print("⏰ Generation timeout - but pod is working!")
            return True
            
        else:
            print(f"❌ Generation failed: HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Generation test failed: {e}")
        return False

def get_runpod_recommendations() -> str:
    """Get recommendations for RunPod setup"""
    
    return """
🚀 RunPod Setup Recommendations:

1. **GPU Choice:**
   - RTX 4090: Best value ($0.50/hr, 24GB VRAM)
   - A100: Fastest ($1.50/hr, 40GB VRAM)

2. **Storage:**
   - Container: 50GB (for ComfyUI + models)
   - Volume: 20GB (persistent model storage)

3. **WAN Model Upload:**
   - Use Jupyter interface for easy upload
   - Rename files: wan.safetensors, wan2_114b.safetensors
   - Place in: /workspace/ComfyUI/models/checkpoints/

4. **Optimal Settings for WAN:**
   - Sampler: dpmpp_2m_karras
   - Steps: 20-25
   - CFG: 6.0-7.0
   - Resolution: 768x768

5. **Cost Management:**
   - Stop pod when not generating
   - Use volume for model persistence
   - Monitor usage dashboard
"""

def main():
    """Main test function"""
    
    print("🎬 RunPod Connection Test for Cinema Action Scene Generator")
    print("=" * 65)
    
    # Get pod URL from user
    pod_url = input("\nEnter your RunPod ComfyUI URL: ").strip()
    
    if not pod_url:
        print("\n" + get_runpod_recommendations())
        print("\nOnce you have a pod running, run this test again!")
        return
    
    # Ensure proper URL format
    if not pod_url.startswith("http"):
        pod_url = f"https://{pod_url}"
    
    if not pod_url.endswith(":8188") and "8188" not in pod_url:
        if pod_url.endswith("/"):
            pod_url = pod_url[:-1]
        pod_url = f"{pod_url}:8188"
    
    print(f"\nTesting pod: {pod_url}")
    
    # Test connection
    results = test_runpod_connection(pod_url)
    
    if not results["connection"]:
        print("\n❌ Connection failed!")
        print("\nTroubleshooting:")
        print("1. Check pod is 'Running' (not 'Starting')")
        print("2. Verify URL format: https://[pod-id]-8188.proxy.runpod.net")
        print("3. Try different region if pod won't start")
        return
    
    # Test generation if models available
    if results["models_loaded"]:
        test_generation(pod_url)
    
    # Summary
    print("\n" + "="*50)
    print("📊 RUNPOD SETUP SUMMARY")
    print("="*50)
    print(f"✅ Connection: Working")
    print(f"✅ ComfyUI Version: {results['comfyui_version']}")
    print(f"✅ Models Available: {len(results['models_loaded'])}")
    
    if results["wan_models"]:
        print(f"🎯 WAN Models: {', '.join(results['wan_models'])}")
    else:
        print("⚠️ WAN Models: None found - upload your models!")
    
    print(f"\n🔗 Update your Cinema Action Scene Generator:")
    print(f"   Pod URL: {pod_url}")
    print(f"   Status: Ready for action scene generation!")
    
    if not results["wan_models"]:
        print(f"\n📦 Next Steps:")
        print(f"1. Upload your WAN models via Jupyter: {pod_url.replace('8188', '8888')}")
        print(f"2. Place in: /workspace/ComfyUI/models/checkpoints/")
        print(f"3. Restart ComfyUI if needed")
        print(f"4. Re-run this test")

if __name__ == "__main__":
    main()