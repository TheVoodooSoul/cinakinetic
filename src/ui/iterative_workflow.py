import streamlit as st
import uuid
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
import json
from PIL import Image, ImageDraw
import io
import base64

@dataclass
class WorkflowNode:
    id: str
    node_type: str  # sketch, edit, motion, combine
    inputs: Dict[str, Any]
    outputs: Dict[str, Any]
    position: Dict[str, float]
    connections: List[str]  # Connected node IDs
    settings: Dict[str, Any]
    status: str = "pending"  # pending, processing, completed, error

class IterativeWorkflow:
    """FloraFauna-style iterative workflow for action scenes"""
    
    def __init__(self):
        if 'workflow_nodes' not in st.session_state:
            st.session_state.workflow_nodes = {}
        if 'workflow_connections' not in st.session_state:
            st.session_state.workflow_connections = []
        if 'selected_node' not in st.session_state:
            st.session_state.selected_node = None
    
    def create_workflow_interface(self):
        """Main workflow interface"""
        
        st.markdown("### ⚡ Iterative Action Workflow")
        st.write("Create complex action sequences through iterative refinement")
        
        # Workflow controls
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("✏️ Add Sketch Node"):
                self._add_node("sketch")
        
        with col2:
            if st.button("🎨 Add Edit Node"):
                self._add_node("edit")
        
        with col3:
            if st.button("🎬 Add Motion Node"):
                self._add_node("motion")
        
        with col4:
            if st.button("🔗 Add Combine Node"):
                self._add_node("combine")
        
        # Workflow canvas
        self._render_workflow_canvas()
        
        # Node editor panel
        if st.session_state.selected_node:
            self._render_node_editor()
    
    def _add_node(self, node_type: str):
        """Add new node to workflow"""
        
        node_id = str(uuid.uuid4())[:8]
        
        node = WorkflowNode(
            id=node_id,
            node_type=node_type,
            inputs={},
            outputs={},
            position={"x": len(st.session_state.workflow_nodes) * 150, "y": 100},
            connections=[],
            settings=self._get_default_settings(node_type)
        )
        
        st.session_state.workflow_nodes[node_id] = node
        st.session_state.selected_node = node_id
        st.rerun()
    
    def _get_default_settings(self, node_type: str) -> Dict[str, Any]:
        """Get default settings for node type"""
        
        defaults = {
            "sketch": {
                "canvas_size": "512x512",
                "drawing_mode": "freedraw",
                "template": "blank",
                "control_type": "openpose"
            },
            "edit": {
                "edit_strength": 0.7,
                "preserve_composition": True,
                "edit_mode": "inpaint",
                "guidance_scale": 7.5
            },
            "motion": {
                "motion_type": "sequence",
                "frame_count": 8,
                "motion_strength": 0.8,
                "interpolation": "linear"
            },
            "combine": {
                "combination_mode": "sequence",
                "transition_type": "cut",
                "duration": 1.0
            }
        }
        
        return defaults.get(node_type, {})
    
    def _render_workflow_canvas(self):
        """Render the workflow canvas with nodes and connections"""
        
        st.markdown("#### Workflow Canvas")
        
        if not st.session_state.workflow_nodes:
            st.info("Add nodes to start building your workflow")
            return
        
        # Create visual representation
        canvas_html = self._generate_canvas_html()
        st.components.v1.html(canvas_html, height=400, scrolling=True)
        
        # Node list with status
        st.markdown("#### Node Status")
        cols = st.columns(min(len(st.session_state.workflow_nodes), 4))
        
        for i, (node_id, node) in enumerate(st.session_state.workflow_nodes.items()):
            with cols[i % 4]:
                status_emoji = {
                    "pending": "⏳",
                    "processing": "🔄", 
                    "completed": "✅",
                    "error": "❌"
                }.get(node.status, "⏳")
                
                if st.button(f"{status_emoji} {node.node_type.title()}\n{node_id}", key=f"select_{node_id}"):
                    st.session_state.selected_node = node_id
                    st.rerun()
    
    def _generate_canvas_html(self) -> str:
        """Generate HTML for workflow canvas visualization"""
        
        # Simple SVG-based visualization
        html = """
        <div style="background: #1e1e1e; border-radius: 8px; padding: 20px; overflow-x: auto;">
            <svg width="800" height="300" style="background: #2d2d2d; border-radius: 4px;">
        """
        
        # Draw nodes
        for node_id, node in st.session_state.workflow_nodes.items():
            x = node.position["x"]
            y = node.position["y"]
            
            color = {
                "sketch": "#4CAF50",
                "edit": "#2196F3", 
                "motion": "#FF9800",
                "combine": "#9C27B0"
            }.get(node.node_type, "#666")
            
            html += f"""
                <g>
                    <rect x="{x}" y="{y}" width="120" height="60" 
                          fill="{color}" rx="8" stroke="#fff" stroke-width="2"/>
                    <text x="{x + 60}" y="{y + 25}" text-anchor="middle" 
                          fill="white" font-size="12" font-weight="bold">
                        {node.node_type.upper()}
                    </text>
                    <text x="{x + 60}" y="{y + 40}" text-anchor="middle" 
                          fill="white" font-size="10">
                        {node_id}
                    </text>
                </g>
            """
        
        # Draw connections
        for connection in st.session_state.workflow_connections:
            from_node = st.session_state.workflow_nodes.get(connection["from"])
            to_node = st.session_state.workflow_nodes.get(connection["to"])
            
            if from_node and to_node:
                x1 = from_node.position["x"] + 120
                y1 = from_node.position["y"] + 30
                x2 = to_node.position["x"]
                y2 = to_node.position["y"] + 30
                
                html += f"""
                    <line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" 
                          stroke="#fff" stroke-width="2" marker-end="url(#arrowhead)"/>
                """
        
        html += """
                <defs>
                    <marker id="arrowhead" markerWidth="10" markerHeight="7" 
                            refX="9" refY="3.5" orient="auto">
                        <polygon points="0 0, 10 3.5, 0 7" fill="#fff"/>
                    </marker>
                </defs>
            </svg>
        </div>
        """
        
        return html
    
    def _render_node_editor(self):
        """Render editor for selected node"""
        
        node_id = st.session_state.selected_node
        node = st.session_state.workflow_nodes[node_id]
        
        st.markdown(f"#### {node.node_type.title()} Node Editor - {node_id}")
        
        with st.expander("Node Settings", expanded=True):
            if node.node_type == "sketch":
                self._render_sketch_editor(node)
            elif node.node_type == "edit":
                self._render_edit_editor(node)
            elif node.node_type == "motion":
                self._render_motion_editor(node)
            elif node.node_type == "combine":
                self._render_combine_editor(node)
        
        # Node actions
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("▶️ Process Node", type="primary"):
                self._process_node(node_id)
        
        with col2:
            if st.button("🔗 Connect To..."):
                self._show_connection_dialog(node_id)
        
        with col3:
            if st.button("🗑️ Delete Node"):
                self._delete_node(node_id)
    
    def _render_sketch_editor(self, node: WorkflowNode):
        """Render sketch node editor"""
        
        from .sketch_interface import SketchInterface
        
        st.write("**Initial Sketch Input**")
        
        # Canvas settings
        col1, col2 = st.columns(2)
        
        with col1:
            canvas_size = st.selectbox(
                "Canvas Size",
                ["512x512", "768x768", "1024x1024"],
                index=0,
                key=f"canvas_size_{node.id}"
            )
            node.settings["canvas_size"] = canvas_size
        
        with col2:
            template = st.selectbox(
                "Template",
                ["Blank", "Fight Scene Layout", "Car Chase", "Explosion"],
                key=f"template_{node.id}"
            )
            node.settings["template"] = template
        
        # Control type
        control_type = st.selectbox(
            "ControlNet Type",
            ["openpose", "canny", "depth", "lineart"],
            key=f"control_{node.id}"
        )
        node.settings["control_type"] = control_type
        
        # Sketch interface
        sketch_ui = SketchInterface()
        sketch_result = sketch_ui.create_drawing_canvas(f"node_{node.id}")
        
        if sketch_result:
            node.outputs["sketch_data"] = sketch_result
            node.status = "completed"
            st.success("✅ Sketch captured!")
    
    def _render_edit_editor(self, node: WorkflowNode):
        """Render edit node editor"""
        
        st.write("**Image Editing Settings**")
        
        # Input source
        input_options = self._get_available_inputs(node.id, ["sketch", "edit", "motion"])
        
        if input_options:
            selected_input = st.selectbox(
                "Input Source",
                list(input_options.keys()),
                key=f"input_{node.id}"
            )
            node.inputs["source"] = selected_input
        else:
            st.warning("No available inputs. Connect a sketch or previous edit node.")
            return
        
        # Edit settings
        col1, col2 = st.columns(2)
        
        with col1:
            edit_mode = st.selectbox(
                "Edit Mode",
                ["inpaint", "img2img", "controlnet", "outpaint"],
                key=f"edit_mode_{node.id}"
            )
            node.settings["edit_mode"] = edit_mode
            
            edit_strength = st.slider(
                "Edit Strength",
                0.1, 1.0, 0.7, 0.1,
                key=f"edit_strength_{node.id}"
            )
            node.settings["edit_strength"] = edit_strength
        
        with col2:
            preserve_composition = st.checkbox(
                "Preserve Composition",
                value=True,
                key=f"preserve_{node.id}"
            )
            node.settings["preserve_composition"] = preserve_composition
            
            guidance_scale = st.slider(
                "Guidance Scale",
                1.0, 20.0, 7.5, 0.5,
                key=f"guidance_{node.id}"
            )
            node.settings["guidance_scale"] = guidance_scale
        
        # Edit prompt
        edit_prompt = st.text_area(
            "Edit Instructions",
            placeholder="Describe what to change: adjust pose, add effects, change lighting...",
            key=f"edit_prompt_{node.id}"
        )
        node.settings["edit_prompt"] = edit_prompt
        
        # Mask/region selection would go here
        if edit_mode == "inpaint":
            st.info("🎨 Draw on the image above to mark areas to edit")
    
    def _render_motion_editor(self, node: WorkflowNode):
        """Render motion node editor"""
        
        st.write("**Motion Sequence Settings**")
        
        # Input source
        input_options = self._get_available_inputs(node.id, ["sketch", "edit"])
        
        if not input_options:
            st.warning("Connect an image source first")
            return
        
        selected_input = st.selectbox(
            "Input Source",
            list(input_options.keys()),
            key=f"motion_input_{node.id}"
        )
        node.inputs["source"] = selected_input
        
        # Motion settings
        col1, col2 = st.columns(2)
        
        with col1:
            motion_type = st.selectbox(
                "Motion Type",
                ["Fight Sequence", "Chase Scene", "Explosion", "Camera Movement"],
                key=f"motion_type_{node.id}"
            )
            node.settings["motion_type"] = motion_type
            
            frame_count = st.slider(
                "Frame Count",
                4, 16, 8,
                key=f"frames_{node.id}"
            )
            node.settings["frame_count"] = frame_count
        
        with col2:
            motion_strength = st.slider(
                "Motion Intensity",
                0.1, 1.0, 0.8, 0.1,
                key=f"motion_strength_{node.id}"
            )
            node.settings["motion_strength"] = motion_strength
            
            interpolation = st.selectbox(
                "Interpolation",
                ["linear", "ease_in", "ease_out", "bounce"],
                key=f"interpolation_{node.id}"
            )
            node.settings["interpolation"] = interpolation
        
        # Motion prompt
        motion_prompt = st.text_area(
            "Motion Description",
            placeholder="Describe the motion: punch sequence, kick combo, dodging...",
            key=f"motion_prompt_{node.id}"
        )
        node.settings["motion_prompt"] = motion_prompt
    
    def _render_combine_editor(self, node: WorkflowNode):
        """Render combine node editor"""
        
        st.write("**Scene Combination Settings**")
        
        # Multiple input sources
        available_nodes = self._get_available_inputs(node.id, ["sketch", "edit", "motion"])
        
        if len(available_nodes) < 2:
            st.warning("Need at least 2 input sources to combine")
            return
        
        # Input selection
        selected_inputs = st.multiselect(
            "Input Sources",
            list(available_nodes.keys()),
            key=f"combine_inputs_{node.id}"
        )
        node.inputs["sources"] = selected_inputs
        
        # Combination settings
        col1, col2 = st.columns(2)
        
        with col1:
            combination_mode = st.selectbox(
                "Combination Mode",
                ["Sequence", "Grid", "Overlay", "Transition"],
                key=f"combine_mode_{node.id}"
            )
            node.settings["combination_mode"] = combination_mode
            
            if combination_mode == "Sequence":
                transition_type = st.selectbox(
                    "Transition",
                    ["Cut", "Fade", "Dissolve", "Wipe"],
                    key=f"transition_{node.id}"
                )
                node.settings["transition_type"] = transition_type
        
        with col2:
            duration = st.slider(
                "Duration (seconds)",
                0.5, 5.0, 1.0, 0.5,
                key=f"duration_{node.id}"
            )
            node.settings["duration"] = duration
            
            if combination_mode == "Grid":
                grid_size = st.selectbox(
                    "Grid Layout",
                    ["2x2", "3x1", "2x3", "1x4"],
                    key=f"grid_{node.id}"
                )
                node.settings["grid_size"] = grid_size
    
    def _get_available_inputs(self, current_node_id: str, node_types: List[str]) -> Dict[str, str]:
        """Get available input nodes"""
        
        available = {}
        
        for node_id, node in st.session_state.workflow_nodes.items():
            if node_id != current_node_id and node.node_type in node_types and node.status == "completed":
                available[f"{node.node_type}_{node_id}"] = node_id
        
        return available
    
    def _process_node(self, node_id: str):
        """Process a workflow node"""
        
        node = st.session_state.workflow_nodes[node_id]
        node.status = "processing"
        
        try:
            if node.node_type == "sketch":
                # Sketch is processed in real-time
                if node.outputs.get("sketch_data"):
                    node.status = "completed"
                    st.success("✅ Sketch node processed")
            
            elif node.node_type == "edit":
                # Would call edit processing
                st.info("🎨 Processing edit node...")
                # Simulate processing
                import time
                time.sleep(1)
                node.status = "completed"
                st.success("✅ Edit node processed")
            
            elif node.node_type == "motion":
                # Would call motion generation
                st.info("🎬 Generating motion sequence...")
                time.sleep(2)
                node.status = "completed"
                st.success("✅ Motion sequence generated")
            
            elif node.node_type == "combine":
                # Would call combination processing
                st.info("🔗 Combining scenes...")
                time.sleep(1)
                node.status = "completed"
                st.success("✅ Scenes combined")
        
        except Exception as e:
            node.status = "error"
            st.error(f"❌ Processing failed: {e}")
        
        st.rerun()
    
    def _show_connection_dialog(self, node_id: str):
        """Show dialog to connect nodes"""
        
        other_nodes = {nid: node for nid, node in st.session_state.workflow_nodes.items() if nid != node_id}
        
        if not other_nodes:
            st.warning("No other nodes to connect to")
            return
        
        target_node = st.selectbox(
            "Connect to:",
            list(other_nodes.keys()),
            format_func=lambda x: f"{other_nodes[x].node_type}_{x}"
        )
        
        if st.button("Create Connection"):
            connection = {"from": node_id, "to": target_node}
            st.session_state.workflow_connections.append(connection)
            st.success("✅ Connection created")
            st.rerun()
    
    def _delete_node(self, node_id: str):
        """Delete a node and its connections"""
        
        # Remove node
        del st.session_state.workflow_nodes[node_id]
        
        # Remove connections
        st.session_state.workflow_connections = [
            conn for conn in st.session_state.workflow_connections 
            if conn["from"] != node_id and conn["to"] != node_id
        ]
        
        # Clear selection
        st.session_state.selected_node = None
        
        st.success("✅ Node deleted")
        st.rerun()
    
    def export_workflow(self) -> Dict:
        """Export workflow configuration"""
        
        return {
            "nodes": {nid: asdict(node) for nid, node in st.session_state.workflow_nodes.items()},
            "connections": st.session_state.workflow_connections
        }
    
    def import_workflow(self, workflow_data: Dict):
        """Import workflow configuration"""
        
        st.session_state.workflow_nodes = {
            nid: WorkflowNode(**node_data) 
            for nid, node_data in workflow_data["nodes"].items()
        }
        st.session_state.workflow_connections = workflow_data["connections"]