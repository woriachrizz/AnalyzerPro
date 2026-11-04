from __future__ import annotations

import sys
from collections import deque
from datetime import datetime
from pathlib import Path
from queue import Empty

import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.analyzer import Analyzer
from web.deriv_stream import DerivStream

MARKETS = {
    "Volatility 10 Index": "R_10",
    "Volatility 10 (1s) Index": "1HZ10V",
    "Volatility 25 Index": "R_25",
    "Volatility 25 (1s) Index": "1HZ25V",
    "Volatility 50 Index": "R_50",
    "Volatility 50 (1s) Index": "1HZ50V",
    "Volatility 75 Index": "R_75",
    "Volatility 75 (1s) Index": "1HZ75V",
    "Volatility 100 Index": "R_100",
    "Volatility 100 (1s) Index": "1HZ100V",
}
WINDOWS = [25, 50, 100, 250, 500, 1000, "Session"]

st.set_page_config(page_title="Analyzer Pro", page_icon="📊", layout="wide")
st.markdown("""
<style>
.stApp{background:#0b1020;color:#e8edf7}
[data-testid="stSidebar"]{background:#10182b;border-right:1px solid #26334d}
[data-testid="stMetric"]{background:#121d33;border:1px solid #263752;padding:13px;border-radius:12px}
[data-testid="stMetricLabel"]{color:#9aabc7}
.hero{padding:18px 22px;border:1px solid #263752;border-radius:16px;background:linear-gradient(115deg,#142440,#10182b);margin-bottom:18px}
.hero h1{margin:0;color:#f4f7ff}.hero p{color:#9aabc7;margin:6px 0 0}
.digit-strip{display:flex;flex-wrap:wrap;gap:7px;margin:8px 0 14px}
.digit-chip{min-width:34px;text-align:center;padding:8px 10px;border-radius:8px;background:#1a2943;border:1px solid #344866;color:#f4f7ff;font-weight:700}
</style>
""", unsafe_allow_html=True)


def init_state():
    defaults = {
        "analyzer": Analyzer(), "stream": None, "connection_status": "disconnected",
        "connection_message": "Not connected", "ticks": deque(maxlen=500),
        "prediction": None, "last_market": "Volatility 25 Index", "last_precision": 3,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def window_value(value):
    return "session" if value == "Session" else int(value)


def reset_sample(message):
    st.session_state.analyzer.reset()
    st.session_state.ticks.clear()
    st.session_state.prediction = None
    st.session_state.connection_message = message


def drain_events():
    stream = st.session_state.stream
    if stream is None:
        return
    for _ in range(1000):
        try:
            event = stream.events.get_nowait()
        except Empty:
            break
        if event["type"] == "status":
            st.session_state.connection_status = event["status"]
            st.session_state.connection_message = event.get("message", "")
        elif event["type"] == "tick":
            st.session_state.analyzer.process_tick(event["quote"], event["digit"])
            epoch = event.get("epoch")
            stamp = datetime.fromtimestamp(epoch).strftime("%H:%M:%S") if epoch else datetime.now().strftime("%H:%M:%S")
            st.session_state.ticks.append({
                "Time": stamp, "Quote": event["quote_string"],
                "Digit": event["digit"], "Symbol": event.get("symbol") or MARKETS[st.session_state.market_name],
            })


def prediction_report(result):
    st.markdown("---")
    st.subheader("Prediction report")
    st.caption("Historical transition estimate only — not a guarantee or a trading instruction.")
    a, b, c, d = st.columns(4)
    a.metric("Predicted qualifying digit", result["predicted_digit"], f'{result["digit_probability"]:.2f}% estimate')
    b.metric("Next-tick probability", f'{result["frequency"]:.2f}%')
    c.metric("Within horizon", f'{result["horizon_probability"]:.2f}%')
    d.metric("Observed sample rate", f'{result["sample_frequency"]:.2f}%')
    e, f, g = st.columns(3)
    e.metric("Sample size", result["sample_size"])
    f.metric("Transition contexts", result["transition_contexts"])
    g.metric("Baseline", f'{result["baseline"]}%')
    st.write(f'**Outcome:** {result["description"]} · **Status:** {result["status"]}')
    st.write(result["recommendation"])
    st.write(
        f'Forward tracking: {result["prediction_hits"]} hits / {result["prediction_misses"]} misses '
        f'over {result["prediction_total"]} ticks ({result["prediction_hit_percent"]:.2f}% hit rate).'
    )


def overview(window):
    analyzer = st.session_state.analyzer
    pred = analyzer.get_prediction_stats()
    quote = st.session_state.ticks[-1]["Quote"] if st.session_state.ticks else "--"
    digit = analyzer.get_current_digit()
    status = st.session_state.connection_status
    icon = "🟢" if status == "connected" else ("🟠" if status == "reconnecting" else "🔴")
    st.markdown(
        f'<div class="hero"><h1>Analyzer Pro</h1><p>Deriv market intelligence · {st.session_state.market_name} · {icon} {status.title()}</p></div>',
        unsafe_allow_html=True,
    )
    a, b, c, d, e = st.columns(5)
    a.metric("Live quote", quote)
    b.metric("Last digit", "--" if digit < 0 else str(digit))
    c.metric("Ticks collected", f'{analyzer.get_total_ticks():,}')
    d.metric("Session runtime", analyzer.get_runtime())
    e.metric("Prediction hit rate", f'{pred["hit_percent"]:.2f}%' if pred["total"] else "--")

    st.subheader("Live digit stream")
    digits = analyzer.get_last_digits()
    if digits:
        chips = "".join(f'<span class="digit-chip">{n}</span>' for n in digits[-20:])
        st.markdown(f'<div class="digit-strip">{chips}</div>', unsafe_allow_html=True)
    else:
        st.info("Start the market feed to collect ticks.")

    st.subheader("Digit frequency")
    frame = pd.DataFrame(analyzer.get_frequency_table(window)).rename(columns={
        "digit": "Digit", "count": "Count", "percent": "Frequency %",
        "gap": "Current gap", "max_gap": "Maximum gap", "avg_gap": "Average gap",
    })
    left, right = st.columns([1.4, 1])
    with left:
        st.bar_chart(frame.set_index("Digit")[["Frequency %"]], height=280)
    with right:
        st.dataframe(frame, hide_index=True, use_container_width=True, height=310)
    if st.session_state.prediction:
        prediction_report(st.session_state.prediction)


def analysis(window):
    analyzer = st.session_state.analyzer
    st.subheader("Market analysis")
    frame = pd.DataFrame(analyzer.get_frequency_table(window)).rename(columns={
        "digit": "Digit", "count": "Count", "percent": "Frequency %",
        "gap": "Current gap", "max_gap": "Maximum gap", "avg_gap": "Average gap",
    })
    st.dataframe(frame, hide_index=True, use_container_width=True)
    parity = analyzer.get_parity_stats(window)
    ranges = analyzer.get_range_stats(window)
    match = analyzer.get_match_stats()
    a, b, c, d = st.columns(4)
    a.metric("Even digits", f'{parity["even_percent"]:.2f}%', f'{parity["even_count"]} occurrences')
    b.metric("Odd digits", f'{parity["odd_percent"]:.2f}%', f'{parity["odd_count"]} occurrences')
    c.metric("Low (0–4)", f'{ranges["low_percent"]:.2f}%', f'{ranges["low_count"]} occurrences')
    d.metric("High (5–9)", f'{ranges["high_percent"]:.2f}%', f'{ranges["high_count"]} occurrences')
    st.subheader("Repeat / differ analysis")
    a, b, c, d = st.columns(4)
    a.metric("Matches", match["match_count"])
    b.metric("Differs", match["differ_count"])
    c.metric("Current match streak", match["current_match_streak"])
    d.metric("Current differ streak", match["current_differ_streak"])
    st.subheader("Digit gaps")
    gaps = pd.DataFrame(analyzer.get_gap_table())
    gaps["gap"] = gaps["gap"].fillna(0).astype(int)
    st.dataframe(gaps.rename(columns={"digit":"Digit","gap":"Ticks since seen","last_seen":"Last seen tick"}), hide_index=True, use_container_width=True)


def prediction_lab(window):
    analyzer = st.session_state.analyzer
    st.subheader("Prediction lab")
    st.caption("Historical digit transitions estimate probabilities; they do not guarantee future outcomes.")
    kind = st.selectbox("Contract type", ["Odd", "Even", "Match", "Differs", "Over", "Under"], key="contract_kind")
    target_option = st.selectbox("Target digit / barrier", ["Auto", *range(10)], key="contract_target")
    horizon = st.selectbox("Forecast horizon", [1, 5, 10, 25], index=1, format_func=lambda n: f"Next {n} tick(s)", key="contract_horizon")
    if st.button("Analyze & track", type="primary", use_container_width=True):
        target = None if target_option == "Auto" else int(target_option)
        result = analyzer.analyze_prediction(kind, target=target, window=window, horizon=horizon)
        analyzer.set_prediction_target(kind, result["target"], horizon)
        st.session_state.prediction = result
    if st.session_state.prediction:
        old = st.session_state.prediction
        result = analyzer.analyze_prediction(old["kind"], target=old["target"], window=window, horizon=old["horizon"])
        st.session_state.prediction = result
        prediction_report(result)
    else:
        st.info("Collect ticks, then run an analysis to start forward tracking.")


def inspector(window):
    analyzer = st.session_state.analyzer
    st.subheader("Digit inspector")
    digit = st.selectbox("Inspect digit", list(range(10)), key="inspect_digit")
    row = next(x for x in analyzer.get_frequency_table(window) if x["digit"] == digit)
    gap = next(x for x in analyzer.get_gap_table() if x["digit"] == digit)
    ordered = sorted(analyzer.get_frequency_table(window), key=lambda x: x["percent"], reverse=True)
    rank = next(i for i, x in enumerate(ordered, 1) if x["digit"] == digit)
    a, b, c, d = st.columns(4)
    a.metric("Frequency", f'{row["percent"]:.2f}%')
    b.metric("Occurrences", row["count"])
    c.metric("Current gap", row["gap"])
    d.metric("Frequency rank", f"#{rank}")
    st.write(f'Average gap: **{row["avg_gap"]}** ticks · Maximum gap: **{row["max_gap"]}** ticks')
    st.write(f'Last seen at tick: **{gap["last_seen"] if gap["last_seen"] is not None else "Not seen"}**')


def history():
    st.subheader("Recent tick history")
    st.caption("Recent ticks are held in memory for this browser session only.")
    if not st.session_state.ticks:
        st.info("No ticks collected yet.")
    else:
        st.dataframe(pd.DataFrame(list(st.session_state.ticks)).iloc[::-1], hide_index=True, use_container_width=True, height=450)


init_state()
st.sidebar.title("Analyzer Pro")
st.sidebar.caption("Live Deriv market analysis")
market_name = st.sidebar.selectbox("Market", list(MARKETS), index=list(MARKETS).index(st.session_state.last_market), key="market_name")
precision = st.sidebar.selectbox("Tick decimals", [2, 3], index=1, key="precision")
window_choice = st.sidebar.selectbox("History window", WINDOWS, index=2, format_func=str, key="window")
window = window_value(window_choice)

if market_name != st.session_state.last_market:
    reset_sample("Market changed; collecting a fresh sample.")
    st.session_state.last_market = market_name
    if st.session_state.stream:
        st.session_state.stream.set_symbol(MARKETS[market_name])
if precision != st.session_state.last_precision:
    reset_sample("Precision changed; collecting a fresh sample.")
    st.session_state.last_precision = precision
    if st.session_state.stream:
        st.session_state.stream.set_precision(precision)

start, stop = st.sidebar.columns(2)
if start.button("▶ Start", type="primary", use_container_width=True):
    if st.session_state.stream is None:
        st.session_state.stream = DerivStream(precision)
    st.session_state.stream.set_precision(precision)
    st.session_state.stream.start(MARKETS[market_name])
if stop.button("■ Stop", use_container_width=True):
    if st.session_state.stream:
        st.session_state.stream.stop()
        st.session_state.stream = None
    st.session_state.connection_status = "disconnected"
    st.session_state.connection_message = "Stopped by user"

st.sidebar.markdown("---")
st.sidebar.write(f'**Connection:** {st.session_state.connection_status.title()}')
st.sidebar.caption(st.session_state.connection_message)
st.sidebar.caption("Public market data only. No account token is requested.")

@st.fragment(run_every="1s")
def live_views():
    drain_events()
    tabs = st.tabs(["Overview", "Analysis", "Prediction Lab", "Digit Inspector", "Tick History"])
    with tabs[0]:
        overview(window)
    with tabs[1]:
        analysis(window)
    with tabs[2]:
        prediction_lab(window)
    with tabs[3]:
        inspector(window)
    with tabs[4]:
        history()

live_views()
st.caption("Analyzer Pro is an educational market-statistics tool. Estimates are not financial advice or guarantees of future outcomes.")
