import pandas as pd
import numpy as np
import plotly.express as px

SYNONYMS = {
    "revenue":  ["revenue","sales","amount","net amount","invoice amount",
                 "total amount","total sales","sale amount","turnover",
                 "income","value","total value","line total"],
    "quantity": ["quantity","qty","units","pieces","pcs","count","volume"],
    "date":     ["date","order date","invoice date","sale date",
                 "transaction date","ship date","delivery date"],
    "customer": ["customer name","client name","customer","client",
                 "buyer","account name"],
    "product":  ["product name","product","item","item name",
                 "description","article"],
    "region":   ["region","territory","zone","area","district","market"],
    "country":  ["country","nation","country name"],
    "profit":   ["profit","net profit","gross profit","earnings","margin amount"],
    "cost":     ["cost","cost price","cogs","purchase price"],
}

PALETTE = ["#6366F1","#8B5CF6","#EC4899","#14B8A6",
           "#F59E0B","#10B981","#3B82F6"]

THEME = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color="#94A3B8", size=11),
    margin=dict(l=20, r=20, t=30, b=20),
)

def apply_theme(fig):
    fig.update_layout(**THEME)
    fig.update_xaxes(gridcolor="#1E293B", linecolor="#334155")
    fig.update_yaxes(gridcolor="#1E293B", linecolor="#334155")
    return fig

def detect_col(columns, role):
    for col in columns:
        clean = col.lower().strip().replace("_"," ")
        if clean in SYNONYMS.get(role, []):
            return col
    for col in columns:
        clean = col.lower().strip().replace("_"," ")
        for alias in SYNONYMS.get(role, []):
            if alias in clean or clean in alias:
                return col
    return None

def fmt_currency(v):
    if abs(v) >= 1_000_000: return f"${v/1_000_000:.2f}M"
    if abs(v) >= 1_000: return f"${v/1_000:.1f}K"
    return f"${v:,.2f}"

def clean_data(df):
    df = df.copy()
    df.columns = [str(c).strip() for c in df.columns]
    blank_rows = int(df.isnull().all(axis=1).sum())
    df.dropna(how="all", inplace=True)
    dup_count = int(df.duplicated().sum())
    df.drop_duplicates(inplace=True)
    df.reset_index(drop=True, inplace=True)
    for col in df.columns:
        if df[col].dtype == object:
            df[col] = df[col].map(
                lambda x: x.strip() if isinstance(x, str) else x)
            df[col].replace(
                ["","N/A","NA","None","NULL","-"],
                np.nan, inplace=True)
    null_pct = df.isnull().mean() * 100
    score = max(0, 100 - null_pct.mean() - (dup_count/max(len(df),1)*10))
    return df, dup_count, blank_rows, round(score, 1)

def compute_kpis(df, cols):
    kpis = []
    rev_col    = cols.get("revenue")
    qty_col    = cols.get("quantity")
    cust_col   = cols.get("customer")
    prod_col   = cols.get("product")
    profit_col = cols.get("profit")
    date_col   = cols.get("date")

    if rev_col:
        rev   = pd.to_numeric(df[rev_col], errors="coerce")
        total = rev.sum()
        kpis.append(("💰","Total Revenue", fmt_currency(total)))
        if len(df) > 0:
            kpis.append(("🛒","Avg Order Value", fmt_currency(total/len(df))))

    kpis.append(("📋","Total Orders", f"{len(df):,}"))

    if cust_col:
        kpis.append(("👥","Unique Customers",
                     f"{df[cust_col].nunique():,}"))
    if prod_col:
        kpis.append(("🏷️","Unique Products",
                     f"{df[prod_col].nunique():,}"))

    if profit_col and rev_col:
        profit    = pd.to_numeric(df[profit_col], errors="coerce").sum()
        rev_total = pd.to_numeric(df[rev_col],    errors="coerce").sum()
        if rev_total > 0:
            margin = profit / rev_total * 100
            kpis.append(("💹","Profit Margin", f"{margin:.1f}%"))

    if date_col:
        try:
            dates = pd.to_datetime(df[date_col], errors="coerce").dropna()
            if len(dates) > 0:
                kpis.append(("📅","Date Range",
                    f"{dates.min().date()} – {dates.max().date()}"))
        except:
            pass

    return kpis

def generate_charts(df, cols):
    charts  = []
    rev_col  = cols.get("revenue")
    date_col = cols.get("date")
    prod_col = cols.get("product")
    cust_col = cols.get("customer")
    reg_col  = cols.get("region")
    qty_col  = cols.get("quantity")

    if date_col and rev_col:
        try:
            df_t = df[[date_col, rev_col]].copy()
            df_t[date_col] = pd.to_datetime(df_t[date_col], errors="coerce")
            df_t[rev_col]  = pd.to_numeric(df_t[rev_col],  errors="coerce")
            df_t.dropna(inplace=True)
            df_t["Month"] = df_t[date_col].dt.to_period("M").dt.to_timestamp()
            monthly = df_t.groupby("Month")[rev_col].sum().reset_index()
            if len(monthly) >= 2:
                fig = px.line(monthly, x="Month", y=rev_col,
                    markers=True,
                    color_discrete_sequence=[PALETTE[0]])
                fig.update_traces(fill="tozeroy",
                    fillcolor="rgba(99,102,241,0.1)",
                    line=dict(width=2.5))
                charts.append(("Monthly Revenue Trend", apply_theme(fig)))
        except:
            pass

    if prod_col and rev_col:
        try:
            agg = (df.groupby(prod_col)[rev_col]
                   .sum().sort_values(ascending=False)
                   .head(10).reset_index())
            agg[rev_col] = pd.to_numeric(agg[rev_col], errors="coerce")
            fig = px.bar(agg, x=rev_col, y=prod_col, orientation="h",
                color_discrete_sequence=[PALETTE[1]])
            fig.update_layout(yaxis=dict(autorange="reversed"))
            charts.append(("Top 10 Products by Revenue", apply_theme(fig)))
        except:
            pass

    if cust_col and rev_col:
        try:
            agg = (df.groupby(cust_col)[rev_col]
                   .sum().sort_values(ascending=False)
                   .head(10).reset_index())
            agg[rev_col] = pd.to_numeric(agg[rev_col], errors="coerce")
            fig = px.bar(agg, x=rev_col, y=cust_col, orientation="h",
                color_discrete_sequence=[PALETTE[2]])
            fig.update_layout(yaxis=dict(autorange="reversed"))
            charts.append(("Top 10 Customers by Revenue", apply_theme(fig)))
        except:
            pass

    if reg_col and rev_col:
        try:
            agg = df.groupby(reg_col)[rev_col].sum().reset_index()
            agg[rev_col] = pd.to_numeric(agg[rev_col], errors="coerce")
            fig = px.pie(agg, names=reg_col, values=rev_col,
                color_discrete_sequence=PALETTE, hole=0.4)
            charts.append(("Revenue by Region", apply_theme(fig)))
        except:
            pass

    if prod_col and qty_col:
        try:
            agg = (df.groupby(prod_col)[qty_col]
                   .sum().sort_values(ascending=False)
                   .head(10).reset_index())
            agg[qty_col] = pd.to_numeric(agg[qty_col], errors="coerce")
            fig = px.bar(agg, x=prod_col, y=qty_col,
                color_discrete_sequence=[PALETTE[4]])
            charts.append(("Top Products by Units Sold", apply_theme(fig)))
        except:
            pass

    return charts

def generate_insights(df, cols, dup_count, quality_score):
    insights = []
    rev_col  = cols.get("revenue")
    date_col = cols.get("date")
    prod_col = cols.get("product")
    cust_col = cols.get("customer")

    if rev_col:
        rev   = pd.to_numeric(df[rev_col], errors="coerce")
        total = rev.sum()

        if date_col:
            try:
                df_t = df[[date_col, rev_col]].copy()
                df_t[date_col] = pd.to_datetime(df_t[date_col], errors="coerce")
                df_t[rev_col]  = pd.to_numeric(df_t[rev_col],  errors="coerce")
                df_t.dropna(inplace=True)
                df_t["Month"] = df_t[date_col].dt.to_period("M")
                monthly = df_t.groupby("Month")[rev_col].sum()
                if len(monthly) >= 2:
                    last = monthly.iloc[-1]
                    prev = monthly.iloc[-2]
                    if prev > 0:
                        pct = (last - prev) / prev * 100
                        if pct > 0:
                            insights.append(("high","📈",
                                f"Revenue grew {pct:.1f}% in the most recent month."))
                        else:
                            insights.append(("high","📉",
                                f"Revenue declined {abs(pct):.1f}% in the most recent month."))
            except:
                pass

        if prod_col:
            try:
                agg = (pd.to_numeric(
                    df.groupby(prod_col)[rev_col].sum(), errors="coerce")
                    .sort_values(ascending=False))
                if len(agg) > 0 and agg.sum() > 0:
                    top_pct = agg.iloc[0] / agg.sum() * 100
                    if top_pct > 30:
                        insights.append(("high","⚠️",
                            f"'{agg.index[0]}' contributes {top_pct:.0f}% of revenue."))
                    top3 = agg.head(3).sum() / agg.sum() * 100
                    if top3 > 60:
                        insights.append(("medium","🏆",
                            f"Top 3 products = {top3:.0f}% of total revenue."))
                    low = int((agg / agg.sum() * 100 < 1).sum())
                    if low > 0:
                        insights.append(("low","🔍",
                            f"{low} products contribute less than 1% each."))
            except:
                pass

        if cust_col:
            try:
                agg = (pd.to_numeric(
                    df.groupby(cust_col)[rev_col].sum(), errors="coerce")
                    .sort_values(ascending=False))
                if len(agg) > 0 and agg.sum() > 0:
                    top_pct = agg.iloc[0] / agg.sum() * 100
                    if top_pct > 25:
                        insights.append(("high","⭐",
                            f"'{agg.index[0]}' is top customer at {top_pct:.0f}% of revenue."))
            except:
                pass

    if dup_count > 0:
        insights.append(("medium","🔄",
            f"{dup_count} duplicate rows removed during cleaning."))
    if quality_score < 70:
        insights.append(("high","⚠️",
            f"Data quality score is {quality_score}/100."))

    return insights
