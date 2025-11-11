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
    # reset camera widget content so they can re-capture
    st.session_state.pop("camera", None)


def render() -> None:
    # -------- Style tweaks so the camera & preview fill their columns nicely --------
    st.markdown(
        """
        <style>
        /* Keep the camera widget from exploding vertically, but allow width to fill column */
        div[data-testid="stCameraInput"] video,
        div[data-testid="stCameraInput"] canvas {
            max-height: 1700px !important;
            width: 100% !important;
            object-fit: cover !important;
        }
        div[data-testid="stCameraInput"] > div {
            width: 100% !important;
            max-width: 100% !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # -------- Lazy-load (cache-ish) segmentation model in session --------
    if "seg_model" not in st.session_state:
        st.session_state.seg_model = SegmentationModel()
    seg_model: SegmentationModel = st.session_state.seg_model

    # -------- Two columns, side by side --------
    # st.markdown("<div style='max-width:1100px; margin:0 auto;'>", unsafe_allow_html=True)
    col_left, col_right = st.columns(2, gap="large")

    # ================= LEFT COLUMN =================
    with col_left:
        st.markdown(
            "<div style='font-weight:600; margin-bottom:0.5rem;'>Your photo</div>",
            unsafe_allow_html=True,
        )

        # live camera widget
        captured_file = st.camera_input(
            label="Take a photo",
            label_visibility="collapsed",
            key="camera",
            help="Line up your outfit and click 'Take photo'.",
        )

        captured_img: Optional[Image.Image] = uploaded_file_to_image(captured_file)

        # Process new capture once
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

        # Retake / Clear button under LEFT column
        retake_disabled = st.session_state.get("original_image_for_classification") is None
        if st.button(
            "❌ Clear photo",
            disabled=retake_disabled,
            use_container_width=True,
        ):
            _clear_capture_state()
            st.session_state.page = "make_picture_page"
            return  # app.py will rerun after this

    # ================= RIGHT COLUMN =================
    with col_right:
        st.markdown(
            "<div style='font-weight:600; margin-bottom:0.5rem;'>Clothing highlight</div>",
            unsafe_allow_html=True,
        )

        overlay_img = st.session_state.get("overlay_preview_image")

        if overlay_img is not None:
            st.image(
                overlay_img,
                use_column_width=True,  # <-- fill the right column width
            )
        else:
            st.info(
                "After you take a photo, we'll highlight only the clothing here.",
                icon="✨",
            )

        # Continue button under RIGHT column
        can_continue = overlay_img is not None
        if st.button(
            "✅ Continue",
            disabled=not can_continue,
            use_container_width=True,
        ):
            # go to loader page; loader_page will do style prediction
            st.session_state.page = "loader_page"
            return  # app.py reruns

    # st.markdown("</div>", unsafe_allow_html=True)
    # IMPORTANT: no st.rerun() in this function; app.py handles reruns.
    return
