"""options_page.py — Bloomberg-card style Options Engine (V2 white/blue)"""
import streamlit as st
import plotly.graph_objects as go
from datetime import datetime, date
import numpy as np

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

STAGE_COLORS = {"PRE_BREAKOUT":"#F59E0B","EARLY_CONFIRMATION":"#3B82F6",
    "MID_CONFIRMATION":"#16A34A","LATE_CONFIRMATION":"#8B5CF6","SURGE_PHASE":"#2563EB"}
STAGE_EXPIRY = {"PRE_BREAKOUT":"5-6 months","EARLY_CONFIRMATION":"4-5 months",
    "MID_CONFIRMATION":"3-4 months","LATE_CONFIRMATION":"2-3 months","SURGE_PHASE":"45-60 days"}

@st.cache_data(ttl=3600)
def _fetch_iv(ticker):
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

def _earnings_countdown(earnings_date_str):
    try:
        ed = datetime.strptime(earnings_date_str, "%Y-%m-%d").date()
        delta = (ed - date.today()).days
        if delta > 0:
            return f"{delta}d", "#2563EB"
        elif delta == 0:
            return "TODAY", "#DC2626"
        else:
            return "PAST", "#6B7280"
    except Exception:
        return "N/A", "#6B7280"

@st.cache_data
def _load():
    from applovin_data import TOP_50_STOCKS, TOP_25_CONVICTION
    return TOP_50_STOCKS, TOP_25_CONVICTION

def render_options_page():
    stocks, top25 = _load()

    st.markdown('''<div style="background:#F8FAFC;border:1px solid #E2E8F0;border-left:4px solid #2563EB;border-radius:8px;padding:28px 32px;margin-bottom:24px;box-shadow:0 1px 3px rgba(0,0,0,0.08);">
    <h1 style="font-size:28px!important;font-weight:700!important;color:#1E293B!important;margin:0!important;">Options Engine</h1>
    <div style="font-size:14px;color:#6B7280!important;margin-top:6px;">Long call + bear put spread for every stock — stage-calibrated expiry, IV-aware sizing</div></div>''', unsafe_allow_html=True)

    # ── STRATEGY OVERVIEW ──
    _section("Strategy Architecture", "Two-leg structure: Long Call (upside) + Bear Put Spread (protection)")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown('''<div style="background:#F8FAFC;border:1px solid #E2E8F0;border-top:3px solid #16A34A;border-radius:8px;padding:16px;box-shadow:0 1px 3px rgba(0,0,0,0.08);">
        <div style="font-size:16px;font-weight:700;color:#16A34A;">Leg 1: Long Call</div>
        <div style="font-size:13px;color:#374151;margin-top:8px;">
        <b>Strike:</b> ATM or 1-2 strikes OTM<br>
        <b>Expiry:</b> Stage-calibrated (see table below)<br>
        <b>Goal:</b> Capture upside from post-earnings momentum<br>
        <b>Max Loss:</b> Premium paid
        </div></div>''', unsafe_allow_html=True)
    with c2:
        st.markdown('''<div style="background:#F8FAFC;border:1px solid #E2E8F0;border-top:3px solid #DC2626;border-radius:8px;padding:16px;box-shadow:0 1px 3px rgba(0,0,0,0.08);">
        <div style="font-size:16px;font-weight:700;color:#DC2626;">Leg 2: Bear Put Spread</div>
        <div style="font-size:13px;color:#374151;margin-top:8px;">
        <b>Long Put:</b> Near support level<br>
        <b>Short Put:</b> 10-15% below long put<br>
        <b>Goal:</b> Reduce cost basis, define max loss<br>
        <b>Max Gain:</b> Spread width - net debit
        </div></div>''', unsafe_allow_html=True)

    st.markdown("**Expiry Calendar by Stage:**")
    stage_html = '<div style="display:flex;gap:8px;flex-wrap:wrap;">'
    for stage, exp in STAGE_EXPIRY.items():
        sc = STAGE_COLORS[stage]
        stage_html += f'<div style="background:#F8FAFC;border:1px solid #E2E8F0;border-top:2px solid {sc};border-radius:6px;padding:8px 14px;text-align:center;flex:1;min-width:140px;"><div style="font-size:11px;font-weight:600;color:{sc};">{stage.replace("_"," ")}</div><div style="font-size:14px;color:#1E293B;font-weight:700;margin-top:2px;">{exp}</div></div>'
    stage_html += '</div>'
    st.markdown(stage_html, unsafe_allow_html=True)

    # ── TOP 25 CONVICTION ──
    _section("Top 25 Conviction Rankings", "Ordered by combined APP score + options risk/reward")
    for item in top25:
        ticker = item["ticker"]
        s = next((x for x in stocks if x["ticker"] == ticker), None)
        if not s:
            continue
        sc = STAGE_COLORS.get(s["app_stage"], "#6B7280")
        rr_color = "#16A34A" if s["recovery_ratio"] >= 3.0 else "#2563EB" if s["recovery_ratio"] >= 2.0 else "#F59E0B"
        st.markdown(f'''<div style="background:#F8FAFC;border:1px solid #E2E8F0;border-left:3px solid {sc};border-radius:8px;padding:12px 16px;margin:6px 0;display:flex;align-items:center;gap:16px;box-shadow:0 1px 3px rgba(0,0,0,0.08);">
        <div style="font-size:20px;font-weight:700;color:#CBD5E1;min-width:30px;">#{item["rank"]}</div>
        <div style="min-width:55px;"><span style="font-size:16px;font-weight:700;color:#2563EB;">{ticker}</span></div>
        <div style="flex:1;font-size:12px;color:#6B7280;">{item["conviction_statement"]}</div>
        <div style="text-align:center;min-width:55px;"><div style="font-size:16px;font-weight:700;color:{sc};">{s["app_score"]}</div><div style="font-size:9px;color:#6B7280;">Score</div></div>
        <div style="text-align:center;min-width:50px;"><div style="font-size:16px;font-weight:700;color:{rr_color};">{s["recovery_ratio"]:.1f}x</div><div style="font-size:9px;color:#6B7280;">R/R</div></div>
        <div style="text-align:center;min-width:50px;"><div style="font-size:14px;font-weight:600;color:#2563EB;">{s["iv_rank"]}</div><div style="font-size:9px;color:#6B7280;">IV Rank</div></div>
        </div>''', unsafe_allow_html=True)

    # ── ALL 50 OPTIONS SETUPS — BLOOMBERG CARD STYLE ──
    _section("All 50 Options Setups", "Bloomberg-terminal style trade cards")

    stage_filter = st.multiselect("Filter by Stage", list(STAGE_COLORS.keys()),
        default=list(STAGE_COLORS.keys()), format_func=lambda x: x.replace("_"," "), key="opt_stage")
    filtered = [s for s in stocks if s["app_stage"] in stage_filter]
    filtered.sort(key=lambda s: s["app_score"], reverse=True)

    for s in filtered:
        sc = STAGE_COLORS.get(s["app_stage"], "#6B7280")
        live_iv = _fetch_iv(s["ticker"])
        iv = live_iv if live_iv is not None else s.get("iv_rank", 0)
        iv_color = "#16A34A" if iv < 40 else "#F59E0B" if iv <= 60 else "#DC2626"
        countdown, cd_color = _earnings_countdown(s.get("next_earnings_date",""))
        current = s["price_current"]
        breakeven = s["upside_breakeven"]

        with st.expander(f"{s['ticker']} — {s['company_name']} | Score: {s['app_score']} | IV: {iv:.0f} | R/R: {s['recovery_ratio']:.1f}x"):
            # ── HEADER BAR ──
            st.markdown(f'''<div style="background:#F8FAFC;border:1px solid #E2E8F0;border-radius:8px;padding:14px 18px;margin-bottom:12px;display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:8px;">
            <div style="display:flex;align-items:center;gap:12px;">
                <span style="font-size:20px;font-weight:800;color:#1E293B;">{s["ticker"]}</span>
                <span style="font-size:13px;color:#6B7280;">{s["company_name"]}</span>
                <span style="background:{sc};color:#FFF;padding:3px 10px;border-radius:6px;font-size:11px;font-weight:600;">{s["app_stage"].replace("_"," ")}</span>
                <span style="font-size:14px;font-weight:700;color:{sc};">{s["app_score"]}</span>
            </div>
            <div style="display:flex;gap:16px;align-items:center;">
                <div style="text-align:center;"><div style="font-size:11px;color:#6B7280;">Earnings</div><div style="font-size:14px;font-weight:700;color:{cd_color};">{countdown}</div></div>
                <div style="text-align:center;"><div style="font-size:11px;color:#6B7280;">IV Rank{"*" if live_iv is not None else ""}</div><div style="font-size:14px;font-weight:700;color:{iv_color};">{iv:.0f}%</div></div>
            </div></div>''', unsafe_allow_html=True)

            # ── TRADE INSTRUCTION BOX ──
            net_debit = s["total_debit"]
            max_loss = s["max_loss"]
            target = s["target_profit_pct"]
            st.markdown(f'''<div style="background:#1E293B;border-radius:8px;padding:16px 20px;margin-bottom:12px;font-family:'Courier New',monospace;font-size:13px;color:#E2E8F0;line-height:1.8;">
BUY 1x {s["ticker"]} {s["call_expiry"]} ${s["call_strike"]:.0f}C @ ${s["call_premium"]:.2f}<br>
BUY 1x {s["ticker"]} {s["put_spread_expiry"]} ${s["put_buy_strike"]:.0f}P<br>
SELL 1x {s["ticker"]} {s["put_spread_expiry"]} ${s["put_sell_strike"]:.0f}P @ ${s["put_spread_cost"]:.2f}<br>
<br>
<span style="color:#CBD5E1;">NET DEBIT:</span> <span style="color:#F59E0B;font-weight:700;">${net_debit:.2f}</span> &nbsp;&nbsp;
<span style="color:#CBD5E1;">MAX LOSS:</span> <span style="color:#DC2626;font-weight:700;">${max_loss:.2f}</span> &nbsp;&nbsp;
<span style="color:#CBD5E1;">BREAKEVEN:</span> <span style="color:#16A34A;font-weight:700;">${breakeven:.0f}</span> &nbsp;&nbsp;
<span style="color:#CBD5E1;">TARGET:</span> <span style="color:#16A34A;font-weight:700;">+{target:.0f}%</span>
</div>''', unsafe_allow_html=True)

            # ── P/L CHART ──
            strike = s["call_strike"]
            prices_range = list(range(int(current * 0.7), int(current * 1.6) + 1, max(1, int(current * 0.02))))
            pnls = []
            for px in prices_range:
                call_val = max(0, px - strike) - s["call_premium"]
                put_val = max(0, s["put_buy_strike"] - px) - max(0, s["put_sell_strike"] - px) - s["put_spread_cost"]
                pnls.append(call_val + put_val)

            fig = go.Figure()
            # Green zone (profit)
            profit_x = [p for p, pnl in zip(prices_range, pnls) if pnl >= 0]
            profit_y = [pnl for pnl in pnls if pnl >= 0]
            # Red zone (loss)
            loss_x = [p for p, pnl in zip(prices_range, pnls) if pnl < 0]
            loss_y = [pnl for pnl in pnls if pnl < 0]

            fig.add_trace(go.Scatter(x=prices_range, y=pnls, mode="lines",
                line=dict(color="#2563EB", width=3), name="P/L",
                hovertemplate="Price: $%{x:.0f}<br>P/L: $%{y:.2f}<extra></extra>"))
            # Fill profit zone
            fig.add_trace(go.Scatter(x=prices_range, y=[max(0, pnl) for pnl in pnls],
                fill="tozeroy", fillcolor="rgba(22,163,74,0.12)", line=dict(width=0),
                showlegend=False, hoverinfo="skip"))
            # Fill loss zone
            fig.add_trace(go.Scatter(x=prices_range, y=[min(0, pnl) for pnl in pnls],
                fill="tozeroy", fillcolor="rgba(220,38,38,0.08)", line=dict(width=0),
                showlegend=False, hoverinfo="skip"))

            fig.add_hline(y=0, line_color="#CBD5E1", line_dash="dash")
            fig.add_vline(x=current, line_color="#2563EB", line_dash="dot",
                annotation_text=f"Current ${current:.0f}", annotation_position="top")
            fig.add_vline(x=breakeven, line_color="#16A34A", line_dash="dot",
                annotation_text=f"BE ${breakeven:.0f}", annotation_position="top")
            fig.update_layout(height=280, title=f"{s['ticker']} P/L at Expiry",
                xaxis_title="Stock Price", yaxis_title="P/L ($)", showlegend=False)
            st.plotly_chart(_white_chart(fig), use_container_width=True)

            # ── ONE-LINE SUMMARY ──
            st.markdown(f'''<div style="background:#EFF6FF;border:1px solid #BFDBFE;border-radius:8px;padding:10px 14px;font-size:13px;color:#1E293B;">
            This trade profits if <b>{s["ticker"]}</b> moves above <b>${breakeven:.0f}</b> by <b>{s["call_expiry"]}</b>
            </div>''', unsafe_allow_html=True)

            # ── RATIONALE + EARNINGS ──
            ec1, ec2 = st.columns(2)
            with ec1:
                st.markdown(f'''<div style="background:#F8FAFC;border:1px solid #E2E8F0;border-radius:8px;padding:12px;">
                <div style="font-size:11px;color:#6B7280;">Options Rationale</div>
                <div style="font-size:12px;color:#374151;margin-top:4px;">{s["options_rationale"]}</div></div>''', unsafe_allow_html=True)
            with ec2:
                st.markdown(f'''<div style="background:#F8FAFC;border:1px solid #E2E8F0;border-radius:8px;padding:12px;">
                <div style="font-size:11px;color:#6B7280;">Next Earnings</div>
                <div style="font-size:16px;font-weight:700;color:#2563EB;margin-top:4px;">{s.get("next_earnings_date","N/A")}</div>
                <div style="font-size:11px;color:#6B7280;margin-top:4px;">IV Rank: <b style="color:{iv_color};">{iv:.0f}%</b></div></div>''', unsafe_allow_html=True)

            # ── CAUTION FLAGS as red pills ──
            if s.get("caution_flags"):
                flags = " ".join(f'<span style="background:#DC2626;color:#FFF;font-size:11px;padding:3px 10px;border-radius:20px;margin:2px;font-weight:600;">{f}</span>' for f in s["caution_flags"])
                st.markdown(f'<div style="margin-top:8px;">{flags}</div>', unsafe_allow_html=True)

    # ── RISK SUMMARY ──
    _section("Portfolio Risk Summary", "Aggregate exposure across all 50 positions")

    total_debit_all = sum(s["total_debit"] for s in stocks)
    avg_rr = sum(s["recovery_ratio"] for s in stocks) / len(stocks)
    avg_iv = sum(s["iv_rank"] for s in stocks) / len(stocks)
    low_iv = len([s for s in stocks if s["iv_rank"] < 40])
    high_iv = len([s for s in stocks if s["iv_rank"] > 60])

    rc1, rc2, rc3, rc4, rc5 = st.columns(5)
    def _rbox(col, label, value, color="#2563EB"):
        col.markdown(f'<div style="background:#F8FAFC;border:1px solid #E2E8F0;border-radius:8px;padding:12px;text-align:center;box-shadow:0 1px 3px rgba(0,0,0,0.08);"><div style="font-size:20px;font-weight:700;color:{color};">{value}</div><div style="font-size:10px;color:#6B7280;">{label}</div></div>', unsafe_allow_html=True)

    _rbox(rc1, "Total Debit (all 50)", f"${total_debit_all:,.0f}", "#F59E0B")
    _rbox(rc2, "Avg Recovery Ratio", f"{avg_rr:.1f}x", "#16A34A")
    _rbox(rc3, "Avg IV Rank", f"{avg_iv:.0f}", "#2563EB")
    _rbox(rc4, "Low IV (<40)", f"{low_iv}", "#16A34A")
    _rbox(rc5, "High IV (>60)", f"{high_iv}", "#DC2626")

    # IV distribution chart
    fig = go.Figure()
    for stage in STAGE_COLORS:
        group = [s for s in stocks if s["app_stage"] == stage]
        if group:
            fig.add_trace(go.Box(y=[s["iv_rank"] for s in group], name=stage.replace("_"," "),
                marker_color=STAGE_COLORS[stage], boxpoints="all", jitter=0.3, pointpos=-1.8))
    fig.update_layout(height=350, title="IV Rank Distribution by Stage", yaxis_title="IV Rank")
    st.plotly_chart(_white_chart(fig), use_container_width=True)

    # Disclaimer
    st.markdown('''<div style="background:#FEF2F2;border:1px solid #FECACA;border-radius:8px;padding:16px;margin-top:24px;">
    <div style="font-size:12px;color:#DC2626;font-weight:700;">DISCLAIMER</div>
    <div style="font-size:11px;color:#6B7280;margin-top:6px;">This is NOT financial advice. All options setups are hypothetical illustrations of the AppLovin Pattern methodology. Options involve significant risk of loss. Past patterns do not guarantee future results. Always conduct your own due diligence and consult a financial advisor before trading options.</div></div>''', unsafe_allow_html=True)
