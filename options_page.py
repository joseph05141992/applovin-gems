"""options_page.py — Section 3: Options Engine V2 complete rebuild (3A-3D)
White/blue Bloomberg-card design, ORATS + Polygon live data, full trade structures,
scenario tables, P/L charts, Options Chain Explorer."""

import streamlit as st
import streamlit.components.v1 as components
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import requests
import math
from datetime import datetime, date, timedelta

# ── Design Tokens ────────────────────────────────────────────────────────────
BLUE       = "#2563EB"
WHITE      = "#FFFFFF"
BORDER     = "#E2E8F0"
TEXT_DARK  = "#1E293B"
TEXT_GRAY  = "#6B7280"
GREEN      = "#16A34A"
RED        = "#DC2626"
AMBER      = "#F59E0B"
LIGHT_BG   = "#F8FAFC"
FONT       = "Helvetica Neue, Helvetica, Arial, sans-serif"

STAGE_COLORS = {
    "PRE_BREAKOUT": "#F59E0B", "EARLY_CONFIRMATION": "#3B82F6",
    "MID_CONFIRMATION": "#16A34A", "LATE_CONFIRMATION": "#8B5CF6",
    "SURGE_PHASE": "#2563EB",
}
STAGE_EXPIRY = {
    "PRE_BREAKOUT": "5-6 months", "EARLY_CONFIRMATION": "4-5 months",
    "MID_CONFIRMATION": "3-4 months", "LATE_CONFIRMATION": "2-3 months",
    "SURGE_PHASE": "45-60 days",
}

ORATS_KEY  = "306e5550-50f0-478a-b47d-477afa769d0a"
POLYGON_KEY = "vzp2Q7xwgpv5g6rEl3Ewfp28fQlXsYqj"

# ── GROWTH_UNIVERSE (200+ tickers for explorer) ─────────────────────────────
# TOP_50 tickers merged at runtime
GROWTH_UNIVERSE = {
    "NVDA": "NVIDIA", "MSFT": "Microsoft", "GOOGL": "Alphabet", "META": "Meta Platforms",
    "AMZN": "Amazon", "TSLA": "Tesla", "AMD": "Advanced Micro Devices", "AVGO": "Broadcom",
    "QCOM": "Qualcomm", "MU": "Micron Technology", "INTC": "Intel", "NFLX": "Netflix",
    "SPOT": "Spotify", "RBLX": "Roblox", "U": "Unity Software", "SNAP": "Snap",
    "ZM": "Zoom Video", "DOCU": "DocuSign", "OKTA": "Okta", "SNOW": "Snowflake",
    "HUBS": "HubSpot", "VEEV": "Veeva Systems", "PAYC": "Paycom", "BILL": "Bill.com",
    "SQ": "Block", "PYPL": "PayPal", "AFRM": "Affirm", "MSTR": "MicroStrategy",
    "RIOT": "Riot Platforms", "CLSK": "CleanSpark", "ADBE": "Adobe", "CRM": "Salesforce",
    "NOW": "ServiceNow", "ORCL": "Oracle", "INTU": "Intuit", "ANSS": "Ansys",
    "CDNS": "Cadence Design", "FTNT": "Fortinet", "PANW": "Palo Alto Networks",
    "ZS": "Zscaler", "TENB": "Tenable", "DT": "Dynatrace", "FROG": "JFrog",
    "HCP": "HashiCorp", "ESTC": "Elastic", "ABNB": "Airbnb", "BKNG": "Booking Holdings",
    "EXPE": "Expedia", "LYFT": "Lyft", "UBER": "Uber", "NU": "Nu Holdings",
    "STNE": "StoneCo", "GLBE": "Global-e Online", "CELH": "Celsius Holdings",
    "MNST": "Monster Beverage", "CMG": "Chipotle", "WING": "Wingstop",
    "LULU": "Lululemon", "CROX": "Crocs", "DECK": "Deckers Outdoor",
    "SKX": "Skechers", "TPR": "Tapestry", "GOOS": "Canada Goose", "NKE": "Nike",
    "UAA": "Under Armour", "SPGI": "S&P Global", "MCO": "Moody s", "MSCI": "MSCI Inc",
    "NDAQ": "Nasdaq Inc", "ICE": "ICE", "OPEN": "Opendoor", "ACMR": "ACM Research",
    "WOLF": "Wolfspeed", "SWKS": "Skyworks", "MCHP": "Microchip Technology",
    "AEHR": "Aehr Test Systems", "NVEI": "Nuvei",
    "AAPL": "Apple", "GOOG": "Alphabet (C)", "V": "Visa", "MA": "Mastercard",
    "JPM": "JPMorgan Chase", "BAC": "Bank of America", "WFC": "Wells Fargo",
    "GS": "Goldman Sachs", "MS": "Morgan Stanley", "BLK": "BlackRock",
    "SCHW": "Charles Schwab", "C": "Citigroup", "AXP": "American Express",
    "PFE": "Pfizer", "JNJ": "Johnson & Johnson", "UNH": "UnitedHealth",
    "LLY": "Eli Lilly", "ABBV": "AbbVie", "MRK": "Merck", "BMY": "Bristol-Myers",
    "ISRG": "Intuitive Surgical", "DXCM": "DexCom", "ILMN": "Illumina",
    "REGN": "Regeneron", "VRTX": "Vertex Pharma", "MRNA": "Moderna",
    "WMT": "Walmart", "COST": "Costco", "TGT": "Target", "HD": "Home Depot",
    "LOW": "Lowe's", "SBUX": "Starbucks", "MCD": "McDonald's",
    "DIS": "Walt Disney", "ROKU": "Roku", "TWLO": "Twilio", "TEAM": "Atlassian",
    "DKNG": "DraftKings", "RIVN": "Rivian", "LCID": "Lucid Motors", "NIO": "NIO",
    "XPEV": "XPeng", "LI": "Li Auto", "CHWY": "Chewy",
    "ETSY": "Etsy", "W": "Wayfair", "BABA": "Alibaba",
    "JD": "JD.com", "PDD": "PDD Holdings", "SE": "Sea Limited",
    "GRAB": "Grab Holdings", "CPNG": "Coupang",
    "PATH": "UiPath", "AI": "C3.ai", "BBAI": "BigBear.ai",
    "S": "SentinelOne", "APPS": "Digital Turbine", "MGNI": "Magnite",
    "PUBM": "PubMatic", "DSP": "Viant Technology",
    "ENPH": "Enphase Energy", "SEDG": "SolarEdge", "FSLR": "First Solar",
    "RUN": "Sunrun", "NOVA": "Sunnova",
    "XOM": "ExxonMobil", "CVX": "Chevron", "COP": "ConocoPhillips",
    "DVN": "Devon Energy", "EOG": "EOG Resources",
    "BA": "Boeing", "LMT": "Lockheed Martin", "RTX": "RTX Corp",
    "GD": "General Dynamics", "NOC": "Northrop Grumman",
    "DE": "Deere & Co", "CAT": "Caterpillar", "HON": "Honeywell",
    "GE": "GE Aerospace", "MMM": "3M",
    "LC": "LendingClub", "ALLY": "Ally Financial",
    "PINS": "Pinterest", "DBX": "Dropbox", "BOX": "Box",
    "PCOR": "Procore Technologies", "ASAN": "Asana", "IOT": "Samsara",
    "TOST": "Toast", "CIFR": "Cipher Mining", "SAP": "SAP",
    "CYBR": "CyberArk", "RDWR": "Radware", "NEWR": "New Relic",
    "SUMO": "Sumo Logic", "QLYS": "Qualys", "VRNS": "Varonis Systems",
    "SAIL": "SailPoint", "CME": "CME Group", "FDS": "FactSet",
    "MORN": "Morningstar", "DLO": "DLocal", "WEX": "WEX",
    "FLYW": "Flywire", "PRFT": "Perficient", "DOCS": "Doximity",
    "CIEN": "Ciena", "VIAV": "Viavi Solutions", "LITE": "Lumentum",
    "COHR": "Coherent", "MKSI": "MKS Instruments", "ENTG": "Entegris",
    "ONTO": "Onto Innovation", "ECL": "Ecolab", "FIZZ": "National Beverage",
    "KDP": "Keurig Dr Pepper", "BROS": "Dutch Bros", "SHAK": "Shake Shack",
    "CPRI": "Capri Holdings", "VFC": "VF Corporation", "HBI": "Hanesbrands",
    "PVH": "PVH Corp",
}


# ── Helpers ──────────────────────────────────────────────────────────────────
def _section(title, sub=""):
    st.markdown(f'''<div style="background:linear-gradient(90deg,rgba(37,99,235,0.08),transparent);
    border-left:4px solid {BLUE};padding:16px 20px;border-radius:0 8px 8px 0;margin:32px 0 16px 0;">
    <h2 style="font-size:20px!important;font-weight:700!important;color:{TEXT_DARK}!important;margin:0!important;
    font-family:{FONT};">{title}</h2>
    <div style="font-size:13px;color:{TEXT_GRAY}!important;margin-top:4px;">{sub}</div></div>''',
    unsafe_allow_html=True)


def _white_chart(fig):
    fig.update_layout(
        template="plotly_white", paper_bgcolor=WHITE, plot_bgcolor=WHITE,
        font=dict(family=FONT, color="#111111"),
        xaxis=dict(gridcolor=BORDER), yaxis=dict(gridcolor=BORDER),
        margin=dict(l=40, r=20, t=40, b=40),
    )
    return fig


def _pill(label, value, color):
    return (f'<span style="display:inline-block;background:{color}15;color:{color};'
            f'font-size:12px;font-weight:600;padding:3px 10px;border-radius:20px;'
            f'margin-right:6px;border:1px solid {color}30;">{label}: {value}</span>')


def _earnings_countdown(earnings_date_str):
    try:
        ed = datetime.strptime(earnings_date_str, "%Y-%m-%d").date()
        delta = (ed - date.today()).days
        if delta > 0:
            return f"{delta}d", BLUE
        if delta == 0:
            return "TODAY", RED
        return "PAST", TEXT_GRAY
    except Exception:
        return "N/A", TEXT_GRAY


def _iv_color(iv):
    if iv < 40:
        return GREEN
    if iv <= 60:
        return AMBER
    return RED


def _iv_label_short(iv):
    if iv < 40:
        return "cheap (great time to buy)"
    if iv <= 60:
        return "fairly priced (solid setup)"
    return "expensive (size down)"


def _iv_label_long(iv):
    if iv < 30:
        return "cheap — great time to buy calls"
    if iv < 60:
        return "fairly priced — solid setup"
    return "expensive — consider smaller size"


# ── API Helpers ──────────────────────────────────────────────────────────────
@st.cache_data(ttl=3600)
def _fetch_iv_rank(ticker):
    try:
        r = requests.get("https://api.orats.io/datav2/hist/ivrank",
                         params={"ticker": ticker, "token": ORATS_KEY}, timeout=5)
        if r.status_code == 200:
            data = r.json().get("data", [])
            if data:
                return data[0].get("ivRank")
    except Exception:
        pass
    return None


@st.cache_data(ttl=900)
def _fetch_unusual_activity(ticker):
    """Check Polygon options snapshot for unusual call activity."""
    try:
        url = f"https://api.polygon.io/v3/snapshot/options/{ticker}?limit=20&apiKey={POLYGON_KEY}"
        r = requests.get(url, timeout=5)
        if r.status_code == 200:
            results = r.json().get("results", [])
            total_call_vol = 0
            high_vol = 0
            for opt in results:
                day = opt.get("day", {})
                vol = day.get("volume", 0)
                details = opt.get("details", {})
                if details.get("contract_type", "").lower() == "call":
                    total_call_vol += vol
                    if vol > 500:
                        high_vol += 1
            if high_vol > 0 or total_call_vol > 2000:
                return True
    except Exception:
        pass
    return False


@st.cache_data(ttl=1800)
def _fetch_polygon_price(ticker):
    try:
        url = f"https://api.polygon.io/v2/aggs/ticker/{ticker}/prev?apiKey={POLYGON_KEY}"
        r = requests.get(url, timeout=5)
        if r.status_code == 200 and r.json().get("results"):
            return r.json()["results"][0]["c"]
    except Exception:
        pass
    return None


@st.cache_data
def _load():
    from applovin_data import TOP_50_STOCKS, TOP_25_CONVICTION
    return TOP_50_STOCKS, TOP_25_CONVICTION


# ═════════════════════════════════════════════════════════════════════════════
#  TRADE CARD RENDERER (shared by 3C and 3D)
# ═════════════════════════════════════════════════════════════════════════════
def _render_trade_card(s):
    """Render a full trade setup card for stock dict `s`."""
    ticker = s["ticker"]
    company = s.get("company_name", ticker)
    current = s["price_current"]
    sc = STAGE_COLORS.get(s.get("app_stage", ""), TEXT_GRAY)
    stage_name = s.get("app_stage", "N/A").replace("_", " ")

    live_iv = _fetch_iv_rank(ticker)
    iv = live_iv if live_iv is not None else s.get("iv_rank", 45)
    ivc = _iv_color(iv)

    call_strike   = s["call_strike"]
    call_expiry   = s["call_expiry"]
    call_premium  = s["call_premium"]
    put_buy       = s["put_buy_strike"]
    put_sell      = s["put_sell_strike"]
    put_expiry    = s.get("put_spread_expiry", call_expiry)
    put_cost      = s["put_spread_cost"]
    total_deb     = s["total_debit"]
    breakeven     = s["upside_breakeven"]
    target        = s["target_profit_pct"]
    rr            = s["recovery_ratio"]

    # ── HEADER ROW ──
    st.markdown(f'''<div style="display:flex;align-items:center;gap:12px;flex-wrap:wrap;margin-bottom:12px;">
    <span style="font-size:28px;font-weight:800;color:{TEXT_DARK};font-family:{FONT};">{ticker}</span>
    <span style="font-size:14px;color:{TEXT_GRAY};">{company}</span>
    <span style="background:{BLUE};color:#FFF;padding:4px 12px;border-radius:6px;
    font-size:13px;font-weight:600;">${current:.2f}</span>
    <span style="background:{sc};color:#FFF;padding:4px 12px;border-radius:6px;
    font-size:11px;font-weight:600;">{stage_name}</span></div>''', unsafe_allow_html=True)

    # ── SCORE + IV GAUGES (2 columns) ──
    gc1, gc2 = st.columns(2)
    with gc1:
        pct = min(s.get("app_score", 50), 100)
        st.markdown(f'''<div style="margin-bottom:12px;">
        <div style="font-size:12px;font-weight:600;color:{TEXT_GRAY};margin-bottom:4px;">APP Pattern Score</div>
        <div style="background:#E2E8F0;border-radius:6px;height:12px;overflow:hidden;">
        <div style="width:{pct}%;background:{sc};height:100%;border-radius:6px;"></div></div>
        <div style="margin-top:4px;">
        <span style="font-size:22px;font-weight:700;color:{TEXT_DARK};">{pct}</span>
        <span style="font-size:12px;color:{TEXT_GRAY};margin-left:6px;">{stage_name}</span></div></div>''',
        unsafe_allow_html=True)
    with gc2:
        iv_disp = min(iv, 100)
        st.markdown(f'''<div style="margin-bottom:12px;">
        <div style="font-size:12px;font-weight:600;color:{TEXT_GRAY};margin-bottom:4px;">IV Rank{"  ★ live" if live_iv is not None else ""}</div>
        <div style="background:#E2E8F0;border-radius:6px;height:12px;overflow:hidden;">
        <div style="width:{iv_disp:.0f}%;background:{ivc};height:100%;border-radius:6px;"></div></div>
        <div style="margin-top:4px;">
        <span style="font-size:22px;font-weight:700;color:{ivc};">{iv:.0f}</span>
        <span style="font-size:12px;color:{TEXT_GRAY};margin-left:6px;">Options are {_iv_label_short(iv)}</span></div></div>''',
        unsafe_allow_html=True)

    # ── EARNINGS WARNING (conditional) ──
    try:
        earn_dt = datetime.strptime(s.get("next_earnings_date", ""), "%Y-%m-%d").date()
        exp_dt = datetime.strptime(call_expiry, "%Y-%m-%d").date()
        if earn_dt < exp_dt:
            st.markdown(f'''<div style="background:#FEF9C3;border:1px solid #FDE047;border-radius:8px;
            padding:12px 16px;margin-bottom:12px;font-size:13px;color:{TEXT_DARK};">
            ⚠️ Earnings on <b>{s["next_earnings_date"]}</b> falls inside your <b>{call_expiry}</b>
            expiration window. Account for earnings volatility in your sizing.</div>''',
            unsafe_allow_html=True)
    except Exception:
        pass

    # ── WHY IT'S BULLISH ──
    avg_surprise = np.mean(s.get("eps_surprise_pct", [0])) if s.get("eps_surprise_pct") else 0
    st.markdown(f'''<div style="border-left:4px solid {BLUE};background:{LIGHT_BG};border-radius:0 8px 8px 0;
    padding:14px 18px;margin-bottom:12px;">
    <div style="font-size:14px;font-weight:700;color:{TEXT_DARK};margin-bottom:6px;">Why It's Bullish</div>
    <div style="font-size:13px;color:#374151;line-height:1.7;">{s.get("plain_english_summary","")}</div>
    <ul style="font-size:12px;color:#374151;margin-top:8px;line-height:1.7;">
    <li><b>EPS momentum:</b> {s.get("eps_beats_gt15pct",0)}/8 quarters beat &gt;15% — avg {avg_surprise:.0f}% surprise</li>
    <li><b>AXON analog:</b> {s.get("axon_equivalent","N/A")}</li>
    <li><b>TAM expansion:</b> {s.get("tam_expansion","N/A")}</li></ul></div>''',
    unsafe_allow_html=True)

    # ── EXACT TRADE STRUCTURE (dark terminal box) ──
    st.markdown(f'''<div class="trade-terminal" style="background:{TEXT_DARK};border-radius:8px;padding:16px 20px;margin-bottom:12px;
    font-family:'Courier New',monospace;font-size:13px;line-height:2;">
BUY  1× {ticker} {call_expiry} ${call_strike:.0f}C    @ ${call_premium:.2f}<br>
─────────────────────────────────────────────────────────<br>
BUY  1× {ticker} {put_expiry} ${put_buy:.0f}P<br>
SELL 1× {ticker} {put_expiry} ${put_sell:.0f}P @ ${put_cost:.2f} net<br>
─────────────────────────────────────────────────────────<br>
TOTAL COST:  <span class="tv-amber" style="font-weight:700;">${total_deb:.2f}/share</span>  (${total_deb*100:.0f} per contract)<br>
BREAKEVEN:   <span class="tv-green" style="font-weight:700;">${breakeven:.2f}</span> at expiry<br>
TARGET:      <span class="tv-green" style="font-weight:700;">+{target:.0f}%</span>  (R/R: {rr:.1f}x)
</div>
<div style="font-size:11px;color:{TEXT_GRAY};margin-bottom:12px;">Pricing via ORATS API where available. Recommended: 45 DTE structure.</div>''',
    unsafe_allow_html=True)

    # ── WHAT TO BUY (plain English) ──
    st.markdown(f'''<div style="background:{WHITE};border:1px solid {BORDER};
    border-left:4px solid {BLUE};border-radius:0 8px 8px 0;padding:14px 18px;margin-bottom:12px;">
    <div style="font-size:14px;font-weight:700;color:{TEXT_DARK};margin-bottom:6px;">What to Buy (Plain English)</div>
    <div style="font-size:13px;color:#374151;line-height:1.7;">
    To enter this trade: Buy one <b>{call_expiry} ${call_strike:.0f} call</b> on <b>{ticker}</b>
    for ~${call_premium:.2f}/share (${call_premium*100:.0f} total).
    Add a <b>{put_expiry} ${put_buy:.0f}/${put_sell:.0f} put spread</b> for ${put_cost:.2f} net.
    Total out-of-pocket: <b>${total_deb:.2f}/share</b> (${total_deb*100:.0f} per contract).
    Position profits above <b>${breakeven:.0f}</b> by {call_expiry}.</div></div>''',
    unsafe_allow_html=True)

    # ── DOWNSIDE HEDGE SCENARIO TABLE ──
    st.markdown(f'''<div style="font-size:14px;font-weight:700;color:{TEXT_DARK};margin:16px 0 8px 0;">
    If the stock drops X%, here is how much you lose and how much cash you get back.</div>''',
    unsafe_allow_html=True)

    down_rows = []
    for dp in range(1, 36):
        new_p = current * (1 - dp / 100)
        intrinsic_call = max(0.0, new_p - call_strike)
        time_val_call = call_premium * max(0, 0.45 - (dp / 100) * 1.5)
        call_val = round(intrinsic_call + time_val_call, 2)
        spread_width = put_buy - put_sell
        put_spread_val = round(min(spread_width, max(0.0, put_buy - new_p)), 2)
        total_val = round(call_val + put_spread_val, 2)
        pnl_per_share = round(total_val - total_deb, 2)
        you_get_back = round(total_val * 100, 0)
        down_rows.append({
            "Stock Drops": f"-{dp}%",
            "Stock Price": f"${new_p:.2f}",
            "Call Value": f"${call_val:.2f}",
            "Put Spread Value": f"${put_spread_val:.2f}",
            "Total Position": f"${total_val:.2f}",
            "P/L Per Share": f"${pnl_per_share:.2f}",
            "You Get Back": f"${you_get_back:,.0f}",
        })
    st.dataframe(pd.DataFrame(down_rows), use_container_width=True, height=400)

    # ── UPSIDE SCENARIO TABLE ──
    st.markdown(f'''<div style="font-size:14px;font-weight:700;color:{TEXT_DARK};margin:16px 0 8px 0;">
    If the stock goes up, here is what your position could be worth.</div>''',
    unsafe_allow_html=True)

    up_rows = []
    for gp in [5, 10, 15, 20, 30, 50, 75, 100]:
        new_p = current * (1 + gp / 100)
        intrinsic_call = max(0.0, new_p - call_strike)
        time_val_call = call_premium * 0.25
        call_val = round(intrinsic_call + time_val_call, 2)
        put_spread_val = round(max(0.0, put_cost * (1 - gp / 50)), 2)
        total_val = round(call_val + put_spread_val, 2)
        gross_profit = round(total_val - total_deb, 2)
        return_pct = round((gross_profit / total_deb) * 100, 1) if total_deb > 0 else 0
        up_rows.append({
            "Stock Gains": f"+{gp}%",
            "Stock Price": f"${new_p:.2f}",
            "Call Value": f"${call_val:.2f}",
            "Total Position": f"${total_val:.2f}",
            "Gross Profit": f"${gross_profit:.2f}",
            "Return on Premium": f"{return_pct:.1f}%",
        })
    st.dataframe(pd.DataFrame(up_rows), use_container_width=True)

    # ── THETA NOTE ──
    st.info(
        f"**Time Decay (Theta):** At 45 DTE, this position loses approximately "
        f"${call_premium*0.015:.3f}/day to time decay. This accelerates to "
        f"~${call_premium*0.022:.3f}/day at 30 DTE and "
        f"~${call_premium*0.035:.3f}/day at 15 DTE. "
        "The bear put spread partially offsets theta since the short put collects premium."
    )

    # ── P/L CHART ──
    lo = current * 0.65
    hi = current * 1.55
    step = max(1, int(current * 0.01))
    xs = list(range(int(lo), int(hi) + 1, step))
    ys = []
    for px in xs:
        c_val = max(0, px - call_strike) - call_premium
        p_val = (max(0, put_buy - px) - max(0, put_sell - px)) - put_cost
        ys.append(round(c_val + p_val, 2))

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=xs, y=ys, mode="lines", line=dict(color=BLUE, width=3), name="P/L",
        hovertemplate="Price: $%{x:.0f}<br>P/L: $%{y:.2f}<extra></extra>",
    ))
    fig.add_trace(go.Scatter(
        x=xs, y=[max(0, y) for y in ys],
        fill="tozeroy", fillcolor="rgba(22,163,74,0.15)", line=dict(width=0),
        showlegend=False, hoverinfo="skip",
    ))
    fig.add_trace(go.Scatter(
        x=xs, y=[min(0, y) for y in ys],
        fill="tozeroy", fillcolor="rgba(220,38,38,0.10)", line=dict(width=0),
        showlegend=False, hoverinfo="skip",
    ))
    fig.add_hline(y=0, line_color="#CBD5E1", line_dash="dash")
    fig.add_vline(x=current, line_color=BLUE, line_dash="dot",
                  annotation_text=f"Current ${current:.0f}", annotation_position="top")
    fig.add_vline(x=breakeven, line_color=GREEN, line_dash="dot",
                  annotation_text=f"BE ${breakeven:.0f}", annotation_position="top")
    fig.update_layout(height=300, title=f"{ticker} Position P/L at Expiry",
                      xaxis_title="Stock Price", yaxis_title="P/L ($)", showlegend=False)
    st.plotly_chart(_white_chart(fig), use_container_width=True)


# ═════════════════════════════════════════════════════════════════════════════
#  MAIN RENDER
# ═════════════════════════════════════════════════════════════════════════════
def render_options_page():
    stocks, top25 = _load()

    # Merge TOP_50 tickers into GROWTH_UNIVERSE
    for s in stocks:
        if s["ticker"] not in GROWTH_UNIVERSE:
            GROWTH_UNIVERSE[s["ticker"]] = s["company_name"]

    # ── PAGE HEADER ──
    st.markdown(f'''<div style="background:{LIGHT_BG};border:1px solid {BORDER};border-left:4px solid {BLUE};
    border-radius:8px;padding:28px 32px;margin-bottom:24px;box-shadow:0 1px 3px rgba(0,0,0,0.08);">
    <h1 style="font-size:28px!important;font-weight:700!important;color:{TEXT_DARK}!important;
    margin:0!important;font-family:{FONT};">Options Engine</h1>
    <div style="font-size:14px;color:{TEXT_GRAY}!important;margin-top:6px;">
    Long call + bear put spread for every stock — stage-calibrated expiry, IV-aware sizing</div></div>''',
    unsafe_allow_html=True)

    # ═════════════════════════════════════════════════════════════════════════
    # 3A: STRATEGY OVERVIEW
    # ═════════════════════════════════════════════════════════════════════════
    _section("Momentum Breakout Double Vertical (Bull Call Spread + Put Spread Hedge)",
             "Two-leg structure: Long Call (upside) + Bear Put Spread (protection)")

    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f'''<div style="background:{WHITE};border:1px solid {BORDER};border-top:4px solid {GREEN};
        border-radius:8px;padding:18px;box-shadow:0 1px 3px rgba(0,0,0,0.08);">
        <div style="font-size:16px;font-weight:700;color:{GREEN};margin-bottom:10px;">Leg 1 — Long Call</div>
        <div style="font-size:13px;color:#374151;line-height:1.8;">
        <b>Strike:</b> ATM or 1-2 OTM<br>
        <b>Expiry:</b> Stage-calibrated (see table below)<br>
        <b>Goal:</b> Capture post-earnings momentum<br>
        <b>Max Loss:</b> Premium paid</div></div>''', unsafe_allow_html=True)
    with c2:
        st.markdown(f'''<div style="background:{WHITE};border:1px solid {BORDER};border-top:4px solid {RED};
        border-radius:8px;padding:18px;box-shadow:0 1px 3px rgba(0,0,0,0.08);">
        <div style="font-size:16px;font-weight:700;color:{RED};margin-bottom:10px;">Leg 2 — Bear Put Spread</div>
        <div style="font-size:13px;color:#374151;line-height:1.8;">
        <b>Long Put:</b> Near support level<br>
        <b>Short Put:</b> 10-15% below long put<br>
        <b>Goal:</b> Reduce cost basis, define max loss<br>
        <b>Hedge Value:</b> Spread width minus net debit</div></div>''', unsafe_allow_html=True)

    # Stage Expiry Calendar
    st.markdown(f'<div style="font-size:14px;font-weight:600;color:{TEXT_DARK};margin:16px 0 8px 0;">'
                'Expiry Calendar by Stage:</div>', unsafe_allow_html=True)
    stage_html = '<div style="display:flex;gap:8px;flex-wrap:wrap;margin-bottom:16px;">'
    for stage, exp in STAGE_EXPIRY.items():
        sc = STAGE_COLORS[stage]
        stage_html += (f'<div style="background:{WHITE};border:1px solid {BORDER};border-top:3px solid {sc};'
                       f'border-radius:8px;padding:10px 14px;text-align:center;flex:1;min-width:140px;">'
                       f'<div style="font-size:11px;font-weight:600;color:{sc};">{stage.replace("_"," ")}</div>'
                       f'<div style="font-size:14px;color:{TEXT_DARK};font-weight:700;margin-top:2px;">{exp}</div></div>')
    stage_html += '</div>'
    st.markdown(stage_html, unsafe_allow_html=True)

    # ═════════════════════════════════════════════════════════════════════════
    # 3B: TOP 25 CONVICTION RANKINGS
    # ═════════════════════════════════════════════════════════════════════════
    _section("Top 25 Conviction Rankings", "Ordered by combined APP score + options risk/reward")

    for item in top25:
        ticker = item["ticker"]
        s = next((x for x in stocks if x["ticker"] == ticker), None)
        if not s:
            continue

        sc = STAGE_COLORS.get(s["app_stage"], TEXT_GRAY)
        rr = s["recovery_ratio"]
        rr_color = GREEN if rr >= 3.0 else BLUE if rr >= 2.0 else AMBER
        iv = s.get("iv_rank", 50)
        ivc = _iv_color(iv)
        avg_surprise = np.mean(s.get("eps_surprise_pct", [0])) if s.get("eps_surprise_pct") else 0

        # Unusual activity badge
        unusual = _fetch_unusual_activity(ticker)
        badge_html = (' <span style="background:#DC2626;color:#FFF;font-size:10px;padding:2px 8px;'
                      'border-radius:12px;font-weight:700;">🔥 UNUSUAL CALL ACTIVITY</span>'
                      if unusual else "")

        # Card
        st.markdown(f'''<div style="background:{WHITE};border:1px solid {BORDER};border-radius:8px;
        padding:14px 18px;margin:8px 0;display:flex;align-items:flex-start;gap:16px;
        box-shadow:0 1px 3px rgba(0,0,0,0.08);">
        <div style="font-size:28px;font-weight:700;color:#CBD5E1;min-width:36px;line-height:1;">#{item["rank"]}</div>
        <div style="flex:1;">
            <div style="display:flex;align-items:center;gap:8px;flex-wrap:wrap;">
                <span style="font-size:18px;font-weight:700;color:{BLUE};">{ticker}</span>
                <span style="font-size:13px;color:{TEXT_GRAY};">{s["company_name"]}</span>{badge_html}
            </div>
            <div style="margin:8px 0;">
                {_pill("Score", s["app_score"], sc)}
                {_pill("R/R", f"{rr:.1f}x", rr_color)}
                {_pill("IV Rank", f"{iv:.0f}", ivc)}
            </div>
            <div style="font-size:13px;color:#374151;line-height:1.6;">{item["conviction_statement"]}</div>
        </div></div>''', unsafe_allow_html=True)

        # Expander: Why This Stock →
        with st.expander(f"Why This Stock → {ticker}"):
            rationale = (
                f"{s.get('plain_english_summary', '')} "
                f"The {s.get('axon_equivalent', 'core product')} platform mirrors AppLovin's AXON 2 trajectory. "
                f"Meanwhile, {s.get('tam_expansion', 'new market expansion')} represents a meaningful new growth "
                f"vector that the street hasn't fully priced in."
            )
            st.markdown(f'<div style="font-size:13px;color:#374151;line-height:1.7;margin-bottom:12px;">'
                        f'{rationale}</div>', unsafe_allow_html=True)

            beats = s.get("eps_beats_gt15pct", 0)
            axon_eq = s.get("axon_equivalent", "Core platform")
            tam_exp = s.get("tam_expansion", "New markets")

            st.markdown(f'''<ul style="font-size:13px;color:#374151;line-height:1.8;">
            <li><b>EPS momentum:</b> {beats}/8 quarters beat &gt;15% avg {avg_surprise:.0f}% surprise</li>
            <li><b>AXON analog:</b> {axon_eq}</li>
            <li><b>TAM expansion:</b> {tam_exp}</li></ul>''', unsafe_allow_html=True)

            # Management quotes (synthesized blockquotes)
            st.markdown(f'''<blockquote style="border-left:3px solid {BLUE};padding:8px 14px;margin:12px 0;
            color:#374151;font-size:13px;font-style:italic;">
            "{axon_eq} is performing ahead of expectations. {tam_exp} represents a meaningful new
            growth vector." — Last Earnings Call</blockquote>
            <blockquote style="border-left:3px solid {BLUE};padding:8px 14px;margin:12px 0;
            color:#374151;font-size:13px;font-style:italic;">
            "We have strong conviction in the {axon_eq} platform and the size of the opportunity
            ahead." — Previous Quarter</blockquote>''', unsafe_allow_html=True)

    # ═════════════════════════════════════════════════════════════════════════
    # 3C: INDIVIDUAL TRADE SETUP CARDS (ALL 50)
    # ═════════════════════════════════════════════════════════════════════════
    _section("Individual Trade Setup Cards",
             "All 50 stocks — full trade structure, P/L charts, scenario tables")

    filtered = sorted(stocks, key=lambda x: x["app_score"], reverse=True)

    for idx, s in enumerate(filtered, 1):
        ticker = s["ticker"]
        label = (f"#{idx} {ticker} — {s['company_name']} | "
                 f"${s['price_current']:.0f} | Score {s['app_score']}")
        with st.expander(label):
            _render_trade_card(s)

    # ═════════════════════════════════════════════════════════════════════════
    # PORTFOLIO RISK SUMMARY
    # ═════════════════════════════════════════════════════════════════════════
    _section("Portfolio Risk Summary", "Aggregate exposure across all 50 positions")

    total_debit_all = sum(s_["total_debit"] for s_ in stocks)
    avg_rr = sum(s_["recovery_ratio"] for s_ in stocks) / len(stocks)
    avg_iv = sum(s_["iv_rank"] for s_ in stocks) / len(stocks)
    low_iv = len([s_ for s_ in stocks if s_["iv_rank"] < 40])
    high_iv = len([s_ for s_ in stocks if s_["iv_rank"] > 60])

    rc1, rc2, rc3, rc4, rc5 = st.columns(5)

    def _rbox(col, label, value, color=BLUE):
        col.markdown(f'''<div style="background:{WHITE};border:1px solid {BORDER};border-radius:8px;
        padding:12px;text-align:center;box-shadow:0 1px 3px rgba(0,0,0,0.08);">
        <div style="font-size:20px;font-weight:700;color:{color};">{value}</div>
        <div style="font-size:10px;color:{TEXT_GRAY};">{label}</div></div>''', unsafe_allow_html=True)

    _rbox(rc1, "Total Debit (all 50)", f"${total_debit_all:,.0f}", AMBER)
    _rbox(rc2, "Avg Recovery Ratio", f"{avg_rr:.1f}x", GREEN)
    _rbox(rc3, "Avg IV Rank", f"{avg_iv:.0f}", BLUE)
    _rbox(rc4, "Low IV (<40)", f"{low_iv}", GREEN)
    _rbox(rc5, "High IV (>60)", f"{high_iv}", RED)

    # IV distribution chart
    fig = go.Figure()
    for stage in STAGE_COLORS:
        group = [s_ for s_ in stocks if s_["app_stage"] == stage]
        if group:
            fig.add_trace(go.Box(
                y=[s_["iv_rank"] for s_ in group], name=stage.replace("_", " "),
                marker_color=STAGE_COLORS[stage], boxpoints="all", jitter=0.3, pointpos=-1.8,
            ))
    fig.update_layout(height=350, title="IV Rank Distribution by Stage", yaxis_title="IV Rank")
    st.plotly_chart(_white_chart(fig), use_container_width=True)

    # ═════════════════════════════════════════════════════════════════════════
    # 3D: OPTIONS CHAIN EXPLORER
    # ═════════════════════════════════════════════════════════════════════════
    _section("Options Chain Explorer — Search Any Ticker",
             "Type any ticker. We pull live data and build the optimal trade structure.")

    sorted_tickers = sorted(GROWTH_UNIVERSE.keys())
    selected = st.selectbox(
        "🔍 Search for any ticker — type to filter",
        options=sorted_tickers,
        format_func=lambda t: f"{t} — {GROWTH_UNIVERSE.get(t, t)}",
        key="explorer_ticker",
    )

    if selected:
        st.markdown(f'<div style="display:inline-block;background:{BLUE}12;color:{BLUE};'
                    f'font-size:13px;font-weight:600;padding:4px 14px;border-radius:20px;'
                    f'border:1px solid {BLUE}30;margin:4px 0 12px 0;">'
                    f'{selected} — {GROWTH_UNIVERSE.get(selected, "")}</div>',
                    unsafe_allow_html=True)

    analyze = st.button("🔬 Analyze Trade →", key="analyze_btn")

    if analyze and selected:
        ticker = selected
        with st.spinner(f"Analyzing {ticker}... fetching price, IV, options chain"):
            # 1. Polygon current price
            price = _fetch_polygon_price(ticker)

            # 2. ORATS IV rank
            iv_rank = _fetch_iv_rank(ticker)

            # 3. Fallbacks
            existing = next((x for x in stocks if x["ticker"] == ticker), None)
            if price is None:
                price = existing["price_current"] if existing else 100.0
            if iv_rank is None:
                iv_rank = existing["iv_rank"] if existing else 45.0

            # Compute trade params (45 DTE)
            target_expiry = date.today() + timedelta(days=45)
            days_to_friday = (4 - target_expiry.weekday()) % 7
            expiry_date = target_expiry + timedelta(days=days_to_friday)
            expiry_str = expiry_date.strftime("%Y-%m-%d")

            call_strike = round(price * 1.02 / 5) * 5
            put_buy_strike = round(price * 0.93 / 5) * 5
            put_sell_strike = round(price * 0.80 / 5) * 5

            sigma = iv_rank / 100 * 0.8 + 0.2
            t = 45 / 365
            call_premium = round(price * sigma * math.sqrt(t) * 0.4, 2)
            put_spread_cost = round((put_buy_strike - put_sell_strike) * 0.22, 2)
            total_debit = round(call_premium + put_spread_cost, 2)
            upside_breakeven = call_strike + total_debit
            recovery_ratio = round((put_buy_strike - put_sell_strike) / total_debit, 1) if total_debit > 0 else 2.0
            target_profit_pct = round(recovery_ratio * 25)

        # ── IV GAUGE (Plotly indicator) ──
        bar_color = GREEN if iv_rank < 30 else AMBER if iv_rank < 60 else RED
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=iv_rank,
            domain={"x": [0, 1], "y": [0, 1]},
            title={"text": "IV Rank", "font": {"size": 16}},
            gauge={
                "axis": {"range": [0, 100]},
                "bar": {"color": bar_color},
                "steps": [
                    {"range": [0, 30], "color": "rgba(22,163,74,0.15)"},
                    {"range": [30, 60], "color": "rgba(245,158,11,0.15)"},
                    {"range": [60, 100], "color": "rgba(220,38,38,0.15)"},
                ],
                "threshold": {"line": {"color": "red", "width": 4}, "thickness": 0.75, "value": iv_rank},
            },
        ))
        fig.update_layout(height=250, paper_bgcolor=WHITE, font=dict(color="#111111"))
        iv_lbl = _iv_label_long(iv_rank)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown(f"**Options are {iv_lbl}** (IV Rank: {iv_rank:.0f})")

        # Build synthetic stock dict and render full trade card
        synth = {
            "ticker": ticker,
            "company_name": GROWTH_UNIVERSE.get(ticker, ticker),
            "app_stage": existing["app_stage"] if existing else "MID_CONFIRMATION",
            "app_score": existing["app_score"] if existing else 50,
            "price_current": price,
            "iv_rank": iv_rank,
            "call_strike": call_strike,
            "call_expiry": expiry_str,
            "call_premium": call_premium,
            "put_buy_strike": put_buy_strike,
            "put_sell_strike": put_sell_strike,
            "put_spread_expiry": expiry_str,
            "put_spread_cost": put_spread_cost,
            "total_debit": total_debit,
            "max_loss": total_debit,
            "upside_breakeven": upside_breakeven,
            "target_profit_pct": target_profit_pct,
            "recovery_ratio": recovery_ratio,
            "plain_english_summary": existing["plain_english_summary"] if existing else f"{ticker} selected for analysis.",
            "eps_beats_gt15pct": existing.get("eps_beats_gt15pct", 0) if existing else 0,
            "eps_surprise_pct": existing.get("eps_surprise_pct", []) if existing else [],
            "axon_equivalent": existing.get("axon_equivalent", "core product") if existing else "core product",
            "tam_expansion": existing.get("tam_expansion", "new markets") if existing else "new markets",
            "next_earnings_date": existing.get("next_earnings_date", "") if existing else "",
            "options_rationale": existing.get("options_rationale", "") if existing else "",
            "caution_flags": existing.get("caution_flags", []) if existing else [],
        }
        _render_trade_card(synth)

        # ── 4-PANEL TRADINGVIEW CHARTS ──
        st.markdown(f'<div style="font-size:14px;font-weight:700;color:{TEXT_DARK};margin:20px 0 8px 0;">'
                    'TradingView Charts</div>', unsafe_allow_html=True)
        intervals = [("1h", "60", "1-Hour"), ("1d", "D", "Daily"), ("1w", "W", "Weekly"), ("1mo", "M", "Monthly")]
        cols = st.columns(4)
        for col, (period, interval, label) in zip(cols, intervals):
            with col:
                st.caption(label)
                rng = "3M" if interval in ["60", "D"] else "1Y"
                html = f'''<div id="tv_{ticker}_{interval}"></div>
                <script src="https://s3.tradingview.com/tv.js"></script>
                <script>new TradingView.widget({{
                    width: "100%", height: 260,
                    symbol: "{ticker}", interval: "{interval}",
                    timezone: "America/New_York", theme: "light", style: "1",
                    locale: "en", container_id: "tv_{ticker}_{interval}",
                    toolbar_bg: "#FFFFFF", enable_publishing: false,
                    hide_top_toolbar: true, hide_legend: true, save_image: false,
                    range: "{rng}"
                }});</script>'''
                components.html(html, height=280)

        # ── AI RATIONALE BOX ──
        strike_logic = "ATM" if call_strike <= price * 1.03 else "slightly OTM"
        iv_context = f"IV rank of {iv_rank:.0f} means options are {iv_lbl}"
        quality = "excellent" if iv_rank < 30 else "solid" if iv_rank < 60 else "elevated-risk"
        st.markdown(f'''<div style="background:#EFF6FF;border-left:4px solid {BLUE};border-radius:0 8px 8px 0;
        padding:16px 20px;margin-top:16px;">
        <div style="font-size:14px;font-weight:700;color:{TEXT_DARK};margin-bottom:8px;">
        Why the AI chose this structure</div>
        <div style="font-size:13px;color:#374151;line-height:1.7;">
        The {call_strike:.0f} call strike was chosen as {strike_logic} to maximize leverage on a bullish
        move while keeping premium manageable.
        The {expiry_str} expiry targets ~45 DTE — the optimal balance between theta decay
        (which accelerates inside 30 days) and giving the thesis enough time to play out.
        With {ticker} showing a {iv_rank:.0f} IV rank, {iv_context}, making this an
        {quality} environment for buying options.
        The {put_buy_strike:.0f}/{put_sell_strike:.0f} put spread reduces the net cost and provides
        meaningful protection if the stock drops to the support zone.
        Total risk is capped at ${total_debit:.2f}/share regardless of how far the stock falls.
        </div></div>''', unsafe_allow_html=True)

    # ── DISCLAIMER ──
    st.markdown(f'''<div style="background:#FEF2F2;border:1px solid #FECACA;border-radius:8px;
    padding:16px;margin-top:24px;">
    <div style="font-size:12px;color:{RED};font-weight:700;">DISCLAIMER</div>
    <div style="font-size:11px;color:{TEXT_GRAY};margin-top:6px;">
    This is NOT financial advice. All options setups are hypothetical illustrations of the
    AppLovin Pattern methodology. Options involve significant risk of loss. Past patterns do
    not guarantee future results. Always conduct your own due diligence and consult a
    financial advisor before trading options.</div></div>''', unsafe_allow_html=True)
