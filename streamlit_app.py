#!/usr/bin/env python3
"""
CinaKinetic.com - Cinema Action Scene Generator
Vercel-optimized entry point
"""

import streamlit as st
import sys
import os
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Configure Streamlit for production
st.set_page_config(
    page_title="CinaKinetic - Cinema Action Scene Generator",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://cinakinetic.com/help',
        'Report a bug': 'https://cinakinetic.com/support',
        'About': """
        # CinaKinetic.com
        
        **Cinema Action Scene Generator**
        
        Create professional action sequences with AI:
        - Character consistency with LoRA training
        - R-rated cinematic violence
        - Fighting style choreography
        - Text-to-video generation
        - Professional storyboard export
        
        Powered by RunPod RTX 6000 Ada
        """
    }
)

# Custom CSS for CinaKinetic branding
st.markdown("""
<style>
    /* CinaKinetic Custom Styling */
    .stApp {
        background: linear-gradient(135deg, #0C0C0C 0%, #1A1A1A 100%);
    }
    
    .main-header {
        background: linear-gradient(90deg, #FF4444 0%, #FF8844 50%, #FFAA44 100%);
        padding: 1rem 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        text-align: center;
        box-shadow: 0 4px 20px rgba(255, 68, 68, 0.3);
    }
    
    .main-header h1 {
        color: white;
        margin: 0;
        font-size: 2.5rem;
        font-weight: 700;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
    }
    
    .main-header p {
        color: rgba(255,255,255,0.9);
        margin: 0.5rem 0 0 0;
        font-size: 1.1rem;
    }
    
    .feature-card {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 68, 68, 0.3);
        border-radius: 10px;
        padding: 1.5rem;
        margin: 1rem 0;
        backdrop-filter: blur(10px);
    }
    
    .metric-card {
        background: linear-gradient(135deg, #FF4444 0%, #FF6644 100%);
        color: white;
        padding: 1rem;
        border-radius: 8px;
        text-align: center;
        margin: 0.5rem 0;
    }
    
    .stSelectbox > div > div {
        background-color: rgba(255, 255, 255, 0.1);
        border: 1px solid rgba(255, 68, 68, 0.3);
    }
    
    .stButton > button {
        background: linear-gradient(90deg, #FF4444 0%, #FF6644 100%);
        color: white;
        border: none;
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        background: linear-gradient(90deg, #FF6644 0%, #FF8844 100%);
        box-shadow: 0 4px 15px rgba(255, 68, 68, 0.4);
        transform: translateY(-2px);
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Custom footer */
    .custom-footer {
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        background: rgba(12, 12, 12, 0.95);
        padding: 0.5rem;
        text-align: center;
        font-size: 0.8rem;
        color: rgba(255, 255, 255, 0.6);
        z-index: 999;
    }
</style>
""", unsafe_allow_html=True)

def main():
    """Main application entry point"""
    
    # CinaKinetic header
    st.markdown("""
    <div class="main-header">
        <h1>🎬 CinaKinetic</h1>
        <p>Cinema Action Scene Generator - Create Epic Action Sequences with AI</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Check if user is authenticated
    try:
        from src.auth.auth_system import AuthSystem
        
        auth = AuthSystem()
        
        if not auth.create_auth_interface():
            return  # Show login page
        
        # Add user sidebar
        auth.create_user_sidebar()
        
    except Exception as e:
        st.error(f"Authentication system error: {e}")
        st.info("Running in development mode without authentication")
    
    # Load main application
    try:
        from src.ui.production_interface import create_production_interface
        
        # Main application interface
        create_production_interface()
        
    except Exception as e:
        st.error(f"Application error: {e}")
        st.info("Please check the server logs for more details")
    
    # Custom footer
    st.markdown("""
    <div class="custom-footer">
        © 2024 CinaKinetic.com - Powered by RunPod RTX 6000 Ada • 
        <a href="https://cinakinetic.com/privacy" style="color: #FF6644;">Privacy</a> • 
        <a href="https://cinakinetic.com/terms" style="color: #FF6644;">Terms</a> • 
        <a href="https://cinakinetic.com/support" style="color: #FF6644;">Support</a>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()