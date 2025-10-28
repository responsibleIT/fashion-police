import streamlit as st

def render() -> None:
    st.markdown(
        """
        <div style="text-align:center; margin:4rem auto 2rem auto;">
            <div style="font-size:1.5rem; font-weight:600;">
                👮 Fashion Police
            </div>
            <div style="color:#ccc; font-size:0.9rem; line-height:1.4; margin-top:0.75rem;">
                We'll analyze your outfit, hide your face for fairness, and predict your fashion style
                (streetwear, formal, vintage, etc.). Everything runs locally.<br/><br/>
                Step 1: let us access your webcam.<br/>
                Step 2: confirm the captured + masked images.<br/>
                Step 3: get your style verdict.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Centered button card
    c = st.container()
    with c:
        # We wrap in columns just to center the button nicely
        left, mid, right = st.columns([1,2,1])
        with mid:
            if st.button(
                "📸 Start",
                type="primary",
                use_container_width=True,
            ):
                # set the next page
                st.session_state.page = "make_picture_page"
                # DO NOT st.rerun() here. app.py will detect the change and rerun cleanly.
                return
