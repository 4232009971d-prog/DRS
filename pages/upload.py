import streamlit as st
import pandas as pd
from utils import detect_col, clean_data, compute_kpis, generate_charts, generate_insights

def show():
    st.markdown("## Upload Your Data")
    st.markdown('<p style="color:#475569">Excel or CSV · up to 50MB</p>',
                unsafe_allow_html=True)

    f = st.file_uploader("Drop file here",
                         type=["xlsx","xls","csv"],
                         label_visibility="collapsed")
    if f:
        if st.button("⚡  Analyse Now"):
            with st.spinner("Analysing your data..."):
                try:
                    if f.name.endswith(".csv"):
                        df = pd.read_csv(f)
                    else:
                        df = pd.read_excel(f)

                    df, dup, blank, score = clean_data(df)

                    cols = {
                        "revenue":  detect_col(df.columns, "revenue"),
                        "quantity": detect_col(df.columns, "quantity"),
                        "date":     detect_col(df.columns, "date"),
                        "customer": detect_col(df.columns, "customer"),
                        "product":  detect_col(df.columns, "product"),
                        "region":   detect_col(df.columns, "region"),
                        "country":  detect_col(df.columns, "country"),
                        "profit":   detect_col(df.columns, "profit"),
                    }

                    kpis     = compute_kpis(df, cols)
                    charts   = generate_charts(df, cols)
                    insights = generate_insights(df, cols, dup, score)

                    st.session_state.df       = df
                    st.session_state.cols     = cols
                    st.session_state.kpis     = kpis
                    st.session_state.charts   = charts
                    st.session_state.insights = insights
                    st.session_state.dup      = dup
                    st.session_state.blank    = blank
                    st.session_state.score    = score
                    st.session_state.fname    = f.name
                    st.session_state.page     = "dashboard"
                    st.rerun()

                except Exception as e:
                    st.error(f"Error processing file: {e}")
