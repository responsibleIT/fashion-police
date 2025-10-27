"""
loader_page.py
----------------

This page displays a loading indicator while the outfit classification
is being performed.  It retrieves the previously captured image and
segmentation outputs from ``st.session_state``, instantiates the
OutfitClassifier (if not already done), and performs classification on
the cropped clothing region.  Upon completion it stores the results
back into the session state and instructs the app to navigate to the
result page.
"""

from __future__ import annotations

import streamlit as st
from PIL import Image  # type: ignore

from scripts.classify_outfit import OutfitClassifier


def render() -> str | None:
    """
    Render the loader page and perform the full outfit classification.

    This page retrieves the previously captured image from the session
    state, instantiates (or reuses) an ``OutfitClassifier``, and runs
    the full pipeline to segment the image, classify the garment and
    predict the high‑level style.  The results are stored back into
    ``st.session_state`` for display on the result page.

    Returns
    -------
    str | None
        The next page id (``"result_page"``) when classification
        completes successfully, or ``None`` if an error occurred.
    """
    st.header("Classifying your outfit…")

    # Retrieve the original photo captured on the previous page.  We
    # ensure that the image exists before proceeding.  The key
    # ``original_image_for_classification`` is set by ``make_picture_page.py``.
    image: Image.Image | None = st.session_state.get("original_image_for_classification")
    if image is None:
        st.error(
            "No image found in session. Please return to the previous page and take a picture."
        )
        return None

    # Instantiate the classifier lazily and cache it in session state.
    # This avoids re‑loading large models on every rerun.
    if "classifier" not in st.session_state:
        st.session_state.classifier = OutfitClassifier()
    classifier: OutfitClassifier = st.session_state.classifier

    # Run the pipeline inside a spinner to give visual feedback to the user.
    with st.spinner("Analyzing your outfit… this may take a few seconds…"):
        try:
            result = classifier.process(image)
        except Exception as e:
            st.error(f"An error occurred during classification: {e}")
            return None

    # Persist the results in session_state for the result page.  We
    # include the overlay, garment label, garment score, predicted
    # style and style score.  The original overlay (with segmentation
    # colours) is used for visualisation.  We also keep the mask and
    # cropped region should the result page or future features need
    # access to them.
    st.session_state.overlay_preview_image = result.get("overlay")
    st.session_state.classification_label = result.get("label")
    st.session_state.classification_score = result.get("score")
    st.session_state.predicted_style = result.get("style")
    st.session_state.predicted_style_score = result.get("style_score")
    st.session_state.segmentation_mask = result.get("mask")
    st.session_state.clothing_crop = result.get("cropped")

    # Automatically proceed to the result page.
    return "result_page"