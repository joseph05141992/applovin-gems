"""scanner_page.py — 50-Stock Scanner with filters, sorting, detail cards"""
import streamlit as st
import plotly.graph_objects as go

def _gold_chart(fig):
    fig.update_layout(template="plotly_dark", paper_bgcolor="#111", plot_bgcolor="#1A1A1A",
        font=dict(family="DM Sans", color="#E8E8E8"),
        xaxis=dict(gridcolor="#2A2A2A"), yaxis=dict(gridcolor="#2A2A2A"),
        margin=dict(l=40, r=20, t=40, b=40))
    return fig

def _section(title, sub=""):
    st.markdown(f'''<div style="background:linear-gradient(90deg,rgba(196,162,101,0.15),transparent);border-left:4px solid #C4A265;padding:16px 20px;border-radius:0 8px 8px 0;margin:32px 0 16px 0;">
    <h2 style="font-size:20px!important;font-weight:700!important;color:#C4A265!important;margin:0!important;">{title}</h2>
    <div style="font-size:13px;color:#999!important;margin-top:4px;">{sub}</div></div>''', unsafe_allow_html=True)

STAGE_COLORS = {
    "PRE_BREAKOUT": "#F59E0B",
    "EARLY_CONFIRMATION": "#3B82F6",
    "MID_CONFIRMATION": "#22C55E",
    "LATE_CONFIRMATION": "#8B5CF6",
    "SURGE_PHASE": "#C4A265",
}
STAGE_ORDER = ["PRE_BREAKOUT","EARLY_CONFIRMATION","MID_CONFIRMATION","LATE_CONFIRMATION","SURGE_PHASE"]

@st.cache_data
def _load():
    from applovin_data import TOP_50_STOCKS
    return TOP_50_STOCKS

def render_scanner_page():
    stocks = _load()

    st.markdown('''<div style="background:linear-gradient(135deg,#1A1A1A,#252525);border:1px solid #2A2A2A;border-left:4px solid #C4A265;border-radius:12px;padding:28px 32px;margin-bottom:24px;">
    <h1 style="font-size:28px!important;font-weight:700!important;color:#C4A265!important;margin:0!important;">🔍 50-Stock Scanner</h1>
    <div style="font-size:14px;color:#999!important;margin-top:6px;">Every stock scored against the AppLovin pattern — filter, sort, drill down</div></div>''', unsafe_allow_html=True)

    # Dashboard
    by_stage = {}
    for s in stocks:
        by_stage.setdefault(s["app_stage"], []).append(s)

    cols = st.columns(5)
    for i, stage in enumerate(STAGE_ORDER):
        group = by_stage.get(stage, [])
        avg_score = sum(s["app_score"] for s in group) / len(group) if group else 0
        color = STAGE_COLORS[stage]
        cols[i].markdown(f'''<div style="background:#1E1E1E;border:1px solid {color}40;border-top:3px solid {color};border-radius:8px;padding:12px;text-align:center;">
        <div style="font-size:22px;font-weight:700;color:{color};">{len(group)}</div>
        <div style="font-size:11px;color:#999;">{stage.replace("_"," ")}</div>
        <div style="font-size:10px;color:#666;">Avg: {avg_score:.0f}</div></div>''', unsafe_allow_html=True)

    # Scatter
    _section("Score vs. Price Performance", "Bubble size = market cap")
    fig = go.Figure()
    for stage in STAGE_ORDER:
        group = by_stage.get(stage, [])
        fig.add_trace(go.Scatter(
            x=[s["app_score"] for s in group],
            y=[s["price_change_q1_to_current_pct"] for s in group],
            mode="markers+text",
            text=[s["ticker"] for s in group],
            textposition="top center",
            textfont=dict(size=9, color=STAGE_COLORS[stage]),
            marker=dict(size=[max(8, min(35, s["market_cap_b"]*0.4)) for s in group],
                color=STAGE_COLORS[stage], opacity=0.7, line=dict(width=1, color="#fff")),
            name=stage.replace("_", " "),
            hovertemplate="<b>%{text}</b><br>Score: %{x}<br>Price: %{y:.1f}%<extra></extra>"))
    fig.update_layout(height=450, xaxis_title="APP Score", yaxis_title="Price Change (%)",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
    st.plotly_chart(_gold_chart(fig), use_container_width=True)

    # Filter bar
    _section("Filter & Sort")
    fc1, fc2, fc3, fc4 = st.columns(4)
    with fc1:
        stage_filter = st.multiselect("Stage", STAGE_ORDER, default=STAGE_ORDER, format_func=lambda x: x.replace("_"," "))
    with fc2:
        min_score = st.slider("Min APP Score", 0, 100, 50)
    with fc3:
        sort_by = st.selectbox("Sort By", ["app_score","conviction_score","price_change_q1_to_current_pct","recovery_ratio","market_cap_b","iv_rank"])
    with fc4:
        sort_dir = st.radio("Order", ["Desc","Asc"], horizontal=True)

    filtered = [s for s in stocks if s["app_stage"] in stage_filter and s["app_score"] >= min_score]
    filtered.sort(key=lambda s: s.get(sort_by, 0), reverse=(sort_dir=="Desc"))
    st.markdown(f'<div style="font-size:13px;color:#999;margin:8px 0;">Showing <b style="color:#C4A265;">{len(filtered)}</b> of {len(stocks)} stocks</div>', unsafe_allow_html=True)

    # Stock list
    for s in filtered:
        sc = STAGE_COLORS.get(s["app_stage"], "#999")
        passed = s["gates_passed"].split(",")
        gates_html = " ".join(
            f'<span style="display:inline-block;width:20px;height:20px;line-height:20px;text-align:center;border-radius:4px;font-size:10px;font-weight:700;'
            f'{"background:"+sc+";color:#111;" if g in passed else "background:#2A2A2A;color:#666;"}">{g}</span>'
            for g in ["A","B","C","D","E"])

        with st.expander(f"#{s['rank']} {s['ticker']} — {s['company_name']} | Score: {s['app_score']} | {s['app_stage'].replace('_',' ')}"):
            m1, m2, m3, m4, m5 = st.columns(5)
            m1.markdown(f'<div style="text-align:center;"><div style="font-size:20px;font-weight:700;color:{sc};">{s["app_score"]}</div><div style="font-size:10px;color:#999;">Score</div></div>', unsafe_allow_html=True)
            pcc = "#22C55E" if s["price_change_q1_to_current_pct"]>0 else "#EF4444"
            m2.markdown(f'<div style="text-align:center;"><div style="font-size:20px;font-weight:700;color:{pcc};">{s["price_change_q1_to_current_pct"]:+.0f}%</div><div style="font-size:10px;color:#999;">Price Δ</div></div>', unsafe_allow_html=True)
            m3.markdown(f'<div style="text-align:center;"><div style="font-size:20px;font-weight:700;color:#C4A265;">${s["market_cap_b"]:.0f}B</div><div style="font-size:10px;color:#999;">Mkt Cap</div></div>', unsafe_allow_html=True)
            m4.markdown(f'<div style="text-align:center;"><div style="font-size:20px;font-weight:700;color:#22C55E;">{s["eps_beats_gt15pct"]}/8</div><div style="font-size:10px;color:#999;">Beats &gt;15%</div></div>', unsafe_allow_html=True)
            m5.markdown(f'<div style="text-align:center;"><div style="font-size:20px;font-weight:700;color:#3B82F6;">{s["conviction_score"]}/10</div><div style="font-size:10px;color:#999;">Conviction</div></div>', unsafe_allow_html=True)

            st.markdown(f'<div style="display:flex;align-items:center;gap:12px;margin:8px 0;"><span style="font-size:11px;color:#999;">Gates:</span> {gates_html} <span style="background:{sc}22;color:{sc};font-size:11px;padding:2px 8px;border-radius:4px;font-weight:600;">{s["app_stage"].replace("_"," ")}</span></div>', unsafe_allow_html=True)

            st.markdown(f'''<div style="background:#1E1E1E;border:1px solid #2A2A2A;border-radius:8px;padding:12px;margin:8px 0;">
            <div style="font-size:12px;color:#999;">AXON Equivalent</div>
            <div style="font-size:13px;color:#E8E8E8;font-weight:600;">{s["axon_equivalent"]}</div>
            <div style="font-size:12px;color:#999;margin-top:6px;">TAM Expansion</div>
            <div style="font-size:13px;color:#3B82F6;">{s["tam_expansion"]}</div></div>''', unsafe_allow_html=True)

            qlabels = [f"Q{i+1}" for i in range(8)]
            fig = go.Figure()
            fig.add_trace(go.Bar(x=qlabels, y=s["eps_actual"], name="Actual", marker_color="#C4A265", opacity=0.9))
            fig.add_trace(go.Bar(x=qlabels, y=s["eps_estimate"], name="Estimate", marker_color="#666", opacity=0.5))
            fig.update_layout(barmode="group", height=250, title=f"{s['ticker']} EPS",
                legend=dict(orientation="h", yanchor="bottom", y=1.02))
            st.plotly_chart(_gold_chart(fig), use_container_width=True)

            fig2 = go.Figure()
            fig2.add_trace(go.Scatter(x=qlabels, y=s["revenue_actual_m"], mode="lines+markers",
                fill="tozeroy", line=dict(color="#22C55E", width=2), fillcolor="rgba(34,197,94,0.1)"))
            fig2.update_layout(height=220, title=f"{s['ticker']} Revenue ($M)")
            st.plotly_chart(_gold_chart(fig2), use_container_width=True)

            st.markdown(f'<div style="background:rgba(196,162,101,0.08);border:1px solid #C4A26540;border-radius:8px;padding:12px;font-size:13px;color:#E8E8E8;">{s["plain_english_summary"]}</div>', unsafe_allow_html=True)

            if s["caution_flags"]:
                flags = " ".join(f'<span style="background:rgba(239,68,68,0.15);color:#EF4444;font-size:11px;padding:2px 6px;border-radius:4px;margin:2px;">⚠ {f}</span>' for f in s["caution_flags"])
                st.markdown(f'<div style="margin-top:8px;">{flags}</div>', unsafe_allow_html=True)
