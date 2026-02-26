"""options_page.py — Options Engine with strategy overview, conviction ranking, P/L scenarios"""
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

STAGE_COLORS = {"PRE_BREAKOUT":"#F59E0B","EARLY_CONFIRMATION":"#3B82F6","MID_CONFIRMATION":"#22C55E","LATE_CONFIRMATION":"#8B5CF6","SURGE_PHASE":"#C4A265"}
STAGE_EXPIRY = {"PRE_BREAKOUT":"5-6 months","EARLY_CONFIRMATION":"4-5 months","MID_CONFIRMATION":"3-4 months","LATE_CONFIRMATION":"2-3 months","SURGE_PHASE":"45-60 days"}

@st.cache_data
def _load():
    from applovin_data import TOP_50_STOCKS, TOP_25_CONVICTION
    return TOP_50_STOCKS, TOP_25_CONVICTION

def render_options_page():
    stocks, top25 = _load()

    st.markdown('''<div style="background:linear-gradient(135deg,#1A1A1A,#252525);border:1px solid #2A2A2A;border-left:4px solid #C4A265;border-radius:12px;padding:28px 32px;margin-bottom:24px;">
    <h1 style="font-size:28px!important;font-weight:700!important;color:#C4A265!important;margin:0!important;">⚡ Options Engine</h1>
    <div style="font-size:14px;color:#999!important;margin-top:6px;">Long call + bear put spread for every stock — stage-calibrated expiry, IV-aware sizing</div></div>''', unsafe_allow_html=True)

    # ── STRATEGY OVERVIEW ──
    _section("Strategy Architecture", "Two-leg structure: Long Call (upside) + Bear Put Spread (protection)")

    c1, c2 = st.columns(2)
    with c1:
        st.markdown('''<div style="background:#1E1E1E;border:1px solid #22C55E40;border-top:3px solid #22C55E;border-radius:8px;padding:16px;">
        <div style="font-size:16px;font-weight:700;color:#22C55E;">📈 Leg 1: Long Call</div>
        <div style="font-size:13px;color:#E8E8E8;margin-top:8px;">
        <b>Strike:</b> ATM or 1-2 strikes OTM<br>
        <b>Expiry:</b> Stage-calibrated (see table below)<br>
        <b>Goal:</b> Capture upside from post-earnings momentum<br>
        <b>Max Loss:</b> Premium paid
        </div></div>''', unsafe_allow_html=True)
    with c2:
        st.markdown('''<div style="background:#1E1E1E;border:1px solid #EF444440;border-top:3px solid #EF4444;border-radius:8px;padding:16px;">
        <div style="font-size:16px;font-weight:700;color:#EF4444;">📉 Leg 2: Bear Put Spread</div>
        <div style="font-size:13px;color:#E8E8E8;margin-top:8px;">
        <b>Long Put:</b> Near support level<br>
        <b>Short Put:</b> 10-15% below long put<br>
        <b>Goal:</b> Reduce cost basis, define max loss<br>
        <b>Max Gain:</b> Spread width - net debit
        </div></div>''', unsafe_allow_html=True)

    # Expiry by stage table
    st.markdown("**Expiry Calendar by Stage:**")
    stage_html = '<div style="display:flex;gap:8px;flex-wrap:wrap;">'
    for stage, exp in STAGE_EXPIRY.items():
        sc = STAGE_COLORS[stage]
        stage_html += f'<div style="background:#1E1E1E;border:1px solid {sc}40;border-top:2px solid {sc};border-radius:6px;padding:8px 14px;text-align:center;flex:1;min-width:150px;"><div style="font-size:11px;font-weight:600;color:{sc};">{stage.replace("_"," ")}</div><div style="font-size:14px;color:#E8E8E8;font-weight:700;margin-top:2px;">{exp}</div></div>'
    stage_html += '</div>'
    st.markdown(stage_html, unsafe_allow_html=True)

    # ── TOP 25 CONVICTION ──
    _section("Top 25 Conviction Rankings", "Ordered by combined APP score + options risk/reward")

    for item in top25:
        ticker = item["ticker"]
        s = next((x for x in stocks if x["ticker"] == ticker), None)
        if not s:
            continue
        sc = STAGE_COLORS.get(s["app_stage"], "#999")
        rr_color = "#22C55E" if s["recovery_ratio"] >= 3.0 else "#C4A265" if s["recovery_ratio"] >= 2.0 else "#F59E0B"

        st.markdown(f'''<div style="background:#1E1E1E;border:1px solid #2A2A2A;border-left:3px solid {sc};border-radius:8px;padding:12px 16px;margin:6px 0;display:flex;align-items:center;gap:16px;">
        <div style="font-size:20px;font-weight:700;color:#666;min-width:30px;">#{item["rank"]}</div>
        <div style="min-width:55px;"><span style="font-size:16px;font-weight:700;color:#C4A265;">{ticker}</span></div>
        <div style="flex:1;font-size:12px;color:#999;">{item["conviction_statement"]}</div>
        <div style="text-align:center;min-width:60px;"><div style="font-size:16px;font-weight:700;color:{sc};">{s["app_score"]}</div><div style="font-size:9px;color:#666;">Score</div></div>
        <div style="text-align:center;min-width:50px;"><div style="font-size:16px;font-weight:700;color:{rr_color};">{s["recovery_ratio"]:.1f}x</div><div style="font-size:9px;color:#666;">R/R</div></div>
        <div style="text-align:center;min-width:50px;"><div style="font-size:14px;font-weight:600;color:#3B82F6;">{s["iv_rank"]}</div><div style="font-size:9px;color:#666;">IV Rank</div></div>
        </div>''', unsafe_allow_html=True)

    # ── ALL 50 OPTIONS SETUPS ──
    _section("All 50 Options Setups", "Click any stock for full trade structure")

    # Stage filter
    stage_filter = st.multiselect("Filter by Stage", list(STAGE_COLORS.keys()),
        default=list(STAGE_COLORS.keys()), format_func=lambda x: x.replace("_"," "), key="opt_stage")

    filtered = [s for s in stocks if s["app_stage"] in stage_filter]
    filtered.sort(key=lambda s: s["app_score"], reverse=True)

    for s in filtered:
        sc = STAGE_COLORS.get(s["app_stage"], "#999")
        with st.expander(f"{s['ticker']} — {s['company_name']} | Score: {s['app_score']} | IV: {s['iv_rank']} | R/R: {s['recovery_ratio']:.1f}x"):
            # Trade structure
            tc1, tc2, tc3 = st.columns(3)
            with tc1:
                st.markdown(f'''<div style="background:#1E1E1E;border:1px solid #22C55E40;border-radius:8px;padding:12px;">
                <div style="font-size:13px;font-weight:700;color:#22C55E;">Long Call</div>
                <div style="font-size:12px;color:#E8E8E8;margin-top:6px;">
                Strike: <b>${s["call_strike"]:.0f}</b><br>
                Expiry: <b>{s["call_expiry"]}</b><br>
                Premium: <b style="color:#F59E0B;">${s["call_premium"]:.2f}</b>
                </div></div>''', unsafe_allow_html=True)
            with tc2:
                st.markdown(f'''<div style="background:#1E1E1E;border:1px solid #EF444440;border-radius:8px;padding:12px;">
                <div style="font-size:13px;font-weight:700;color:#EF4444;">Bear Put Spread</div>
                <div style="font-size:12px;color:#E8E8E8;margin-top:6px;">
                Long Put: <b>${s["put_buy_strike"]:.0f}</b><br>
                Short Put: <b>${s["put_sell_strike"]:.0f}</b><br>
                Cost: <b style="color:#F59E0B;">${s["put_spread_cost"]:.2f}</b><br>
                Expiry: <b>{s["put_spread_expiry"]}</b>
                </div></div>''', unsafe_allow_html=True)
            with tc3:
                rr_color = "#22C55E" if s["recovery_ratio"] >= 3.0 else "#C4A265" if s["recovery_ratio"] >= 2.0 else "#F59E0B"
                st.markdown(f'''<div style="background:#1E1E1E;border:1px solid #C4A26540;border-radius:8px;padding:12px;">
                <div style="font-size:13px;font-weight:700;color:#C4A265;">Summary</div>
                <div style="font-size:12px;color:#E8E8E8;margin-top:6px;">
                Total Debit: <b style="color:#F59E0B;">${s["total_debit"]:.2f}</b><br>
                Max Loss: <b style="color:#EF4444;">${s["max_loss"]:.2f}</b><br>
                Breakeven: <b>${s["upside_breakeven"]:.0f}</b><br>
                Target: <b style="color:#22C55E;">+{s["target_profit_pct"]:.0f}%</b><br>
                R/R: <b style="color:{rr_color};">{s["recovery_ratio"]:.1f}x</b>
                </div></div>''', unsafe_allow_html=True)

            # P/L chart
            current = s["price_current"]
            strike = s["call_strike"]
            premium = s["total_debit"]
            prices = [current * (1 + p/100) for p in range(-30, 61, 5)]
            pnls = []
            for px in prices:
                call_value = max(0, px - strike) - s["call_premium"]
                put_value = max(0, s["put_buy_strike"] - px) - max(0, s["put_sell_strike"] - px) - s["put_spread_cost"]
                pnls.append(call_value + put_value)

            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=prices, y=pnls, mode="lines", fill="tozeroy",
                line=dict(color="#C4A265", width=2),
                fillcolor="rgba(196,162,101,0.1)",
                hovertemplate="Price: $%{x:.0f}<br>P/L: $%{y:.2f}<extra></extra>"))
            fig.add_hline(y=0, line_color="#666", line_dash="dash")
            fig.add_vline(x=current, line_color="#3B82F6", line_dash="dot",
                annotation_text=f"Current ${current:.0f}", annotation_position="top")
            fig.add_vline(x=s["upside_breakeven"], line_color="#22C55E", line_dash="dot",
                annotation_text=f"BE ${s['upside_breakeven']:.0f}", annotation_position="top")
            fig.update_layout(height=280, title=f"{s['ticker']} P/L at Expiry", xaxis_title="Stock Price", yaxis_title="P/L ($)")
            st.plotly_chart(_gold_chart(fig), use_container_width=True)

            # Rationale + earnings + caution
            ec1, ec2 = st.columns(2)
            with ec1:
                st.markdown(f'<div style="background:rgba(196,162,101,0.08);border:1px solid #C4A26540;border-radius:8px;padding:12px;"><div style="font-size:11px;color:#999;">Options Rationale</div><div style="font-size:12px;color:#E8E8E8;margin-top:4px;">{s["options_rationale"]}</div></div>', unsafe_allow_html=True)
            with ec2:
                st.markdown(f'''<div style="background:rgba(59,130,246,0.08);border:1px solid #3B82F640;border-radius:8px;padding:12px;">
                <div style="font-size:11px;color:#999;">Next Earnings</div>
                <div style="font-size:16px;font-weight:700;color:#3B82F6;margin-top:4px;">{s["next_earnings_date"]}</div>
                <div style="font-size:11px;color:#999;margin-top:4px;">IV Rank: <b style="color:{"#22C55E" if s["iv_rank"]<40 else "#F59E0B" if s["iv_rank"]<60 else "#EF4444"}">{s["iv_rank"]}</b></div></div>''', unsafe_allow_html=True)

            if s["caution_flags"]:
                flags = " ".join(f'<span style="background:rgba(239,68,68,0.15);color:#EF4444;font-size:11px;padding:2px 6px;border-radius:4px;margin:2px;">⚠ {f}</span>' for f in s["caution_flags"])
                st.markdown(f'<div style="margin-top:8px;">{flags}</div>', unsafe_allow_html=True)

    # ── RISK SUMMARY ──
    _section("Portfolio Risk Summary", "Aggregate exposure across all 50 positions")

    total_debit = sum(s["total_debit"] for s in stocks)
    avg_rr = sum(s["recovery_ratio"] for s in stocks) / len(stocks)
    avg_iv = sum(s["iv_rank"] for s in stocks) / len(stocks)
    low_iv = len([s for s in stocks if s["iv_rank"] < 40])
    high_iv = len([s for s in stocks if s["iv_rank"] > 60])

    rc1, rc2, rc3, rc4, rc5 = st.columns(5)
    def _rbox(col, label, value, color="#C4A265"):
        col.markdown(f'<div style="background:#1E1E1E;border:1px solid #2A2A2A;border-radius:8px;padding:12px;text-align:center;"><div style="font-size:20px;font-weight:700;color:{color};">{value}</div><div style="font-size:10px;color:#999;">{label}</div></div>', unsafe_allow_html=True)

    _rbox(rc1, "Total Debit (all 50)", f"${total_debit:,.0f}", "#F59E0B")
    _rbox(rc2, "Avg Recovery Ratio", f"{avg_rr:.1f}x", "#22C55E")
    _rbox(rc3, "Avg IV Rank", f"{avg_iv:.0f}", "#3B82F6")
    _rbox(rc4, "Low IV (<40)", f"{low_iv}", "#22C55E")
    _rbox(rc5, "High IV (>60)", f"{high_iv}", "#EF4444")

    # IV distribution chart
    fig = go.Figure()
    for stage in STAGE_COLORS:
        group = [s for s in stocks if s["app_stage"] == stage]
        if group:
            fig.add_trace(go.Box(y=[s["iv_rank"] for s in group], name=stage.replace("_"," "),
                marker_color=STAGE_COLORS[stage], boxpoints="all", jitter=0.3, pointpos=-1.8))
    fig.update_layout(height=350, title="IV Rank Distribution by Stage", yaxis_title="IV Rank")
    st.plotly_chart(_gold_chart(fig), use_container_width=True)

    # Disclaimer
    st.markdown('''<div style="background:rgba(239,68,68,0.05);border:1px solid #EF444430;border-radius:8px;padding:16px;margin-top:24px;">
    <div style="font-size:12px;color:#EF4444;font-weight:700;">⚠️ DISCLAIMER</div>
    <div style="font-size:11px;color:#999;margin-top:6px;">This is NOT financial advice. All options setups are hypothetical illustrations of the AppLovin Pattern methodology. Options involve significant risk of loss. Past patterns do not guarantee future results. Always conduct your own due diligence and consult a financial advisor before trading options. Data shown is representative and may not reflect current market conditions.</div></div>''', unsafe_allow_html=True)
