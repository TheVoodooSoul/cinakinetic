"""
RunPod On-Demand Pod Manager
Automatically start/stop pods to minimize costs
"""

import requests
import time
import os
from typing import Optional, Dict

class RunPodManager:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.runpod.ai/graphql"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    
    def start_pod(self, template_id: str, gpu_type: str = "NVIDIA RTX 6000 Ada Generation") -> Optional[Dict]:
        """Start a new pod with specified template"""
        query = """
        mutation {
            podRentInterruptable(input: {
                bidPerGpu: 2.00,
                cloudType: COMMUNITY,
                gpuCount: 1,
                volumeInGb: 50,
                containerDiskInGb: 50,
                minVcpuCount: 8,
                minMemoryInGb: 32,
                gpuTypeId: "%s",
                templateId: "%s",
                name: "cinakinetic-auto"
            }) {
                id
                desiredStatus
                imageName
                env
                machineId
                machine {
                    podHostId
                }
            }
        }
        """ % (gpu_type, template_id)
        
        response = requests.post(
            self.base_url,
            json={"query": query},
            headers=self.headers
        )
        
        if response.status_code == 200:
            return response.json()
        return None
    
    def get_pod_status(self, pod_id: str) -> Optional[Dict]:
        """Get current pod status and endpoint"""
        query = """
        query {
            pod(input: {podId: "%s"}) {
                id
                name
                runtime {
                    uptimeInSeconds
                    ports {
                        ip
                        isIpPublic
                        privatePort
                        publicPort
                        type
                    }
                }
                machine {
                    podHostId
                }
                desiredStatus
                lastStatusChange
            }
        }
        """ % pod_id
        
        response = requests.post(
            self.base_url,
            json={"query": query},
            headers=self.headers
        )
        
        if response.status_code == 200:
            return response.json()
        return None
    
    def stop_pod(self, pod_id: str) -> bool:
        """Stop a running pod"""
        query = """
        mutation {
            podStop(input: {podId: "%s"}) {
                id
                desiredStatus
            }
        }
        """ % pod_id
        
        response = requests.post(
            self.base_url,
            json={"query": query},
            headers=self.headers
        )
        
        return response.status_code == 200
    
    def get_endpoint_url(self, pod_id: str) -> Optional[str]:
        """Get the HTTP endpoint URL for a pod"""
        pod_data = self.get_pod_status(pod_id)
        
        if not pod_data or 'data' not in pod_data:
            return None
        
        pod = pod_data['data']['pod']
        if not pod or not pod.get('runtime'):
            return None
        
        ports = pod['runtime'].get('ports', [])
        for port in ports:
            if port.get('privatePort') == 8188:  # ComfyUI default port
                if port.get('isIpPublic'):
                    ip = port.get('ip')
                    public_port = port.get('publicPort')
                    return f"https://{ip}:{public_port}"
        
        return None
    
    def wait_for_pod_ready(self, pod_id: str, timeout: int = 300) -> Optional[str]:
        """Wait for pod to be ready and return endpoint URL"""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            endpoint = self.get_endpoint_url(pod_id)
            if endpoint:
                # Test if ComfyUI is responding
                try:
                    response = requests.get(f"{endpoint}/system_stats", timeout=5)
                    if response.status_code == 200:
                        return endpoint
                except:
                    pass
            
            time.sleep(10)  # Check every 10 seconds
        
        return None

# Usage example
def auto_manage_pod():
    """Example of automatic pod management"""
    manager = RunPodManager(os.getenv("RUNPOD_API_KEY"))
    
    # Start pod when user makes request
    print("🚀 Starting pod for generation...")
    pod_result = manager.start_pod("your_template_id")
    
    if pod_result and 'data' in pod_result:
        pod_id = pod_result['data']['podRentInterruptable']['id']
        print(f"✅ Pod started: {pod_id}")
        
        # Wait for pod to be ready
        print("⏳ Waiting for pod to be ready...")
        endpoint = manager.wait_for_pod_ready(pod_id)
        
        if endpoint:
            print(f"🎉 Pod ready! Endpoint: {endpoint}")
            
            # Use endpoint for generation
            # ... your generation code here ...
            
            # Stop pod after generation (or after timeout)
            print("🛑 Stopping pod...")
            manager.stop_pod(pod_id)
            print("✅ Pod stopped")
        else:
            print("❌ Pod failed to start properly")
    else:
        print("❌ Failed to start pod")

if __name__ == "__main__":
    auto_manage_pod()