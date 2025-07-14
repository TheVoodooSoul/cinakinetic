from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict
import json
import uuid
from datetime import datetime

from ..models.scene_models import (
    Storyboard, SceneNode, GenerationRequest, GenerationResponse,
    SceneParameters, GenerationConfig
)
from ..ai_pipeline.comfyui_client import ComfyUIClient
from ..database.storyboard_db import StoryboardDatabase

app = FastAPI(title="Cinema Action Scene Generator API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Initialize components
db = StoryboardDatabase()
comfy_client = ComfyUIClient()

# WebSocket connections for real-time updates
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # Handle real-time communication
            await manager.send_personal_message(f"Received: {data}", websocket)
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@app.get("/")
async def root():
    return {"message": "Cinema Action Scene Generator API", "status": "running"}

@app.post("/storyboards/", response_model=Storyboard)
async def create_storyboard(title: str, description: str = None):
    storyboard = Storyboard(
        id=str(uuid.uuid4()),
        title=title,
        description=description
    )
    saved_storyboard = await db.save_storyboard(storyboard)
    return saved_storyboard

@app.get("/storyboards/", response_model=List[Storyboard])
async def list_storyboards():
    return await db.get_all_storyboards()

@app.get("/storyboards/{storyboard_id}", response_model=Storyboard)
async def get_storyboard(storyboard_id: str):
    storyboard = await db.get_storyboard(storyboard_id)
    if not storyboard:
        raise HTTPException(status_code=404, detail="Storyboard not found")
    return storyboard

@app.put("/storyboards/{storyboard_id}", response_model=Storyboard)
async def update_storyboard(storyboard_id: str, storyboard: Storyboard):
    storyboard.updated_at = datetime.now()
    updated = await db.update_storyboard(storyboard_id, storyboard)
    if not updated:
        raise HTTPException(status_code=404, detail="Storyboard not found")
    return updated

@app.delete("/storyboards/{storyboard_id}")
async def delete_storyboard(storyboard_id: str):
    deleted = await db.delete_storyboard(storyboard_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Storyboard not found")
    return {"message": "Storyboard deleted successfully"}

@app.post("/generate-scene/", response_model=GenerationResponse)
async def generate_scene(request: GenerationRequest):
    try:
        # Generate the scene using ComfyUI
        result = await comfy_client.generate_scene(
            prompt=request.prompt,
            scene_params=request.scene_params,
            config=request.generation_config
        )
        
        response = GenerationResponse(
            node_id=request.node_id,
            image_url=result["image_url"],
            generation_time=result["generation_time"],
            success=True
        )
        
        # Broadcast update to connected clients
        await manager.broadcast(json.dumps({
            "type": "scene_generated",
            "node_id": request.node_id,
            "image_url": result["image_url"]
        }))
        
        return response
        
    except Exception as e:
        return GenerationResponse(
            node_id=request.node_id,
            image_url="",
            generation_time=0.0,
            success=False,
            error=str(e)
        )

@app.get("/scene-templates/")
async def get_scene_templates():
    """Get pre-defined scene templates for different action types"""
    templates = {
        "car_chase": {
            "name": "High-Speed Car Chase",
            "description": "Dynamic vehicle pursuit through city streets",
            "default_prompt": "high-speed car chase through city streets, police pursuit, dramatic lighting, motion blur, cinematic angle",
            "scene_params": {
                "scene_type": "car_chase",
                "violence_level": "r_rated",
                "camera_angle": "low_angle",
                "setting": "urban city streets",
                "lighting": "dramatic sunset",
                "motion_blur": True
            }
        },
        "fight_scene": {
            "name": "Hand-to-Hand Combat",
            "description": "Intense martial arts fight sequence",
            "default_prompt": "intense hand-to-hand combat, martial arts fight, dramatic lighting, action poses, cinematic composition",
            "scene_params": {
                "scene_type": "fight_scene",
                "violence_level": "r_rated",
                "camera_angle": "medium_shot",
                "setting": "urban rooftop",
                "lighting": "moody night lighting"
            }
        },
        "explosion": {
            "name": "Dramatic Explosion",
            "description": "High-impact explosion scene with debris",
            "default_prompt": "massive explosion with debris flying, dramatic fireball, smoke and sparks, cinematic wide shot",
            "scene_params": {
                "scene_type": "explosion",
                "violence_level": "r_rated",
                "camera_angle": "wide_shot",
                "setting": "industrial facility",
                "lighting": "fire glow"
            }
        }
    }
    return templates

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "database": await db.health_check(),
            "comfyui": await comfy_client.health_check()
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)