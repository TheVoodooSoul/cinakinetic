#!/usr/bin/env python3
"""
Test ComfyUI connection for Cinema Action Scene Generator
"""

import requests
import time
import json

def test_comfyui_connection(max_attempts=10):
    """Test connection to ComfyUI server"""
    
    print("🎬 Testing ComfyUI Connection...")
    print("=" * 40)
    
    for attempt in range(max_attempts):
        try:
            print(f"Attempt {attempt + 1}/{max_attempts}...")
            
            response = requests.get("http://localhost:8188/system_stats", timeout=10)
            
            if response.status_code == 200:
                print("✅ ComfyUI is running successfully!")
                
                # Parse response
                stats = response.json() if response.headers.get('content-type') == 'application/json' else response.text
                print(f"Response: {str(stats)[:200]}...")
                
                # Test object info endpoint
                try:
                    obj_response = requests.get("http://localhost:8188/object_info", timeout=5)
                    if obj_response.status_code == 200:
                        print("✅ Object info endpoint working")
                        obj_info = obj_response.json()
                        print(f"Available nodes: {len(obj_info)} types")
                    else:
                        print("⚠️ Object info endpoint not ready")
                except:
                    print("⚠️ Object info endpoint not accessible")
                
                return True
                
            else:
                print(f"❌ HTTP {response.status_code}")
                
        except requests.exceptions.ConnectionError:
            print("🔄 ComfyUI still starting up...")
        except requests.exceptions.Timeout:
            print("⏰ Request timeout")
        except Exception as e:
            print(f"❌ Error: {e}")
        
        if attempt < max_attempts - 1:
            time.sleep(5)
    
    print("❌ ComfyUI connection failed after all attempts")
    return False

def show_runpod_option():
    """Show RunPod setup information"""
    print("\n🚀 RunPod Alternative Setup")
    print("=" * 40)
    print("""
If local ComfyUI is too slow or you prefer cloud GPU:

1. Go to https://runpod.io
2. Create account and add payment method
3. Launch a ComfyUI template pod:
   - Search for "ComfyUI" in community templates
   - Choose RTX 4090 or A100 for best performance
   - Select "ComfyUI" template (pre-installed)

4. Once pod is running:
   - Note the pod's external IP and port
   - Access ComfyUI at: http://[POD_IP]:[PORT]
   - Update cinema_action_scene_generator config:
   
     # In config/settings.py
     comfyui_url = "http://[POD_IP]:[PORT]"

5. Advantages:
   - Much faster generation (30s vs 5min locally)
   - More VRAM for larger models
   - Pay only when running
   - Pre-installed models

6. Costs:
   - RTX 4090: ~$0.50/hour
   - A100: ~$1.50/hour
   - Stop pod when not in use
""")

def main():
    print("🎬 Cinema Action Scene Generator - ComfyUI Test")
    print("=" * 50)
    
    # Test local ComfyUI
    local_success = test_comfyui_connection()
    
    if not local_success:
        print("\n💡 Local ComfyUI Issues")
        print("=" * 30)
        print("""
Local setup troubleshooting:
1. Check if ComfyUI is still starting (can take 2-5 minutes)
2. Verify port 8188 is not blocked
3. Check ComfyUI logs for errors
4. Try restarting ComfyUI:
   cd /Users/watson/Workspace/ComfyUI
   source .venv/bin/activate
   python main.py --listen --port 8188
""")
        
        # Show RunPod option
        show_runpod_option()
    
    else:
        print("\n🎉 Local ComfyUI is working!")
        print("You can now run the Cinema Action Scene Generator:")
        print("cd /Users/watson/Workspace/cinema_action_scene_generator")
        print("python run_dev.py")

if __name__ == "__main__":
    main()