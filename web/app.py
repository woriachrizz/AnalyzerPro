from __future__ import annotations

import os
import sys
from datetime import datetime, timezone

import pandas as pd
import streamlit as st

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from core.analyzer import Analyzer
from web.stream_client import DerivStream


st.set_page_config(page_title="Analyzer Pro | Live Market Intelligence", page_icon="◈", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Manrope:wght@400;500;600;700;800&display=swap');
:root { --bg:#080d18; --panel:#101a2b; --line:#24344b; --muted:#8da1bb; --cyan:#36d6c2; --green:#45d49a; --red:#ff7185; }
.stApp { background:radial-gradient(ellipse at 50% -20%,#172a42 0%,#080d18 55%); color:#e8f0fa; font-family:'Manrope',sans-serif; }
[data-testid="stHeader"] { background:transparent; }
[data-testid="stSidebar"] { background:#0b1423; border-right:1px solid var(--line); }
.block-container { padding-top:1.5rem; max-width:1500px; }
h1,h2,h3 { letter-spacing:-.04em; }
.hero { padding:1.2rem 0 1rem; }
.eyebrow { color:var(--cyan); font:500 11px 'DM Mono',monospace; letter-spacing:.18em; text-transform:uppercase; }
.hero-title { font-size:clamp(30px,4vw,48px); font-weight:800; line-height:1.05; margin:.4rem 0; }
.hero-sub { color:var(--muted); font-size:14px; }
.panel { background:linear-gradient(145deg,rgba(19,32,51,.96),rgba(12,22,37,.96)); border:1px solid var(--line); border-radius:15px; padding:17px 19px; min-height:104px; }
.metric-label { color:var(--muted); font-size:11px; text-transform:uppercase; letter-spacing:.12em; }
.metric-value { font:500 27px 'DM Mono',monospace; color:#f2f7ff; margin-top:9px; }
.metric-note { color:var(--muted); font-size:11px; margin-top:3px; }
.section-title { color:#e8f0fa; font-size:17px; font-weight:750; margin:1.2rem 0 .7rem; }
div[data-testid="stMetric"] { background:#101a2b; border:1px solid var(--line); border-radius:13px; padding:14px; }
div[data-testid="stMetricLabel"] { color:#8da1bb; }
.stButton button { border-radius:9px; font-weight:700; }
div[data-testid="stDataFrame"] { border:1px solid var(--line); border-radius:12px; overflow:hidden; }
small, .muted { color:var(--muted); }
footer { visibility:hidden; }
</style>
""", unsafe_allow_html=True)

SYMBOLS = {
    "Volatility 10 Index": "R_10",
    "Volatility 25 Index": "R_25",
    "Volatility 50 Index": "R_50",
    "Volatility 75 Index": "R_75",
    "Volatility 100 Index": "R_100",
    "Volatility 10 (1s) Index": "1HZ10V",
    "Volatility 25 (1s) Index": "1HZ25V",
    "Volatility 50 (1s) Index": "1HZ50V",
    "Volatility 75 (1s) Index": "1HZ75V",
    "Volatility 100 (1s) Index": "1HZ100V",
}

if "analyzer" not in st.session_state:
    st.session_state.analyzer = Analyzer()
if "stream" not in st.session_state:
    st.session_state.stream = None
if "connection_status" not in st.session_state:
    st.session_state.connection_status = "Disconnected"
if "last_quote_text" not in st.session_state:
    st.session_state.last_quote_text = "—"
if "last_epoch" not in st.session_state:
    st.session_state.last_epoch = None
if "selected_symbol" not in st.session_state:
    st.session_state.selected_symbol = "R_25"

with st.sidebar:
    st.markdown("## ◈ ANALYZER PRO")
    st.caption("LIVE MARKET INTELLIGENCE")
    chosen_label = st.selectbox("MARKET", list(SYMBOLS), index=list(SYMBOLS.values()).index(st.session_state.selected_symbol))
    chosen_symbol = SYMBOLS[chosen_label]
    if chosen_symbol != st.session_state.selected_symbol:
        st.session_state.selected_symbol = chosen_symbol
        st.session_state.analyzer = Analyzer()
        st.session_state.last_quote_text = "—"
        if st.session_state.stream:
            st.session_state.stream.set_symbol(chosen_symbol)
    st.divider()
    st.markdown("**STREAM CONTROL**")
    if st.button("Connect to Deriv", use_container_width=True, type="primary", disabled=st.session_state.connection_status in ("Connected", "Reconnecting")):
        app_id = str(st.secrets.get("DERIV_APP_ID", os.getenv("DERIV_APP_ID", "1089")))
        stream = DerivStream(app_id=app_id, symbol=st.session_state.selected_symbol)
        st.session_state.stream = stream
        stream.start()
        st.session_state.connection_status = "Connecting"
        st.rerun()
    if st.button("Disconnect", use_container_width=True, disabled=st.session_state.stream is None):
        st.session_state.stream.stop()
        st.session_state.stream = None
        st.session_state.connection_status = "Disconnected"
        st.rerun()
    st.caption("Public read-only market ticks. No trading or account authorization.")
    st.divider()
    st.markdown("**SESSION**")
    if st.button("Reset analysis", use_container_width=True):
        st.session_state.analyzer.reset()
        st.session_state.last_quote_text = "—"
        st.rerun()
    st.caption("Reset clears collected session statistics, not the market connection.")

st.markdown("""
<div class="hero">
  <div class="eyebrow">DERIV · SYNTHETIC INDICES</div>
  <div class="hero-title">Market intelligence,<br><span style="color:#36d6c2">digit by digit.</span></div>
  <div class="hero-sub">Real-time tick monitoring, frequency analysis and probability modelling.</div>
</div>
""", unsafe_allow_html=True)

status = st.session_state.connection_status
status_color = "#45d49a" if status == "Connected" else "#ffbd69" if status in ("Connecting", "Reconnecting") else "#8da1bb"
st.markdown(f'<div style="font:12px DM Mono,monospace;color:{status_color};margin:0 0 12px">● {status.upper()} &nbsp; / &nbsp; {chosen_label}</div>', unsafe_allow_html=True)

@st.fragment(run_every="1s")
def live_dashboard():
    stream = st.session_state.stream
    analyzer = st.session_state.analyzer
    if stream:
        while True:
            try:
                event = stream.events.get_nowait()
            except Exception:
                break
            if event["type"] == "status":
                st.session_state.connection_status = event["value"]
            elif event["type"] == "error":
                st.session_state.connection_status = "Error"
                st.session_state.last_error = event["value"]
            elif event["type"] == "tick" and event.get("symbol") == st.session_state.selected_symbol:
                analyzer.process_tick(event["quote"], event["digit"])
                st.session_state.last_quote_text = event["quote_text"]
                st.session_state.last_epoch = event.get("epoch")

    c1,c2,c3,c4 = st.columns(4)
    with c1:
        st.metric("LIVE QUOTE", st.session_state.last_quote_text, chosen_symbol)
    with c2:
        st.metric("LAST DIGIT", analyzer.get_current_digit() if analyzer.get_current_digit() >= 0 else "—")
    with c3:
        st.metric("TICKS CAPTURED", f"{analyzer.get_total_ticks():,}")
    with c4:
        st.metric("SESSION RUNTIME", analyzer.get_runtime())

    if hasattr(st.session_state, "last_error"):
        st.warning(st.session_state.last_error)

    left,right = st.columns([1.35,1])
    with left:
        st.markdown('<div class="section-title">Digit frequency</div>', unsafe_allow_html=True)
        freq = analyzer.get_frequency_table()
        df = pd.DataFrame(freq)
        if not df.empty:
            st.bar_chart(df.set_index("digit")[["percent"]], height=230, color="#36d6c2")
            st.dataframe(df.rename(columns={"digit":"Digit","count":"Count","percent":"Frequency %","gap":"Current gap","max_gap":"Max gap","avg_gap":"Average gap"}), use_container_width=True, hide_index=True, height=285)
    with right:
        st.markdown('<div class="section-title">Recent digit stream</div>', unsafe_allow_html=True)
        digits = analyzer.get_last_digits()
        if digits:
            tiles = "".join(f'<span style="display:inline-flex;align-items:center;justify-content:center;width:34px;height:38px;margin:3px;border:1px solid #2b405b;border-radius:8px;background:#14243a;color:#dce9f8;font:500 15px DM Mono">{d}</span>' for d in reversed(digits))
            st.markdown(tiles, unsafe_allow_html=True)
        else:
            st.caption("Waiting for the first tick…")
        st.markdown('<div class="section-title">Session balance</div>', unsafe_allow_html=True)
        parity = analyzer.get_parity_stats()
        ranges = analyzer.get_range_stats()
        st.metric("Even / Odd", f'{parity["even_percent"]:.1f}% / {parity["odd_percent"]:.1f}%')
        st.metric("Low 0–4 / High 5–9", f'{ranges["low_percent"]:.1f}% / {ranges["high_percent"]:.1f}%')

    st.markdown('<div class="section-title">Gap monitor</div>', unsafe_allow_html=True)
    gaps = pd.DataFrame(analyzer.get_gap_table())
    st.dataframe(gaps.rename(columns={"digit":"Digit","gap":"Ticks since last seen","last_seen":"Last seen tick"}), use_container_width=True, hide_index=True)

live_dashboard()

st.markdown('<div class="section-title">Prediction laboratory</div>', unsafe_allow_html=True)
p1,p2,p3,p4 = st.columns([1,1,1,1])
with p1:
    prediction_kind = st.selectbox("Contract type", ["Match","Differs","Over","Under","Odd","Even"], key="prediction_kind")
with p2:
    prediction_target = st.selectbox("Digit / barrier", list(range(10)), index=4, key="prediction_target")
with p3:
    prediction_window = st.selectbox("Sample window", ["session","100","250","500","1000"], key="prediction_window")
with p4:
    prediction_horizon = st.number_input("Horizon (ticks)", min_value=1, max_value=100, value=1)

if st.button("Run analysis", type="primary"):
    target = prediction_target if prediction_kind in ("Match","Differs","Over","Under") else None
    result = st.session_state.analyzer.analyze_prediction(
        prediction_kind, target, prediction_window, int(prediction_horizon)
    )
    st.session_state.prediction_result = result

if "prediction_result" in st.session_state:
    result = st.session_state.prediction_result
    a,b,c,d = st.columns(4)
    a.metric("NEXT-TICK ESTIMATE", f'{result["frequency"]:.2f}%')
    b.metric("HORIZON ESTIMATE", f'{result["horizon_probability"]:.2f}%')
    c.metric("OBSERVED FREQUENCY", f'{result["sample_frequency"]:.2f}%')
    d.metric("BASELINE", f'{result["baseline"]:.0f}%')
    st.info(f'**{result["status"]}** · {result["recommendation"]}')
    st.caption(f'Sample: {result["sample_size"]:,} ticks · Transition context: {result["transition_contexts"]:,} · Predicted digit: {result["predicted_digit"]} ({result["digit_probability"]:.2f}% model probability)')
    st.caption("These are descriptive estimates from recent observations, not reliable forecasts or guarantees. Synthetic-index outcomes remain uncertain.")

st.divider()
st.caption("ANALYZER PRO · Independent analytics interface · Data supplied by Deriv public market feed")
