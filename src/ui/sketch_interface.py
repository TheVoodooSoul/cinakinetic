import streamlit as st
from streamlit_drawable_canvas import st_canvas
import cv2
import numpy as np
from PIL import Image, ImageOps
import base64
import io
from typing import Optional, Tuple
import json

class SketchInterface:
    def __init__(self):
        self.canvas_width = 512
        self.canvas_height = 512
        self.drawing_mode = "freedraw"
        
    def create_drawing_canvas(self, key_suffix=""):
        """Create an interactive drawing canvas"""
        
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col1:
            st.subheader("Drawing Tools")
            
            # Drawing mode
            drawing_mode = st.selectbox(
                "Drawing Mode",
                ["freedraw", "line", "rect", "circle", "transform"],
                key=f"drawing_mode_{key_suffix}"
            )
            
            # Stroke settings
            stroke_width = st.slider("Stroke Width", 1, 25, 3, key=f"stroke_width_{key_suffix}")
            stroke_color = st.color_picker("Stroke Color", "#000000", key=f"stroke_color_{key_suffix}")
            
            # Canvas size
            canvas_size = st.selectbox(
                "Canvas Size",
                ["512x512", "768x768", "1024x1024"],
                key=f"canvas_size_{key_suffix}"
            )
            width, height = map(int, canvas_size.split('x'))
            
            # Quick actions
            if st.button("Clear Canvas", key=f"clear_{key_suffix}"):
                st.rerun()
            
            # Template sketches
            st.subheader("Action Templates")
            
            template_options = {
                "Blank": None,
                "Car Chase Layout": "car_chase_template",
                "Fight Scene Poses": "fight_template", 
                "Explosion Composition": "explosion_template"
            }
            
            selected_template = st.selectbox(
                "Load Template",
                list(template_options.keys()),
                key=f"template_{key_suffix}"
            )
            
        with col2:
            st.subheader("Sketch Canvas")
            
            # Create background image
            bg_image = None
            if selected_template != "Blank":
                bg_image = self._get_template_image(template_options[selected_template], width, height)
            
            # Canvas component
            canvas_result = st_canvas(
                fill_color="rgba(255, 255, 255, 0)",
                stroke_width=stroke_width,
                stroke_color=stroke_color,
                background_color="#FFFFFF",
                background_image=bg_image,
                update_streamlit=True,
                width=width,
                height=height,
                drawing_mode=drawing_mode,
                point_display_radius=0,
                key=f"canvas_{key_suffix}"
            )
            
        with col3:
            st.subheader("Processing")
            
            if canvas_result.image_data is not None:
                
                # Convert to different formats
                sketch_image = Image.fromarray(canvas_result.image_data.astype('uint8'), 'RGBA')
                
                # Preview options
                preview_type = st.selectbox(
                    "Preview Type",
                    ["Original", "Lineart", "Canny Edge", "Depth"],
                    key=f"preview_{key_suffix}"
                )
                
                processed_image = self._process_sketch(sketch_image, preview_type)
                st.image(processed_image, caption=f"{preview_type} Preview", use_container_width=True)
                
                # Control settings
                st.subheader("ControlNet Settings")
                control_strength = st.slider("Control Strength", 0.1, 2.0, 0.8, 0.1, key=f"control_strength_{key_suffix}")
                
                # Generate button
                if st.button("🎨 Generate from Sketch", type="primary", key=f"generate_{key_suffix}"):
                    return {
                        "sketch_data": canvas_result.image_data,
                        "processed_image": processed_image,
                        "control_type": preview_type.lower().replace(" ", ""),
                        "control_strength": control_strength,
                        "canvas_size": (width, height)
                    }
        
        return None
    
    def _get_template_image(self, template_name: str, width: int, height: int) -> Optional[Image.Image]:
        """Get template background image"""
        
        # Create simple template layouts
        img = Image.new('RGB', (width, height), 'white')
        
        if template_name == "car_chase_template":
            # Simple road layout
            from PIL import ImageDraw
            draw = ImageDraw.Draw(img)
            
            # Road lines
            road_y = height // 2
            draw.rectangle([0, road_y - 50, width, road_y + 50], fill='lightgray')
            
            # Lane dividers
            for x in range(0, width, 40):
                draw.rectangle([x, road_y - 2, x + 20, road_y + 2], fill='white')
            
            # Car outlines
            car_width, car_height = 60, 30
            draw.rectangle([100, road_y - car_height//2, 100 + car_width, road_y + car_height//2], outline='black', width=2)
            draw.rectangle([300, road_y - car_height//2, 300 + car_width, road_y + car_height//2], outline='black', width=2)
            
        elif template_name == "fight_template":
            # Simple stick figures for pose reference
            from PIL import ImageDraw
            draw = ImageDraw.Draw(img)
            
            # Ground line
            ground_y = height - 50
            draw.line([0, ground_y, width, ground_y], fill='lightgray', width=2)
            
            # Basic stick figure outlines
            self._draw_stick_figure(draw, 150, ground_y - 100, "fighting")
            self._draw_stick_figure(draw, 350, ground_y - 100, "fighting")
            
        elif template_name == "explosion_template":
            # Explosion composition guides
            from PIL import ImageDraw
            draw = ImageDraw.Draw(img)
            
            # Explosion center
            center_x, center_y = width // 2, height // 2
            
            # Radial guidelines
            for angle in range(0, 360, 45):
                end_x = center_x + 100 * np.cos(np.radians(angle))
                end_y = center_y + 100 * np.sin(np.radians(angle))
                draw.line([center_x, center_y, end_x, end_y], fill='lightblue', width=1)
            
            # Explosion shape guide
            draw.ellipse([center_x - 80, center_y - 80, center_x + 80, center_y + 80], outline='orange', width=2)
        
        return img
    
    def _draw_stick_figure(self, draw, x: int, y: int, pose: str):
        """Draw simple stick figure for pose reference"""
        
        # Head
        draw.ellipse([x - 10, y - 40, x + 10, y - 20], outline='black', width=2)
        
        # Body
        draw.line([x, y - 20, x, y + 20], fill='black', width=2)
        
        if pose == "fighting":
            # Fighting pose - arms up
            draw.line([x, y - 10, x - 20, y - 30], fill='black', width=2)  # Left arm
            draw.line([x, y - 10, x + 25, y - 15], fill='black', width=2)  # Right arm
            
            # Legs in stance
            draw.line([x, y + 20, x - 15, y + 50], fill='black', width=2)  # Left leg
            draw.line([x, y + 20, x + 10, y + 50], fill='black', width=2)   # Right leg
        else:
            # Normal pose
            draw.line([x, y - 10, x - 15, y + 10], fill='black', width=2)  # Left arm
            draw.line([x, y - 10, x + 15, y + 10], fill='black', width=2)  # Right arm
            draw.line([x, y + 20, x - 10, y + 50], fill='black', width=2)  # Left leg
            draw.line([x, y + 20, x + 10, y + 50], fill='black', width=2)  # Right leg
    
    def _process_sketch(self, image: Image.Image, process_type: str) -> Image.Image:
        """Process sketch into different control formats"""
        
        if process_type == "Original":
            return image
        
        # Convert to OpenCV format
        img_array = np.array(image.convert('RGB'))
        
        if process_type == "Lineart":
            # Simple edge detection
            gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
            edges = cv2.Canny(gray, 50, 150)
            edges = cv2.bitwise_not(edges)  # Invert for white background
            processed = cv2.cvtColor(edges, cv2.COLOR_GRAY2RGB)
            
        elif process_type == "Canny Edge":
            # Canny edge detection
            gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
            edges = cv2.Canny(gray, 100, 200)
            processed = cv2.cvtColor(edges, cv2.COLOR_GRAY2RGB)
            
        elif process_type == "Depth":
            # Simple depth simulation (darker = closer)
            gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
            # Simple depth effect - invert and blur
            depth = cv2.bitwise_not(gray)
            depth = cv2.GaussianBlur(depth, (5, 5), 0)
            processed = cv2.cvtColor(depth, cv2.COLOR_GRAY2RGB)
        
        else:
            processed = img_array
        
        return Image.fromarray(processed)
    
    def create_refinement_workflow(self, initial_result=None):
        """Create iterative refinement interface"""
        
        st.subheader("🔄 Iterative Refinement")
        
        if initial_result is None:
            st.info("Generate an initial image first to start refinement")
            return None
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Current Result**")
            if isinstance(initial_result, str):
                # If it's a file path or URL
                st.image(initial_result, caption="Current Generation")
            else:
                st.image(initial_result, caption="Current Generation")
            
            # Refinement options
            refinement_type = st.selectbox(
                "Refinement Type",
                ["Sketch Over", "Mask Edit", "Prompt Adjust", "Style Transfer"],
                key="refinement_type"
            )
            
            if refinement_type == "Sketch Over":
                st.write("Draw over the image to guide changes:")
                
                # Overlay canvas for sketching on top of result
                overlay_canvas = st_canvas(
                    fill_color="rgba(255, 0, 0, 0.3)",
                    stroke_width=3,
                    stroke_color="#FF0000",
                    background_color="rgba(0, 0, 0, 0)",
                    background_image=initial_result if isinstance(initial_result, Image.Image) else None,
                    update_streamlit=True,
                    width=512,
                    height=512,
                    drawing_mode="freedraw",
                    key="overlay_canvas"
                )
            
        with col2:
            st.write("**Refinement Controls**")
            
            # Refinement strength
            refine_strength = st.slider("Refinement Strength", 0.1, 1.0, 0.5, 0.1)
            
            # Additional prompt for refinement
            refine_prompt = st.text_area(
                "Additional Instructions",
                placeholder="Add more details, change lighting, adjust pose...",
                height=100
            )
            
            # Preserve areas
            preserve_composition = st.checkbox("Preserve Composition", value=True)
            preserve_colors = st.checkbox("Preserve Color Scheme", value=False)
            
            if st.button("🔄 Refine Image", type="primary"):
                return {
                    "type": refinement_type,
                    "strength": refine_strength,
                    "prompt": refine_prompt,
                    "preserve_composition": preserve_composition,
                    "preserve_colors": preserve_colors,
                    "overlay_data": overlay_canvas.image_data if refinement_type == "Sketch Over" else None
                }
        
        return None
    
    def image_to_base64(self, image: Image.Image) -> str:
        """Convert PIL Image to base64 string"""
        buffered = io.BytesIO()
        image.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        return img_str
    
    def create_controlnet_comparison(self, original_sketch, generated_results):
        """Show comparison of different ControlNet approaches"""
        
        st.subheader("🎯 ControlNet Comparison")
        
        if len(generated_results) == 0:
            st.info("Generate some results to see comparisons")
            return
        
        # Show results in grid
        cols = st.columns(min(len(generated_results), 4))
        
        for i, (control_type, result) in enumerate(generated_results.items()):
            with cols[i % 4]:
                st.image(result["image"], caption=f"{control_type.title()}")
                st.write(f"Strength: {result['strength']}")
                st.write(f"Time: {result.get('generation_time', 'N/A')}s")
                
                if st.button(f"Refine {control_type}", key=f"refine_{control_type}_{i}"):
                    st.session_state[f"refine_base_{control_type}"] = result