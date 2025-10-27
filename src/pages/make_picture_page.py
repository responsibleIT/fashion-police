"""
make_picture_page.py
--------------------

This module implements the page where the user captures their outfit
photo.  After taking a picture with ``st.camera_input`` the page
performs semantic segmentation to highlight the clothing region and
provides a preview.  The user can then choose to retake the photo or
continue to the next step for classification and style prediction.

The page stores intermediate results in ``st.session_state`` under
well‑defined keys:

``original_image_for_classification``
    The full resolution PIL image captured from the camera.

``overlay_preview_image``
    A PIL image showing the segmentation mask blended with the
    original.  Faces are not yet masked here; masking happens in
    ``OutfitClassifier.process``.

``segmentation_mask``
    The raw segmentation mask as a 2‑D numpy array (optional but
    preserved for debugging or potential future use).

``clothing_crop``
    The cropped clothing region extracted from the original image.  This
    is not directly used by the style predictor but may be useful for
    display or extensions.

On clicking **Continue** the page sets ``st.session_state.page`` to
``"loader_page"`` and triggers a rerun.  The loader page then performs
classification and style prediction.
"""

from __future__ import annotations

from io import BytesIO
from typing import Optional

import streamlit as st
from PIL import Image

from scripts.make_picture import uploaded_file_to_image
from scripts.load_model import SegmentationModel


def _pil_to_bytes(img: Image.Image) -> bytes:
    """Serialize a PIL image to bytes so it can be compared between reruns."""
    buf = BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def render() -> str | None:
    """
    Render the picture taking page and handle user interactions.

    Returns
    -------
    str | None
        The next page id (``"loader_page"``) when the user clicks
        continue, or ``None`` to stay on the current page.
    """
    # Wide layout provides more room for side‑by‑side previews.
    st.set_page_config(layout="wide")

    st.markdown(
        """
        <div style="max-width:1000px;margin:0 auto;">
          <h2 style="margin-bottom:0.25rem;">Capture your outfit 👕</h2>
          <ol style="margin-top:0.25rem; line-height:1.5;">
            <li>Take a photo with your webcam.</li>
            <li>We'll segment the clothing and show a preview.</li>
            <li>If you're happy, press <b>Continue</b> to classify your outfit and predict a style.</li>
          </ol>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Lazily create and cache the segmentation model.  Loading the
    # SegFormer weights only once reduces latency on reruns.
    if "seg_model" not in st.session_state:
        st.session_state.seg_model = SegmentationModel()
    seg_model: SegmentationModel = st.session_state.seg_model

    # Display the camera widget.  Each time the user captures a photo
    # the widget returns an UploadedFile which we convert to a PIL image.
    captured_file = st.camera_input("Take a picture", key="camera")
    captured_img: Optional[Image.Image] = uploaded_file_to_image(captured_file)

    # If a new photo was captured, run segmentation and update state.
    if captured_img is not None:
        # We compare the raw bytes of the new image with the previous
        # captured image to avoid unnecessary segmentation work.  This
        # prevents recomputation when Streamlit reruns the script for
        # unrelated reasons (e.g. button clicks).
        img_bytes = _pil_to_bytes(captured_img)
        if st.session_state.get("_last_capture_bytes") != img_bytes:
            st.session_state._last_capture_bytes = img_bytes
            try:
                mask, overlay = seg_model.segment(captured_img)
                crop = seg_model.extract_clothing_crop(captured_img, mask)
                # Store the raw inputs for later use in the loader page.
                st.session_state.original_image_for_classification = captured_img
                st.session_state.overlay_preview_image = overlay
                st.session_state.segmentation_mask = mask
                st.session_state.clothing_crop = crop
            except Exception as e:
                st.error(f"Failed to segment image: {e}")

    # If we have a preview available, display it alongside the camera.
    if st.session_state.get("overlay_preview_image") is not None:
        # Use a container to align columns neatly.
        container = st.container()
        with container:
            col_left, col_right = st.columns(2)
            with col_left:
                st.subheader("Your photo")
                # Show the captured image.  If the user hasn't taken a
                # picture yet this will be None and nothing will be
                # displayed.
                if st.session_state.get("original_image_for_classification") is not None:
                    st.image(
                        st.session_state.original_image_for_classification,
                        caption="Captured photo",
                        width=500,
                    )
            with col_right:
                st.subheader("Segmentation preview")
                st.image(
                    st.session_state.overlay_preview_image,
                    caption="Detected clothing highlighted",
                    width=500,
                )

        # Action buttons presented below the preview.  We separate the
        # buttons from the preview to avoid layout wrapping.
        st.markdown(
            "<div style='height:1rem'></div>", unsafe_allow_html=True
        )
        col_ret, col_cont = st.columns([1, 1])
        with col_ret:
            if st.button("🔄 Retake", use_container_width=True):
                # Clear all capture‑related state and remove the camera
                # widget value so the user can take a fresh photo.
                for key in [
                    "_last_capture_bytes",
                    "original_image_for_classification",
                    "overlay_preview_image",
                    "segmentation_mask",
                    "clothing_crop",
                ]:
                    st.session_state.pop(key, None)
                # Reset the camera widget state.
                st.session_state.pop("camera", None)
                st.rerun()
        with col_cont:
            can_continue = st.session_state.get("overlay_preview_image") is not None
            if st.button("✅ Continue", use_container_width=True, disabled=not can_continue):
                # Navigate to the loader page.  We set the page in
                # session_state and trigger a rerun.  The loader page
                # will read the stored image and perform classification.
                st.session_state.page = "loader_page"
                st.rerun()

    return None