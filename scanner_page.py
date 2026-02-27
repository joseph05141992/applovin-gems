"""scanner_page.py — 50-Stock Scanner with TradingView charts, ORATS IV, white/blue design (V2)"""
import streamlit as st
import plotly.graph_objects as go

def _white_chart(fig):
    fig.update_layout(template="plotly_white", paper_bgcolor="#FFFFFF", plot_bgcolor="#FFFFFF",
        font=dict(family="Helvetica Neue, Helvetica, Arial, sans-serif", color="#111111"),
        xaxis=dict(gridcolor="#E2E8F0"), yaxis=dict(gridcolor="#E2E8F0"),
        margin=dict(l=40, r=20, t=40, b=40))
    return fig

def _section(title, sub=""):
    st.markdown(f'''<div style="background:linear-gradient(90deg,rgba(37,99,235,0.08),transparent);border-left:4px solid #2563EB;padding:16px 20px;border-radius:0 8px 8px 0;margin:32px 0 16px 0;">
    <h2 style="font-size:20px!important;font-weight:700!important;color:#1E293B!important;margin:0!important;">{title}</h2>
    <div style="font-size:13px;color:#6B7280!important;margin-top:4px;">{sub}</div></div>''', unsafe_allow_html=True)

STAGE_COLORS = {
    "PRE_BREAKOUT":"#F59E0B","EARLY_CONFIRMATION":"#3B82F6",
    "MID_CONFIRMATION":"#16A34A","LATE_CONFIRMATION":"#8B5CF6","SURGE_PHASE":"#2563EB",
}
STAGE_ORDER = ["SURGE_PHASE","LATE_CONFIRMATION","MID_CONFIRMATION","EARLY_CONFIRMATION","PRE_BREAKOUT"]

# APP phase-to-date mapping for "APP was here" comparison
APP_PHASE_MAP = {
    "PRE_BREAKOUT":     {"date":"Q4'22 (Feb 2023)","price":"$17","description":"Cost cuts underway, pre-AXON 2, stock at bottoming phase"},
    "EARLY_CONFIRMATION":{"date":"Q1'23 (May 2023)","price":"$20","description":"AXON 2 first mentioned, stock starting to recover on bad EPS"},
    "MID_CONFIRMATION": {"date":"Q2'23 (Aug 2023)","price":"$40","description":"AXON 2 live, first blowout EPS +175%, ignition phase"},
    "LATE_CONFIRMATION":{"date":"Q4'23 (Feb 2024)","price":"$75","description":"$1B run-rate, e-commerce 30%+ of rev, acceleration phase"},
    "SURGE_PHASE":      {"date":"Q3'24 (Nov 2024)","price":"$340","description":"AXON 3 preview, stock +42% in one day, full surge"},
}

def tradingview_chart(ticker, height=420):
    """Embed a TradingView lightweight chart for a ticker."""
    exchange_map = {"IOT":"NYSE","DASH":"NYSE","CVNA":"NYSE","FOUR":"NYSE",
                    "TOST":"NYSE","ONON":"NYSE","CAVA":"NYSE","FICO":"NYSE"}
    exchange = exchange_map.get(ticker, "NASDAQ")
    html = f"""<div style='height:{height}px;width:100%;'><div id='tv_{ticker}'></div>
    <script src='https://s3.tradingview.com/tv.js'></script>
    <script>new TradingView.widget({{"width":"100%","height":{height},
    "symbol":"{exchange}:{ticker}","interval":"D","timezone":"America/New_York",
    "theme":"light","style":"1","locale":"en","container_id":"tv_{ticker}",
    "range":"6M"}});</script></div>"""
    import streamlit.components.v1 as components
    components.html(html, height=height+30)

@st.cache_data(ttl=3600)
def fetch_iv_rank(ticker):
    """Fetch live IV rank from ORATS API with fallback to hardcoded data."""
    try:
        import requests
        key = st.secrets.get("ORATS_KEY", "306e5550-50f0-478a-b47d-477afa769d0a")
        r = requests.get("https://api.orats.io/datav2/hist/ivrank",
                         params={"ticker": ticker, "token": key}, timeout=5)
        if r.status_code == 200:
            data = r.json().get("data", [])
            if data:
                return data[0].get("ivRank")
    except Exception:
        pass
    return None

@st.cache_data
def _load():
    from applovin_data import TOP_50_STOCKS
    return TOP_50_STOCKS

def render_scanner_page():
    stocks = _load()

    st.markdown('''<div style="background:#F8FAFC;border:1px solid #E2E8F0;border-left:4px solid #2563EB;border-radius:8px;padding:28px 32px;margin-bottom:24px;box-shadow:0 1px 3px rgba(0,0,0,0.08);">
    <h1 style="font-size:28px!important;font-weight:700!important;color:#1E293B!important;margin:0!important;">50-Stock Scanner</h1>
    <div style="font-size:14px;color:#6B7280!important;margin-top:6px;">Every stock scored against the AppLovin pattern — filter, sort, drill down</div></div>''', unsafe_allow_html=True)

    # Dashboard
    by_stage = {}
    for s in stocks:
        by_stage.setdefault(s["app_stage"], []).append(s)

    cols = st.columns(5)
    for i, stage in enumerate(STAGE_ORDER):
        group = by_stage.get(stage, [])
        avg_score = sum(s["app_score"] for s in group) / len(group) if group else 0
        color = STAGE_COLORS[stage]
        cols[i].markdown(f'''<div style="background:#F8FAFC;border:1px solid #E2E8F0;border-top:3px solid {color};border-radius:8px;padding:12px;text-align:center;box-shadow:0 1px 3px rgba(0,0,0,0.08);">
        <div style="font-size:22px;font-weight:700;color:{color};">{len(group)}</div>
        <div style="font-size:11px;color:#6B7280;">{stage.replace("_"," ")}</div>
        <div style="font-size:10px;color:#6B7280;">Avg: {avg_score:.0f}</div></div>''', unsafe_allow_html=True)

    # Scatter
    _section("Score vs. Price Performance", "Bubble size = market cap")
    fig = go.Figure()
    for stage in STAGE_ORDER:
        group = by_stage.get(stage, [])
        if not group:
            continue
        fig.add_trace(go.Scatter(
            x=[s["app_score"] for s in group],
            y=[s["price_change_q1_to_current_pct"] for s in group],
            mode="markers+text",
            text=[s["ticker"] for s in group],
            textposition="top center",
            textfont=dict(size=9, color=STAGE_COLORS[stage]),
            marker=dict(size=[max(8, min(35, s["market_cap_b"]*0.4)) for s in group],
                color=STAGE_COLORS[stage], opacity=0.7, line=dict(width=1, color="#E2E8F0")),
            name=stage.replace("_", " "),
            hovertemplate="<b>%{text}</b><br>Score: %{x}<br>Price: %{y:.1f}%<extra></extra>"))
    fig.update_layout(height=450, xaxis_title="APP Score", yaxis_title="Price Change (%)",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
    st.plotly_chart(_white_chart(fig), use_container_width=True)

    # Filter bar
    _section("Filter & Sort")
    fc1, fc2, fc3, fc4 = st.columns(4)
    with fc1:
        stage_filter = st.multiselect("Stage", STAGE_ORDER, default=STAGE_ORDER,
                                       format_func=lambda x: x.replace("_"," "))
    with fc2:
        min_score = st.slider("Min APP Score", 0, 100, 50)
    with fc3:
        sort_by = st.selectbox("Sort By", ["app_score","conviction_score",
            "price_change_q1_to_current_pct","recovery_ratio","market_cap_b","iv_rank"])
    with fc4:
        sort_dir = st.radio("Order", ["Desc","Asc"], horizontal=True)

    filtered = [s for s in stocks if s["app_stage"] in stage_filter and s["app_score"] >= min_score]
    # Default sort: SURGE_PHASE first, then stage order
    stage_rank = {s: i for i, s in enumerate(STAGE_ORDER)}
    if sort_by == "app_score" and sort_dir == "Desc":
        filtered.sort(key=lambda s: (stage_rank.get(s["app_stage"], 99), -s["app_score"]))
    else:
        filtered.sort(key=lambda s: s.get(sort_by, 0), reverse=(sort_dir=="Desc"))

    st.markdown(f'<div style="font-size:13px;color:#6B7280;margin:8px 0;">Showing <b style="color:#2563EB;">{len(filtered)}</b> of {len(stocks)} stocks</div>', unsafe_allow_html=True)

    # Stock list
    for s in filtered:
        sc = STAGE_COLORS.get(s["app_stage"], "#6B7280")
        passed = s["gates_passed"].split(",")
        gates_html = " ".join(
            f'<span style="display:inline-block;width:22px;height:22px;line-height:22px;text-align:center;border-radius:4px;font-size:10px;font-weight:700;'
            f'{"background:"+sc+";color:#FFF;" if g in passed else "background:#E2E8F0;color:#6B7280;"}">{g}</span>'
            for g in ["A","B","C","D","E"])

        # Phase badge + APP comparison
        phase_info = APP_PHASE_MAP.get(s["app_stage"], {})

        with st.expander(f"#{s['rank']} {s['ticker']} — {s['company_name']} | Score: {s['app_score']} | {s['app_stage'].replace('_',' ')}"):
            # Prominent phase badge
            st.markdown(f'''<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px;">
            <span style="background:{sc};color:#FFF;padding:6px 16px;border-radius:8px;font-weight:700;font-size:14px;">{s["app_stage"].replace("_"," ")}</span>
            <span style="font-size:12px;color:#6B7280;">{s["sector"]}</span></div>''', unsafe_allow_html=True)

            # "APP was here" explanation
            if phase_info:
                st.markdown(f'''<div style="background:#EFF6FF;border:1px solid #BFDBFE;border-radius:8px;padding:10px 14px;margin-bottom:12px;font-size:12px;">
                <b style="color:#2563EB;">Currently in {s["app_stage"].replace("_"," ")}</b> — APP was here at <b>{phase_info["date"]}</b> at <b>{phase_info["price"]}</b>
                <div style="color:#6B7280;margin-top:2px;">{phase_info["description"]}</div></div>''', unsafe_allow_html=True)

            # Why bullish bullets
            summary = s.get("plain_english_summary", "")
            bullets = [b.strip() for b in summary.replace(". ", ".\n").split("\n") if b.strip()][:5]
            if bullets:
                st.markdown("**Why Bullish:**")
                for b in bullets:
                    st.markdown(f'<div style="font-size:12px;color:#374151;margin:2px 0;">&#8226; {b}</div>', unsafe_allow_html=True)

            # Metrics row
            m1, m2, m3, m4, m5 = st.columns(5)
            pcc = "#16A34A" if s["price_change_q1_to_current_pct"] > 0 else "#DC2626"
            m1.markdown(f'<div style="text-align:center;background:#F8FAFC;border:1px solid #E2E8F0;border-radius:8px;padding:10px;"><div style="font-size:20px;font-weight:700;color:{sc};">{s["app_score"]}</div><div style="font-size:10px;color:#6B7280;">Score</div></div>', unsafe_allow_html=True)
            m2.markdown(f'<div style="text-align:center;background:#F8FAFC;border:1px solid #E2E8F0;border-radius:8px;padding:10px;"><div style="font-size:20px;font-weight:700;color:{pcc};">{s["price_change_q1_to_current_pct"]:+.0f}%</div><div style="font-size:10px;color:#6B7280;">Price Chg</div></div>', unsafe_allow_html=True)
            m3.markdown(f'<div style="text-align:center;background:#F8FAFC;border:1px solid #E2E8F0;border-radius:8px;padding:10px;"><div style="font-size:20px;font-weight:700;color:#1E293B;">${s["market_cap_b"]:.0f}B</div><div style="font-size:10px;color:#6B7280;">Mkt Cap</div></div>', unsafe_allow_html=True)
            m4.markdown(f'<div style="text-align:center;background:#F8FAFC;border:1px solid #E2E8F0;border-radius:8px;padding:10px;"><div style="font-size:20px;font-weight:700;color:#16A34A;">{s["eps_beats_gt15pct"]}/8</div><div style="font-size:10px;color:#6B7280;">Beats >15%</div></div>', unsafe_allow_html=True)
            m5.markdown(f'<div style="text-align:center;background:#F8FAFC;border:1px solid #E2E8F0;border-radius:8px;padding:10px;"><div style="font-size:20px;font-weight:700;color:#2563EB;">{s["conviction_score"]}/10</div><div style="font-size:10px;color:#6B7280;">Conviction</div></div>', unsafe_allow_html=True)

            # Gates
            st.markdown(f'<div style="display:flex;align-items:center;gap:12px;margin:8px 0;"><span style="font-size:11px;color:#6B7280;">Gates:</span> {gates_html}</div>', unsafe_allow_html=True)

            # AXON + TAM
            st.markdown(f'''<div style="background:#F8FAFC;border:1px solid #E2E8F0;border-radius:8px;padding:12px;margin:8px 0;">
            <div style="font-size:12px;color:#6B7280;">AXON Equivalent</div>
            <div style="font-size:13px;color:#1E293B;font-weight:600;">{s["axon_equivalent"]}</div>
            <div style="font-size:12px;color:#6B7280;margin-top:6px;">TAM Expansion</div>
            <div style="font-size:13px;color:#2563EB;">{s["tam_expansion"]}</div></div>''', unsafe_allow_html=True)

            # TradingView chart
            tradingview_chart(s["ticker"])

            # EPS chart (white bg, blue bars positive, red negative)
            qlabels = [f"Q{i+1}" for i in range(8)]
            fig = go.Figure()
            fig.add_trace(go.Bar(x=qlabels, y=s["eps_actual"], name="Actual",
                marker_color=["#2563EB" if v >= 0 else "#DC2626" for v in s["eps_actual"]], opacity=0.9))
            fig.add_trace(go.Bar(x=qlabels, y=s["eps_estimate"], name="Estimate",
                marker_color="#CBD5E1", opacity=0.5))
            fig.update_layout(barmode="group", height=250, title=f"{s['ticker']} EPS: Actual vs Estimate",
                legend=dict(orientation="h", yanchor="bottom", y=1.02))
            st.plotly_chart(_white_chart(fig), use_container_width=True)

            # Options quick-view
            live_iv = fetch_iv_rank(s["ticker"])
            iv = live_iv if live_iv is not None else s.get("iv_rank", 0)
            iv_color = "#16A34A" if iv < 40 else "#F59E0B" if iv <= 60 else "#DC2626"
            st.markdown(f'''<div style="background:#F8FAFC;border:1px solid #E2E8F0;border-radius:8px;padding:12px;margin:8px 0;display:flex;justify-content:space-between;align-items:center;">
            <div><span style="font-size:12px;color:#6B7280;">Options Quick-View</span>
            <div style="font-size:13px;color:#1E293B;margin-top:2px;">Call: ${s["call_strike"]:.0f} {s["call_expiry"]} @ ${s["call_premium"]:.1f} | R/R: {s["recovery_ratio"]:.1f}x</div></div>
            <div style="text-align:center;"><div style="font-size:18px;font-weight:700;color:{iv_color};">{iv:.0f}%</div>
            <div style="font-size:10px;color:#6B7280;">IV Rank{"*" if live_iv is not None else ""}</div></div></div>''', unsafe_allow_html=True)

            # Caution flags
            if s.get("caution_flags"):
                flags = " ".join(f'<span style="background:#FEF2F2;color:#DC2626;font-size:11px;padding:2px 8px;border-radius:4px;margin:2px;">&#9888; {f}</span>' for f in s["caution_flags"])
                st.markdown(f'<div style="margin-top:8px;">{flags}</div>', unsafe_allow_html=True)
