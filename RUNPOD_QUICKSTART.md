# 🚀 RunPod Quick Start for Action Scene Generation

## Step-by-Step Setup (5 minutes)

### 1. Create RunPod Account
- Go to https://runpod.io
- Sign up with email
- Add payment method (credit card)
- **Get API key**: https://runpod.io/console/user/settings

### 2. Launch ComfyUI Pod
**Recommended Template:**
```
Template: "ComfyUI" (Official RunPod template)
GPU: RTX 4090 (24GB) - $0.50/hour
Container Disk: 50GB
Volume: 20GB (optional, for persistent storage)
Region: US-East or US-West
```

**Click Deploy** → Wait 2-3 minutes for startup

### 3. Upload Your WAN Models
Once pod is running, you'll get:
- **ComfyUI URL**: `https://[pod-id]-8188.proxy.runpod.net`
- **Jupyter URL**: `https://[pod-id]-8888.proxy.runpod.net`

**Upload via Jupyter:**
1. Open Jupyter URL
2. Navigate to: `/workspace/ComfyUI/models/checkpoints/`
3. Upload your files:
   - `wan.safetensors` 
   - `wan2.114b` (rename to `wan2_114b.safetensors`)

### 4. Connect to Your Action Scene Generator
1. Run your local app: `python run_dev.py`
2. Go to **Setup & Config** tab
3. Click **"Connect Existing Pod"**
4. Enter your ComfyUI URL: `https://[pod-id]-8188.proxy.runpod.net`
5. Click **"Test Connection"** → Should show ✅ and detect your WAN models

### 5. Start Creating!
- Go to **Iterative Workflow** tab
- Add **Sketch Node** → Draw your fight scene
- Connect **Edit Node** → Refine iteratively  
- Add **Motion Node** → Generate fight sequences
- Use **Combine Node** → Stitch scenes together

## Expected Performance on RTX 4090

```
512x512:  10-15 seconds
768x768:  15-25 seconds  
1024x1024: 25-40 seconds

vs Local M2 Max: 1-3 minutes
= 10x speed improvement!
```

## Cost Management

**Smart Usage:**
- **Stop pod when not generating** (saves $$)
- Use **"On-Demand"** pricing
- Monitor in RunPod dashboard

**Daily Costs:**
- Light use (1 hour): ~$0.50
- Heavy use (4 hours): ~$2.00
- Full day: ~$12.00

## WAN Model Optimization

Your WAN models work best with:
```yaml
Sampler: dpmpp_2m_karras
Steps: 20-25 (sweet spot)
CFG Scale: 6.0-7.0
CLIP Skip: 2
Resolution: 768x768 recommended
```

## Troubleshooting

**Pod won't start:**
- Try different region
- Check RunPod status page
- Contact support chat

**Can't connect:**
- Verify pod status is "Running" (not "Starting")
- Check URL format: `https://[pod-id]-8188.proxy.runpod.net`
- Try HTTPS (not HTTP)

**Models not loading:**
- Check file upload completed
- Verify file names (no spaces)
- Restart ComfyUI: Jupyter → Terminal → `supervisorctl restart comfyui`

## Quick Test

Run this to verify everything works:
```bash
python test_runpod_connection.py
```

Enter your pod URL when prompted.

## Next Steps

1. **Test basic generation** first
2. **Upload your WAN models**
3. **Try the iterative workflow**:
   - Sketch → Edit → Motion → Combine
4. **Create epic action sequences**! 🥊💥

Your setup should give you professional-quality action scene generation with 10x faster iteration than local generation. Perfect for rapid prototyping and production work!

**Questions?** The test scripts will help diagnose any issues.