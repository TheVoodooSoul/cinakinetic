import json
import os
from typing import List, Optional, Dict, Any
from datetime import datetime
import aiofiles
from ..models.scene_models import Storyboard

class StoryboardDatabase:
    """Simple file-based database for storyboards"""
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        self.storyboards_file = os.path.join(data_dir, "storyboards.json")
        self._ensure_data_dir()
    
    def _ensure_data_dir(self):
        """Ensure data directory exists"""
        os.makedirs(self.data_dir, exist_ok=True)
        if not os.path.exists(self.storyboards_file):
            with open(self.storyboards_file, 'w') as f:
                json.dump({}, f)
    
    async def health_check(self) -> bool:
        """Check if database is accessible"""
        try:
            return os.path.exists(self.storyboards_file)
        except Exception:
            return False
    
    async def save_storyboard(self, storyboard: Storyboard) -> Storyboard:
        """Save a storyboard to the database"""
        
        # Load existing data
        data = await self._load_data()
        
        # Convert to dict for storage
        storyboard_dict = storyboard.model_dump()
        storyboard_dict['created_at'] = storyboard.created_at.isoformat()
        storyboard_dict['updated_at'] = storyboard.updated_at.isoformat()
        
        # Convert node timestamps
        for node in storyboard_dict.get('nodes', []):
            if 'timestamp' in node:
                node['timestamp'] = node['timestamp'].isoformat() if isinstance(node['timestamp'], datetime) else node['timestamp']
        
        # Save to data
        data[storyboard.id] = storyboard_dict
        
        # Write back to file
        await self._save_data(data)
        
        return storyboard
    
    async def get_storyboard(self, storyboard_id: str) -> Optional[Storyboard]:
        """Get a storyboard by ID"""
        
        data = await self._load_data()
        
        if storyboard_id not in data:
            return None
        
        storyboard_dict = data[storyboard_id]
        
        # Convert timestamps back to datetime
        storyboard_dict['created_at'] = datetime.fromisoformat(storyboard_dict['created_at'])
        storyboard_dict['updated_at'] = datetime.fromisoformat(storyboard_dict['updated_at'])
        
        for node in storyboard_dict.get('nodes', []):
            if 'timestamp' in node:
                node['timestamp'] = datetime.fromisoformat(node['timestamp'])
        
        return Storyboard(**storyboard_dict)
    
    async def get_all_storyboards(self) -> List[Storyboard]:
        """Get all storyboards"""
        
        data = await self._load_data()
        storyboards = []
        
        for storyboard_dict in data.values():
            # Convert timestamps
            storyboard_dict = storyboard_dict.copy()
            storyboard_dict['created_at'] = datetime.fromisoformat(storyboard_dict['created_at'])
            storyboard_dict['updated_at'] = datetime.fromisoformat(storyboard_dict['updated_at'])
            
            for node in storyboard_dict.get('nodes', []):
                if 'timestamp' in node:
                    node['timestamp'] = datetime.fromisoformat(node['timestamp'])
            
            storyboards.append(Storyboard(**storyboard_dict))
        
        return sorted(storyboards, key=lambda x: x.updated_at, reverse=True)
    
    async def update_storyboard(self, storyboard_id: str, storyboard: Storyboard) -> Optional[Storyboard]:
        """Update an existing storyboard"""
        
        data = await self._load_data()
        
        if storyboard_id not in data:
            return None
        
        # Update the storyboard
        storyboard.updated_at = datetime.now()
        return await self.save_storyboard(storyboard)
    
    async def delete_storyboard(self, storyboard_id: str) -> bool:
        """Delete a storyboard"""
        
        data = await self._load_data()
        
        if storyboard_id not in data:
            return False
        
        del data[storyboard_id]
        await self._save_data(data)
        
        return True
    
    async def _load_data(self) -> Dict[str, Any]:
        """Load data from file"""
        try:
            async with aiofiles.open(self.storyboards_file, 'r') as f:
                content = await f.read()
                return json.loads(content)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}
    
    async def _save_data(self, data: Dict[str, Any]):
        """Save data to file"""
        async with aiofiles.open(self.storyboards_file, 'w') as f:
            await f.write(json.dumps(data, indent=2, default=str))