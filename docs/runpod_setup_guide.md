# RunPod Setup Guide for Action Scene Generation

## Quick Setup Steps

### 1. Create RunPod Account
1. Go to https://runpod.io
2. Sign up and verify email
3. Add payment method (credit card or PayPal)
4. Get API key from https://runpod.io/console/user/settings

### 2. Launch ComfyUI Pod

**Recommended Template:**
- Search "ComfyUI" in Community Templates
- Choose: **"ComfyUI"** by RunPod (official template)
- GPU: **RTX 4090** (best value at ~$0.50/hr)
- Storage: **50GB** (enough for WAN models + generated images)

**Pod Configuration:**
```
Template: ComfyUI (Official)
GPU: RTX 4090 (24GB VRAM)
Container Disk: 50GB
Volume: 20GB (for persistent models)
```

### 3. Access Your Pod

Once running, you'll get:
- **ComfyUI URL**: `https://[pod-id]-8188.proxy.runpod.net`
- **Jupyter URL**: `https://[pod-id]-8888.proxy.runpod.net`
- **SSH Access**: For advanced users

### 4. Upload Your WAN Models

**Method 1: Jupyter Upload (Easiest)**
1. Open Jupyter URL
2. Navigate to `/workspace/ComfyUI/models/checkpoints/`
3. Upload your WAN models:
   - `wan.safetensors`
   - `wan2.114b` (rename to `wan2_114b.safetensors`)

**Method 2: Direct URL (If models are online)**
```bash
# SSH into pod and run:
cd /workspace/ComfyUI/models/checkpoints/
wget [your-model-url] -O wan_safetensors.safetensors
```

### 5. Configure Action Scene Generator

In your local app (Setup & Config):
```python
RunPod Settings:
- API Key: [your-runpod-api-key]
- Pod URL: https://[pod-id]-8188.proxy.runpod.net
- Models: wan.safetensors, wan2_114b.safetensors
```

### 6. Test Connection

Run this test:
```bash
python test_runpod_connection.py
```

## Optimized Settings for WAN on RTX 4090

```yaml
WAN Model Settings:
  sampler: "dpmpp_2m_karras"
  steps: 20-25
  cfg_scale: 6.0-7.0
  resolution: 768x768 (or 1024x1024)
  batch_size: 1-2
  clip_skip: 2

Expected Performance:
  512x512: ~10-15 seconds
  768x768: ~15-25 seconds
  1024x1024: ~25-40 seconds
```

## Cost Management

**Smart Usage:**
- Stop pod when not actively generating
- Use "On-Demand" pricing (pay per minute)
- Monitor usage in RunPod dashboard

**Cost Estimates:**
- RTX 4090: $0.50/hour = $0.008/minute
- Typical session: 1-2 hours = $0.50-$1.00
- Heavy use day: $5-10/day

## Troubleshooting

**Pod won't start:**
- Try different region (US-East, US-West, EU)
- Check RunPod status page
- Contact support

**Models not loading:**
- Check file names (no spaces, proper extensions)
- Verify upload completed
- Restart ComfyUI: `supervisorctl restart comfyui`

**Connection issues:**
- Use HTTPS URLs only
- Check firewall/VPN settings
- Verify pod is "Running" not "Starting"

## Security Best Practices

- Don't share pod URLs publicly
- Stop pods when not in use
- Use volume storage for important models
- Regular backups of generated content

## Advanced: Custom Installation

If you need specific versions:

```bash
# SSH into pod
cd /workspace
git clone https://github.com/your-custom-comfyui-fork.git
# Install custom nodes, models, etc.
```

## Integration with Action Scene Generator

The app will automatically:
1. Detect RunPod connection
2. Upload workflows to your pod
3. Monitor generation progress
4. Download results
5. Cache images locally

**Workflow Speed Comparison:**
- Local M2 Max: 1-3 minutes per image
- RunPod RTX 4090: 10-30 seconds per image
- **10x faster iteration!**

## Next Steps After Setup

1. Test basic generation
2. Upload your WAN models
3. Try the iterative workflow:
   - Sketch → Edit → Motion → Combine
4. Generate your first action sequence
5. Export and share!

Happy generating! 🚀