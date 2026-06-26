import streamlit as st
import pandas as pd

def show():
    df = st.session_state.df
    if df is None:
        st.info("Upload a file first.")
        return

    col1, col2 = st.columns([4,1])
    with col1:
        st.markdown(f"## {st.session_state.fname}")
        st.markdown(
            f'<p style="color:#475569">{len(df):,} rows · '
            f'{len(df.columns)} columns</p>',
            unsafe_allow_html=True)
    with col2:
        s     = st.session_state.score
        color = "#10B981" if s>=80 else "#F59E0B" if s>=60 else "#EF4444"
        icon  = "✅" if s>=80 else "⚠️" if s>=60 else "❌"
        st.markdown(
            f'<div style="text-align:right;padding-top:20px">'
            f'<span style="background:rgba(99,102,241,0.15);color:{color};'
            f'padding:6px 14px;border-radius:20px;font-size:13px;font-weight:600">'
            f'{icon} {s}/100 Quality</span></div>',
            unsafe_allow_html=True)

    st.markdown('<div class="section-heading">Key Metrics</div>',
                unsafe_allow_html=True)

    kpis = st.session_state.kpis
    if kpis:
        cards = "".join(
            f'<div class="kpi-card">'
            f'<div class="kpi-icon">{icon}</div>'
            f'<div class="kpi-value">{val}</div>'
            f'<div class="kpi-label">{label}</div>'
            f'</div>'
            for icon, label, val in kpis)
        st.markdown(f'<div class="kpi-grid">{cards}</div>',
                    unsafe_allow_html=True)

    charts = st.session_state.charts
    if charts:
        st.markdown('<div class="section-heading">Charts</div>',
                    unsafe_allow_html=True)
        cols_ui = st.columns(2, gap="medium")
        for i, (title, fig) in enumerate(charts):
            with cols_ui[i % 2]:
                st.markdown(
                    f'<div style="font-size:11px;font-weight:700;color:#475569;'
                    f'text-transform:uppercase;letter-spacing:0.8px;'
                    f'margin-bottom:8px">{title}</div>',
                    unsafe_allow_html=True)
                st.plotly_chart(fig, use_container_width=True,
                               config={"displayModeBar": False})

    with st.expander("🗂️ Column Detection"):
        detected = {k:v for k,v in st.session_state.cols.items() if v}
        if detected:
            st.dataframe(
                pd.DataFrame([{"Role":k,"Column Found":v}
                              for k,v in detected.items()]),
                hide_index=True)
