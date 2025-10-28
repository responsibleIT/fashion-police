import streamlit as st
from pages import start_page, make_picture_page, loader_page, result_page

PAGES = {
    "start_page": start_page.render,
    "make_picture_page": make_picture_page.render,
    "loader_page": loader_page.render,
    "result_page": result_page.render,
}

def main():
    # 1. init session_state.page
    if "page" not in st.session_state:
        st.session_state.page = "start_page"

    # 2. capture the page when we entered this run
    current_page = st.session_state.page

    # 3. run that page's render()
    next_func = PAGES[current_page]
    next_func()  # we don't rely on return value anymore

    # 4. if code in that render() changed st.session_state.page,
    #    trigger a clean rerun here (centralized) so subpages don't call st.rerun()
    if st.session_state.page != current_page:
        st.rerun()

if __name__ == "__main__":
    main()
