# Cinema Action Scene Generator

A generative AI platform for creating cinematic action sequences with R-rated violence levels, focusing on artistic and dramatic storytelling rather than gratuitous content.

## Features

- **Node-based Storyboard Editor**: Visual workflow for sequencing action scenes
- **AI Image Generation**: Integration with ComfyUI, Stable Diffusion, and Huanyan models
- **ControlNet Support**: OpenPose and other control methods for precise scene direction
- **Action Scene Templates**: Pre-built configurations for car chases, fights, explosions, etc.
- **Sequence Choreography**: Connect and flow between generated scenes
- **Export Options**: Storyboard PDFs, image sequences, and video previews

## Architecture

```
Frontend (Streamlit/Web UI)
├── Node-based storyboard editor
├── Scene parameter controls
└── Preview and export tools

Backend (FastAPI)
├── API endpoints
├── Scene generation orchestration
└── Database management

AI Pipeline (ComfyUI Integration)
├── Model management (SD, WAN2.1, Huanyan)
├── ControlNet processing
└── Image generation workflows
```

## Getting Started

1. Install dependencies: `uv pip install -r requirements.txt`
2. Set up ComfyUI backend (instructions in `/docs/comfyui_setup.md`)
3. Run the development server: `python run_dev.py`

## Content Guidelines

This tool is designed for creating cinematic action sequences with:
- ✅ R-rated violence levels (similar to major action films)
- ✅ Artistic and dramatic storytelling
- ✅ Professional cinematography techniques
- ❌ Gratuitous or grotesque content
- ❌ Hate-fueled or discriminatory content
- ❌ Content that glorifies real violence

## License

MIT License - See LICENSE file for details