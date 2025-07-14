# Cinema Action Scene Generator - Usage Guide

## Quick Start

1. **Activate the environment:**
   ```bash
   cd /Users/watson/Workspace/cinema_action_scene_generator
   source .venv/bin/activate
   ```

2. **Start the development server:**
   ```bash
   python run_dev.py
   ```

3. **Access the application:**
   - **Web Interface**: http://localhost:8501
   - **API Documentation**: http://localhost:8000/docs
   - **API Health Check**: http://localhost:8000/health

## Features Overview

### 🎯 Scene Types Supported
- **Car Chases**: High-speed pursuits, street racing, police chases
- **Fight Scenes**: Hand-to-hand combat, martial arts, boxing matches
- **Explosions**: Building demolitions, industrial accidents, action blasts
- **Shootouts**: Tactical combat, gunfights, action movie sequences
- **Aerial Combat**: Dogfights, space battles, aerial maneuvers
- **Boxing/Sports**: Professional boxing, athletic combat sports

### 🎬 Violence Levels
- **PG-13**: Mild action, family-friendly intensity
- **R-Rated**: Realistic impact, cinematic violence (default)
- **Cinematic**: Professional blockbuster-style action

### 📹 Camera Angles
- Wide Shot, Medium Shot, Close-up
- Low Angle, High Angle, Dutch Angle
- Point of View (POV), Over-Shoulder

## Using the Web Interface

### Creating a Storyboard

1. **Start New Project**
   - Click "Create New Storyboard" in sidebar
   - Enter title (e.g., "Epic Car Chase Sequence")
   - Add optional description

2. **Design Scenes**
   - Select scene type from dropdown
   - Choose violence level and camera angle
   - Set location/environment
   - Configure lighting and effects

3. **Generate Scenes**
   - Write detailed scene prompt
   - Use templates for quick start
   - Adjust generation settings (resolution, steps, etc.)
   - Enable ControlNet for precise control

4. **Review and Export**
   - View generated scenes in storyboard timeline
   - Export as PDF, image sequence, or JSON data

### Example Workflows

**Car Chase Scene:**
```
Scene Type: Car Chase
Violence Level: R-Rated
Camera Angle: Low Angle
Setting: busy city streets
Lighting: dramatic sunset
Prompt: "High-speed police chase through downtown, multiple vehicles, tire screeching, dramatic lighting"
```

**Fight Scene:**
```
Scene Type: Fight Scene
Violence Level: Cinematic
Camera Angle: Medium Shot
Setting: urban rooftop
Lighting: moody night lighting
Prompt: "Intense martial arts combat on rooftop, two fighters, dynamic poses, cinematic composition"
```

## API Usage

### Creating a Storyboard via API

```python
import requests

# Create new storyboard
response = requests.post(
    "http://localhost:8000/storyboards/",
    params={"title": "My Action Sequence"}
)
storyboard = response.json()
```

### Generating a Scene

```python
generation_request = {
    "node_id": "scene-1",
    "prompt": "Epic car chase through city streets",
    "scene_params": {
        "scene_type": "car_chase",
        "violence_level": "r_rated",
        "camera_angle": "low_angle",
        "setting": "urban streets",
        "lighting": "dramatic",
        "motion_blur": True
    },
    "generation_config": {
        "width": 1024,
        "height": 1024,
        "steps": 30,
        "cfg_scale": 7.5
    }
}

response = requests.post(
    "http://localhost:8000/generate-scene/",
    json=generation_request
)
result = response.json()
```

## Advanced Features

### ControlNet Integration

Enable precise control over character poses and scene composition:

```python
"controlnet": {
    "type": "openpose",
    "enabled": True,
    "strength": 0.8,
    "reference_image": "base64_encoded_image"
}
```

### Custom Prompts

The system enhances your prompts with scene-specific keywords:

**Your Input:**
```
"Car chase through downtown"
```

**Enhanced Prompt:**
```
"Car chase through downtown, high-speed car chase, vehicle pursuit, racing through streets, intense action, realistic impact, cinematic intensity, low angle shot, heroic angle, dramatic perspective, set in urban streets, dramatic lighting, high contrast, motion blur, speed effect, 8k resolution, ultra detailed, masterpiece, cinematic composition, dynamic pose, action shot"
```

### Scene Templates

Pre-built templates for common action scenes:

- **Car Chase Template**: Optimized for vehicle action
- **Fight Scene Template**: Enhanced for combat choreography  
- **Explosion Template**: Specialized for destruction effects

## Content Guidelines

### ✅ Appropriate Content
- Cinematic action violence (similar to major action films)
- Professional stunt choreography
- Dramatic storytelling sequences
- Artistic action cinematography

### ❌ Inappropriate Content
- Gratuitous or excessive violence
- Real-world hate or discrimination
- Gore or grotesque imagery
- Content glorifying actual violence

## Troubleshooting

### Common Issues

1. **"Failed to connect to API server"**
   - Ensure the development server is running
   - Check that port 8000 is available

2. **"Generation failed"**
   - ComfyUI may not be installed (optional for development)
   - Check generation parameters are valid
   - Try reducing image resolution

3. **Slow generation**
   - Reduce image size or steps
   - Ensure adequate system resources
   - Consider GPU acceleration

### Development Mode

The system works without ComfyUI installed:
- Uses placeholder images for development
- All features except actual AI generation work
- Perfect for testing UI and workflow

## File Structure

```
cinema_action_scene_generator/
├── src/                    # Source code
│   ├── api/               # FastAPI backend
│   ├── ui/                # Streamlit frontend
│   ├── ai_pipeline/       # ComfyUI integration
│   ├── models/            # Data models
│   ├── database/          # Database layer
│   └── utils/             # Utilities
├── config/                # Configuration
├── docs/                  # Documentation
├── data/                  # Stored storyboards
├── static/                # Static files
└── requirements.txt       # Dependencies
```

## Performance Tips

1. **Optimize Generation Settings**
   - Start with 512x512 resolution for testing
   - Use 20-30 steps for balance of quality/speed
   - CFG scale 7-8 for most scenes

2. **Resource Management**
   - Close other applications when generating
   - Monitor memory usage with complex scenes
   - Use batch processing for multiple scenes

3. **Template Usage**
   - Start with provided templates
   - Customize gradually based on results
   - Save successful settings as presets

## Next Steps

1. **Install ComfyUI** (optional): See `docs/comfyui_setup.md`
2. **Create your first storyboard**: Use the web interface
3. **Experiment with settings**: Try different scene types and parameters
4. **Export results**: Generate PDFs and image sequences
5. **Integrate with workflow**: Use API for automation

For technical support or feature requests, refer to the documentation or create an issue in the project repository.