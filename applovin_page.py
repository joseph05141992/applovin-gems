"""applovin_page.py — The AppLovin Strategy deep-dive page (V2 white/blue)"""
import streamlit as st
import plotly.graph_objects as go
from datetime import datetime

# ── PHASE COLORS ──
PHASE_COLORS = {
    "IPO_GROWTH":"#2563EB","PEAK":"#16A34A","SELLOFF_TRIGGER":"#F59E0B",
    "SELLOFF":"#DC2626","CAPITULATION_ANOMALY":"#7C3AED","LATE_SELLOFF":"#DC2626",
    "BOTTOMING":"#F59E0B","EARLY_RECOVERY":"#16A34A","IGNITION":"#2563EB",
    "CONFIRMATION":"#16A34A","ACCELERATION":"#8B5CF6","SURGE":"#F59E0B",
    "EXTENDED_BULL":"#16A34A","CATALYST_QUARTER":"#2563EB",
}

def _white_chart(fig):
    """Apply white/blue design system to Plotly figure."""
    fig.update_layout(
        template="plotly_white",
        paper_bgcolor="#FFFFFF",
        plot_bgcolor="#FFFFFF",
        font=dict(family="Helvetica Neue, Helvetica, Arial, sans-serif", color="#111111"),
        xaxis=dict(gridcolor="#E2E8F0", zerolinecolor="#E2E8F0"),
        yaxis=dict(gridcolor="#E2E8F0", zerolinecolor="#E2E8F0"),
        margin=dict(l=40, r=20, t=40, b=40),
    )
    return fig

def _card(html):
    st.markdown(f'<div style="background:#F8FAFC;border:1px solid #E2E8F0;border-radius:8px;padding:16px;margin:8px 0;box-shadow:0 1px 3px rgba(0,0,0,0.08);">{html}</div>', unsafe_allow_html=True)

def _section(title, sub=""):
    st.markdown(f'''<div style="background:linear-gradient(90deg,rgba(37,99,235,0.08),transparent);border-left:4px solid #2563EB;padding:16px 20px;border-radius:0 8px 8px 0;margin:32px 0 16px 0;">
    <h2 style="font-size:20px!important;font-weight:700!important;color:#1E293B!important;margin:0!important;">{title}</h2>
    <div style="font-size:13px;color:#6B7280!important;margin-top:4px;">{sub}</div></div>''', unsafe_allow_html=True)

def _metric_box(label, value, color="#2563EB"):
    return f'<div style="background:#F8FAFC;border:1px solid #E2E8F0;border-radius:8px;padding:12px 16px;flex:1;text-align:center;"><div style="font-size:22px;font-weight:700;color:{color}!important;">{value}</div><div style="font-size:11px;color:#6B7280!important;margin-top:2px;">{label}</div></div>'

@st.cache_data
def _load_data():
    from applovin_data import (APP_QUARTERS, APP_FULL_CYCLE, GATE_DEFINITIONS,
        NON_FINANCIAL_PATTERNS, BEARISH_PHASE_DATA, INSTITUTIONAL_PILLARS,
        SURGE_ANALYSIS, QUOTE_TIMELINE, TOP_50_STOCKS)
    return APP_QUARTERS, APP_FULL_CYCLE, GATE_DEFINITIONS, NON_FINANCIAL_PATTERNS, BEARISH_PHASE_DATA, INSTITUTIONAL_PILLARS, SURGE_ANALYSIS, QUOTE_TIMELINE, TOP_50_STOCKS

def render_applovin_page():
    quarters, phases, gates, patterns, bearish, pillars, surge, quotes, stocks = _load_data()

    # ── HEADER ──
    st.markdown('''<div style="background:#F8FAFC;border:1px solid #E2E8F0;border-left:4px solid #2563EB;border-radius:8px;padding:28px 32px;margin-bottom:24px;box-shadow:0 1px 3px rgba(0,0,0,0.08);">
    <h1 style="font-size:28px!important;font-weight:700!important;color:#1E293B!important;margin:0!important;">The AppLovin Strategy</h1>
    <div style="font-size:14px;color:#6B7280!important;margin-top:6px;">How APP went from $9.40 to $733 — and the pattern that finds the next one</div>
    <div style="display:flex;gap:24px;margin-top:12px;font-size:12px;color:#6B7280!important;">
        <span>Ticker: <span style="color:#2563EB;font-weight:600;">APP</span></span>
        <span>18 Quarters Analyzed</span>
        <span>10 Cycle Phases</span>
        <span>5 Signal Gates</span>
    </div></div>''', unsafe_allow_html=True)

    # ═══════════════════════════════════════════════════════════════════════
    # SECTION 1A: 18 EXPANDABLE QUARTER CARDS
    # ═══════════════════════════════════════════════════════════════════════
    _section("Quarter-by-Quarter Breakdown", "18 quarters of earnings data with management signals (Q1'21 — Q2'25)")

    for q in quarters:
        phase = q.get("phase_name", "UNKNOWN")
        pc = PHASE_COLORS.get(phase, "#6B7280")
        eps_surprise = q["eps_surprise_pct"]
        rev = q["revenue_actual_m"]
        reaction = q["stock_reaction_pct"]

        # Collapsed summary
        label = (f"{q['quarter']}  |  "
                 f"<span style='background:{pc}22;color:{pc};padding:2px 8px;border-radius:4px;font-size:11px;font-weight:600;'>{phase.replace('_',' ')}</span>  |  "
                 f"EPS: {eps_surprise:+.1f}%  |  Rev: ${rev:,.0f}M  |  Stock: {reaction:+.1f}%")

        with st.expander(f"{q['quarter']} — {phase.replace('_',' ')} | EPS {eps_surprise:+.1f}% | ${rev:,.0f}M | Stock {reaction:+.1f}%"):
            # Phase badge
            st.markdown(f'<span style="background:{pc}22;color:{pc};padding:4px 12px;border-radius:6px;font-weight:700;font-size:13px;">{phase.replace("_"," ")}</span> <span style="color:#6B7280;font-size:12px;margin-left:8px;">{q["report_date"]}</span>', unsafe_allow_html=True)

            # EPS & Revenue table
            c1, c2, c3, c4 = st.columns(4)
            eps_color = "#16A34A" if eps_surprise > 0 else "#DC2626"
            rev_color = "#16A34A" if q.get("revenue_surprise_pct",0) > 0 else "#DC2626"
            react_color = "#16A34A" if reaction > 0 else "#DC2626"
            c1.markdown(_metric_box("EPS Surprise", f"{eps_surprise:+.1f}%", eps_color), unsafe_allow_html=True)
            c2.markdown(_metric_box("Revenue", f"${rev:,.0f}M", "#2563EB"), unsafe_allow_html=True)
            c3.markdown(_metric_box("EBITDA Margin", f"{q['ebitda_margin_pct']:.0f}%", "#1E293B"), unsafe_allow_html=True)
            c4.markdown(_metric_box("Stock Reaction", f"{reaction:+.1f}%", react_color), unsafe_allow_html=True)

            # EPS detail row
            c5, c6, c7, c8 = st.columns(4)
            c5.markdown(_metric_box("EPS Actual", f"${q['eps_actual']:.2f}", "#111111"), unsafe_allow_html=True)
            c6.markdown(_metric_box("EPS Estimate", f"${q['eps_estimate']:.2f}", "#6B7280"), unsafe_allow_html=True)
            pre = q.get("stock_price_pre", q.get("stock_price", 0))
            post = q.get("stock_price_post", pre)
            c7.markdown(_metric_box("Price Pre", f"${pre:,.0f}", "#6B7280"), unsafe_allow_html=True)
            c8.markdown(_metric_box("Price Post", f"${post:,.0f}", react_color), unsafe_allow_html=True)

            # Management quotes in styled blockquotes
            if q.get("mgmt_quotes"):
                st.markdown('<div style="margin-top:12px;">', unsafe_allow_html=True)
                for mq in q["mgmt_quotes"]:
                    st.markdown(f'<blockquote style="border-left:3px solid #2563EB;padding:8px 12px;margin:6px 0;background:#F8FAFC;border-radius:0 6px 6px 0;font-size:13px;color:#374151;font-style:italic;">"{mq}"</blockquote>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

            # AXON badge + TAM tags + Confidence meter
            tam_tags = "".join(f'<span style="background:#EFF6FF;color:#2563EB;font-size:11px;padding:2px 8px;border-radius:4px;margin:0 4px 0 0;">{t}</span>' for t in q.get("tam_mentions",[]))
            conf = q.get("management_confidence", 5)
            st.markdown(f"""<div style="display:flex;gap:12px;margin-top:12px;align-items:center;flex-wrap:wrap;">
            <span style="background:#F3E8FF;color:#7C3AED;font-size:11px;padding:3px 10px;border-radius:4px;font-weight:600;">AXON: {q.get('axon_stage','')}</span>
            {tam_tags}
            <span style="font-size:11px;color:#6B7280;">Confidence:</span>
            <div style="background:#E2E8F0;border-radius:4px;width:100px;height:8px;display:inline-block;"><div style="background:#2563EB;border-radius:4px;height:8px;width:{conf*10}%;"></div></div>
            <span style="font-size:11px;color:#2563EB;font-weight:600;">{conf}/10</span>
            </div>""", unsafe_allow_html=True)

            # Key themes
            theme_tags = "".join(f'<span style="display:inline-block;background:#FEF3C7;color:#92400E;font-size:11px;padding:2px 8px;border-radius:4px;margin:2px 4px 2px 0;">{t}</span>' for t in q.get("key_themes",[]))
            st.markdown(f'<div style="margin-top:8px;">{theme_tags}</div>', unsafe_allow_html=True)

            # FCF & Buybacks
            fcf = q.get("free_cash_flow_m")
            bb = q.get("buyback_m")
            if fcf is not None:
                fc1, fc2, fc3 = st.columns(3)
                fcf_color = "#16A34A" if fcf > 0 else "#DC2626"
                fc1.markdown(_metric_box("Free Cash Flow", f"${fcf:,.0f}M", fcf_color), unsafe_allow_html=True)
                fc2.markdown(_metric_box("Buybacks", f"${bb:,.0f}M" if bb else "N/A", "#2563EB"), unsafe_allow_html=True)
                shares = q.get("shares_outstanding_m")
                fc3.markdown(_metric_box("Shares Out", f"{shares:.0f}M" if shares else "N/A", "#6B7280"), unsafe_allow_html=True)

    # ═══════════════════════════════════════════════════════════════════════
    # SECTION 1B: SURGE ANALYSIS — $370 to $733 in 53 days
    # ═══════════════════════════════════════════════════════════════════════
    _section("Why APP Surged from $370 to $733 in 53 Days", "The anatomy of a momentum event")

    # Hero stat card
    st.markdown(f'''<div style="background:linear-gradient(135deg,#EFF6FF,#F8FAFC);border:2px solid #2563EB;border-radius:12px;padding:32px;text-align:center;margin-bottom:20px;">
    <div style="font-size:48px;font-weight:800;color:#2563EB;">+{surge["total_return_pct"]:.0f}%</div>
    <div style="font-size:18px;color:#1E293B;font-weight:600;margin-top:4px;">${surge["start_price"]} → ${surge["end_price"]} in {surge["duration_days"]} days</div>
    <div style="font-size:13px;color:#6B7280;margin-top:8px;">{surge["trigger"]}</div>
    </div>''', unsafe_allow_html=True)

    # 5 catalyst cards
    st.markdown("**53-Day Catalyst Timeline**")
    for cat in surge["catalysts"]:
        day_pct = (cat["day"] / 53) * 100
        st.markdown(f'''<div style="background:#F8FAFC;border:1px solid #E2E8F0;border-left:4px solid #2563EB;border-radius:0 8px 8px 0;padding:12px 16px;margin:6px 0;display:flex;justify-content:space-between;align-items:center;">
        <div>
            <span style="background:#2563EB;color:#FFF;font-size:11px;padding:2px 8px;border-radius:4px;font-weight:600;">Day {cat["day"]}</span>
            <span style="font-weight:600;color:#1E293B;margin-left:8px;">{cat["event"]}</span>
            <div style="font-size:12px;color:#6B7280;margin-top:4px;">{cat["description"]}</div>
        </div>
        <div style="font-size:20px;font-weight:700;color:#2563EB;">${cat["price"]}</div>
        </div>''', unsafe_allow_html=True)

    # 8-quarter momentum timeline chart
    st.markdown("**8-Quarter Momentum Build**")
    mom = surge["eight_quarter_momentum"]
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=[m["quarter"] for m in mom],
        y=[m["stock_reaction"] for m in mom],
        marker_color=["#16A34A" if m["stock_reaction"] > 0 else "#DC2626" for m in mom],
        name="Earnings Reaction %"
    ))
    fig.add_trace(go.Scatter(
        x=[m["quarter"] for m in mom],
        y=[m["cumulative_return"] for m in mom],
        mode="lines+markers", line=dict(color="#2563EB", width=3),
        marker=dict(size=8), name="Cumulative Return %", yaxis="y2"
    ))
    fig.update_layout(
        height=350, showlegend=True,
        yaxis=dict(title="Earnings Reaction %"),
        yaxis2=dict(title="Cumulative Return %", overlaying="y", side="right", gridcolor="transparent"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02)
    )
    st.plotly_chart(_white_chart(fig), use_container_width=True)

    # Comparison to Nov 2024 surge
    comp = surge["comparison_to_nov_2024"]
    c1, c2 = st.columns(2)
    with c1:
        _card(f'''<div style="font-size:14px;font-weight:700;color:#2563EB;">Nov 2024 Surge</div>
        <div style="font-size:13px;color:#374151;margin-top:4px;">{comp["nov_2024_surge"]}</div>''')
    with c2:
        _card(f'''<div style="font-size:14px;font-weight:700;color:#16A34A;">Aug 2025 Surge</div>
        <div style="font-size:13px;color:#374151;margin-top:4px;">{comp["aug_2025_surge"]}</div>''')
    st.markdown(f'<div style="font-size:12px;color:#6B7280;text-align:center;margin:8px 0;">{comp["key_difference"]}</div>', unsafe_allow_html=True)

    # ═══════════════════════════════════════════════════════════════════════
    # SECTION 1C: INSTITUTIONAL BULLISH PILLARS
    # ═══════════════════════════════════════════════════════════════════════
    _section("The 5 Institutional Bullish Pillars", "Why institutions are long APP — and which stocks share each pillar")

    pillar_colors = ["#2563EB","#16A34A","#F59E0B","#7C3AED","#DC2626"]
    for i, p in enumerate(pillars):
        pc = pillar_colors[i % len(pillar_colors)]
        evidence_html = "".join(f'<li style="font-size:12px;color:#374151;">{e}</li>' for e in p["evidence"])
        sharing_html = "".join(f'<span style="background:#EFF6FF;color:#2563EB;font-size:11px;padding:2px 6px;border-radius:4px;margin:0 4px 0 0;">{s}</span>' for s in p["stocks_sharing"])
        _card(f'''<div style="border-left:4px solid {pc};padding-left:12px;">
        <div style="font-size:16px;font-weight:700;color:{pc};">Pillar {p["pillar_number"]}: {p["pillar_name"]}</div>
        <div style="font-size:13px;color:#374151;margin-top:4px;">{p["description"]}</div>
        <ul style="margin:8px 0 8px 16px;padding:0;">{evidence_html}</ul>
        <div style="margin-top:6px;"><span style="font-size:11px;color:#6B7280;">Stocks sharing this pillar: </span>{sharing_html}</div>
        </div>''')

    # Cross-reference matrix: pillars vs top 20 stocks
    st.markdown("**Cross-Reference Matrix — Top 20 Stocks x 5 Pillars**")
    pillar_names = [p["pillar_name"] for p in pillars]
    pillar_stocks = [set(p["stocks_sharing"]) for p in pillars]

    # Get top 20 stocks by score
    top20 = sorted(stocks, key=lambda s: s["app_score"], reverse=True)[:20]
    matrix_html = '<table style="width:100%;border-collapse:collapse;font-size:12px;">'
    matrix_html += '<tr style="background:#F8FAFC;"><th style="padding:8px;text-align:left;border-bottom:2px solid #E2E8F0;">Stock</th>'
    for pn in pillar_names:
        short = pn[:12]
        matrix_html += f'<th style="padding:8px;text-align:center;border-bottom:2px solid #E2E8F0;font-size:11px;">{short}</th>'
    matrix_html += '</tr>'
    for s in top20:
        matrix_html += f'<tr style="border-bottom:1px solid #E2E8F0;"><td style="padding:6px 8px;font-weight:600;color:#1E293B;">{s["ticker"]}</td>'
        for ps in pillar_stocks:
            check = "&#10003;" if s["ticker"] in ps else ""
            color = "#16A34A" if check else "#E2E8F0"
            matrix_html += f'<td style="padding:6px;text-align:center;color:{color};font-weight:700;">{check}</td>'
        matrix_html += '</tr>'
    matrix_html += '</table>'
    st.markdown(matrix_html, unsafe_allow_html=True)

    # ═══════════════════════════════════════════════════════════════════════
    # SECTION 1D: THE 5 GATES (kept, white/blue charts)
    # ═══════════════════════════════════════════════════════════════════════
    _section("The 5 Signal Gates", "The scoring system that identifies APP-pattern stocks")

    tab_b, tab_c, tab_d, tab_e, tab_a, tab_react = st.tabs([
        "Gate B: EPS (35%)", "Gate C: Revenue (20%)", "Gate D: Guidance (15%)",
        "Gate E: Narrative (15%)", "Gate A: Washout", "Earnings Reaction (15%)"])

    with tab_b:
        g = gates["gate_b"]
        st.markdown(f"**{g['name']}** — Weight: {g['weight']*100:.0f}%")
        st.markdown(f"Threshold: `{g['threshold']}`")
        st.markdown(f"*{g['app_calibration']}*")
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=[q["quarter"] for q in quarters],
            y=[q["eps_surprise_pct"] for q in quarters],
            marker_color=["#2563EB" if q["eps_surprise_pct"] > 0 else "#DC2626" for q in quarters]
        ))
        fig.add_hline(y=15, line_dash="dash", line_color="#F59E0B", annotation_text="15% threshold")
        fig.update_layout(title="EPS Surprise % by Quarter (18Q)", height=380, yaxis_title="Surprise %")
        st.plotly_chart(_white_chart(fig), use_container_width=True)

    with tab_c:
        g = gates["gate_c"]
        st.markdown(f"**{g['name']}** — Weight: {g['weight']*100:.0f}%")
        st.markdown(f"*{g['app_calibration']}*")
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=[q["quarter"] for q in quarters],
            y=[q["revenue_actual_m"] for q in quarters],
            marker_color=["#2563EB" if q.get("revenue_surprise_pct",0) > 3 else "#CBD5E1" for q in quarters]
        ))
        fig.add_hline(y=715, line_dash="dot", line_color="#DC2626", annotation_text="$715M ceiling")
        fig.update_layout(title="Revenue by Quarter ($M)", height=380, yaxis_title="Revenue ($M)")
        st.plotly_chart(_white_chart(fig), use_container_width=True)

    with tab_d:
        g = gates["gate_d"]
        st.markdown(f"**{g['name']}** — Weight: {g['weight']*100:.0f}%")
        st.markdown(f"*{g['app_calibration']}*")
        guidance_qs = [q for q in quarters if q.get("guidance_next_q_low_m") is not None]
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=[q["quarter"] for q in guidance_qs],
            y=[(q["guidance_next_q_low_m"]+q["guidance_next_q_high_m"])/2 for q in guidance_qs],
            mode="lines+markers", line=dict(color="#2563EB", width=2),
            marker=dict(size=8, color="#2563EB"), name="Guidance Midpoint"))
        fig.update_layout(title="Guidance Midpoint Trend", height=350, yaxis_title="Guidance ($M)")
        st.plotly_chart(_white_chart(fig), use_container_width=True)

    with tab_e:
        g = gates["gate_e"]
        st.markdown(f"**{g['name']}** — Weight: {g['weight']*100:.0f}%")
        st.markdown(f"*{g['app_calibration']}*")
        for q in quarters:
            tags = " ".join(f'<span style="background:#F3E8FF;color:#7C3AED;font-size:11px;padding:2px 6px;border-radius:4px;margin:2px;">{t}</span>' for t in q.get("tam_mentions",[]))
            st.markdown(f'<div style="margin:4px 0;"><b style="color:#1E293B;font-size:12px;">{q["quarter"]}</b> <span style="background:#EFF6FF;color:#2563EB;font-size:11px;padding:2px 6px;border-radius:4px;">{q.get("axon_stage","")}</span> {tags}</div>', unsafe_allow_html=True)

    with tab_a:
        g = gates["gate_a"]
        st.markdown(f"**{g['name']}** — Pass/Fail Filter")
        st.markdown(f"*{g['app_calibration']}*")
        fig = go.Figure(go.Waterfall(
            x=["Peak ($112)","Fed Tightening","ATT Privacy","EPS Misses","Ad Collapse","Bottom ($9.40)"],
            y=[112,-30,-20,-35,-17.6,0],
            measure=["absolute","relative","relative","relative","relative","total"],
            connector=dict(line=dict(color="#E2E8F0")),
            decreasing=dict(marker=dict(color="#DC2626")),
            totals=dict(marker=dict(color="#F59E0B")),
        ))
        fig.update_layout(title="AppLovin Drawdown: $112 to $9.40 (-92%)", height=350)
        st.plotly_chart(_white_chart(fig), use_container_width=True)

    with tab_react:
        g = gates["event_reaction"]
        st.markdown(f"**{g['name']}** — Weight: {g['weight']*100:.0f}%")
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=[q["quarter"] for q in quarters],
            y=[q["stock_reaction_pct"] for q in quarters],
            marker_color=["#16A34A" if q["stock_reaction_pct"] > 0 else "#DC2626" for q in quarters]
        ))
        fig.update_layout(title="Stock Reaction on Earnings Day (%)", height=380, yaxis_title="Reaction %")
        st.plotly_chart(_white_chart(fig), use_container_width=True)

    # ═══════════════════════════════════════════════════════════════════════
    # SECTION 1E: QUOTE TIMELINE + CONFIDENCE CHART
    # ═══════════════════════════════════════════════════════════════════════
    _section("Management Quote Timeline", "Adam Foroughi's tone evolution across 18 quarters")

    # Vertical timeline
    for qt in quotes:
        tc = qt.get("tone_color","#6B7280")
        st.markdown(f'''<div style="display:flex;gap:16px;margin:8px 0;align-items:flex-start;">
        <div style="min-width:56px;text-align:right;">
            <div style="font-size:12px;font-weight:700;color:#1E293B;">{qt["quarter"]}</div>
            <div style="font-size:10px;color:#6B7280;">{qt["date"]}</div>
        </div>
        <div style="width:3px;background:{tc};border-radius:2px;min-height:48px;"></div>
        <div style="flex:1;">
            <span style="background:{tc}22;color:{tc};font-size:10px;padding:2px 8px;border-radius:4px;font-weight:600;text-transform:uppercase;">{qt["tone"]}</span>
            <div style="font-size:13px;color:#374151;margin-top:4px;font-style:italic;">"{qt["quote"]}"</div>
            <div style="font-size:11px;color:#6B7280;margin-top:2px;">{qt["context"]}</div>
        </div></div>''', unsafe_allow_html=True)

    # Enhanced management confidence chart
    st.markdown("**Management Confidence & Tone Rating**")
    fig = go.Figure()
    tone_ratings = [q.get("mgmt_tone_rating", q.get("management_confidence",5)) for q in quarters]
    conf_ratings = [q.get("management_confidence",5) for q in quarters]
    fig.add_trace(go.Bar(
        x=[q["quarter"] for q in quarters], y=tone_ratings,
        marker_color=[PHASE_COLORS.get(q.get("phase_name",""),"#6B7280") for q in quarters],
        name="Tone Rating", opacity=0.6
    ))
    fig.add_trace(go.Scatter(
        x=[q["quarter"] for q in quarters], y=conf_ratings,
        mode="lines+markers", line=dict(color="#2563EB", width=3),
        marker=dict(size=8, color="#2563EB"), name="Confidence (1-10)"
    ))
    fig.update_layout(height=350, yaxis=dict(range=[0,11], title="Score"), showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02))
    st.plotly_chart(_white_chart(fig), use_container_width=True)

    # Margin progression chart
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=[q["quarter"] for q in quarters], y=[q["ebitda_margin_pct"] for q in quarters],
        mode="lines+markers", fill="tozeroy", line=dict(color="#2563EB", width=2),
        fillcolor="rgba(37,99,235,0.08)", name="EBITDA Margin"
    ))
    fig.update_layout(title="Margin Trajectory: 14% to 68%", height=300, yaxis_title="EBITDA Margin %")
    st.plotly_chart(_white_chart(fig), use_container_width=True)

    # ═══════════════════════════════════════════════════════════════════════
    # SECTION 1F: BEARISH PHASE
    # ═══════════════════════════════════════════════════════════════════════
    st.markdown('''<div style="background:linear-gradient(90deg,rgba(220,38,38,0.08),transparent);border-left:4px solid #DC2626;padding:16px 20px;border-radius:0 8px 8px 0;margin:32px 0 16px 0;">
    <h2 style="font-size:20px!important;font-weight:700!important;color:#DC2626!important;margin:0!important;">Bearish Phase — Reverse Pattern Recognition</h2>
    <div style="font-size:13px;color:#6B7280!important;margin-top:4px;">How to detect when a stock is in the APP selloff phase — and when it's bottoming</div></div>''', unsafe_allow_html=True)

    # EPS miss magnitude chart
    bqs = bearish["bearish_quarters"]
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=[q["quarter"] for q in bqs], y=[q["eps_miss_pct"] for q in bqs],
        marker_color=["#DC2626" if q["eps_miss_pct"] < -100 else "#F59E0B" for q in bqs]
    ))
    fig.update_layout(title="EPS Miss Magnitude — Worsening Then Improving", height=300, yaxis_title="Miss %")
    st.plotly_chart(_white_chart(fig), use_container_width=True)

    # Warning vs Bottoming signals
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**Warning Signals**")
        for w in bearish["bearish_warning_rules"]:
            st.markdown(f'<div style="font-size:12px;color:#DC2626;margin:4px 0;">&#10007; {w}</div>', unsafe_allow_html=True)
    with c2:
        st.markdown("**Bottoming Signals**")
        for b in bearish["bottoming_signals"]:
            st.markdown(f'<div style="font-size:12px;color:#16A34A;margin:4px 0;">&#10003; {b}</div>', unsafe_allow_html=True)

    # May 2022 Anomaly callout — purple left border
    _card(f'''<div style="border-left:4px solid #7C3AED;padding-left:12px;">
    <div style="font-size:15px;font-weight:700;color:#7C3AED;">The May 2022 Anomaly</div>
    <div style="font-size:13px;color:#374151;margin-top:6px;">Q1'22 reported a <b style="color:#DC2626;">-750% EPS miss</b> — one of the worst in APP history. Yet the stock <b style="color:#16A34A;">rallied 34%</b> the next day. This is the classic <b>capitulation exhaustion signal</b>: when the worst possible news fails to push the price lower, sellers are exhausted. Management's tone shifted from defensive to restructuring. Three months later, AXON 2 development was announced. This is the signal that separates bottoming from continued decline.</div></div>''')

    # ── Non-financial patterns ──
    _section("Non-Financial Pattern Recognition", "8 qualitative signals that precede price moves")

    for i in range(0, len(patterns), 2):
        c1, c2 = st.columns(2)
        for col, idx in [(c1, i), (c2, i+1 if i+1 < len(patterns) else None)]:
            if idx is not None:
                p = patterns[idx]
                with col:
                    _card(f"""<div style="font-size:14px;font-weight:700;color:#1E293B;">{p['pattern_name']}</div>
                    <div style="font-size:12px;color:#6B7280;margin:6px 0;">{p['description']}</div>
                    <div style="font-size:11px;color:#16A34A;">APP Evidence: {p['app_evidence']}</div>
                    <div style="display:flex;justify-content:space-between;align-items:center;margin-top:8px;">
                        <span style="font-size:10px;color:#6B7280;">Weight: {p['weight']*100:.0f}%</span>
                        <div style="background:#E2E8F0;border-radius:4px;width:60px;height:6px;"><div style="background:#2563EB;border-radius:4px;height:6px;width:{p['weight']*100*6.67:.0f}%;"></div></div>
                    </div>""")
