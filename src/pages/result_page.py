"""
result_page.py
---------------

This page presents the final classification result to the user.  It
displays the original image with the segmentation overlay, shows the
predicted clothing category along with the associated confidence score,
and offers the option to return to the start page to analyse another
outfit.
"""

from __future__ import annotations

import streamlit as st


def render() -> str | None:
    """
    Render the result page and return the next page id when done.

    This page presents the final classification and style prediction to
    the user.  It displays the face‑masked segmentation overlay, the
    predicted garment category and the high‑level style along with
    confidence scores.  It also provides an option to start over.
    """
    st.header("Fashion Police verdict")

    # Retrieve the data saved by the loader page.  We expect the
    # overlay image, classification label and score, and style
    # prediction to be present in the session state.  If any are
    # missing, instruct the user to restart.
    overlay = st.session_state.get("overlay_preview_image")
    garment_label = st.session_state.get("classification_label")
    garment_score = st.session_state.get("classification_score")
    style = st.session_state.get("predicted_style")
    style_score = st.session_state.get("predicted_style_score")
    if any(x is None for x in [overlay, garment_label, garment_score, style, style_score]):
        st.error(
            "Required data missing. Please start over by returning to the start page."
        )
        if st.button("🔙 Back to start"):
            # Clear all known keys to ensure a fresh start.
            for k in [
                "original_image_for_classification",
                "overlay_preview_image",
                "segmentation_mask",
                "clothing_crop",
                "classification_label",
                "classification_score",
                "predicted_style",
                "predicted_style_score",
            ]:
                st.session_state.pop(k, None)
            # Also remove the classifier so it can be re‑initialised.
            st.session_state.pop("classifier", None)
            return "start_page"
        return None

    # Display the segmentation overlay.  We use ``width="stretch"``
    # instead of the deprecated ``use_container_width``.  The caption
    # explains that the face has been masked for fairness.
    st.image(
        overlay,
        caption="Detected clothing highlighted (face masked for fairness)",
        width="stretch",
    )

    # Present the garment classification and style prediction.  We
    # emphasise the style since it is the main result.  Confidence
    # scores are displayed as percentages for readability.
    st.markdown(
        f"### 📌 Predicted garment:\n"
        f"<span style='font-size:1.5rem;font-weight:600'>{garment_label}</span><br>"
        f"Confidence: {garment_score * 100:.1f}%",
        unsafe_allow_html=True,
    )

    st.markdown(
        f"### 🎨 Style verdict:\n"
        f"<span style='font-size:2rem;font-weight:700;color:#ff4d4f'>{style}</span><br>"
        f"Confidence: {style_score * 100:.1f}%",
        unsafe_allow_html=True,
    )

    st.write(
        "The style prediction is based on the detected garments and the overall look. "
        "Results may vary depending on lighting, pose and how much of the outfit is visible."
    )

    # Provide a button to restart the process.  Reset all relevant
    # session state keys so the user can take a new photo.
    if st.button("🔁 Analyze another outfit"):
        for k in [
            "original_image_for_classification",
            "overlay_preview_image",
            "segmentation_mask",
            "clothing_crop",
            "classification_label",
            "classification_score",
            "predicted_style",
            "predicted_style_score",
        ]:
            st.session_state.pop(k, None)
        st.session_state.pop("classifier", None)
        return "start_page"
    return None