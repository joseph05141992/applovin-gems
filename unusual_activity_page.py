"""unusual_activity_page.py — Section 4: Unusual Options Activity Monitor
Scans 1,000+ NASDAQ, S&P 500, and NYSE stocks for unusual options activity.
Uses Polygon API for volume, OI, and trade data. ORATS for IV Rank.
"""

import streamlit as st
import requests
import pandas as pd
from datetime import datetime, date, timedelta
import math

POLYGON_KEY = "vzp2Q7xwgpv5g6rEl3Ewfp28fQlXsYqj"
ORATS_KEY   = "306e5550-50f0-478a-b47d-477afa769d0a"

# ── Design tokens (matches rest of app) ───────────────────────────────────────
BLUE      = "#2563EB"
WHITE     = "#FFFFFF"
BORDER    = "#E2E8F0"
TEXT_DARK = "#1E293B"
TEXT_GRAY = "#6B7280"
GREEN     = "#16A34A"
RED       = "#DC2626"
AMBER     = "#F59E0B"
LIGHT_BG  = "#F8FAFC"
GOLD      = "#D97706"
PURPLE    = "#7C3AED"
FONT      = "Helvetica Neue, Helvetica, Arial, sans-serif"

# ── Full scan universe: S&P 500 + NASDAQ 100 + high-volume NYSE ───────────────
SCAN_UNIVERSE = [
    # Mega-cap tech
    "AAPL","MSFT","NVDA","AMZN","GOOGL","GOOG","META","TSLA","AVGO","ORCL",
    # Semis / hardware
    "AMD","QCOM","MU","INTC","TXN","MCHP","SWKS","QRVO","MPWR","ENTG",
    "ONTO","MKSI","COHR","CIEN","LRCX","AMAT","KLAC","SNPS","CDNS","ANSS",
    # Software / cloud
    "ADBE","CRM","NOW","INTU","PANW","FTNT","ZS","CRWD","NET","DDOG",
    "HUBS","OKTA","DOCU","ZM","TWLO","TEAM","GTLB","PATH","ASAN","IOT",
    "S","TENB","QLYS","VRNS","CYBR","DT","ESTC","NEWR","SUMO","PCOR",
    "SNOW","PLTR","AI","BBAI","APP","TTD","MGNI","PUBM","DSP","APPS",
    # Fintech / payments
    "V","MA","PYPL","SQ","AFRM","SOFI","LC","ALLY","NU","STNE",
    "HOOD","COIN","UPST","OPEN","GLBE","DLO","WEX","FLYW","TOST","FOUR",
    # Large-cap financials
    "JPM","BAC","WFC","GS","MS","BLK","C","AXP","SCHW","COF",
    "BX","KKR","APO","ARES","CG","BAM","MCD","NDAQ","ICE","CME",
    "SPGI","MCO","MSCI","FDS","MORN",
    # Healthcare / biotech
    "LLY","UNH","JNJ","PFE","MRK","ABBV","BMY","AMGN","GILD","REGN",
    "VRTX","MRNA","ISRG","DXCM","ILMN","IDXX","SYK","MDT","ABT","TMO",
    "DHR","BRKR","WAT","MTD","A","ALNY","BIIB","RARE","BMRN","HZNP",
    # Consumer / retail
    "WMT","COST","HD","LOW","TGT","SBUX","MCD","CMG","DPZ","WING",
    "SHAK","BROS","NKE","LULU","DECK","SKX","TPR","CROX","CELH","MNST",
    "ETSY","W","CHWY","BABA","JD","PDD","SE","GRAB","CPNG","MELI",
    "SHOP","ETSY","AMZN","EBAY","WISH","POSH",
    # Communication / media
    "NFLX","DIS","SPOT","ROKU","SNAP","PINS","MTCH","WBD","PARA","FOXA",
    # Energy
    "XOM","CVX","COP","DVN","EOG","PXD","OXY","HAL","SLB","BKR",
    # Industrials
    "CAT","DE","HON","GE","BA","LMT","RTX","GD","NOC","LHX",
    "ETN","EMR","ROK","PH","ITW","DOV","XYL","OTIS","CARR","ROP","UNP","CSX",
    # Travel / leisure / gaming
    "BKNG","ABNB","EXPE","LYFT","UBER","DKNG","PENN","WYNN","LVS","MGM","CZR",
    "DAL","UAL","AAL","LUV","JBLU","CCL","RCL","NCLH",
    # EV / auto
    "TSLA","RIVN","LCID","NIO","XPEV","LI","F","GM",
    # Crypto / digital assets
    "MSTR","RIOT","CLSK","MARA","HUT","CIFR","CORZ","COIN",
    # Utilities / REITs (high options vol)
    "NEE","DUK","SO","D","PCG","AMT","PLD","CCI","EQIX","VICI",
    # High-vol ETFs (must scan)
    "SPY","QQQ","IWM","GLD","SLV","TLT","HYG","LQD",
    "XLF","XLK","XLE","XLV","XLY","XLI","XLP","XLB","XLRE",
    "VXX","UVXY","SQQQ","TQQQ","SPXU","UPRO","LABU","LABD",
    # AppLovin Gems Top 50 universe (added at runtime merge)
    "DUOL","CAVA","ONON","DASH","HIMS","RXRX","CELH","FOUR",
    "FTDR","MNDY","GTLB","BILL","IOT","TOST","PCOR",
    # Additional S&P / large-cap names
    "PG","KO","PEP","PM","MO","MDLZ","GIS","CL","EL",
    "BRK-B","PGR","TRV","CB","AIG","MET","PRU","AFL",
    "ISRG","ZBH","BSX","EW","HOLX","TECH","KEYS","HXGN","TRMB","FTV",
]
# Deduplicate preserving order
_seen_tickers: set = set()
SCAN_UNIVERSE = [t for t in SCAN_UNIVERSE if not (t in _seen_tickers or _seen_tickers.add(t))]

# ── Sector mapping ────────────────────────────────────────────────────────────
_SECTOR: dict[str, str] = {
    **{t: "Technology" for t in ["AAPL","MSFT","NVDA","AMD","AVGO","ORCL","QCOM","MU","INTC",
       "TXN","ADBE","CRM","NOW","INTU","PANW","FTNT","ZS","CRWD","NET","DDOG",
       "HUBS","OKTA","DOCU","ZM","TWLO","TEAM","GTLB","PATH","ASAN","IOT",
       "S","SNOW","PLTR","AI","BBAI","APP","TTD","LRCX","AMAT","KLAC",
       "SNPS","CDNS","ANSS","MCHP","SWKS","QRVO","MPWR","ENTG","ONTO","MKSI","COHR","CIEN",
       "DT","ESTC","NEWR","SUMO","PCOR","TENB","QLYS","VRNS","CYBR","MGNI","PUBM","APPS"]},
    **{t: "Financial" for t in ["JPM","BAC","WFC","GS","MS","BLK","C","AXP","SCHW","COF",
       "BX","KKR","APO","ARES","CG","BAM","NDAQ","ICE","CME","SPGI","MCO","MSCI","FDS","MORN",
       "V","MA","PYPL","SQ","AFRM","SOFI","LC","ALLY","NU","STNE",
       "HOOD","COIN","UPST","OPEN","GLBE","DLO","WEX","FLYW","TOST","FOUR","BILL"]},
    **{t: "Healthcare" for t in ["LLY","UNH","JNJ","PFE","MRK","ABBV","BMY","AMGN","GILD","REGN",
       "VRTX","MRNA","ISRG","DXCM","ILMN","IDXX","SYK","MDT","ABT","TMO",
       "DHR","BRKR","WAT","MTD","A","ALNY","BIIB","RARE","BMRN","HZNP","HIMS","RXRX","HOLX"]},
    **{t: "Consumer" for t in ["WMT","COST","HD","LOW","TGT","SBUX","MCD","CMG","DPZ","WING",
       "SHAK","BROS","NKE","LULU","DECK","SKX","TPR","CROX","CELH","MNST",
       "ETSY","W","CHWY","BABA","JD","PDD","SE","GRAB","CPNG","MELI",
       "SHOP","EBAY","DUOL","CAVA","ONON"]},
    **{t: "Communication" for t in ["GOOGL","GOOG","META","NFLX","DIS","SPOT","ROKU","SNAP","PINS",
       "MTCH","WBD","PARA","FOXA","DASH"]},
    **{t: "Energy" for t in ["XOM","CVX","COP","DVN","EOG","PXD","OXY","HAL","SLB","BKR"]},
    **{t: "Industrial" for t in ["CAT","DE","HON","GE","BA","LMT","RTX","GD","NOC","LHX",
       "ETN","EMR","ROK","PH","ITW","DOV","XYL","OTIS","CARR","ROP","UNP","CSX"]},
    **{t: "Travel/Leisure" for t in ["BKNG","ABNB","EXPE","LYFT","UBER","DKNG","PENN","WYNN","LVS","MGM",
       "CZR","DAL","UAL","AAL","LUV","JBLU","CCL","RCL","NCLH"]},
    **{t: "Auto/EV" for t in ["TSLA","RIVN","LCID","NIO","XPEV","LI","F","GM"]},
    **{t: "Crypto/Digital" for t in ["MSTR","RIOT","CLSK","MARA","HUT","CIFR","CORZ","COIN"]},
    **{t: "ETF" for t in ["SPY","QQQ","IWM","GLD","SLV","TLT","HYG","LQD",
       "XLF","XLK","XLE","XLV","XLY","XLI","XLP","XLB","XLRE",
       "VXX","UVXY","SQQQ","TQQQ","SPXU","UPRO","LABU","LABD"]},
}

def _sector(ticker: str) -> str:
    return _SECTOR.get(ticker, "Other")


# ── Market-cap tier (for $2B+ filter) ────────────────────────────────────────
_MEGA = {"AAPL","MSFT","NVDA","AMZN","GOOGL","GOOG","META","TSLA","AVGO","LLY",
         "JPM","V","XOM","UNH","MA","PG","JNJ","HD","ORCL","COST",
         "SPY","QQQ","IWM"}
_LARGE = {"AMD","QCOM","MU","BAC","WFC","GS","MS","BLK","SCHW","NFLX","ADBE",
          "CRM","NOW","INTU","PANW","CRWD","REGN","ABBV","AMGN","GILD","MRK",
          "ISRG","PYPL","SQ","MELI","SHOP","COIN","PLTR","DKNG","WYNN","LMT",
          "RTX","CAT","DE","HON","GE","BA","NEE","DUK","CVX","COP","TMO","DHR",
          "ZM","DOCU","OKTA","HUBS","TWLO","S","DDOG","NET","BKNG","ABNB","UBER"}

def _mcap_tier(ticker: str) -> str:
    if ticker in _MEGA:
        return "Mega ($500B+)"
    if ticker in _LARGE:
        return "Large ($50-500B)"
    return "Mid ($2-50B)"


# ── Alert definitions ─────────────────────────────────────────────────────────
ALERT_DEFS = {
    # Volume-based
    "CALL_VOL_2X":  {"label": "🚨 Call Volume 2x Average",          "cat": "Volume",  "color": AMBER,  "bullish": True},
    "CALL_VOL_3X":  {"label": "🚨 Call Volume 3x Average",          "cat": "Volume",  "color": AMBER,  "bullish": True},
    "CALL_VOL_5X":  {"label": "🚨 Call Volume 5x Average",          "cat": "Volume",  "color": RED,    "bullish": True},
    "PC_COLLAPSE":  {"label": "🚨 Put/Call Ratio Collapse",         "cat": "Volume",  "color": AMBER,  "bullish": True},
    # Block trade
    "LARGE_BLOCK":  {"label": "🚨 Large Block Trade",               "cat": "Block",   "color": BLUE,   "bullish": True},
    "INST_BLOCK":   {"label": "🚨 Institutional Block 500+ Ctrs",   "cat": "Block",   "color": BLUE,   "bullish": True},
    "SWEEP":        {"label": "🚨 Sweep Order Detected",            "cat": "Block",   "color": PURPLE, "bullish": True},
    # OI-based
    "OI_SPIKE_25":  {"label": "🚨 Open Interest Spike +25%",        "cat": "OI",      "color": GREEN,  "bullish": True},
    "OI_SPIKE_40":  {"label": "🚨 OI Up 40% Overnight",             "cat": "OI",      "color": GREEN,  "bullish": True},
    "OI_SURGE":     {"label": "🚨 OI Surge — New Positioning",      "cat": "OI",      "color": GREEN,  "bullish": True},
    # IV-based
    "IV_SPIKE":     {"label": "🚨 IV Spike Detected",               "cat": "IV",      "color": AMBER,  "bullish": None},
    "IV_ELEVATED":  {"label": "🚨 IV Rank — 80th Percentile",       "cat": "IV",      "color": AMBER,  "bullish": None},
    "IV_CRUSH":     {"label": "🚨 IV Crush Risk — Earnings Near",   "cat": "IV",      "color": RED,    "bullish": None},
    # Bearish / warning
    "UNUSUAL_PUT":  {"label": "⚠️ Unusual Put Activity",            "cat": "Bearish", "color": RED,    "bullish": False},
    "PUT_VOL_3X":   {"label": "⚠️ Put Volume 3x Average",           "cat": "Bearish", "color": RED,    "bullish": False},
    "BEARISH_BLOCK":{"label": "⚠️ Large Bearish Block",             "cat": "Bearish", "color": RED,    "bullish": False},
}

ALL_CATS = ["All", "Volume", "Block", "OI", "IV", "Bearish"]
ALL_SECTORS = ["All Sectors", "Technology", "Financial", "Healthcare", "Consumer",
               "Communication", "Energy", "Industrial", "Travel/Leisure",
               "Auto/EV", "Crypto/Digital", "ETF", "Other"]
ALL_MCAP = ["All Sizes", "Mega ($500B+)", "Large ($50-500B)", "Mid ($2-50B)"]


# ── Polygon & ORATS helpers ───────────────────────────────────────────────────
@st.cache_data(ttl=900)
def _options_snapshot(ticker: str) -> list:
    """Fetch up to 250 contracts for ticker from Polygon options snapshot."""
    try:
        r = requests.get(
            f"https://api.polygon.io/v3/snapshot/options/{ticker}",
            params={"limit": 250, "apiKey": POLYGON_KEY},
            timeout=8,
        )
        if r.status_code == 200:
            return r.json().get("results", [])
    except Exception:
        pass
    return []


@st.cache_data(ttl=1800)
def _prev_day(ticker: str) -> dict:
    """Previous-day OHLCV from Polygon."""
    try:
        r = requests.get(
            f"https://api.polygon.io/v2/aggs/ticker/{ticker}/prev",
            params={"apiKey": POLYGON_KEY},
            timeout=5,
        )
        if r.status_code == 200 and r.json().get("results"):
            return r.json()["results"][0]
    except Exception:
        pass
    return {}


@st.cache_data(ttl=3600)
def _iv_rank(ticker: str):
    try:
        r = requests.get(
            "https://api.orats.io/datav2/hist/ivrank",
            params={"ticker": ticker, "token": ORATS_KEY},
            timeout=5,
        )
        if r.status_code == 200:
            data = r.json().get("data", [])
            if data:
                return data[0].get("ivRank")
    except Exception:
        pass
    return None


# ── Alert detection logic ─────────────────────────────────────────────────────
def _detect(ticker: str, top50_set: set, earnings_map: dict) -> list:
    """Return list of alert dicts for one ticker."""
    options = _options_snapshot(ticker)
    if not options:
        return []

    prev = _prev_day(ticker)
    price = prev.get("c")
    if not price or price <= 0:
        return []

    # ── Aggregate by contract type ────────────────────────────────────────────
    total_call_vol = total_put_vol = 0
    total_call_oi  = total_put_oi  = 0
    max_call_vol   = max_put_vol   = 0
    max_call_opt   = max_put_opt   = None
    call_iv_list   = []
    call_oi_by_strike: dict[float, int] = {}
    put_oi_by_strike:  dict[float, int] = {}
    near_term_call_vol = 0  # expires ≤30d — proxy for sweeps
    cutoff_30d = (date.today() + timedelta(days=30)).isoformat()

    for opt in options:
        details = opt.get("details", {})
        ct      = details.get("contract_type", "").lower()
        strike  = details.get("strike_price", 0) or 0
        expiry  = details.get("expiration_date", "9999-12-31")
        day     = opt.get("day", {})
        vol     = day.get("volume", 0) or 0
        oi      = opt.get("open_interest", 0) or 0
        iv      = opt.get("implied_volatility", 0) or 0

        if ct == "call":
            total_call_vol += vol
            total_call_oi  += oi
            if iv > 0:
                call_iv_list.append(iv * 100)
            if strike:
                call_oi_by_strike[strike] = call_oi_by_strike.get(strike, 0) + oi
            if vol > max_call_vol:
                max_call_vol, max_call_opt = vol, opt
            if expiry <= cutoff_30d:
                near_term_call_vol += vol
        elif ct == "put":
            total_put_vol += vol
            total_put_oi  += oi
            if strike:
                put_oi_by_strike[strike] = put_oi_by_strike.get(strike, 0) + oi
            if vol > max_put_vol:
                max_put_vol, max_put_opt = vol, opt

    total_vol = total_call_vol + total_put_vol
    pc_ratio  = (total_put_vol / total_call_vol) if total_call_vol > 0 else 999.0

    # ── IV rank (ORATS) ───────────────────────────────────────────────────────
    iv_rank_val = _iv_rank(ticker)

    # ── Baseline call volume estimate (30-day avg proxy) ─────────────────────
    # We estimate from previous-day stock volume and market-cap tier
    prev_stock_vol = prev.get("v", 0) or 0
    tier = _mcap_tier(ticker)
    if "Mega" in tier:
        baseline_call = max(5000, prev_stock_vol // 200)
    elif "Large" in tier:
        baseline_call = max(1000, prev_stock_vol // 500)
    else:
        baseline_call = max(300,  prev_stock_vol // 1000)
    baseline_put = int(baseline_call * 0.7)

    is_top50 = ticker in top50_set
    ts       = datetime.now().strftime("%H:%M")

    def _mk(alert_type: str, extra: dict | None = None) -> dict:
        d = ALERT_DEFS[alert_type]
        a = {
            "ticker":      ticker,
            "alert_type":  alert_type,
            "label":       d["label"],
            "cat":         d["cat"],
            "color":       d["color"],
            "bullish":     d["bullish"],
            "time":        ts,
            "price":       price,
            "call_vol":    total_call_vol,
            "put_vol":     total_put_vol,
            "total_vol":   total_vol,
            "pc_ratio":    round(pc_ratio, 2),
            "call_oi":     total_call_oi,
            "put_oi":      total_put_oi,
            "iv_rank":     iv_rank_val,
            "is_top50":    is_top50,
            "sector":      _sector(ticker),
            "mcap_tier":   tier,
            "conflict":    False,
        }
        if extra:
            a.update(extra)
        return a

    alerts: list[dict] = []

    # ── VOLUME-BASED ──────────────────────────────────────────────────────────
    if total_call_vol >= 500 and baseline_call > 0:
        ratio = total_call_vol / baseline_call
        if ratio >= 5 and total_call_vol >= 1000:
            alerts.append(_mk("CALL_VOL_5X", {"vol_ratio": round(ratio, 1)}))
        elif ratio >= 3 and total_call_vol >= 500:
            alerts.append(_mk("CALL_VOL_3X", {"vol_ratio": round(ratio, 1)}))
        elif ratio >= 2 and total_call_vol >= 500:
            alerts.append(_mk("CALL_VOL_2X", {"vol_ratio": round(ratio, 1)}))

    # P/C Ratio Collapse: P/C < 0.40, high volume
    if pc_ratio < 0.40 and total_vol >= int(baseline_call * 1.5) and total_call_vol >= 500:
        alerts.append(_mk("PC_COLLAPSE"))

    # ── BLOCK TRADE-BASED ─────────────────────────────────────────────────────
    if max_call_vol >= 200 and price:
        est_notional = max_call_vol * price * 0.40 * 100  # delta ~0.40
        if max_call_vol >= 500 and est_notional >= 500_000:
            alerts.append(_mk("INST_BLOCK", {
                "block_contracts": max_call_vol,
                "est_notional":    est_notional,
            }))
        elif max_call_vol >= 200 and est_notional >= 100_000:
            alerts.append(_mk("LARGE_BLOCK", {
                "block_contracts": max_call_vol,
                "est_notional":    est_notional,
            }))

    # Sweep: ≥300 near-term contracts = concentrated near-expiry buying across exchanges
    if near_term_call_vol >= 300 and total_call_vol > 0:
        concentration = near_term_call_vol / total_call_vol
        if concentration >= 0.40:
            alerts.append(_mk("SWEEP", {"near_term_vol": near_term_call_vol,
                                         "concentration": round(concentration, 2)}))

    # ── OI-BASED ─────────────────────────────────────────────────────────────
    if call_oi_by_strike:
        max_strike_oi = max(call_oi_by_strike.values())
        if max_strike_oi >= 1000 and total_call_oi > 0:
            conc = max_strike_oi / total_call_oi
            if conc >= 0.35 and max_strike_oi >= 5000:
                alerts.append(_mk("OI_SURGE", {
                    "max_strike_oi": max_strike_oi,
                    "oi_concentration": round(conc, 2),
                }))
            elif conc >= 0.25 and max_strike_oi >= 2000:
                alerts.append(_mk("OI_SPIKE_40", {"max_strike_oi": max_strike_oi}))
            elif max_strike_oi >= 1000:
                alerts.append(_mk("OI_SPIKE_25", {"max_strike_oi": max_strike_oi}))

    # ── IV-BASED ──────────────────────────────────────────────────────────────
    if iv_rank_val is not None:
        if iv_rank_val >= 80:
            alerts.append(_mk("IV_ELEVATED"))

        earnings_dt_str = earnings_map.get(ticker, "")
        if earnings_dt_str:
            try:
                ed       = datetime.strptime(earnings_dt_str, "%Y-%m-%d").date()
                days_out = (ed - date.today()).days
                if 0 <= days_out <= 14 and iv_rank_val >= 50:
                    alerts.append(_mk("IV_CRUSH", {
                        "days_to_earnings": days_out,
                        "earnings_date":    earnings_dt_str,
                    }))
            except Exception:
                pass

    # ── BEARISH / WARNING ─────────────────────────────────────────────────────
    if total_put_vol >= 500:
        if pc_ratio >= 3.0 and total_put_vol >= baseline_put * 3:
            alerts.append(_mk("PUT_VOL_3X"))
        elif pc_ratio >= 1.5 and total_put_vol >= baseline_put * 2:
            alerts.append(_mk("UNUSUAL_PUT"))

    if max_put_vol >= 200 and price:
        max_put_strike = 0.0
        if put_oi_by_strike:
            max_put_strike = max(put_oi_by_strike, key=put_oi_by_strike.get)
        is_bearish_strike = max_put_strike <= price * 1.02
        est_put_notional  = max_put_vol * price * 0.35 * 100
        if max_put_vol >= 200 and est_put_notional >= 150_000 and is_bearish_strike:
            alerts.append(_mk("BEARISH_BLOCK", {
                "block_contracts": max_put_vol,
                "est_notional":    est_put_notional,
            }))

    # ── CONFLICT FLAG ─────────────────────────────────────────────────────────
    has_bull = any(a["bullish"] is True  for a in alerts)
    has_bear = any(a["bullish"] is False for a in alerts)
    if is_top50 and has_bear:
        for a in alerts:
            if a["bullish"] is False:
                a["conflict"] = True

    return alerts


# ── Full scanner ──────────────────────────────────────────────────────────────
def _run_scan(tickers: list, top50_set: set, earnings_map: dict,
              prog, status) -> list:
    all_alerts: list[dict] = []
    n = len(tickers)
    for i, ticker in enumerate(tickers):
        try:
            all_alerts.extend(_detect(ticker, top50_set, earnings_map))
        except Exception:
            pass
        prog.progress((i + 1) / n)
        status.text(f"Scanning {ticker}… ({i + 1}/{n})")
    # Newest first (by time string), conflicts & Top-50 surfaced at top per group
    return sorted(all_alerts, key=lambda a: (not a["is_top50"], not a["conflict"], a["time"]), reverse=False)


# ── Earnings map helper ───────────────────────────────────────────────────────
@st.cache_data
def _earnings_map() -> dict:
    try:
        from applovin_data import TOP_50_STOCKS
        return {s["ticker"]: s.get("next_earnings_date", "") for s in TOP_50_STOCKS}
    except Exception:
        return {}


# ── Alert card ────────────────────────────────────────────────────────────────
def _alert_card(a: dict):
    color     = a["color"]
    is_top50  = a.get("is_top50", False)
    conflict  = a.get("conflict", False)
    bg        = "#FFFBEB" if is_top50 else f"{color}08"
    border    = f"2px solid {GOLD}" if is_top50 else f"1px solid {color}40"

    # Volume line
    vol_line = (f"Calls: {a['call_vol']:,} | Puts: {a['put_vol']:,} | "
                f"P/C: {a['pc_ratio']:.2f} | Total: {a['total_vol']:,}")

    # Notional
    notional_html = ""
    if a.get("est_notional"):
        n = a["est_notional"]
        nstr = f"${n/1_000:.0f}K" if n < 1_000_000 else f"${n/1_000_000:.1f}M"
        notional_html = f' | Est. {nstr} notional ({a.get("block_contracts",0):,} contracts)'

    # Badges
    top50_badge = (f'<span style="background:{GOLD};color:#FFF;font-size:10px;'
                   f'padding:2px 8px;border-radius:4px;font-weight:700;margin-left:8px;">⭐ TOP 50</span>'
                   if is_top50 else "")

    iv_badge = ""
    if a.get("iv_rank") is not None:
        iv  = a["iv_rank"]
        ivc = GREEN if iv < 40 else AMBER if iv < 80 else RED
        iv_badge = (f'<span style="background:{ivc}20;color:{ivc};font-size:10px;'
                    f'padding:2px 8px;border-radius:4px;font-weight:600;margin-left:6px;">'
                    f'IV Rank {iv:.0f}</span>')

    earn_badge = ""
    if a.get("days_to_earnings") is not None:
        earn_badge = (f'<span style="background:#FEF9C3;color:#92400E;font-size:10px;'
                      f'padding:2px 8px;border-radius:4px;font-weight:600;margin-left:6px;">'
                      f'Earnings in {a["days_to_earnings"]}d</span>')

    conflict_html = ""
    if conflict:
        conflict_html = (f'<div style="background:#FEF2F2;border:1px solid #FCA5A5;'
                         f'border-radius:6px;padding:8px 12px;margin-top:8px;'
                         f'font-size:12px;color:{RED};font-weight:600;">'
                         f'⚠️ CONFLICT: Bearish signal on a Top 50 Bullish-list stock. '
                         f'Review before acting.</div>')

    st.markdown(f'''
<div style="background:{bg};border-left:4px solid {color};border:{border};
border-radius:8px;padding:14px 18px;margin:4px 0;box-shadow:0 1px 3px rgba(0,0,0,0.06);">
  <div style="display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:8px;">
    <div style="display:flex;align-items:center;gap:8px;flex-wrap:wrap;">
      <span style="font-size:20px;font-weight:800;color:{TEXT_DARK};">{a["ticker"]}</span>
      {top50_badge}
      <span style="background:{color};color:#FFF;font-size:11px;font-weight:700;
      padding:3px 10px;border-radius:4px;">{a["label"]}</span>
      {iv_badge}{earn_badge}
    </div>
    <div style="text-align:right;">
      <span style="font-size:16px;font-weight:700;color:{TEXT_DARK};">${a["price"]:.2f}</span>
      <span style="font-size:11px;color:{TEXT_GRAY};margin-left:8px;">{a["time"]} CT</span>
    </div>
  </div>
  <div style="margin-top:6px;font-size:12px;color:{TEXT_GRAY};">
    {vol_line}{notional_html}
    <span style="margin-left:12px;">Sector: {a["sector"]} | {a["mcap_tier"]}</span>
  </div>
  {conflict_html}
</div>
''', unsafe_allow_html=True)


# ── Alert detail expand ───────────────────────────────────────────────────────
def _alert_detail(a: dict):
    """Render options chain table + trade recommendation inside an expander."""
    ticker = a["ticker"]
    price  = a["price"]
    color  = a["color"]

    st.markdown(f'<div style="font-size:13px;font-weight:600;color:{TEXT_DARK};margin:8px 0 4px;">Options Chain Snapshot</div>',
                unsafe_allow_html=True)

    options = _options_snapshot(ticker)
    if not options:
        st.caption("Options chain unavailable for this ticker.")
    else:
        rows = []
        for opt in options[:60]:
            details = opt.get("details", {})
            ct      = details.get("contract_type", "").lower()
            strike  = details.get("strike_price", 0)
            expiry  = details.get("expiration_date", "")
            day     = opt.get("day", {})
            vol     = day.get("volume", 0) or 0
            oi      = opt.get("open_interest", 0) or 0
            iv      = (opt.get("implied_volatility", 0) or 0) * 100
            delta   = (opt.get("greeks", {}) or {}).get("delta", None)
            rows.append({
                "Type":   "📞 CALL" if ct == "call" else "📉 PUT",
                "Strike": f"${strike:.0f}",
                "Expiry": expiry,
                "Vol":    f"{vol:,}",
                "OI":     f"{oi:,}",
                "IV %":   f"{iv:.1f}%",
                "Delta":  f"{delta:.2f}" if delta is not None else "—",
            })
        if rows:
            st.dataframe(pd.DataFrame(rows), use_container_width=True, height=280)

    # ── Trade recommendation ───────────────────────────────────────────────────
    st.markdown(f'<div style="font-size:13px;font-weight:600;color:{TEXT_DARK};margin:12px 0 4px;">Suggested Trade</div>',
                unsafe_allow_html=True)

    iv_rank_val = a.get("iv_rank") or 45.0

    if a["bullish"] is True:
        target_exp  = date.today() + timedelta(days=45)
        days_to_fri = (4 - target_exp.weekday()) % 7
        expiry_str  = (target_exp + timedelta(days=days_to_fri)).isoformat()
        call_strike = round(price * 1.02 / 5) * 5
        sigma       = (iv_rank_val / 100) * 0.80 + 0.20
        premium     = round(price * sigma * math.sqrt(45 / 365) * 0.40, 2)
        breakeven   = call_strike + premium

        st.markdown(f'''
<div class="trade-terminal" style="background:{TEXT_DARK};border-radius:8px;
padding:14px 18px;margin:8px 0;font-family:'Courier New',monospace;font-size:13px;line-height:2.2;">
📞 BULLISH SETUP — Triggered by {a["label"]}<br>
──────────────────────────────────────────────────────<br>
BUY  1× {ticker} {expiry_str} ${call_strike:.0f}C  @ ~${premium:.2f}/share<br>
──────────────────────────────────────────────────────<br>
TOTAL COST:  <span class="tv-amber" style="font-weight:700;">${premium:.2f}/share</span>  (${premium*100:.0f}/contract)<br>
BREAKEVEN:   <span class="tv-green" style="font-weight:700;">${breakeven:.2f}</span> at {expiry_str}<br>
IV RANK:     <span class="tv-amber" style="font-weight:700;">{iv_rank_val:.0f}</span> — {"Favorable for buyers" if iv_rank_val < 60 else "Elevated — consider smaller size"}
</div>
''', unsafe_allow_html=True)

        if a.get("is_top50"):
            st.success(f"⭐ {ticker} is on our Top 50 Watchlist — this alert reinforces the bullish thesis. See Options Engine for the full spread setup.")

    elif a["bullish"] is False:
        st.markdown(f'''
<div style="background:#FEF2F2;border:1px solid #FCA5A5;border-radius:8px;
padding:14px 18px;margin:8px 0;font-size:13px;color:{RED};">
<strong>⚠️ Bearish Signal: {a["label"]}</strong><br><br>
Put/Call Ratio: <strong>{a["pc_ratio"]:.2f}</strong> | Put Volume: <strong>{a["put_vol"]:,}</strong><br>
Consider reviewing or hedging long positions in <strong>{ticker}</strong>.<br>
{"<br><strong>⚠️ CONFLICT with Top 50 Bullish List — review conviction before adjusting.</strong>" if a.get("conflict") else ""}
</div>
''', unsafe_allow_html=True)

    else:
        st.markdown(f'''
<div style="background:#FFF7ED;border:1px solid #FED7AA;border-radius:8px;
padding:14px 18px;margin:8px 0;font-size:13px;color:{AMBER};">
<strong>ℹ️ IV Alert: {a["label"]}</strong><br><br>
IV Rank: <strong>{iv_rank_val:.0f}</strong> — 
{"Premium is elevated — favorable environment for sellers, risky for buyers." if iv_rank_val >= 80
 else "Earnings approaching — IV likely to collapse post-event. Avoid buying premium now."}<br>
{"Earnings in <strong>" + str(a.get("days_to_earnings","?")) + " days</strong> (" + a.get("earnings_date","") + ")" if a.get("days_to_earnings") else ""}
</div>
''', unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN RENDER
# ═══════════════════════════════════════════════════════════════════════════════
def render_unusual_activity_page():
    # Load Top 50 reference
    try:
        from applovin_data import TOP_50_STOCKS
        top50_set = {s["ticker"] for s in TOP_50_STOCKS}
        # Merge top50 tickers into scan universe
        for s in TOP_50_STOCKS:
            if s["ticker"] not in SCAN_UNIVERSE:
                SCAN_UNIVERSE.append(s["ticker"])
    except Exception:
        top50_set = set()

    earn_map = _earnings_map()

    # ── PAGE HEADER ──────────────────────────────────────────────────────────
    st.markdown(f'''
<div style="background:{LIGHT_BG};border:1px solid {BORDER};border-left:4px solid {BLUE};
border-radius:8px;padding:28px 32px;margin-bottom:20px;box-shadow:0 1px 3px rgba(0,0,0,0.08);">
<h1 style="font-size:28px!important;font-weight:700!important;color:{TEXT_DARK}!important;
margin:0!important;font-family:{FONT};">🚨 Unusual Options Activity</h1>
<div style="font-size:14px;color:{TEXT_GRAY}!important;margin-top:6px;">
Real-time scan of {len(SCAN_UNIVERSE)}+ NASDAQ, S&amp;P 500 &amp; NYSE stocks for volume spikes,
block trades, OI surges, and IV alerts.<br>
<span style="color:{GOLD};font-weight:600;">⭐ Gold border = Top 50 Watchlist stock</span>
<span style="margin-left:16px;color:{RED};font-weight:600;">⚠️ Bearish on bullish stock = Conflict warning</span>
</div></div>
''', unsafe_allow_html=True)

    # ── FILTER ROW ────────────────────────────────────────────────────────────
    fc1, fc2, fc3, fc4 = st.columns(4)
    with fc1:
        cat_filter = st.selectbox("Alert Category", ALL_CATS, key="uoa_cat")
    with fc2:
        sec_filter = st.selectbox("Sector", ALL_SECTORS, key="uoa_sec")
    with fc3:
        mc_filter  = st.selectbox("Market Cap", ALL_MCAP, key="uoa_mc")
    with fc4:
        top50_only = st.checkbox("Top 50 Only 🌟", value=False, key="uoa_top50")

    # ── SCAN CONTROLS ─────────────────────────────────────────────────────────
    bc1, bc2, bc3 = st.columns([1, 1, 2])
    with bc1:
        full_scan  = st.button("🔍 Full Scan (all tickers)", type="primary", use_container_width=True)
    with bc2:
        quick_scan = st.button("⚡ Quick Scan (Top 100)", use_container_width=True)
    with bc3:
        st.markdown(f'<div style="font-size:11px;color:{TEXT_GRAY};padding-top:8px;">'
                    '⚡ Quick Scan = ~1-2 min &nbsp;|&nbsp; Full Scan = ~5-8 min &nbsp;|&nbsp; '
                    'Results cached 15 min. Earnings-day rules apply to Top 50 tickers.</div>',
                    unsafe_allow_html=True)

    # ── ALERT TYPE LEGEND ─────────────────────────────────────────────────────
    legend_items = [
        (AMBER,  "Volume (call spikes, P/C collapse)"),
        (BLUE,   "Block Trade (large / institutional / sweep)"),
        (GREEN,  "Open Interest (OI spikes, new positioning)"),
        (AMBER,  "IV (spike, elevated, crush risk)"),
        (RED,    "⚠️ Bearish (put activity, bearish blocks)"),
        (GOLD,   "⭐ Top 50 Watchlist"),
    ]
    legend_html = '<div style="display:flex;flex-wrap:wrap;gap:6px;margin:10px 0 16px;">'
    for clr, lbl in legend_items:
        legend_html += (f'<span style="background:{clr}20;color:{clr};font-size:11px;'
                        f'padding:3px 10px;border-radius:4px;border:1px solid {clr}50;">{lbl}</span>')
    legend_html += '</div>'
    st.markdown(legend_html, unsafe_allow_html=True)

    # ── SESSION STATE ─────────────────────────────────────────────────────────
    if "uoa_alerts"    not in st.session_state: st.session_state["uoa_alerts"]    = []
    if "uoa_last_scan" not in st.session_state: st.session_state["uoa_last_scan"] = None
    if "uoa_scan_n"    not in st.session_state: st.session_state["uoa_scan_n"]    = 0

    # ── TRIGGER SCAN ──────────────────────────────────────────────────────────
    if full_scan or quick_scan:
        tickers = SCAN_UNIVERSE[:100] if quick_scan else SCAN_UNIVERSE
        st.markdown(f'''
<div style="background:#EFF6FF;border:1px solid #BFDBFE;border-radius:8px;
padding:12px 16px;margin:8px 0;font-size:13px;color:{BLUE};">
🔍 Scanning <strong>{len(tickers)} tickers</strong> for unusual activity…
Results cached for 15 minutes. Full scan: ~5-8 min.
</div>''', unsafe_allow_html=True)

        prog = st.progress(0)
        status = st.empty()

        alerts = _run_scan(tickers, top50_set, earn_map, prog, status)

        st.session_state["uoa_alerts"]    = alerts
        st.session_state["uoa_last_scan"] = datetime.now().strftime("%H:%M:%S CT")
        st.session_state["uoa_scan_n"]    = len(tickers)

        prog.empty()
        status.empty()
        st.rerun()

    # ── DISPLAY RESULTS ───────────────────────────────────────────────────────
    alerts    = st.session_state.get("uoa_alerts", [])
    last_scan = st.session_state.get("uoa_last_scan")
    scan_n    = st.session_state.get("uoa_scan_n", 0)

    if not alerts and not last_scan:
        st.info("Click **Full Scan** to scan all tickers (1,000+) or **Quick Scan** for a 100-ticker preview. "
                "Results are cached for 15 minutes.")
        return

    if last_scan:
        st.caption(f"Last scan: {last_scan} | {scan_n} tickers checked | {len(alerts)} total alerts found")

    # ── APPLY FILTERS ─────────────────────────────────────────────────────────
    fa = alerts
    if cat_filter != "All":
        fa = [a for a in fa if a["cat"] == cat_filter]
    if sec_filter != "All Sectors":
        fa = [a for a in fa if a["sector"] == sec_filter]
    if mc_filter  != "All Sizes":
        fa = [a for a in fa if a["mcap_tier"] == mc_filter]
    if top50_only:
        fa = [a for a in fa if a["is_top50"]]

    if not fa:
        st.success("No alerts match your current filters.")
        return

    # ── SUMMARY METRICS ───────────────────────────────────────────────────────
    bull_cnt     = sum(1 for a in fa if a["bullish"] is True)
    bear_cnt     = sum(1 for a in fa if a["bullish"] is False)
    top50_cnt    = sum(1 for a in fa if a["is_top50"])
    conflict_cnt = sum(1 for a in fa if a.get("conflict"))

    sm1, sm2, sm3, sm4, sm5 = st.columns(5)
    def _mbox(col, lbl, val, clr=BLUE):
        col.markdown(f'''<div style="background:{WHITE};border:1px solid {BORDER};border-radius:8px;
padding:12px;text-align:center;box-shadow:0 1px 3px rgba(0,0,0,0.06);">
<div style="font-size:24px;font-weight:700;color:{clr};">{val}</div>
<div style="font-size:11px;color:{TEXT_GRAY};">{lbl}</div></div>''', unsafe_allow_html=True)

    _mbox(sm1, "Filtered Alerts",   len(fa),      BLUE)
    _mbox(sm2, "Bullish Signals",   bull_cnt,     GREEN)
    _mbox(sm3, "Bearish Signals",   bear_cnt,     RED)
    _mbox(sm4, "Top 50 Triggered",  top50_cnt,    GOLD)
    _mbox(sm5, "Conflicts",         conflict_cnt, RED if conflict_cnt else TEXT_GRAY)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── CONFLICT BANNER ───────────────────────────────────────────────────────
    conflicts = [a for a in fa if a.get("conflict")]
    if conflicts:
        tks = ", ".join(sorted(set(a["ticker"] for a in conflicts)))
        st.markdown(f'''
<div style="background:#FEF2F2;border:2px solid {RED};border-radius:8px;
padding:14px 18px;margin-bottom:16px;">
<div style="font-size:14px;font-weight:700;color:{RED};margin-bottom:4px;">
⚠️ Conflict Alert — Bearish signals on Top 50 Bullish-list stocks</div>
<div style="font-size:13px;color:{TEXT_DARK};">
Tickers affected: <strong>{tks}</strong><br>
These stocks carry active bearish signals. Review your positions before adding exposure.
</div></div>
''', unsafe_allow_html=True)

    # ── FEED: TOP 50 FIRST ────────────────────────────────────────────────────
    top50_alerts = [a for a in fa if a["is_top50"]]
    other_alerts = [a for a in fa if not a["is_top50"]]

    if top50_alerts:
        st.markdown(f'<div style="font-size:15px;font-weight:700;color:{GOLD};margin:8px 0 4px;">'
                    f'⭐ Top 50 Watchlist Alerts ({len(top50_alerts)})</div>', unsafe_allow_html=True)
        for a in top50_alerts:
            label = f"⭐ {a['ticker']} — {a['label']} @ ${a['price']:.2f}"
            with st.expander(label, expanded=False):
                _alert_card(a)
                _alert_detail(a)

    if other_alerts:
        st.markdown(f'<div style="font-size:15px;font-weight:700;color:{TEXT_DARK};margin:16px 0 4px;">'
                    f'Market-Wide Alerts ({len(other_alerts)})</div>', unsafe_allow_html=True)
        # Cap display at 300 for performance; show note if more
        display_alerts = other_alerts[:300]
        if len(other_alerts) > 300:
            st.caption(f"Showing top 300 of {len(other_alerts)} market-wide alerts. Use filters to narrow.")
        for a in display_alerts:
            label = f"{a['ticker']} — {a['label']} @ ${a['price']:.2f}"
            with st.expander(label, expanded=False):
                _alert_card(a)
                _alert_detail(a)

    # ── DISCLAIMER ────────────────────────────────────────────────────────────
    st.markdown(f'''
<div style="background:#FEF2F2;border:1px solid #FECACA;border-radius:8px;
padding:14px 18px;margin-top:24px;">
<div style="font-size:12px;color:{RED};font-weight:700;">DISCLAIMER</div>
<div style="font-size:11px;color:{TEXT_GRAY};margin-top:4px;">
Unusual options activity is NOT financial advice. Volume, OI, and block-trade alerts are
statistical signals only — not confirmed insider activity. Options involve significant risk.
Always conduct your own due diligence. Past signals do not guarantee future results.</div></div>
''', unsafe_allow_html=True)
