from __future__ import annotations

import streamlit as st

from data.styles import STYLE_NAMES
from scripts.data_storage import DataStorage


def render() -> None:
    """Correct me if I am wrong page - placeholder for future functionality."""
    st.title("Correct me if I am wrong")
    
    # Two-column layout: image on left, buttons on right
    col_left, col_right = st.columns([1, 1], gap="large")
    
    # LEFT COLUMN: Display the person's image
    with col_left:
        if "evidence_image" in st.session_state:
            st.image(
                st.session_state["evidence_image"],
                caption="Your outfit",
                use_column_width=True,
            )
        elif "original_image_for_classification" in st.session_state:
            st.image(
                st.session_state["original_image_for_classification"],
                caption="Your outfit",
                use_column_width=True,
            )
        else:
            st.warning("No image available. Please start over.")
    
    # RIGHT COLUMN: Style selection buttons
    with col_right:
        st.subheader("What style do you think this is?")
        st.write("Select the style that best matches your outfit:")
        
        # Get styles from centralized data file
        styles = STYLE_NAMES
        
        # Create buttons in a vertical list (full width in right column)
        for style in styles:
            if st.button(style, use_container_width=True, key=f"style_{style}"):
                # Save user input to data storage
                st.session_state["user_selected_style"] = style
                
                # Update the record with user input if we have a record_id
                if "current_record_id" in st.session_state:
                    storage = DataStorage()
                    storage.update_user_input(
                        st.session_state["current_record_id"],
                        style
                    )
                    st.success(f"✅ Saved! You selected: {style}")
                    st.balloons()
    
    st.markdown("---")
    
    # Back button to return to start
    if st.button("← Back to Start", use_container_width=True):
        # Clear all session state data for a fresh start
        for k in [
            "classification_done",
            "evidence_image",
            "ranked_styles",
            "original_image_for_classification",
            "overlay_preview_image",
            "segmentation_mask",
            "clothing_crop",
            "current_record_id",
            "user_selected_style",
            "_last_capture_bytes",
        ]:
            st.session_state.pop(k, None)
        st.session_state.page = "start_page"
        return
