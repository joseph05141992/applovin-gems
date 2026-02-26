"""applovin_page.py — The AppLovin Strategy deep-dive page"""
import streamlit as st
import plotly.graph_objects as go
from datetime import datetime

def _gold_chart(fig):
    """Apply dark gold theme to any Plotly figure."""
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="#111",
        plot_bgcolor="#1A1A1A",
        font=dict(family="DM Sans", color="#E8E8E8"),
        xaxis=dict(gridcolor="#2A2A2A", zerolinecolor="#2A2A2A"),
        yaxis=dict(gridcolor="#2A2A2A", zerolinecolor="#2A2A2A"),
        margin=dict(l=40, r=20, t=40, b=40),
    )
    return fig

def _card(html):
    st.markdown(f'<div style="background:#1E1E1E;border:1px solid #2A2A2A;border-radius:10px;padding:16px;margin:8px 0;">{html}</div>', unsafe_allow_html=True)

def _section(title, sub=""):
    st.markdown(f'''<div style="background:linear-gradient(90deg,rgba(196,162,101,0.15),transparent);border-left:4px solid #C4A265;padding:16px 20px;border-radius:0 8px 8px 0;margin:32px 0 16px 0;">
    <h2 style="font-size:20px!important;font-weight:700!important;color:#C4A265!important;margin:0!important;">{title}</h2>
    <div style="font-size:13px;color:#999!important;margin-top:4px;">{sub}</div></div>''', unsafe_allow_html=True)

def _metric_box(label, value, color="#C4A265"):
    return f'<div style="background:rgba(255,255,255,0.03);border:1px solid #2A2A2A;border-radius:8px;padding:12px 16px;flex:1;text-align:center;"><div style="font-size:22px;font-weight:700;color:{color}!important;">{value}</div><div style="font-size:11px;color:#999!important;margin-top:2px;">{label}</div></div>'

@st.cache_data
def _load_data():
    from applovin_data import APP_QUARTERS, APP_FULL_CYCLE, GATE_DEFINITIONS, NON_FINANCIAL_PATTERNS, BEARISH_PHASE_DATA
    return APP_QUARTERS, APP_FULL_CYCLE, GATE_DEFINITIONS, NON_FINANCIAL_PATTERNS, BEARISH_PHASE_DATA

def render_applovin_page():
    quarters, phases, gates, patterns, bearish = _load_data()

    # ── HEADER ──
    st.markdown('''<div style="background:linear-gradient(135deg,#1A1A1A,#252525);border:1px solid #2A2A2A;border-left:4px solid #C4A265;border-radius:12px;padding:28px 32px;margin-bottom:24px;">
    <h1 style="font-size:28px!important;font-weight:700!important;color:#C4A265!important;margin:0!important;">📈 The AppLovin Strategy</h1>
    <div style="font-size:14px;color:#999!important;margin-top:6px;">How APP went from $9.40 to $745 — and the pattern that finds the next one</div>
    <div style="display:flex;gap:24px;margin-top:12px;font-size:12px;color:#999!important;">
        <span>Ticker: <span style="color:#C4A265;font-weight:600;">APP</span></span>
        <span>9 Quarters Analyzed</span>
        <span>10 Cycle Phases</span>
        <span>5 Signal Gates</span>
    </div></div>''', unsafe_allow_html=True)

    # ── SECTION 1: FULL CYCLE TIMELINE ──
    _section("Full Cycle Timeline", "AppLovin stock price through all 10 phases — IPO to $745")

    # Build price timeline chart
    fig = go.Figure()
    # Phase background rectangles
    for p in phases:
        fig.add_vrect(
            x0=p["date_start"], x1=p["date_end"],
            fillcolor=p["color"], opacity=0.08, line_width=0,
            annotation_text=p["phase_name"] if p["duration_days"] > 30 else "",
            annotation_position="top left",
            annotation=dict(font_size=9, font_color=p["color"])
        )
    # Price line from earnings data
    dates = [q["report_date"] for q in quarters]
    prices = [q["stock_price"] for q in quarters]
    fig.add_trace(go.Scatter(x=dates, y=prices, mode="lines+markers",
        line=dict(color="#C4A265", width=3),
        marker=dict(size=10, symbol="diamond", color="#C4A265"),
        hovertemplate="<b>%{x}</b><br>Price: $%{y}<extra></extra>",
        name="APP Price at Earnings"))
    fig.update_layout(title="", height=400, showlegend=False,
        yaxis_title="Stock Price ($)", xaxis_title="")
    st.plotly_chart(_gold_chart(fig), use_container_width=True)

    # Phase cards
    cols = st.columns(5)
    for i, p in enumerate(phases):
        with cols[i % 5]:
            st.markdown(f'''<div style="background:#1E1E1E;border:1px solid {p["color"]}40;border-top:3px solid {p["color"]};border-radius:8px;padding:10px;margin:4px 0;text-align:center;">
            <div style="font-size:11px;font-weight:700;color:{p["color"]};">{p["phase_name"]}</div>
            <div style="font-size:10px;color:#999;">${p["price_low"]:.0f} → ${p["price_high"]:.0f}</div>
            <div style="font-size:9px;color:#666;">{p["duration_days"]}d</div></div>''', unsafe_allow_html=True)

    # ── SECTION 2: QUARTER-BY-QUARTER ──
    _section("Quarter-by-Quarter Breakdown", "9 quarters of earnings data with management signals")

    stage_colors = {"bottoming":"#F59E0B","early_recovery":"#22C55E","ignition":"#C4A265","confirmation":"#22C55E","acceleration":"#8B5CF6","surge":"#C4A265"}

    for q in quarters:
        sc = stage_colors.get(q["app_stage"], "#999")
        with st.expander(f"{q['quarter']} — {q['app_stage'].upper().replace('_',' ')} | EPS: {q['eps_surprise_pct']:+.1f}% | Rev: ${q['revenue_actual_m']:.0f}M"):
            c1, c2, c3, c4 = st.columns(4)
            eps_color = "#22C55E" if q["eps_surprise_pct"] > 0 else "#EF4444"
            rev_color = "#22C55E" if q["revenue_surprise_pct"] > 0 else "#EF4444"
            react_color = "#22C55E" if q["stock_reaction_pct"] > 0 else "#EF4444"
            c1.markdown(_metric_box("EPS Surprise", f"{q['eps_surprise_pct']:+.1f}%", eps_color), unsafe_allow_html=True)
            c2.markdown(_metric_box("Revenue", f"${q['revenue_actual_m']:.0f}M", rev_color), unsafe_allow_html=True)
            c3.markdown(_metric_box("EBITDA Margin", f"{q['ebitda_margin_pct']:.0f}%", "#C4A265"), unsafe_allow_html=True)
            c4.markdown(_metric_box("Stock Reaction", f"{q['stock_reaction_pct']:+.1f}%", react_color), unsafe_allow_html=True)

            # Key themes
            for theme in q["key_themes"]:
                st.markdown(f"<span style='display:inline-block;background:rgba(196,162,101,0.15);color:#C4A265;font-size:12px;padding:2px 8px;border-radius:4px;margin:2px 4px 2px 0;'>{theme}</span>", unsafe_allow_html=True)

            # AXON stage + TAM + Confidence
            st.markdown(f"""<div style="display:flex;gap:12px;margin-top:8px;align-items:center;">
            <span style="background:rgba(139,92,246,0.2);color:#8B5CF6;font-size:11px;padding:2px 8px;border-radius:4px;">AXON: {q['axon_stage']}</span>
            {''.join(f'<span style="background:rgba(59,130,246,0.15);color:#3B82F6;font-size:11px;padding:2px 8px;border-radius:4px;">{t}</span>' for t in q['tam_mentions'])}
            <span style="font-size:11px;color:#999;">Confidence: </span>
            <div style="background:#2A2A2A;border-radius:4px;width:100px;height:8px;display:inline-block;"><div style="background:#C4A265;border-radius:4px;height:8px;width:{q['management_confidence']*10}%;"></div></div>
            <span style="font-size:11px;color:#C4A265;">{q['management_confidence']}/10</span>
            </div>""", unsafe_allow_html=True)

    # ── SECTION 3: THE 5 GATES ──
    _section("The 5 Signal Gates", "The scoring system that identifies APP-pattern stocks")

    tab_b, tab_c, tab_d, tab_e, tab_a, tab_react = st.tabs(["Gate B: EPS (35%)", "Gate C: Revenue (20%)", "Gate D: Guidance (15%)", "Gate E: Narrative (15%)", "Gate A: Washout", "Earnings Reaction (15%)"])

    with tab_b:
        g = gates["gate_b"]
        st.markdown(f"**{g['name']}** — Weight: {g['weight']*100:.0f}%")
        st.markdown(f"Threshold: `{g['threshold']}`")
        st.markdown(f"APP calibration: *{g['app_calibration']}*")
        fig = go.Figure()
        fig.add_trace(go.Bar(x=[q["quarter"] for q in quarters], y=[q["eps_surprise_pct"] for q in quarters],
            marker_color=["#C4A265" if q["eps_surprise_pct"]>50 else "#22C55E" if q["eps_surprise_pct"]>0 else "#EF4444" for q in quarters]))
        fig.add_hline(y=50, line_dash="dash", line_color="#C4A265", annotation_text="50% threshold")
        fig.update_layout(title="EPS Surprise % by Quarter", height=350, yaxis_title="Surprise %")
        st.plotly_chart(_gold_chart(fig), use_container_width=True)

    with tab_c:
        g = gates["gate_c"]
        st.markdown(f"**{g['name']}** — Weight: {g['weight']*100:.0f}%")
        st.markdown(f"APP calibration: *{g['app_calibration']}*")
        fig = go.Figure()
        fig.add_trace(go.Bar(x=[q["quarter"] for q in quarters], y=[q["revenue_actual_m"] for q in quarters],
            marker_color=["#C4A265" if q["revenue_surprise_pct"]>3 else "#22C55E" for q in quarters]))
        fig.add_hline(y=715, line_dash="dot", line_color="#EF4444", annotation_text="$715M ceiling")
        fig.update_layout(title="Revenue by Quarter ($M)", height=350, yaxis_title="Revenue ($M)")
        st.plotly_chart(_gold_chart(fig), use_container_width=True)

    with tab_d:
        g = gates["gate_d"]
        st.markdown(f"**{g['name']}** — Weight: {g['weight']*100:.0f}%")
        st.markdown(f"APP calibration: *{g['app_calibration']}*")
        guidance_qs = [q for q in quarters if q["guidance_next_q_low_m"] is not None]
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=[q["quarter"] for q in guidance_qs],
            y=[(q["guidance_next_q_low_m"]+q["guidance_next_q_high_m"])/2 for q in guidance_qs],
            mode="lines+markers", line=dict(color="#C4A265", width=2), name="Guidance Midpoint"))
        fig.update_layout(title="Guidance Midpoint Trend", height=350, yaxis_title="Guidance ($M)")
        st.plotly_chart(_gold_chart(fig), use_container_width=True)

    with tab_e:
        g = gates["gate_e"]
        st.markdown(f"**{g['name']}** — Weight: {g['weight']*100:.0f}%")
        st.markdown(f"APP calibration: *{g['app_calibration']}*")
        for q in quarters:
            tags = " ".join(f'<span style="background:rgba(139,92,246,0.15);color:#8B5CF6;font-size:11px;padding:2px 6px;border-radius:4px;margin:2px;">{t}</span>' for t in q["tam_mentions"])
            st.markdown(f'<div style="margin:4px 0;"><b style="color:#C4A265;font-size:12px;">{q["quarter"]}</b> <span style="background:rgba(196,162,101,0.15);color:#C4A265;font-size:11px;padding:2px 6px;border-radius:4px;">{q["axon_stage"]}</span> {tags}</div>', unsafe_allow_html=True)

    with tab_a:
        g = gates["gate_a"]
        st.markdown(f"**{g['name']}** — Pass/Fail Filter")
        st.markdown(f"APP calibration: *{g['app_calibration']}*")
        fig = go.Figure(go.Waterfall(
            x=["Peak ($112)", "Fed Tightening", "ATT Privacy", "EPS Misses", "Ad Collapse", "Bottom ($9.40)"],
            y=[112, -30, -20, -35, -17.6, 0],
            measure=["absolute","relative","relative","relative","relative","total"],
            connector=dict(line=dict(color="#2A2A2A")),
            decreasing=dict(marker=dict(color="#EF4444")),
            totals=dict(marker=dict(color="#F59E0B")),
        ))
        fig.update_layout(title="AppLovin Drawdown: $112 → $9.40 (−92%)", height=350)
        st.plotly_chart(_gold_chart(fig), use_container_width=True)

    with tab_react:
        g = gates["event_reaction"]
        st.markdown(f"**{g['name']}** — Weight: {g['weight']*100:.0f}%")
        reactions = [(q["quarter"], q["stock_reaction_pct"]) for q in quarters]
        fig = go.Figure()
        fig.add_trace(go.Bar(x=[r[0] for r in reactions], y=[r[1] for r in reactions],
            marker_color=["#22C55E" if r[1]>0 else "#EF4444" for r in reactions]))
        fig.update_layout(title="Stock Reaction on Earnings Day (%)", height=350, yaxis_title="Reaction %")
        st.plotly_chart(_gold_chart(fig), use_container_width=True)

    # ── SECTION 4: NON-FINANCIAL PATTERNS ──
    _section("Non-Financial Pattern Recognition", "8 qualitative signals that precede price moves")

    for i in range(0, len(patterns), 2):
        c1, c2 = st.columns(2)
        for col, idx in [(c1, i), (c2, i+1 if i+1 < len(patterns) else None)]:
            if idx is not None:
                p = patterns[idx]
                with col:
                    _card(f"""<div style="font-size:14px;font-weight:700;color:#C4A265;">{p['pattern_name']}</div>
                    <div style="font-size:12px;color:#999;margin:6px 0;">{p['description']}</div>
                    <div style="font-size:11px;color:#22C55E;">APP Evidence: {p['app_evidence']}</div>
                    <div style="display:flex;justify-content:space-between;margin-top:8px;">
                        <span style="font-size:10px;color:#666;">Weight: {p['weight']*100:.0f}%</span>
                        <div style="background:#2A2A2A;border-radius:4px;width:60px;height:6px;display:inline-block;"><div style="background:#C4A265;border-radius:4px;height:6px;width:{p['weight']*100*6.67:.0f}%;"></div></div>
                    </span></div>""")

    # Margin progression chart
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=[q["quarter"] for q in quarters], y=[q["ebitda_margin_pct"] for q in quarters],
        mode="lines+markers", fill="tozeroy", line=dict(color="#22C55E", width=2),
        fillcolor="rgba(34,197,94,0.1)", name="EBITDA Margin"))
    fig.update_layout(title="Margin Trajectory: 38% → 62%", height=300, yaxis_title="EBITDA Margin %")
    st.plotly_chart(_gold_chart(fig), use_container_width=True)

    # Management confidence chart
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=[q["quarter"] for q in quarters], y=[q["management_confidence"] for q in quarters],
        mode="lines+markers", line=dict(color="#C4A265", width=2), name="Confidence"))
    fig.update_layout(title="Management Confidence Escalation (1-10)", height=250, yaxis=dict(range=[0,11]))
    st.plotly_chart(_gold_chart(fig), use_container_width=True)

    # ── SECTION 5: BEARISH PHASE ──
    st.markdown('''<div style="background:linear-gradient(90deg,rgba(239,68,68,0.15),transparent);border-left:4px solid #EF4444;padding:16px 20px;border-radius:0 8px 8px 0;margin:32px 0 16px 0;">
    <h2 style="font-size:20px!important;font-weight:700!important;color:#EF4444!important;margin:0!important;">Bearish Phase — Reverse Pattern Recognition</h2>
    <div style="font-size:13px;color:#999!important;margin-top:4px;">How to detect when a stock is in the APP selloff phase — and when it's bottoming</div></div>''', unsafe_allow_html=True)

    # EPS miss magnitude chart
    bqs = bearish["bearish_quarters"]
    fig = go.Figure()
    fig.add_trace(go.Bar(x=[q["quarter"] for q in bqs], y=[q["eps_miss_pct"] for q in bqs],
        marker_color=["#EF4444" if q["eps_miss_pct"]<-100 else "#F59E0B" for q in bqs]))
    fig.update_layout(title="EPS Miss Magnitude — Worsening Then Improving", height=300, yaxis_title="Miss %")
    st.plotly_chart(_gold_chart(fig), use_container_width=True)

    # Warning signals
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**⚠️ Warning Signals**")
        for w in bearish["bearish_warning_rules"]:
            st.markdown(f'<div style="font-size:12px;color:#EF4444;margin:4px 0;">✗ {w}</div>', unsafe_allow_html=True)
    with c2:
        st.markdown("**✅ Bottoming Signals**")
        for b in bearish["bottoming_signals"]:
            st.markdown(f'<div style="font-size:12px;color:#22C55E;margin:4px 0;">✓ {b}</div>', unsafe_allow_html=True)

    # May 2022 Anomaly callout
    _card(f"""<div style="border-left:3px solid #F59E0B;padding-left:12px;">
    <div style="font-size:14px;font-weight:700;color:#F59E0B;">💡 The May 2022 Anomaly</div>
    <div style="font-size:12px;color:#E8E8E8;margin-top:6px;">Q1'22 reported a <b style="color:#EF4444;">−1,646% EPS miss</b> — the worst in APP history. Yet the stock <b style="color:#22C55E;">rallied 34%</b> the next day. This is the classic <b>capitulation exhaustion signal</b>: when the worst possible news fails to push the price lower, sellers are exhausted. Management's tone shifted from defensive to honest about restructuring. Three months later, AXON 2 was announced. This is the signal that separates bottoming from continued decline.</div></div>""")
