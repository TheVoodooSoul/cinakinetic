from typing import Dict, List
from ..models.scene_models import SceneParameters, SceneType, ViolenceLevel, CameraAngle

class ActionPromptBuilder:
    def __init__(self):
        self.scene_keywords = {
            SceneType.CAR_CHASE: [
                "high-speed car chase", "vehicle pursuit", "racing through streets",
                "police chase", "dramatic driving", "tire screeching", "speed blur"
            ],
            SceneType.FIGHT_SCENE: [
                "intense combat", "martial arts fight", "hand-to-hand combat",
                "fighting poses", "action choreography", "dynamic movement"
            ],
            SceneType.EXPLOSION: [
                "massive explosion", "fireball", "debris flying", "blast wave",
                "smoke and fire", "destruction", "impact crater"
            ],
            SceneType.SHOOTOUT: [
                "gunfight", "muzzle flashes", "cover shooting", "tactical combat",
                "bullets flying", "action movie shootout"
            ],
            SceneType.AERIAL_COMBAT: [
                "dogfight", "aerial battle", "fighter jets", "missiles firing",
                "aerial maneuvers", "sky combat", "aircraft battle"
            ],
            SceneType.SPACE_BATTLE: [
                "space warfare", "starships fighting", "laser beams", "spacecraft battle",
                "cosmic conflict", "space combat", "interstellar war"
            ],
            SceneType.BOXING_MATCH: [
                "boxing match", "boxing ring", "fighting stance", "punch impact",
                "athletic combat", "sport fighting", "boxing gloves"
            ],
            SceneType.MARTIAL_ARTS: [
                "martial arts", "kung fu fighting", "karate combat", "taekwondo",
                "combat arts", "fighting techniques", "martial combat"
            ]
        }
        
        self.violence_modifiers = {
            ViolenceLevel.PG13: [
                "mild action", "bloodless", "family-friendly action",
                "light impact", "non-graphic"
            ],
            ViolenceLevel.R_RATED: [
                "intense action", "realistic impact", "dramatic violence",
                "action movie style", "cinematic intensity"
            ],
            ViolenceLevel.CINEMATIC: [
                "epic action", "blockbuster style", "cinematic drama",
                "professional cinematography", "movie quality"
            ]
        }
        
        self.camera_modifiers = {
            CameraAngle.WIDE_SHOT: [
                "wide angle shot", "establishing shot", "full scene view",
                "panoramic view", "environmental context"
            ],
            CameraAngle.MEDIUM_SHOT: [
                "medium shot", "waist up", "mid-range view",
                "balanced composition", "character focus"
            ],
            CameraAngle.CLOSE_UP: [
                "close-up shot", "facial detail", "intimate view",
                "emotional intensity", "detailed focus"
            ],
            CameraAngle.LOW_ANGLE: [
                "low angle shot", "looking up", "heroic angle",
                "dramatic perspective", "power shot"
            ],
            CameraAngle.HIGH_ANGLE: [
                "high angle shot", "bird's eye view", "looking down",
                "aerial perspective", "overview shot"
            ],
            CameraAngle.DUTCH_ANGLE: [
                "dutch angle", "tilted camera", "dynamic angle",
                "tension angle", "unbalanced composition"
            ],
            CameraAngle.POV: [
                "point of view shot", "first person view", "character perspective",
                "immersive angle", "subjective camera"
            ]
        }
        
        self.lighting_styles = {
            "dramatic": ["dramatic lighting", "chiaroscuro", "high contrast", "moody lighting"],
            "action": ["dynamic lighting", "fast-paced lighting", "energetic illumination"],
            "cinematic": ["cinematic lighting", "movie-style lighting", "professional lighting"],
            "night": ["night lighting", "low light", "shadows", "artificial lighting"],
            "day": ["daylight", "natural lighting", "bright illumination"],
            "sunset": ["golden hour", "warm lighting", "sunset glow"],
            "neon": ["neon lighting", "colorful lights", "urban glow", "cyberpunk lighting"]
        }
        
        self.quality_enhancers = [
            "8k resolution", "ultra detailed", "masterpiece", "best quality",
            "cinematic composition", "professional photography", "award winning",
            "hyper realistic", "photorealistic", "sharp focus", "high definition"
        ]
        
        self.action_enhancers = [
            "dynamic pose", "action shot", "motion blur", "speed lines",
            "impact frame", "explosive moment", "kinetic energy", "dramatic timing",
            "freeze frame", "action sequence", "stunt choreography"
        ]

    def build_action_prompt(self, base_prompt: str, scene_params: SceneParameters) -> str:
        """Build enhanced prompt for action scene generation"""
        
        components = [base_prompt]
        
        # Add scene-specific keywords
        if scene_params.scene_type in self.scene_keywords:
            scene_words = self.scene_keywords[scene_params.scene_type][:3]  # Top 3 keywords
            components.extend(scene_words)
        
        # Add violence level modifiers
        if scene_params.violence_level in self.violence_modifiers:
            violence_words = self.violence_modifiers[scene_params.violence_level][:2]
            components.extend(violence_words)
        
        # Add camera angle modifiers
        if scene_params.camera_angle in self.camera_modifiers:
            camera_words = self.camera_modifiers[scene_params.camera_angle][:2]
            components.extend(camera_words)
        
        # Add setting and environment
        if scene_params.setting:
            components.append(f"set in {scene_params.setting}")
        
        # Add lighting
        if scene_params.lighting in self.lighting_styles:
            lighting_words = self.lighting_styles[scene_params.lighting][:2]
            components.extend(lighting_words)
        
        # Add time and weather
        if scene_params.time_of_day != "day":
            components.append(f"{scene_params.time_of_day} time")
        
        if scene_params.weather:
            components.append(f"{scene_params.weather} weather")
        
        # Add motion blur if enabled
        if scene_params.motion_blur:
            components.extend(["motion blur", "speed effect"])
        
        # Add characters if specified
        if scene_params.characters:
            char_desc = ", ".join(scene_params.characters[:2])  # Limit to 2 characters
            components.append(f"featuring {char_desc}")
        
        # Add props if specified
        if scene_params.props:
            prop_desc = ", ".join(scene_params.props[:3])  # Limit to 3 props
            components.append(f"with {prop_desc}")
        
        # Add quality enhancers
        components.extend(self.quality_enhancers[:4])
        
        # Add action enhancers
        components.extend(self.action_enhancers[:3])
        
        # Join all components
        enhanced_prompt = ", ".join(components)
        
        return enhanced_prompt
    
    def get_scene_suggestions(self, scene_type: SceneType) -> Dict[str, List[str]]:
        """Get suggestions for a specific scene type"""
        
        suggestions = {
            "keywords": self.scene_keywords.get(scene_type, []),
            "settings": self._get_setting_suggestions(scene_type),
            "props": self._get_prop_suggestions(scene_type),
            "characters": self._get_character_suggestions(scene_type)
        }
        
        return suggestions
    
    def _get_setting_suggestions(self, scene_type: SceneType) -> List[str]:
        """Get setting suggestions for scene type"""
        
        setting_map = {
            SceneType.CAR_CHASE: [
                "busy city streets", "mountain highway", "desert road",
                "urban tunnel", "rainy highway", "bridge chase"
            ],
            SceneType.FIGHT_SCENE: [
                "urban rooftop", "warehouse", "alleyway", "dojo",
                "underground fight club", "abandoned building"
            ],
            SceneType.EXPLOSION: [
                "industrial facility", "building demolition", "military base",
                "oil refinery", "construction site", "laboratory"
            ],
            SceneType.AERIAL_COMBAT: [
                "cloudy sky", "over ocean", "mountain valley",
                "urban airspace", "desert aerial", "storm clouds"
            ],
            SceneType.SPACE_BATTLE: [
                "deep space", "asteroid field", "planetary orbit",
                "nebula backdrop", "space station vicinity", "starfield"
            ]
        }
        
        return setting_map.get(scene_type, ["generic action setting"])
    
    def _get_prop_suggestions(self, scene_type: SceneType) -> List[str]:
        """Get prop suggestions for scene type"""
        
        prop_map = {
            SceneType.CAR_CHASE: [
                "sports cars", "motorcycles", "police vehicles",
                "helicopters", "roadblocks", "traffic"
            ],
            SceneType.FIGHT_SCENE: [
                "martial arts weapons", "broken glass", "metal pipes",
                "wooden crates", "fire barrels", "chain-link fence"
            ],
            SceneType.EXPLOSION: [
                "dynamite", "fuel barrels", "debris", "smoke",
                "sparks", "shattered glass", "concrete chunks"
            ],
            SceneType.SHOOTOUT: [
                "assault rifles", "pistols", "cover barriers",
                "muzzle flashes", "shell casings", "tactical gear"
            ]
        }
        
        return prop_map.get(scene_type, ["action props"])
    
    def _get_character_suggestions(self, scene_type: SceneType) -> List[str]:
        """Get character suggestions for scene type"""
        
        character_map = {
            SceneType.CAR_CHASE: [
                "professional driver", "police officer", "chase suspect",
                "motorcycle rider", "getaway driver"
            ],
            SceneType.FIGHT_SCENE: [
                "martial artist", "street fighter", "trained combatant",
                "action hero", "skilled warrior"
            ],
            SceneType.BOXING_MATCH: [
                "professional boxer", "heavyweight fighter", "athletic boxer",
                "boxing champion", "determined fighter"
            ]
        }
        
        return character_map.get(scene_type, ["action character"])