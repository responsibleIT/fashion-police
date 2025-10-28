from __future__ import annotations
import streamlit as st
from PIL import Image

def render() -> str | None:
    # Check required session data
    if "evidence_image" not in st.session_state or "ranked_styles" not in st.session_state:
        st.error("Missing results. Please start over.")
        if st.button("⬅ Back to start"):
            # clean slate
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
        return None

    evidence_image = st.session_state["evidence_image"]
    ranked_styles = st.session_state["ranked_styles"]

    # pick top 3 styles for display
    top3 = ranked_styles[:3]

    # Layout: two columns
    left_col, right_col = st.columns([1,1], gap="large")

    with left_col:
        st.markdown(
            "<div style='font-weight:600; font-size:1.1rem; margin-bottom:0.5rem;'>Evidence photo 👇</div>",
            unsafe_allow_html=True,
        )
        st.image(
            evidence_image,
            caption="We focused on your clothing when predicting style.",
            use_column_width=True,
        )

        # Optionally: let them restart
        if st.button("🔄 Try another outfit", use_container_width=True):
            # reset app state for a new run
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
            st.session_state.page = "make_picture_page"
            return

    with right_col:
        st.markdown(
            "<div style='font-weight:600; font-size:1.1rem; margin-bottom:0.5rem;'>Your style vibe ✨</div>",
            unsafe_allow_html=True,
        )

        if len(top3) > 0:
            # Biggest / winner card
            best = top3[0]
            st.markdown(
                f"""
                <div style="
                    border:1px solid rgba(255,255,255,0.2);
                    border-radius:8px;
                    padding:0.75rem 1rem;
                    margin-bottom:1rem;
                    background:rgba(255,255,255,0.05);
                ">
                    <div style="font-size:0.8rem; color:#aaa;">Top match</div>
                    <div style="font-size:1.3rem; font-weight:600; margin:0.25rem 0 0.5rem 0;">
                        {best["name"]}
                    </div>
                    <div style="font-size:0.9rem; color:#ccc; margin-bottom:0.5rem;">
                        {best["desc"]}
                    </div>
                    <div style="font-size:0.8rem; color:#888;">
                        Match strength: {(best["score"]*100):.1f}%
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        # Runner-ups
        if len(top3) > 1:
            st.markdown(
                "<div style='font-size:0.8rem; font-weight:600; color:#aaa; margin-bottom:0.5rem;'>Also similar:</div>",
                unsafe_allow_html=True,
            )

        for alt in top3[1:]:
            st.markdown(
                f"""
                <div style="
                    border:1px solid rgba(255,255,255,0.15);
                    border-radius:6px;
                    padding:0.5rem 0.75rem;
                    margin-bottom:0.5rem;
                    background:rgba(255,255,255,0.02);
                ">
                    <div style="font-size:1rem; font-weight:600; margin-bottom:0.25rem;">
                        {alt["name"]}
                    </div>
                    <div style="font-size:0.8rem; color:#ccc; margin-bottom:0.25rem;">
                        {alt["desc"]}
                    </div>
                    <div style="font-size:0.7rem; color:#888;">
                        Match strength: {(alt["score"]*100):.1f}%
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown("</div>", unsafe_allow_html=True)
    return None
