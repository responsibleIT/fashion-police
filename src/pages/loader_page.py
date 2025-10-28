from __future__ import annotations
import streamlit as st
from scripts.classify_outfit import OutfitClassifier

def render() -> str | None:
    st.title("Classifying your outfit...")

    # Safety check: we need the captured photo from make_picture_page
    if "original_image_for_classification" not in st.session_state:
        st.error("No photo found in session. Please go back and take a picture.")
        if st.button("⬅ Back to start"):
            st.session_state.page = "start_page"
            return

    image = st.session_state["original_image_for_classification"]

    # Run model ONCE per session
    if "classification_done" not in st.session_state:
        try:
            classifier = OutfitClassifier()
            result = classifier.process(image)

            # Store results for the result_page
            st.session_state["evidence_image"] = result["evidence_image"]
            st.session_state["ranked_styles"] = result["ranked_styles"]

            st.session_state["classification_done"] = True

            # jump to result_page
            st.session_state.page = "result_page"
            return

        except Exception as e:
            st.error(f"Classification failed: {e}")
            if st.button("⬅ Back to start"):
                # it's safest to reset session if we blew up here
                for k in [
                    "classification_done",
                    "evidence_image",
                    "ranked_styles",
                    "original_image_for_classification",
                    "overlay_preview_image",
                    "segmentation_mask",
                    "clothing_crop",
                ]:
                    st.session_state.pop(k, None)
                st.session_state.page = "start_page"
                st.rerun()
            return None

    # Fallback: if classification_done is already set but we somehow didn't rerun yet,
    # just push to result_page.
    st.session_state.page = "result_page"
    st.rerun()
    return None
