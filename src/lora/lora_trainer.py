import streamlit as st
import os
import json
import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime
import zipfile
import io

@dataclass
class LoRAConfig:
    name: str
    type: str  # character, style, pose, fighting_style
    description: str
    training_images: List[str]
    settings: Dict[str, Any]
    status: str = "pending"  # pending, training, completed, error
    created_at: datetime = None
    file_path: Optional[str] = None

class LoRATrainer:
    """LoRA training system for character consistency and fight styles"""
    
    def __init__(self):
        self.lora_configs = {
            "character": {
                "name": "Character LoRA",
                "description": "Train on 15-25 images of the same character in different poses",
                "min_images": 15,
                "max_images": 25,
                "steps": 1000,
                "learning_rate": 1e-4,
                "batch_size": 1,
                "network_dim": 64,
                "network_alpha": 32,
                "use_case": "Character consistency across action scenes"
            },
            "fighting_style": {
                "name": "Fighting Style LoRA", 
                "description": "Train on specific martial arts or combat styles",
                "min_images": 20,
                "max_images": 40,
                "steps": 1500,
                "learning_rate": 8e-5,
                "batch_size": 2,
                "network_dim": 32,
                "network_alpha": 16,
                "use_case": "Consistent fighting choreography and techniques"
            },
            "action_pose": {
                "name": "Action Pose LoRA",
                "description": "Train on dynamic action poses and movements", 
                "min_images": 10,
                "max_images": 30,
                "steps": 800,
                "learning_rate": 1.2e-4,
                "batch_size": 1,
                "network_dim": 48,
                "network_alpha": 24,
                "use_case": "Specific action poses and combat stances"
            },
            "scene_style": {
                "name": "Scene Style LoRA",
                "description": "Train on specific cinematography or visual style",
                "min_images": 25,
                "max_images": 50,
                "steps": 2000,
                "learning_rate": 6e-5,
                "batch_size": 2,
                "network_dim": 80,
                "network_alpha": 40,
                "use_case": "Consistent visual style across action sequences"
            }
        }
    
    def create_lora_interface(self):
        """Main LoRA training interface"""
        
        st.title("🎯 LoRA Training Studio")
        st.write("Create custom LoRAs for character consistency and fighting styles")
        
        # Tabs for different functions
        tab1, tab2, tab3, tab4 = st.tabs([
            "📚 Train New LoRA",
            "👥 Character Manager", 
            "🥊 Fighting Styles",
            "📖 LoRA Library"
        ])
        
        with tab1:
            self.create_training_interface()
        
        with tab2:
            self.create_character_manager()
        
        with tab3:
            self.create_fighting_styles_interface()
        
        with tab4:
            self.create_lora_library()
    
    def create_training_interface(self):
        """Interface for training new LoRAs"""
        
        st.header("📚 Train New LoRA")
        
        # LoRA type selection
        lora_type = st.selectbox(
            "LoRA Type",
            list(self.lora_configs.keys()),
            format_func=lambda x: self.lora_configs[x]["name"]
        )
        
        config = self.lora_configs[lora_type]
        
        # Show configuration info
        with st.expander("ℹ️ Training Configuration", expanded=True):
            col1, col2 = st.columns(2)
            
            with col1:
                st.write(f"**Description:** {config['description']}")
                st.write(f"**Use Case:** {config['use_case']}")
                st.write(f"**Images Needed:** {config['min_images']}-{config['max_images']}")
            
            with col2:
                st.write(f"**Training Steps:** {config['steps']}")
                st.write(f"**Learning Rate:** {config['learning_rate']}")
                st.write(f"**Network Dim:** {config['network_dim']}")
        
        # LoRA details
        col1, col2 = st.columns(2)
        
        with col1:
            lora_name = st.text_input(
                "LoRA Name",
                placeholder="e.g., 'ActionHero_John', 'KungFu_Style', 'ExplosiveAction'"
            )
            
            trigger_word = st.text_input(
                "Trigger Word",
                placeholder="e.g., 'johnhero', 'kungfustyle', 'explosiveaction'",
                help="Word to activate this LoRA in prompts"
            )
        
        with col2:
            description = st.text_area(
                "Description",
                placeholder="Describe what this LoRA does...",
                height=100
            )
        
        # Image upload
        st.subheader("📸 Training Images")
        
        if lora_type == "character":
            st.info("👤 **Character LoRA Tips:**\n- Use 15-25 high-quality images\n- Same character, different poses/angles\n- Include close-ups and full-body shots\n- Vary lighting and backgrounds")
        elif lora_type == "fighting_style":
            st.info("🥊 **Fighting Style Tips:**\n- 20-40 images of specific martial art\n- Include various techniques and stances\n- Different practitioners OK\n- Focus on pose accuracy")
        
        uploaded_files = st.file_uploader(
            "Upload Training Images",
            type=['png', 'jpg', 'jpeg'],
            accept_multiple_files=True,
            help=f"Upload {config['min_images']}-{config['max_images']} images"
        )
        
        if uploaded_files:
            num_images = len(uploaded_files)
            
            # Show upload status
            if num_images < config['min_images']:
                st.warning(f"⚠️ Need at least {config['min_images']} images (you have {num_images})")
            elif num_images > config['max_images']:
                st.warning(f"⚠️ Too many images! Maximum {config['max_images']} (you have {num_images})")
            else:
                st.success(f"✅ Perfect! {num_images} images uploaded")
            
            # Show image preview
            with st.expander("🖼️ Image Preview"):
                cols = st.columns(min(len(uploaded_files), 5))
                for i, file in enumerate(uploaded_files[:5]):
                    with cols[i]:
                        st.image(file, caption=f"Image {i+1}", width=100)
                
                if len(uploaded_files) > 5:
                    st.write(f"... and {len(uploaded_files) - 5} more images")
        
        # Training settings
        with st.expander("⚙️ Advanced Training Settings"):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                custom_steps = st.number_input(
                    "Training Steps",
                    min_value=500,
                    max_value=3000,
                    value=config['steps']
                )
                
                learning_rate = st.number_input(
                    "Learning Rate",
                    min_value=1e-5,
                    max_value=5e-4,
                    value=config['learning_rate'],
                    format="%.0e"
                )
            
            with col2:
                network_dim = st.selectbox(
                    "Network Dimension",
                    [16, 32, 48, 64, 80, 128],
                    index=[16, 32, 48, 64, 80, 128].index(config['network_dim'])
                )
                
                network_alpha = st.selectbox(
                    "Network Alpha",
                    [8, 16, 24, 32, 40, 64],
                    index=[8, 16, 24, 32, 40, 64].index(config['network_alpha'])
                )
            
            with col3:
                resolution = st.selectbox(
                    "Training Resolution",
                    ["512x512", "768x768", "1024x1024"],
                    index=1
                )
                
                batch_size = st.selectbox(
                    "Batch Size",
                    [1, 2, 4],
                    index=config['batch_size'] - 1
                )
        
        # Training cost and time estimate
        training_cost = self.calculate_training_cost(custom_steps, num_images if uploaded_files else 0, resolution)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Estimated Time", f"{training_cost['time_minutes']} min")
        with col2:
            st.metric("Credits Required", training_cost['credits'])
        with col3:
            st.metric("GPU Cost", f"${training_cost['gpu_cost']:.2f}")
        
        # Start training
        can_train = (
            lora_name and 
            trigger_word and 
            uploaded_files and 
            config['min_images'] <= len(uploaded_files) <= config['max_images']
        )
        
        if st.button("🚀 Start Training", type="primary", disabled=not can_train):
            if can_train:
                self.start_lora_training(
                    lora_name, lora_type, trigger_word, description,
                    uploaded_files, custom_steps, learning_rate,
                    network_dim, network_alpha, resolution, batch_size
                )
            else:
                st.error("❌ Please complete all required fields and upload proper number of images")
    
    def create_character_manager(self):
        """Character consistency management system"""
        
        st.header("👥 Character Manager")
        st.write("Manage characters for consistent action sequences")
        
        # Character library
        if 'characters' not in st.session_state:
            st.session_state.characters = {}
        
        # Add new character
        with st.expander("➕ Add New Character", expanded=len(st.session_state.characters) == 0):
            col1, col2 = st.columns(2)
            
            with col1:
                char_name = st.text_input("Character Name", placeholder="e.g., 'Action Hero John'")
                char_description = st.text_area("Description", placeholder="Describe the character's appearance, style, etc.")
            
            with col2:
                char_image = st.file_uploader("Reference Image", type=['png', 'jpg', 'jpeg'])
                
                if char_image:
                    st.image(char_image, caption="Character Reference", width=200)
            
            # Character fighting style
            fighting_style = st.selectbox(
                "Primary Fighting Style",
                ["Boxing", "Martial Arts", "MMA", "Street Fighting", "Sword Combat", "Gun Combat", "Mixed"]
            )
            
            signature_moves = st.text_input(
                "Signature Moves",
                placeholder="e.g., 'spinning kick, uppercut combo, defensive blocks'"
            )
            
            if st.button("💾 Save Character") and char_name:
                char_id = char_name.lower().replace(" ", "_")
                st.session_state.characters[char_id] = {
                    "name": char_name,
                    "description": char_description,
                    "fighting_style": fighting_style,
                    "signature_moves": signature_moves,
                    "reference_image": char_image,
                    "lora_trained": False,
                    "lora_name": None,
                    "scenes_used": 0,
                    "created_at": datetime.now()
                }
                st.success(f"✅ Character '{char_name}' added!")
                st.rerun()
        
        # Existing characters
        if st.session_state.characters:
            st.subheader("📋 Character Library")
            
            for char_id, char in st.session_state.characters.items():
                with st.expander(f"👤 {char['name']}", expanded=False):
                    col1, col2, col3 = st.columns([1, 2, 1])
                    
                    with col1:
                        if char.get('reference_image'):
                            st.image(char['reference_image'], width=150)
                    
                    with col2:
                        st.write(f"**Description:** {char['description']}")
                        st.write(f"**Fighting Style:** {char['fighting_style']}")
                        st.write(f"**Signature Moves:** {char['signature_moves']}")
                        
                        # LoRA status
                        if char['lora_trained']:
                            st.success(f"✅ LoRA Trained: `{char['lora_name']}`")
                        else:
                            st.warning("⚠️ No LoRA trained yet")
                    
                    with col3:
                        st.metric("Scenes Used", char['scenes_used'])
                        
                        if not char['lora_trained']:
                            if st.button(f"🎯 Train LoRA", key=f"train_{char_id}"):
                                st.session_state['train_character'] = char_id
                                st.info("Go to 'Train New LoRA' tab to upload training images")
                        
                        if st.button(f"🎬 Use in Scene", key=f"use_{char_id}"):
                            st.session_state['selected_character'] = char_id
                            st.success(f"Character '{char['name']}' selected for generation!")
                        
                        if st.button(f"🗑️ Delete", key=f"delete_{char_id}"):
                            del st.session_state.characters[char_id]
                            st.success(f"Character '{char['name']}' deleted")
                            st.rerun()
        
        else:
            st.info("👆 Add your first character to get started with consistency!")
    
    def create_fighting_styles_interface(self):
        """Interface for managing fighting style LoRAs"""
        
        st.header("🥊 Fighting Style Library")
        st.write("Create and manage custom fighting style LoRAs")
        
        # Pre-built fighting style templates
        fighting_styles = {
            "boxing": {
                "name": "Professional Boxing",
                "description": "Classic boxing stances, jabs, hooks, uppercuts",
                "trigger": "boxingstyle",
                "sample_prompts": [
                    "boxer in fighting stance, boxingstyle",
                    "powerful jab punch, boxingstyle, dynamic pose",
                    "defensive guard position, boxingstyle"
                ]
            },
            "kungfu": {
                "name": "Kung Fu Martial Arts",
                "description": "Traditional kung fu poses, kicks, blocks",
                "trigger": "kungfustyle",
                "sample_prompts": [
                    "martial artist in crane stance, kungfustyle",
                    "high kick technique, kungfustyle, flowing motion",
                    "defensive block and counter, kungfustyle"
                ]
            },
            "mma": {
                "name": "Mixed Martial Arts",
                "description": "Ground fighting, grappling, striking combinations",
                "trigger": "mmastyle", 
                "sample_prompts": [
                    "grappling position, mmastyle, ground fighting",
                    "striking combination, mmastyle, aggressive stance",
                    "submission hold, mmastyle, technical position"
                ]
            },
            "swordplay": {
                "name": "Sword Combat",
                "description": "Sword fighting techniques, parries, thrusts",
                "trigger": "swordstyle",
                "sample_prompts": [
                    "sword fighting stance, swordstyle, blade ready",
                    "parrying attack, swordstyle, defensive position", 
                    "thrust attack, swordstyle, aggressive lunge"
                ]
            }
        }
        
        # Fighting style cards
        cols = st.columns(2)
        
        for i, (style_id, style) in enumerate(fighting_styles.items()):
            with cols[i % 2]:
                with st.container():
                    st.subheader(f"🥊 {style['name']}")
                    st.write(style['description'])
                    st.code(f"Trigger: {style['trigger']}")
                    
                    # Sample prompts
                    with st.expander("📝 Sample Prompts"):
                        for prompt in style['sample_prompts']:
                            st.code(prompt)
                    
                    # Status check
                    lora_exists = self.check_lora_exists(style['trigger'])
                    
                    if lora_exists:
                        st.success("✅ LoRA Available")
                        if st.button(f"🎬 Use {style['name']}", key=f"use_style_{style_id}"):
                            st.session_state['selected_fighting_style'] = style['trigger']
                            st.success(f"Fighting style '{style['name']}' selected!")
                    else:
                        st.warning("⚠️ LoRA Not Trained")
                        if st.button(f"🎯 Train {style['name']} LoRA", key=f"train_style_{style_id}"):
                            st.session_state['train_fighting_style'] = style_id
                            st.info("Go to 'Train New LoRA' tab to upload training images")
        
        # Custom fighting style creator
        with st.expander("➕ Create Custom Fighting Style"):
            col1, col2 = st.columns(2)
            
            with col1:
                custom_name = st.text_input("Style Name", placeholder="e.g., 'Parkour Combat'")
                custom_trigger = st.text_input("Trigger Word", placeholder="e.g., 'parkourcombat'")
            
            with col2:
                custom_description = st.text_area(
                    "Description",
                    placeholder="Describe the fighting style characteristics..."
                )
            
            training_images = st.file_uploader(
                "Training Images",
                type=['png', 'jpg', 'jpeg'],
                accept_multiple_files=True,
                help="Upload 20-40 images showing this fighting style"
            )
            
            if st.button("🚀 Train Custom Style") and custom_name and custom_trigger and training_images:
                st.success(f"Training custom style '{custom_name}'...")
                # Would start training process
    
    def create_lora_library(self):
        """Library of all trained LoRAs"""
        
        st.header("📖 LoRA Library")
        st.write("Manage all your trained LoRAs")
        
        # Mock LoRA library
        if 'lora_library' not in st.session_state:
            st.session_state.lora_library = [
                {
                    "name": "ActionHero_John",
                    "type": "character", 
                    "trigger": "johnhero",
                    "description": "Consistent character for action sequences",
                    "trained_date": "2024-01-15",
                    "uses": 23,
                    "rating": 4.8,
                    "file_size": "144 MB",
                    "status": "active"
                },
                {
                    "name": "KungFu_Style",
                    "type": "fighting_style",
                    "trigger": "kungfustyle", 
                    "description": "Traditional kung fu martial arts poses",
                    "trained_date": "2024-01-12",
                    "uses": 15,
                    "rating": 4.6,
                    "file_size": "89 MB", 
                    "status": "active"
                }
            ]
        
        # LoRA management interface
        for lora in st.session_state.lora_library:
            with st.expander(f"🎯 {lora['name']} ({lora['type']})", expanded=False):
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.write(f"**Trigger:** `{lora['trigger']}`")
                    st.write(f"**Type:** {lora['type'].replace('_', ' ').title()}")
                    st.write(f"**Status:** {lora['status'].title()}")
                
                with col2:
                    st.metric("Uses", lora['uses'])
                    st.metric("Rating", f"{lora['rating']}/5.0")
                
                with col3:
                    st.write(f"**Trained:** {lora['trained_date']}")
                    st.write(f"**Size:** {lora['file_size']}")
                
                with col4:
                    if st.button(f"📥 Download", key=f"download_{lora['name']}"):
                        # Would trigger download
                        st.info("Downloading LoRA file...")
                    
                    if st.button(f"🎬 Use in Generation", key=f"use_lora_{lora['name']}"):
                        st.session_state['selected_lora'] = lora['trigger']
                        st.success(f"LoRA '{lora['name']}' selected!")
                    
                    if st.button(f"🗑️ Delete", key=f"delete_lora_{lora['name']}"):
                        st.warning(f"Delete '{lora['name']}'? This cannot be undone.")
        
        # LoRA usage analytics
        st.subheader("📊 LoRA Analytics")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total LoRAs", len(st.session_state.lora_library))
        with col2:
            total_uses = sum(lora['uses'] for lora in st.session_state.lora_library)
            st.metric("Total Uses", total_uses)
        with col3:
            avg_rating = sum(lora['rating'] for lora in st.session_state.lora_library) / len(st.session_state.lora_library)
            st.metric("Avg Rating", f"{avg_rating:.1f}/5.0")
    
    def calculate_training_cost(self, steps: int, num_images: int, resolution: str) -> Dict[str, Any]:
        """Calculate LoRA training cost and time"""
        
        # Base calculations for RTX 6000 Ada
        base_time_per_step = 0.8  # seconds per step on RTX 6000
        resolution_multiplier = {
            "512x512": 1.0,
            "768x768": 1.5, 
            "1024x1024": 2.2
        }.get(resolution, 1.0)
        
        image_multiplier = 1 + (num_images / 100)  # More images = longer training
        
        total_time_seconds = steps * base_time_per_step * resolution_multiplier * image_multiplier
        time_minutes = int(total_time_seconds / 60)
        
        # Cost calculation (RTX 6000 at ~$2/hour)
        gpu_cost = (total_time_seconds / 3600) * 2.0
        
        # Credits (roughly 1 credit per minute of training)
        credits = max(time_minutes, 50)  # Minimum 50 credits
        
        return {
            "time_minutes": time_minutes,
            "gpu_cost": gpu_cost,
            "credits": credits
        }
    
    def start_lora_training(self, name: str, lora_type: str, trigger: str, description: str,
                          images: List, steps: int, learning_rate: float,
                          network_dim: int, network_alpha: int, resolution: str, batch_size: int):
        """Start LoRA training process"""
        
        # Create training configuration
        training_config = {
            "name": name,
            "type": lora_type,
            "trigger_word": trigger,
            "description": description,
            "num_images": len(images),
            "steps": steps,
            "learning_rate": learning_rate,
            "network_dim": network_dim,
            "network_alpha": network_alpha,
            "resolution": resolution,
            "batch_size": batch_size,
            "started_at": datetime.now().isoformat()
        }
        
        # Simulate training process
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Training phases
        phases = [
            "Preprocessing images...",
            "Setting up training environment...", 
            "Starting LoRA training...",
            "Training in progress...",
            "Validation and testing...",
            "Finalizing LoRA model...",
            "Training completed!"
        ]
        
        for i, phase in enumerate(phases):
            status_text.text(phase)
            progress_bar.progress((i + 1) / len(phases))
            time.sleep(1)  # Simulate training time
        
        # Add to library
        new_lora = {
            "name": name,
            "type": lora_type,
            "trigger": trigger,
            "description": description,
            "trained_date": datetime.now().strftime("%Y-%m-%d"),
            "uses": 0,
            "rating": 0.0,
            "file_size": "156 MB",
            "status": "active"
        }
        
        if 'lora_library' not in st.session_state:
            st.session_state.lora_library = []
        
        st.session_state.lora_library.append(new_lora)
        
        st.success(f"🎉 LoRA '{name}' training completed!")
        st.balloons()
        
        # Show usage instructions
        st.info(f"💡 **How to use your new LoRA:**\n\nAdd `{trigger}` to your prompts to activate this LoRA.\n\nExample: `epic fight scene, {trigger}, dynamic action`")
    
    def check_lora_exists(self, trigger: str) -> bool:
        """Check if LoRA exists in library"""
        if 'lora_library' not in st.session_state:
            return False
        
        return any(lora['trigger'] == trigger for lora in st.session_state.lora_library)

def integrate_lora_with_generation():
    """Integration with main generation system"""
    
    # This would be called from the main generation interface
    st.subheader("🎯 LoRA Selection")
    
    # Character selection
    if 'characters' in st.session_state and st.session_state.characters:
        character_options = ["None"] + list(st.session_state.characters.keys())
        selected_char = st.selectbox(
            "Character",
            character_options,
            format_func=lambda x: "No character" if x == "None" else st.session_state.characters[x]['name']
        )
        
        if selected_char != "None":
            char = st.session_state.characters[selected_char]
            if char['lora_trained']:
                st.success(f"✅ Using character LoRA: {char['lora_name']}")
            else:
                st.warning("⚠️ Character LoRA not trained yet")
    
    # Fighting style selection
    if 'selected_fighting_style' in st.session_state:
        st.success(f"✅ Fighting style: {st.session_state.selected_fighting_style}")
    
    # Additional LoRAs
    if 'lora_library' in st.session_state and st.session_state.lora_library:
        additional_loras = st.multiselect(
            "Additional LoRAs",
            [lora['trigger'] for lora in st.session_state.lora_library],
            format_func=lambda x: next((lora['name'] for lora in st.session_state.lora_library if lora['trigger'] == x), x)
        )
        
        if additional_loras:
            st.info(f"Selected LoRAs: {', '.join(additional_loras)}")
    
    return {
        "character_lora": selected_char if 'selected_char' in locals() and selected_char != "None" else None,
        "fighting_style": st.session_state.get('selected_fighting_style'),
        "additional_loras": additional_loras if 'additional_loras' in locals() else []
    }