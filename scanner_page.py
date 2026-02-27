"""scanner_page.py — 50-Stock Scanner V2 Redesign (Sections 2A–2D)"""
import streamlit as st
import plotly.graph_objects as go

# ── Try numpy for trend line (available via pandas/plotly) ──
try:
    import numpy as np
    _HAS_NUMPY = True
except ImportError:
    _HAS_NUMPY = False

# ─────────────────────────────────────────────────────────────────────────────
# DESIGN CONSTANTS
# ─────────────────────────────────────────────────────────────────────────────
STAGE_COLORS = {
    "PRE_BREAKOUT":       "#94A3B8",  # slate gray  — "not there yet"
    "EARLY_CONFIRMATION": "#60A5FA",  # sky blue    — early signals
    "MID_CONFIRMATION":   "#3B82F6",  # blue        — building conviction
    "LATE_CONFIRMATION":  "#1D4ED8",  # deep blue   — near breakout
    "SURGE_PHASE":        "#F59E0B",  # amber       — standout accent
}
STAGE_LABELS = {
    "PRE_BREAKOUT":       "Pre Breakout",
    "EARLY_CONFIRMATION": "Early Conf.",
    "MID_CONFIRMATION":   "Mid Conf.",
    "LATE_CONFIRMATION":  "Late Conf.",
    "SURGE_PHASE":        "Surge Phase",
}
STAGE_ORDER = [
    "SURGE_PHASE", "LATE_CONFIRMATION", "MID_CONFIRMATION",
    "EARLY_CONFIRMATION", "PRE_BREAKOUT",
]

PILLAR_SHORT = {
    1: "AI Engine",
    2: "Margin Machine",
    3: "TAM Multiplier",
    4: "Capital Return",
    5: "Mgmt Execution",
}
PILLAR_COLORS = ["#2563EB", "#16A34A", "#F59E0B", "#7C3AED", "#DC2626"]

APP_PHASE_MAP = {
    "PRE_BREAKOUT":       {"date": "Q4'22", "price": "$17",  "desc": "Cost cuts underway, pre-AXON 2 rebuild"},
    "EARLY_CONFIRMATION": {"date": "Q1'23", "price": "$20",  "desc": "AXON 2 first mentioned, recovering on bad EPS"},
    "MID_CONFIRMATION":   {"date": "Q2'23", "price": "$40",  "desc": "AXON 2 live, blowout EPS +175%, ignition phase"},
    "LATE_CONFIRMATION":  {"date": "Q4'23", "price": "$75",  "desc": "$1B run-rate, e-commerce 30%+ of revenue"},
    "SURGE_PHASE":        {"date": "Q3'24", "price": "$340", "desc": "AXON 3 preview, +42% in one day, full surge"},
}

# ─────────────────────────────────────────────────────────────────────────────
# DATA LOADERS
# ─────────────────────────────────────────────────────────────────────────────
@st.cache_data
def _load():
    from applovin_data import TOP_50_STOCKS, INSTITUTIONAL_PILLARS
    pillar_map: dict = {}
    for p in INSTITUTIONAL_PILLARS:
        for ticker in p["stocks_sharing"]:
            pillar_map.setdefault(ticker, []).append(p["pillar_number"])
    return TOP_50_STOCKS, pillar_map


@st.cache_data(ttl=3600)
def fetch_iv_rank(ticker: str):
    try:
        import requests
        key = "306e5550-50f0-478a-b47d-477afa769d0a"
        r = requests.get(
            "https://api.orats.io/datav2/hist/ivrank",
            params={"ticker": ticker, "token": key},
            timeout=5,
        )
        if r.status_code == 200:
            data = r.json().get("data", [])
            if data:
                return data[0].get("ivRank")
    except Exception:
        pass
    return None


# ─────────────────────────────────────────────────────────────────────────────
# SHARED HELPERS
# ─────────────────────────────────────────────────────────────────────────────
def _white_chart(fig):
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


def _section_header(title: str, sub: str = ""):
    st.markdown(
        f'<div style="border-left:3px solid #2563EB;padding:12px 16px;margin:28px 0 14px 0;'
        f'background:#FAFAFA;border-radius:0 6px 6px 0;">'
        f'<div style="font-size:16px;font-weight:700;color:#111;">{title}</div>'
        f'{"<div style=font-size:12px;color:#6B7280;margin-top:3px;>" + sub + "</div>" if sub else ""}'
        f"</div>",
        unsafe_allow_html=True,
    )


def tradingview_chart(ticker: str, height: int = 380):
    exchange_map = {
        "IOT": "NYSE", "DASH": "NYSE", "CVNA": "NYSE", "FOUR": "NYSE",
        "TOST": "NYSE", "ONON": "NYSE", "CAVA": "NYSE", "FICO": "NYSE",
    }
    exchange = exchange_map.get(ticker, "NASDAQ")
    html = (
        f"<div style='height:{height}px;width:100%;'>"
        f"<div id='tv_{ticker}'></div>"
        f"<script src='https://s3.tradingview.com/tv.js'></script>"
        f"<script>new TradingView.widget({{"
        f'"width":"100%","height":{height},'
        f'"symbol":"{exchange}:{ticker}","interval":"D","timezone":"America/New_York",'
        f'"theme":"light","style":"1","locale":"en","container_id":"tv_{ticker}","range":"6M"'
        f"}});</script></div>"
    )
    import streamlit.components.v1 as components
    components.html(html, height=height + 30)


# ─────────────────────────────────────────────────────────────────────────────
# 2A — HEADER
# ─────────────────────────────────────────────────────────────────────────────
def _render_header(stocks: list, by_stage: dict, filtered: list):
    avg_f = sum(s["app_score"] for s in filtered) / len(filtered) if filtered else 0

    st.markdown(
        '<div style="padding:20px 0 8px 0;">'
        '<h1 style="font-size:32px!important;font-weight:800!important;color:#111!important;'
        'margin:0!important;letter-spacing:-0.5px;">50-Stock Scanner</h1>'
        '<p style="font-size:14px;color:#6B7280;margin:5px 0 0 0;">'
        "Every stock scored against the AppLovin pattern — filter, sort, drill down"
        "</p></div>",
        unsafe_allow_html=True,
    )

    # Stage count pills — left border only (not full-color boxes)
    cols = st.columns(5)
    for i, stage in enumerate(STAGE_ORDER):
        group = by_stage.get(stage, [])
        avg_s = sum(s["app_score"] for s in group) / len(group) if group else 0
        color = STAGE_COLORS[stage]
        label = STAGE_LABELS[stage]
        cols[i].markdown(
            f'<div style="border-left:3px solid {color};background:#FFFFFF;border:1px solid #E2E8F0;'
            f'border-left:3px solid {color};border-radius:0 6px 6px 0;padding:10px 14px;">'
            f'<div style="font-size:22px;font-weight:700;color:{color};line-height:1;">{len(group)}</div>'
            f'<div style="font-size:11px;color:#374151;margin-top:2px;font-weight:500;">{label}</div>'
            f'<div style="font-size:10px;color:#9CA3AF;">Avg {avg_s:.0f}</div>'
            f"</div>",
            unsafe_allow_html=True,
        )

    # Compact top bar
    st.markdown(
        f'<div style="display:flex;gap:16px;align-items:center;padding:10px 0;margin-top:10px;'
        f'border-top:1px solid #F3F4F6;font-size:12px;color:#6B7280;">'
        f'Showing <strong style="color:#111;margin:0 4px;">{len(filtered)}</strong> of {len(stocks)} stocks'
        f'<span style="color:#D1D5DB;">|</span>'
        f'Avg score <strong style="color:#2563EB;margin:0 4px;">{avg_f:.0f}</strong>'
        f'<span style="color:#D1D5DB;">|</span>'
        f'Live IV data via ORATS</div>',
        unsafe_allow_html=True,
    )


# ─────────────────────────────────────────────────────────────────────────────
# 2B — BUBBLE CHART (enhanced)
# ─────────────────────────────────────────────────────────────────────────────
def _render_bubble_chart(stocks: list, by_stage: dict):
    _section_header(
        "Score vs. Price Performance",
        "Bubble size = market cap · Hover for details · Click a bubble to jump to its card",
    )

    fig = go.Figure()
    all_x, all_y = [], []

    for stage in STAGE_ORDER:
        group = by_stage.get(stage, [])
        if not group:
            continue
        color = STAGE_COLORS[stage]
        label = STAGE_LABELS[stage]

        xs = [s["app_score"] for s in group]
        ys = [s["price_change_q1_to_current_pct"] for s in group]
        sizes = [max(12, min(50, s["market_cap_b"] * 0.5)) for s in group]
        customdata = [
            [s["ticker"], s["app_stage"], s["market_cap_b"],
             s["price_change_q1_to_current_pct"], s["app_score"]]
            for s in group
        ]
        all_x.extend(xs)
        all_y.extend(ys)

        fig.add_trace(
            go.Scatter(
                x=xs, y=ys,
                mode="markers+text",
                name=label,
                text=[s["ticker"] for s in group],
                textposition="top center",
                textfont=dict(size=9, color=color),
                marker=dict(
                    size=sizes, color=color, opacity=0.80,
                    line=dict(width=1.5, color="#FFFFFF"),
                ),
                customdata=customdata,
                hovertemplate=(
                    "<b style='font-size:14px;'>%{customdata[0]}</b><br>"
                    "Score: <b>%{customdata[4]}</b><br>"
                    "Price Change: <b>%{customdata[3]:.1f}%</b><br>"
                    "Stage: %{customdata[1]}<br>"
                    "Market Cap: $%{customdata[2]:.1f}B"
                    "<extra></extra>"
                ),
            )
        )

    # Trend line
    if _HAS_NUMPY and len(all_x) >= 4:
        try:
            z = np.polyfit(all_x, all_y, 1)
            p = np.poly1d(z)
            x_line = list(range(int(min(all_x)) - 2, int(max(all_x)) + 3))
            fig.add_trace(
                go.Scatter(
                    x=x_line, y=[p(xi) for xi in x_line],
                    mode="lines", name="Trend",
                    line=dict(color="#CBD5E1", width=1.5, dash="dot"),
                    hoverinfo="skip",
                )
            )
        except Exception:
            pass

    fig.update_layout(
        height=500,
        xaxis_title="APP Score",
        yaxis_title="Price Change (%)",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        hoverlabel=dict(bgcolor="white", bordercolor="#E2E8F0", font_size=13),
    )
    _white_chart(fig)

    # Render with on_select for click-to-jump
    try:
        event = st.plotly_chart(
            fig, key="bubble_chart", on_select="rerun",
            selection_mode=["points"], use_container_width=True,
        )
        if event and hasattr(event, "selection") and event.selection and event.selection.points:
            pt = event.selection.points[0]
            cd = pt.get("customdata")
            if cd and len(cd) > 0:
                st.session_state["focused_ticker"] = cd[0]
    except Exception:
        st.plotly_chart(fig, use_container_width=True)


# ─────────────────────────────────────────────────────────────────────────────
# 2C — FILTER & SORT (enhanced)
# ─────────────────────────────────────────────────────────────────────────────
def _render_filters(stocks: list) -> list:
    _section_header("Filter & Sort")

    row1, row2 = st.columns([2, 2]), st.columns([4, 1])

    with row1[0]:
        stage_options = ["All Stages"] + STAGE_ORDER
        stage_fmt = {**{s: STAGE_LABELS.get(s, s) for s in STAGE_ORDER}, "All Stages": "All Stages"}
        stage_sel = st.selectbox(
            "Stage",
            options=stage_options,
            format_func=lambda x: stage_fmt.get(x, x),
        )

    with row1[1]:
        min_score = st.slider("Minimum APP Score", 0, 100, 50)

    sort_fields = {
        "app_score":                       "APP Score",
        "conviction_score":                "Conviction",
        "price_change_q1_to_current_pct":  "Price Change",
        "recovery_ratio":                  "R/R Ratio",
        "market_cap_b":                    "Market Cap",
        "iv_rank":                         "IV Rank",
    }

    st.markdown(
        '<div style="font-size:11px;color:#9CA3AF;font-weight:600;'
        'text-transform:uppercase;letter-spacing:0.5px;margin:6px 0 3px 0;">Sort by</div>',
        unsafe_allow_html=True,
    )
    sort_by = st.radio(
        "Sort by",
        options=list(sort_fields.keys()),
        format_func=lambda x: sort_fields[x],
        horizontal=True,
        label_visibility="collapsed",
    )
    sort_dir = st.radio("Order", ["↓ High → Low", "↑ Low → High"], horizontal=True)
    desc = sort_dir.startswith("↓")

    # Apply filters
    if stage_sel == "All Stages":
        filtered = [s for s in stocks if s["app_score"] >= min_score]
    else:
        filtered = [
            s for s in stocks
            if s["app_stage"] == stage_sel and s["app_score"] >= min_score
        ]

    # Sort
    stage_rank = {s: i for i, s in enumerate(STAGE_ORDER)}
    if sort_by == "app_score" and desc:
        filtered.sort(key=lambda s: (stage_rank.get(s["app_stage"], 99), -s["app_score"]))
    else:
        filtered.sort(key=lambda s: s.get(sort_by, 0), reverse=desc)

    return filtered


# ─────────────────────────────────────────────────────────────────────────────
# 2D — STOCK DETAIL CARDS (redesigned)
# ─────────────────────────────────────────────────────────────────────────────
def _gate_dots(gates_passed_str: str, stage_color: str) -> str:
    passed = set(gates_passed_str.split(","))
    html = (
        '<div style="display:flex;gap:6px;align-items:center;flex-wrap:wrap;margin:6px 0;">'
        '<span style="font-size:10px;color:#9CA3AF;font-weight:600;'
        'text-transform:uppercase;letter-spacing:0.5px;margin-right:4px;">Gates</span>'
    )
    for g in ["A", "B", "C", "D", "E"]:
        if g in passed:
            html += (
                f'<span title="Gate {g} — Passed" style="display:inline-flex;align-items:center;'
                f'justify-content:center;width:24px;height:24px;border-radius:50%;'
                f'background:{stage_color};color:#FFF;font-size:10px;font-weight:700;">{g}</span>'
            )
        else:
            html += (
                f'<span title="Gate {g} — Not yet" style="display:inline-flex;align-items:center;'
                f'justify-content:center;width:24px;height:24px;border-radius:50%;'
                f'background:transparent;border:1.5px solid #D1D5DB;'
                f'color:#9CA3AF;font-size:10px;">{g}</span>'
            )
    html += "</div>"
    return html


def _pillar_tags(ticker: str, pillar_map: dict) -> str:
    nums = sorted(pillar_map.get(ticker, []))
    if not nums:
        return ""
    html = (
        '<div style="display:flex;gap:5px;flex-wrap:wrap;margin:6px 0;">'
        '<span style="font-size:10px;color:#9CA3AF;font-weight:600;'
        'text-transform:uppercase;letter-spacing:0.5px;align-self:center;margin-right:4px;">Pillars</span>'
    )
    for n in nums:
        c = PILLAR_COLORS[(n - 1) % len(PILLAR_COLORS)]
        name = PILLAR_SHORT.get(n, f"P{n}")
        html += (
            f'<span style="background:{c}18;color:{c};border:1px solid {c}50;'
            f'font-size:10px;font-weight:600;padding:2px 8px;border-radius:4px;">'
            f"P{n}: {name}</span>"
        )
    html += "</div>"
    return html


def _metric_pill(label: str, value: str, color: str = "#2563EB") -> str:
    return (
        f'<div style="background:#F8FAFC;border:1px solid #E2E8F0;border-radius:6px;'
        f'padding:8px 4px;text-align:center;">'
        f'<div style="font-size:18px;font-weight:700;color:{color};line-height:1.1;">{value}</div>'
        f'<div style="font-size:10px;color:#9CA3AF;margin-top:2px;">{label}</div>'
        f"</div>"
    )


def _render_card(s: dict, pillar_map: dict, show_expanded: bool = False):
    sc = STAGE_COLORS.get(s["app_stage"], "#6B7280")
    stage_label = STAGE_LABELS.get(s["app_stage"], s["app_stage"])
    pcc = "#16A34A" if s["price_change_q1_to_current_pct"] >= 0 else "#DC2626"
    phase_info = APP_PHASE_MAP.get(s["app_stage"], {})

    expander_label = (
        f"#{s['rank']}  {s['ticker']}  ·  {s['company_name']}  "
        f"|  Score {s['app_score']}  |  {stage_label}  |  "
        f"{s['price_change_q1_to_current_pct']:+.0f}%"
    )

    with st.expander(expander_label, expanded=show_expanded):
        # ── Card top: left accent + identity row ─────────────────────────
        st.markdown(
            f'<div style="border-left:4px solid {sc};padding-left:14px;margin-bottom:12px;">'
            f'<div style="display:flex;align-items:center;gap:10px;flex-wrap:wrap;">'
            f'<span style="font-size:24px;font-weight:800;color:#111;">#{s["rank"]} {s["ticker"]}</span>'
            f'<span style="font-size:14px;color:#6B7280;">{s["company_name"]}</span>'
            f'<span style="background:{sc}18;color:{sc};border:1px solid {sc}50;'
            f'font-size:11px;font-weight:700;padding:3px 10px;border-radius:4px;">{stage_label}</span>'
            f'<span style="font-size:11px;color:#9CA3AF;">{s["sector"]}</span>'
            f"</div></div>",
            unsafe_allow_html=True,
        )

        # ── Metric row ───────────────────────────────────────────────────
        m1, m2, m3, m4, m5 = st.columns(5)
        m1.markdown(_metric_pill("Score", str(s["app_score"]), sc), unsafe_allow_html=True)
        m2.markdown(_metric_pill("Price Δ", f"{s['price_change_q1_to_current_pct']:+.0f}%", pcc), unsafe_allow_html=True)
        m3.markdown(_metric_pill("Mkt Cap", f"${s['market_cap_b']:.0f}B", "#111"), unsafe_allow_html=True)
        m4.markdown(_metric_pill("Beats", f"{s['eps_beats_gt15pct']}/8", "#16A34A"), unsafe_allow_html=True)
        m5.markdown(_metric_pill("Conviction", f"{s['conviction_score']}/10", sc), unsafe_allow_html=True)

        # ── Gates (filled = passed, outline = not) ───────────────────────
        st.markdown(_gate_dots(s["gates_passed"], sc), unsafe_allow_html=True)

        # ── Institutional Pillar tags ────────────────────────────────────
        pt = _pillar_tags(s["ticker"], pillar_map)
        if pt:
            st.markdown(pt, unsafe_allow_html=True)

        # ── APP comparison ───────────────────────────────────────────────
        if phase_info:
            st.markdown(
                f'<div style="background:#EFF6FF;border:1px solid #BFDBFE;border-radius:6px;'
                f'padding:8px 14px;margin:8px 0;font-size:12px;">'
                f'<strong style="color:#2563EB;">APP was here:</strong> {phase_info["date"]} at '
                f'<strong>{phase_info["price"]}</strong> — {phase_info["desc"]}</div>',
                unsafe_allow_html=True,
            )

        # ── Plain-English summary ────────────────────────────────────────
        summary = s.get("plain_english_summary", "")
        if summary:
            st.markdown(
                f'<div style="background:#F9FAFB;border:1px solid #E5E7EB;border-radius:6px;'
                f'padding:12px;margin:8px 0;font-size:13px;color:#374151;line-height:1.6;">'
                f"{summary}</div>",
                unsafe_allow_html=True,
            )

        # ── AXON + TAM ───────────────────────────────────────────────────
        st.markdown(
            f'<div style="display:flex;gap:10px;flex-wrap:wrap;margin:6px 0;">'
            f'<div style="flex:1;min-width:180px;background:#F3E8FF;border-radius:6px;padding:8px 12px;">'
            f'<div style="font-size:10px;color:#7C3AED;font-weight:600;text-transform:uppercase;'
            f'letter-spacing:0.5px;">AXON Equivalent</div>'
            f'<div style="font-size:12px;color:#1E293B;margin-top:3px;">{s["axon_equivalent"]}</div></div>'
            f'<div style="flex:1;min-width:180px;background:#EFF6FF;border-radius:6px;padding:8px 12px;">'
            f'<div style="font-size:10px;color:#2563EB;font-weight:600;text-transform:uppercase;'
            f'letter-spacing:0.5px;">TAM Expansion</div>'
            f'<div style="font-size:12px;color:#1E293B;margin-top:3px;">{s["tam_expansion"]}</div></div>'
            f"</div>",
            unsafe_allow_html=True,
        )

        # ── Charts: EPS (blue/gray) + Revenue (blue fill) ────────────────
        qlabels = [f"Q{i + 1}" for i in range(8)]
        ch1, ch2 = st.columns(2)

        # EPS bar chart — blue actual, gray estimate
        with ch1:
            fig_eps = go.Figure()
            fig_eps.add_trace(
                go.Bar(
                    x=qlabels, y=s["eps_estimate"], name="Estimate",
                    marker_color="#CBD5E1", opacity=0.85,
                )
            )
            fig_eps.add_trace(
                go.Bar(
                    x=qlabels, y=s["eps_actual"], name="Actual",
                    marker_color=[
                        "#2563EB" if v >= 0 else "#DC2626" for v in s["eps_actual"]
                    ],
                    opacity=0.95,
                )
            )
            fig_eps.update_layout(
                barmode="overlay", height=230,
                title=dict(text="EPS: Actual vs Estimate", font=dict(size=12)),
                legend=dict(orientation="h", y=1.18, font=dict(size=10)),
                margin=dict(l=30, r=10, t=44, b=30),
            )
            st.plotly_chart(_white_chart(fig_eps), use_container_width=True)

        # Revenue chart — blue line + light blue fill
        with ch2:
            fig_rev = go.Figure()
            fig_rev.add_trace(
                go.Scatter(
                    x=qlabels, y=s["revenue_actual_m"],
                    mode="lines+markers", name="Revenue ($M)",
                    fill="tozeroy", fillcolor="rgba(37,99,235,0.09)",
                    line=dict(color="#2563EB", width=2.5),
                    marker=dict(size=6, color="#2563EB"),
                )
            )
            fig_rev.update_layout(
                height=230,
                title=dict(text="Revenue Trend ($M)", font=dict(size=12)),
                margin=dict(l=30, r=10, t=44, b=30),
                showlegend=False,
            )
            st.plotly_chart(_white_chart(fig_rev), use_container_width=True)

        # TradingView live chart
        tradingview_chart(s["ticker"])

        # ── Options quick-view ───────────────────────────────────────────
        live_iv = fetch_iv_rank(s["ticker"])
        iv = live_iv if live_iv is not None else s.get("iv_rank", 0)
        iv_color = "#16A34A" if iv < 40 else "#F59E0B" if iv <= 60 else "#DC2626"
        iv_label = "Low" if iv < 40 else "Moderate" if iv <= 60 else "Elevated"
        live_mark = "*" if live_iv is not None else ""

        st.markdown(
            f'<div style="background:#F8FAFC;border:1px solid #E2E8F0;border-radius:6px;'
            f'padding:12px 16px;margin:10px 0;display:flex;'
            f'justify-content:space-between;align-items:center;">'
            f'<div>'
            f'<div style="font-size:10px;color:#9CA3AF;font-weight:600;text-transform:uppercase;'
            f'letter-spacing:0.5px;">Options Setup</div>'
            f'<div style="font-size:13px;color:#1E293B;margin-top:4px;">'
            f'Call ${s["call_strike"]:.0f} · {s["call_expiry"]} · Premium ${s["call_premium"]:.1f}</div>'
            f'<div style="font-size:12px;color:#6B7280;margin-top:3px;">'
            f'R/R: <strong style="color:#2563EB;">{s["recovery_ratio"]:.1f}x</strong> · '
            f'Next earnings: <strong>{s["next_earnings_date"]}</strong></div>'
            f'<div style="font-size:11px;color:#9CA3AF;margin-top:3px;font-style:italic;">'
            f'{s.get("options_rationale", "")}</div>'
            f'</div>'
            f'<div style="text-align:center;min-width:72px;">'
            f'<div style="font-size:26px;font-weight:800;color:{iv_color};">{iv:.0f}</div>'
            f'<div style="font-size:10px;color:#9CA3AF;">IV Rank{live_mark}</div>'
            f'<div style="font-size:10px;color:{iv_color};font-weight:600;">{iv_label}</div>'
            f"</div></div>",
            unsafe_allow_html=True,
        )

        # ── Caution flags ─────────────────────────────────────────────────
        if s.get("caution_flags"):
            flags = " ".join(
                f'<span style="background:#FEF2F2;color:#DC2626;border:1px solid #FCA5A5;'
                f'font-size:11px;padding:3px 9px;border-radius:4px;">⚠ {f}</span>'
                for f in s["caution_flags"]
            )
            st.markdown(
                f'<div style="display:flex;gap:6px;flex-wrap:wrap;margin:8px 0;">{flags}</div>',
                unsafe_allow_html=True,
            )


# ─────────────────────────────────────────────────────────────────────────────
# MAIN ENTRY POINT
# ─────────────────────────────────────────────────────────────────────────────
def render_scanner_page():
    stocks, pillar_map = _load()

    # Session state for click-to-jump
    if "focused_ticker" not in st.session_state:
        st.session_state["focused_ticker"] = None

    by_stage: dict = {}
    for s in stocks:
        by_stage.setdefault(s["app_stage"], []).append(s)

    # 2C filters run first so header can show live stats
    filtered = _render_filters(stocks)

    # 2A: Header (needs filtered for stats)
    _render_header(stocks, by_stage, filtered)

    # 2B: Bubble chart
    _render_bubble_chart(stocks, by_stage)

    # Quick-view panel when a bubble has been clicked
    focused = st.session_state.get("focused_ticker")
    if focused:
        focused_stock = next((s for s in stocks if s["ticker"] == focused), None)
        if focused_stock:
            sc = STAGE_COLORS.get(focused_stock["app_stage"], "#2563EB")
            info_col, btn_col = st.columns([6, 1])
            with info_col:
                st.markdown(
                    f'<div style="background:#EFF6FF;border:1.5px solid {sc};border-radius:6px;'
                    f'padding:10px 16px;font-size:13px;color:{sc};font-weight:600;">'
                    f'📌 Quick View: {focused_stock["ticker"]} — {focused_stock["company_name"]}</div>',
                    unsafe_allow_html=True,
                )
            with btn_col:
                if st.button("✕ Clear", key="clear_focused"):
                    st.session_state["focused_ticker"] = None
                    st.rerun()
            _render_card(focused_stock, pillar_map, show_expanded=True)
            st.markdown("---")

    # 2D: Stock detail cards
    _section_header(
        "Stock Detail Cards",
        f"{len(filtered)} stocks match your filters — expand any card for full analysis",
    )

    for s in filtered:
        _render_card(
            s, pillar_map,
            show_expanded=(s["ticker"] == st.session_state.get("focused_ticker")),
        )
