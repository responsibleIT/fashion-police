from __future__ import annotations

from io import BytesIO
from typing import Optional

import streamlit as st
from PIL import Image

from scripts.make_picture import uploaded_file_to_image
from scripts.load_model import SegmentationModel

def _pil_to_bytes(img: Image.Image) -> bytes:
    buf = BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def _clear_capture_state():
    """Reset session so user can retake cleanly."""
    for key in [
        "_last_capture_bytes",
        "original_image_for_classification",
        "overlay_preview_image",
        "segmentation_mask",
        "clothing_crop",
    ]:
        st.session_state.pop(key, None)
    st.session_state.pop("camera", None)  # reset the camera widget value


def render() -> str | None:
    # --- Cache/load the segmentation model once ---
    if "seg_model" not in st.session_state:
        st.session_state.seg_model = SegmentationModel()
    seg_model: SegmentationModel = st.session_state.seg_model

    # --- Outer wrapper with fixed max width so content is centered ---
    st.markdown("<div style='max-width:1100px; margin:0 auto;'>", unsafe_allow_html=True)

    # Side-by-side columns that match your paint sketch
    col_left, col_right = st.columns([1, 1], gap="large")

    # ================= LEFT COLUMN =================
    with col_left:
        st.markdown(
            "<div style='font-weight:600; margin-bottom:0.5rem;'>Your photo</div>",
            unsafe_allow_html=True,
        )

        captured_file = st.camera_input(
            label="Take a photo",
            label_visibility="collapsed",  # avoids empty-label warnings
            key="camera",
            help="Frame your outfit clearly, then click 'Take photo'.",
        )

        captured_img: Optional[Image.Image] = uploaded_file_to_image(captured_file)

        # If we just captured a new image, run segmentation once and stash state
        if captured_img is not None:
            img_bytes = _pil_to_bytes(captured_img)
            if st.session_state.get("_last_capture_bytes") != img_bytes:
                st.session_state["_last_capture_bytes"] = img_bytes
                try:
                    mask, overlay = seg_model.segment(captured_img)
                    crop = seg_model.extract_clothing_crop(captured_img, mask)

                    st.session_state["original_image_for_classification"] = captured_img
                    st.session_state["overlay_preview_image"] = overlay
                    st.session_state["segmentation_mask"] = mask
                    st.session_state["clothing_crop"] = crop
                except Exception as e:
                    st.error(f"Failed to segment image: {e}")

        # # Show the final still image we'll use downstream
        # if st.session_state.get("original_image_for_classification") is not None:
        #     st.image(
        #         st.session_state["original_image_for_classification"],
        #         caption="Captured photo",
        #         width=TARGET_DISPLAY_WIDTH,
        #     )
        # else:
        #     st.info(
        #         "Take a photo above. We'll show it here.",
        #         icon="📷",
        #     )

        # Retake button under LEFT column
        retake_disabled = st.session_state.get("original_image_for_classification") is None
        if st.button("🔄 Retake", disabled=retake_disabled, use_container_width=True):
            _clear_capture_state()
            st.rerun()

    # ================= RIGHT COLUMN =================
    with col_right:
        st.markdown(
            "<div style='font-weight:600; margin-bottom:0.5rem;'>Clothing highlight</div>",
            unsafe_allow_html=True,
        )

        if st.session_state.get("overlay_preview_image") is not None:
            st.image(
                st.session_state["overlay_preview_image"],
                caption="Detected clothing regions",
                width="content",
            )
        else:
            st.info(
                "After you snap a photo, we'll highlight just the clothing here.",
                icon="✨",
            )

        # Continue button under RIGHT column
        can_continue = st.session_state.get("overlay_preview_image") is not None
        if st.button(
            "✅ Continue",
            disabled=not can_continue,
            use_container_width=True,
        ):
            st.session_state.page = "loader_page"
            st.rerun()

    # Close wrapper
    st.markdown("</div>", unsafe_allow_html=True)

    # Critically, DO NOT render anything else below this point.
    # That prevents new rows from pushing content off-screen.
    return None
