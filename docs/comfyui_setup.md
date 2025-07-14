# ComfyUI Setup Guide

This guide explains how to set up ComfyUI as the backend for the Cinema Action Scene Generator.

## Prerequisites

- Python 3.8+
- NVIDIA GPU with CUDA support (recommended)
- 8GB+ VRAM for optimal performance
- 16GB+ RAM

## Installation Methods

### Method 1: Standalone Installation (Recommended)

1. **Clone ComfyUI Repository**
   ```bash
   git clone https://github.com/comfyanonymous/ComfyUI.git
   cd ComfyUI
   ```

2. **Install Dependencies**
   ```bash
   pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
   pip install -r requirements.txt
   ```

3. **Download Models**
   Create the following directory structure:
   ```
   ComfyUI/
   ├── models/
   │   ├── checkpoints/
   │   ├── controlnet/
   │   ├── loras/
   │   └── vae/
   ```

4. **Download Required Models**
   
   **Base Models** (place in `models/checkpoints/`):
   - `realisticVisionV60_v60B1.safetensors` - For realistic action scenes
   - `epicrealismXL_v10.safetensors` - For dramatic scenes
   - `juggernautXL_v8Rundiffusion.safetensors` - For explosions/effects
   - `dreamshaper_8.safetensors` - For aerial scenes

   **ControlNet Models** (place in `models/controlnet/`):
   - `control_v11p_sd15_openpose.pth` - For pose control
   - `control_v11f1p_sd15_depth.pth` - For depth control
   - `control_v11p_sd15_canny.pth` - For edge control

5. **Start ComfyUI Server**
   ```bash
   python main.py --listen --port 8188
   ```

### Method 2: ComfyUI Manager (Alternative)

1. **Install ComfyUI Manager**
   - Follow the instructions at: https://github.com/ltdrdata/ComfyUI-Manager

2. **Use Manager to Install Models**
   - Access ComfyUI web interface
   - Use Manager to download recommended models

## Model Recommendations for Action Scenes

### Primary Models

1. **Realistic Vision V6.0**
   - Best for: Car chases, realistic action
   - Download: https://civitai.ai/models/4201

2. **Epic Realism XL**
   - Best for: Fight scenes, dramatic lighting
   - Download: https://civitai.ai/models/277058

3. **Juggernaut XL**
   - Best for: Explosions, destruction scenes
   - Download: https://civitai.ai/models/133005

### ControlNet Models

1. **OpenPose**
   - Essential for character positioning
   - Controls human poses and action stances

2. **Depth**
   - Controls scene depth and perspective
   - Good for environmental composition

3. **Canny**
   - Edge detection for precise control
   - Useful for vehicle and object positioning

## Configuration

### ComfyUI Settings

Edit `extra_model_paths.yaml` in ComfyUI directory:

```yaml
base_path: /path/to/ComfyUI/

checkpoints:
  - models/checkpoints

controlnet:
  - models/controlnet

loras:
  - models/loras

vae:
  - models/vae
```

### Action Scene Generator Integration

Update `config/settings.py`:

```python
# ComfyUI Settings
comfyui_url = "http://localhost:8188"
comfyui_timeout = 300  # 5 minutes for complex scenes
```

## Custom Workflows

The Cinema Action Scene Generator includes pre-built ComfyUI workflows for:

- **Car Chase Workflow**: Optimized for vehicle action
- **Fight Scene Workflow**: Enhanced for combat choreography
- **Explosion Workflow**: Specialized for destruction effects
- **Aerial Combat Workflow**: Designed for air/space battles

## Performance Optimization

### GPU Settings

```python
# In ComfyUI launch command
python main.py --listen --port 8188 --gpu-only --highvram
```

### Memory Management

```python
# For 8GB VRAM
python main.py --listen --port 8188 --normalvram

# For 4GB VRAM
python main.py --listen --port 8188 --lowvram

# For CPU only (slow)
python main.py --listen --port 8188 --cpu
```

## Troubleshooting

### Common Issues

1. **CUDA Out of Memory**
   - Reduce image resolution
   - Use `--lowvram` flag
   - Close other GPU applications

2. **Model Loading Errors**
   - Check model file paths
   - Verify model compatibility
   - Ensure sufficient disk space

3. **Connection Timeout**
   - Increase timeout in settings
   - Check firewall settings
   - Verify ComfyUI server is running

### Development Mode

For development without ComfyUI:

```python
# The system includes fallback placeholder images
# Set COMFYUI_URL to None in settings to use development mode
comfyui_url = None
```

## API Endpoints

ComfyUI exposes these endpoints used by the generator:

- `POST /prompt` - Submit generation workflow
- `GET /history/{prompt_id}` - Check generation status
- `GET /system_stats` - Health check
- `GET /object_info` - Available nodes and models

## Security Considerations

- Run ComfyUI on localhost only for development
- Use authentication for production deployments
- Regularly update ComfyUI and models
- Monitor resource usage to prevent abuse

## Content Safety

The Cinema Action Scene Generator includes content filtering:

- Violence level controls (PG-13, R-rated, Cinematic)
- Automatic negative prompts for inappropriate content
- Model selection based on scene appropriateness
- Output review before serving to users

## Next Steps

After setting up ComfyUI:

1. Test the connection: `python test_comfyui.py`
2. Start the development server: `python run_dev.py`
3. Create your first action scene in the web interface
4. Experiment with different models and settings