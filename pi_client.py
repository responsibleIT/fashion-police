"""
Pi Client - Minimal version with dummy server response.
Only runs camera capture and displays mock results.
"""

from __future__ import annotations

import streamlit as st
import time
from PIL import Image
import io

st.set_page_config(page_title="Fashion Police - Pi Client", layout="wide")


def get_dummy_response() -> dict:
    """
    Dummy server response for testing.
    Replace this with actual API call later.
    """
    time.sleep(2)  # Simulate server processing time
    
    return {
        "record_id": "dummy_123456",
        "predictions": [
            {
                "name": "Urban Streetwear",
                "description": "Casual streetwear outfit with hoodies, relaxed fit, sneakers, sporty energy.",
                "confidence": 0.82
            },
            {
                "name": "Casual Chic",
                "description": "Clean modern casual outfit: simple basics styled in a polished way.",
                "confidence": 0.65
            },
            {
                "name": "Sporty / Athleisure",
                "description": "Athletic activewear look: sportswear, gym-ready vibe.",
                "confidence": 0.58
            }
        ],
        "top_prediction": {
            "name": "Urban Streetwear",
            "description": "Casual streetwear outfit with hoodies, relaxed fit, sneakers, sporty energy.",
            "confidence": 0.82
        }
    }


def send_feedback(record_id: str, user_style: str) -> bool:
    """
    Dummy feedback function.
    Replace with actual API call later.
    """
    time.sleep(0.5)  # Simulate network delay
    return True


def main():
    # Initialize session state
    if "page" not in st.session_state:
        st.session_state.page = "camera"
    if "result" not in st.session_state:
        st.session_state.result = None
    if "captured_image" not in st.session_state:
        st.session_state.captured_image = None
    
    # Page: Camera
    if st.session_state.page == "camera":
        st.title("👮 Fashion Police")
        st.write("Take a photo of your outfit to get style predictions!")
        
        # Camera input
        img_file = st.camera_input("Take a photo")
        
        if img_file is not None:
            captured_image = Image.open(img_file)
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.image(captured_image, caption="Your photo", use_column_width=True)
            
            with col2:
                if st.button("✅ Analyze Style", use_container_width=True, type="primary"):
                    st.session_state.captured_image = captured_image
                    
                    with st.spinner("🔄 Processing (dummy mode)..."):
                        result = get_dummy_response()
                    
                    if result:
                        st.session_state.result = result
                        st.session_state.page = "results"
                        st.rerun()
    
    # Page: Results
    elif st.session_state.page == "results":
        result = st.session_state.result
        captured_image = st.session_state.captured_image
        
        if result is None:
            st.error("No results available")
            st.session_state.page = "camera"
            st.rerun()
            return
        
        st.title("Your Style Results ✨")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Your Photo")
            if captured_image:
                st.image(captured_image, use_column_width=True)
            
            if st.button("📸 Take Another Photo", use_container_width=True):
                st.session_state.page = "camera"
                st.session_state.result = None
                st.session_state.captured_image = None
                st.rerun()
        
        with col2:
            st.subheader("Top Prediction")
            top = result["top_prediction"]
            
            st.markdown(f"""
            <div style="
                border:2px solid rgba(0,255,0,0.5);
                border-radius:8px;
                padding:1rem;
                margin-bottom:1rem;
                background:rgba(0,255,0,0.1);
            ">
                <h2>{top['name']}</h2>
                <p>{top['description']}</p>
                <p><strong>Confidence:</strong> {top['confidence']*100:.1f}%</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.subheader("Other Matches")
            for pred in result["predictions"][1:4]:
                st.markdown(f"""
                <div style="
                    border:1px solid rgba(255,255,255,0.2);
                    border-radius:6px;
                    padding:0.5rem;
                    margin-bottom:0.5rem;
                ">
                    <strong>{pred['name']}</strong> - {pred['confidence']*100:.1f}%
                </div>
                """, unsafe_allow_html=True)
            
            if st.button("❓ Correct me if I am wrong", use_container_width=True):
                st.session_state.page = "feedback"
                st.rerun()
    
    # Page: Feedback
    elif st.session_state.page == "feedback":
        st.title("What style do you think this is?")
        
        result = st.session_state.result
        captured_image = st.session_state.captured_image
        
        # Style options
        styles = [
            "Urban Streetwear", "Formal Business", "Casual Chic",
            "Sporty / Athleisure", "Vintage / Retro", "Bohemian",
            "Elegant Evening", "Preppy", "Punk / Alt", "Gothic",
            "Artsy / Expressive"
        ]
        
        col1, col2 = st.columns(2)
        
        with col1:
            if captured_image:
                st.image(captured_image, use_column_width=True)
        
        with col2:
            for style in styles:
                if st.button(style, use_container_width=True, key=f"style_{style}"):
                    success = send_feedback(result["record_id"], style)
                    if success:
                        st.success(f"✅ Saved! You selected: {style}")
                        st.balloons()
        
        st.markdown("---")
        if st.button("← Back to Results", use_container_width=True):
            st.session_state.page = "results"
            st.rerun()


if __name__ == "__main__":
    main()
