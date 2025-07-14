# Add this to the main function after the hero video section

    # Featured Gallery Section
    st.markdown("## 🎨 Featured Action Scenes")
    st.markdown("*Professional quality results from our AI generation platform*")
    
    gallery_col1, gallery_col2, gallery_col3 = st.columns(3)
    
    with gallery_col1:
        st.image("https://picsum.photos/400/600?random=1", caption="🥊 Underground Fight Club")
        st.caption("Generated with: *Dark warehouse, two fighters, dramatic lighting, cinematic*")
    
    with gallery_col2:
        st.image("https://picsum.photos/400/600?random=2", caption="⚔️ Martial Arts Duel") 
        st.caption("Generated with: *Ancient temple, martial artists, dynamic poses, epic*")
    
    with gallery_col3:
        st.image("https://picsum.photos/400/600?random=3", caption="🏃 Rooftop Chase")
        st.caption("Generated with: *Night rooftop, action sequence, cinematic lighting*")
    
    # Call-to-action
    st.markdown("---")
    cta_col1, cta_col2, cta_col3 = st.columns([1, 2, 1])
    with cta_col2:
        st.markdown("### 🚀 Ready to Create Your Action Scenes?")
        if st.button("🎬 Start Generating Now", type="primary", key="main_cta"):
            st.balloons()
            st.success("🎉 Welcome to CinaKinetic! Use the sidebar to explore our professional tools.")
