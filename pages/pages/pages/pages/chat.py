import streamlit as st

def show():
    st.markdown("## Chat with Your Data")

    suggestions = ["Total revenue?","How many customers?",
                   "How many orders?","Data quality score?"]
    cols_s = st.columns(4)
    for i, s in enumerate(suggestions):
        with cols_s[i]:
            if st.button(s, key=f"sug_{i}"):
                _answer(s)
                st.rerun()

    st.markdown("---")
    for msg in st.session_state.chat:
        if msg["role"] == "user":
            st.markdown(
                f'<div style="background:rgba(99,102,241,0.1);'
                f'border:1px solid rgba(99,102,241,0.2);'
                f'border-radius:10px;padding:10px 14px;'
                f'margin:6px 0 6px 15%;font-size:14px;color:#C7D2FE">'
                f'{msg["content"]}</div>',
                unsafe_allow_html=True)
        else:
            st.markdown(
                f'<div style="background:#1E2235;border:1px solid #2D3150;'
                f'border-radius:10px;padding:10px 14px;'
                f'margin:6px 15% 6px 0;font-size:14px;color:#94A3B8">'
                f'{msg["content"]}</div>',
                unsafe_allow_html=True)

    user_input = st.chat_input("Ask anything about your data...")
    if user_input:
        _answer(user_input)
        st.rerun()

def _answer(question):
    st.session_state.chat.append({"role":"user","content":question})
    kpis    = st.session_state.kpis
    kpi_map = {k[1].lower(): k[2] for k in kpis}
    q       = question.lower()

    if "revenue" in q:
        ans = f"Total revenue is **{kpi_map.get('total revenue','N/A')}**"
    elif "customer" in q:
        ans = f"There are **{kpi_map.get('unique customers','N/A')}** unique customers"
    elif "order" in q:
        ans = f"There are **{kpi_map.get('total orders','N/A')}** total orders"
    elif "product" in q:
        ans = f"There are **{kpi_map.get('unique products','N/A')}** unique products"
    elif "margin" in q or "profit" in q:
        ans = f"Profit margin is **{kpi_map.get('profit margin','N/A')}**"
    elif "quality" in q:
        ans = f"Data quality score is **{st.session_state.score}/100**"
    else:
        top = [t for _,_,t in st.session_state.insights[:3]]
        ans = ("Key insights:\n\n" + "\n\n".join(f"• {t}" for t in top)
               if top else "Try asking about revenue, customers, or products.")

    st.session_state.chat.append({"role":"assistant","content":ans})
