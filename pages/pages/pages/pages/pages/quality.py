import streamlit as st
import pandas as pd
import plotly.express as px

def show():
    st.markdown("## Data Quality Report")
    df = st.session_state.df
    if df is None:
        st.info("Upload a file first.")
        return

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Quality Score",      f"{st.session_state.score}/100")
    c2.metric("Total Rows",         f"{len(df):,}")
    c3.metric("Duplicates Removed", st.session_state.dup)
    c4.metric("Blank Rows Removed", st.session_state.blank)

    st.markdown("### Column Analysis")
    rows = []
    for col in df.columns:
        null_pct = df[col].isnull().mean() * 100
        status   = ("✅ Good"    if null_pct < 5  else
                    "⚠️ Issues"  if null_pct < 50 else
                    "❌ Critical")
        rows.append({
            "Column":    col,
            "Type":      str(df[col].dtype),
            "Missing %": f"{null_pct:.1f}%",
            "Unique":    df[col].nunique(),
            "Status":    status,
        })
    st.dataframe(pd.DataFrame(rows),
                 use_container_width=True, hide_index=True)

    missing = [(c["Column"], float(c["Missing %"].replace("%","")))
               for c in rows if float(c["Missing %"].replace("%","")) > 0]
    if missing:
        mdf = pd.DataFrame(missing, columns=["Column","Missing %"])
        mdf.sort_values("Missing %", ascending=False, inplace=True)
        fig = px.bar(mdf, x="Column", y="Missing %",
            color="Missing %",
            color_continuous_scale=["#10B981","#F59E0B","#EF4444"])
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#94A3B8"),
            margin=dict(l=20,r=20,t=30,b=20))
        st.plotly_chart(fig, use_container_width=True,
                       config={"displayModeBar": False})
