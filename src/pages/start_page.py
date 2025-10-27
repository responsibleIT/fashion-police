from __future__ import annotations
import streamlit as st

def render() -> str | None:
    # Hero block centered
    st.markdown(
        """
        <div style="
            max-width:700px;
            margin:2rem auto 3rem auto;
            text-align:center;
        ">
            <div style="font-size:2rem; font-weight:600;">👮‍♀️ Fashion Police</div>
            <p style="color:#ccc; line-height:1.5; font-size:1rem; margin-top:1rem;">
                We'll analyze your outfit, hide your face for fairness,
                and predict your fashion style (streetwear, formal, vintage, etc.).
                Everything runs locally.
            </p>
            <p style="color:#999; font-size:0.9rem;">
                Step 1: let us access your webcam.<br/>
                Step 2: confirm the captured + masked images.<br/>
                Step 3: get your style verdict.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # CTA button
    c = st.container()
    with c:
        col1, col2, col3 = st.columns([1,1,1])
        with col2:
            if st.button("📸 Start", type="primary", use_container_width=True):
                return "make_picture_page"

    return None
