import streamlit as st

def show():
    st.markdown("## AI Business Insights")
    insights = st.session_state.insights

    if not insights:
        st.info("Upload a file first.")
        return

    for level, icon, text in insights:
        st.markdown(
            f'<div class="insight-card {level}">'
            f'<div style="font-size:1.1rem">{icon}</div>'
            f'<div class="insight-text">{text}</div>'
            f'</div>',
            unsafe_allow_html=True)
