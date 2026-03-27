from __future__ import annotations

from html import escape
from typing import Any, Dict, List

import graphviz
import pandas as pd
import requests
import streamlit as st

try:
    import plotly.express as px
    import plotly.graph_objects as go
    PLOTLY_OK = True
except Exception:
    PLOTLY_OK = False

API_URL_DEFAULT = "http://127.0.0.1:8000"

st.set_page_config(page_title="ASA Research Observatory", page_icon="⚡", layout="wide", initial_sidebar_state="expanded")

st.markdown(
    """
<style>
#MainMenu {visibility:hidden;} footer {visibility:hidden;} header {visibility:hidden; height:0rem;}
.block-container { padding-top: 1.2rem; }
.stApp {
    background:
        radial-gradient(circle at 8% 10%, rgba(78,122,255,0.16), transparent 20%),
        radial-gradient(circle at 92% 8%, rgba(29,209,161,0.12), transparent 18%),
        radial-gradient(circle at 50% 100%, rgba(245,158,11,0.08), transparent 22%),
        linear-gradient(180deg, #071019 0%, #0b1320 42%, #101826 100%);
    color: #e8eef7;
}
.hero,.panel,.kpi {
    background: linear-gradient(180deg, rgba(16,28,45,0.98), rgba(10,18,31,0.98));
    border: 1px solid rgba(115,163,223,0.20);
    border-radius: 18px;
    box-shadow: 0 18px 36px rgba(0,0,0,0.18);
}
.hero {
    padding: 24px 26px;
    margin-bottom: 16px;
    border-radius: 26px;
    position: relative;
    overflow: hidden;
}
.hero::before {
    content: "";
    position: absolute;
    inset: 0;
    background:
        linear-gradient(135deg, rgba(78,122,255,0.10), transparent 38%),
        linear-gradient(315deg, rgba(29,209,161,0.08), transparent 34%);
    pointer-events: none;
}
.kpi {
    padding: 14px;
    min-height: 118px;
    transition: transform 140ms ease, border-color 140ms ease, box-shadow 140ms ease;
}
.kpi:hover {
    transform: translateY(-2px);
    border-color: rgba(134,182,255,0.38);
    box-shadow: 0 22px 42px rgba(0,0,0,0.24);
}
.panel { padding: 16px; margin-bottom: 14px; }
.hero-title { font-size: 2.2rem; font-weight: 900; color: #f7fbff; letter-spacing: -0.02em; }
.hero-kicker,.meta { font-size: 0.78rem; text-transform: uppercase; letter-spacing: 0.10em; color: #8aa4c8; font-weight: 700; }
.note { font-size: 0.94rem; color: #b8c9df; line-height: 1.5; }
.anchor {
    margin-top: 12px; border:1px solid rgba(64,203,184,0.35); border-radius:14px;
    padding: 12px 14px; background: rgba(20,39,56,0.55); color:#dff8f3; font-family: Consolas, monospace;
    backdrop-filter: blur(8px);
}
.badge {
    display:inline-block; border-radius:999px; padding:0.28rem 0.68rem; font-size:0.76rem; font-weight:700;
    margin-right:0.35rem; border:1px solid rgba(255,255,255,0.08);
}
.hero-strip {
    display:flex;
    gap:0.5rem;
    flex-wrap:wrap;
    margin-top:0.9rem;
}
.hero-pill {
    display:inline-block;
    border-radius:999px;
    padding:0.32rem 0.78rem;
    font-size:0.74rem;
    font-weight:700;
    background: rgba(255,255,255,0.06);
    color:#dbe7f7;
    border:1px solid rgba(255,255,255,0.08);
}
.live-ribbon {
    display:flex;
    align-items:center;
    gap:0.7rem;
    margin-top:0.95rem;
    padding:0.72rem 0.92rem;
    border-radius:16px;
    background: linear-gradient(90deg, rgba(20,39,56,0.80), rgba(15,30,48,0.58));
    border:1px solid rgba(96,165,250,0.16);
    overflow:hidden;
    position:relative;
}
.live-ribbon::after {
    content:"";
    position:absolute;
    top:0;
    left:-32%;
    width:32%;
    height:100%;
    background: linear-gradient(90deg, rgba(255,255,255,0.0), rgba(125,211,252,0.18), rgba(255,255,255,0.0));
    animation: live-scan 3.6s linear infinite;
}
.live-dot {
    width:12px;
    height:12px;
    border-radius:999px;
    background:#22d3ee;
    box-shadow: 0 0 0 rgba(34,211,238,0.65);
    animation: live-pulse 1.8s infinite;
    flex:0 0 auto;
}
.live-label {
    font-size:0.73rem;
    font-weight:800;
    letter-spacing:0.12em;
    text-transform:uppercase;
    color:#dff7ff;
    white-space:nowrap;
}
.live-track {
    flex:1;
    height:10px;
    border-radius:999px;
    background: rgba(255,255,255,0.05);
    border:1px solid rgba(255,255,255,0.05);
    position:relative;
    overflow:hidden;
}
.live-bar {
    position:absolute;
    left:-24%;
    top:0;
    width:24%;
    height:100%;
    border-radius:999px;
    background: linear-gradient(90deg, rgba(59,130,246,0.12), rgba(34,211,238,0.95), rgba(96,165,250,0.20));
    box-shadow: 0 0 18px rgba(34,211,238,0.30);
    animation: live-bar 2.8s ease-in-out infinite;
}
.live-meta {
    font-size:0.74rem;
    color:#9ec7da;
    white-space:nowrap;
}
.heat-row { display:flex; gap:8px; flex-wrap:wrap; margin-top:0.55rem; }
.heat-cell {
    min-width:84px;
    border-radius:12px;
    padding:10px 8px;
    text-align:center;
    font-size:0.76rem;
    font-weight:700;
    border:1px solid rgba(255,255,255,0.12);
    color:white;
    box-shadow: inset 0 1px 0 rgba(255,255,255,0.08);
}
.section-title {
    font-size: 1.05rem;
    font-weight: 800;
    color: #f1f6ff;
    margin-bottom: 0.35rem;
}
.snapshot-card {
    background: linear-gradient(180deg, rgba(20,34,54,0.98), rgba(12,22,38,0.98));
    border: 1px solid rgba(122,160,214,0.22);
    border-radius: 20px;
    box-shadow: 0 14px 32px rgba(0,0,0,0.16);
    padding: 16px 16px 14px 16px;
    min-height: 240px;
    margin-bottom: 14px;
}
.snapshot-title {
    font-size: 0.95rem;
    font-weight: 800;
    color: #f5f8ff;
    margin-bottom: 0.55rem;
}
.snapshot-metrics {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 8px;
    margin-top: 0.8rem;
}
.snapshot-metric {
    border-radius: 14px;
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.06);
    padding: 10px 10px 8px 10px;
}
.snapshot-metric-label {
    font-size: 0.66rem;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: #8aa4c8;
    font-weight: 700;
}
.snapshot-metric-value {
    font-size: 1rem;
    color: #f7fbff;
    font-weight: 800;
    margin-top: 4px;
}
.subtle-divider {
    height: 1px;
    border: 0;
    background: linear-gradient(90deg, rgba(122,160,214,0.0), rgba(122,160,214,0.42), rgba(122,160,214,0.0));
    margin: 0.8rem 0 1rem 0;
}
@keyframes live-pulse {
    0% { box-shadow: 0 0 0 0 rgba(34,211,238,0.65); opacity: 1; }
    70% { box-shadow: 0 0 0 12px rgba(34,211,238,0.0); opacity: 0.92; }
    100% { box-shadow: 0 0 0 0 rgba(34,211,238,0.0); opacity: 1; }
}
@keyframes live-bar {
    0% { left: -24%; }
    100% { left: 100%; }
}
@keyframes live-scan {
    0% { left: -32%; }
    100% { left: 100%; }
}
</style>
""",
    unsafe_allow_html=True,
)


def api_get(url: str) -> Dict[str, Any]:
    response = requests.get(url, timeout=20)
    response.raise_for_status()
    return response.json()


def safe_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except Exception:
        return default


def badge(text: str, color: str) -> str:
    return f'<span class="badge" style="background:{color}22;color:{color};border-color:{color}55;">{escape(str(text))}</span>'


def state_color(state: str) -> str:
    return {
        "stable_dialogue": "#2e8b57",
        "drift_risk": "#d94b4b",
        "listening_threshold": "#c8a43d",
        "symbiotic_coherence": "#3f7df6",
        "fragile_coherence": "#8f63d2",
    }.get(state, "#5d6d7e")


def envelope_color(state: str) -> str:
    return {
        "healthy": "#2e8b57",
        "narrowing": "#2563eb",
        "brittle": "#d97706",
        "collapsed": "#d94b4b",
    }.get(state, "#5d6d7e")


def heat_color(value: float) -> str:
    if value >= 0.85:
        return "#7f1d1d"
    if value >= 0.70:
        return "#b91c1c"
    if value >= 0.55:
        return "#d97706"
    if value >= 0.35:
        return "#2563eb"
    return "#1f6f4a"


def fetch_sessions(api_url: str) -> list[dict]:
    try:
        return api_get(f"{api_url}/sessions").get("items", [])
    except Exception:
        return []


def fetch_global_system_summary(api_url: str) -> tuple[dict, str | None]:
    try:
        return api_get(f"{api_url}/global/system-summary"), None
    except Exception as exc:
        return {}, str(exc)


def fetch_global_patterns(api_url: str) -> tuple[dict, str | None]:
    try:
        return api_get(f"{api_url}/global/patterns"), None
    except Exception as exc:
        return {}, str(exc)


def fetch_global_clusters(api_url: str) -> tuple[dict, str | None]:
    try:
        return api_get(f"{api_url}/global/clusters"), None
    except Exception as exc:
        return {}, str(exc)


def fetch_trajectory_similarity(api_url: str) -> tuple[dict, str | None]:
    try:
        return api_get(f"{api_url}/global/trajectory-similarity"), None
    except Exception as exc:
        return {}, str(exc)


def fetch_session_bundle(api_url: str, session_id: str) -> Dict[str, Any]:
    bundle = {"state": {}, "snapshots": [], "turns": [], "anchor_text": ""}
    try:
        bundle["state"] = api_get(f"{api_url}/sessions/{session_id}/state")
        bundle["snapshots"] = api_get(f"{api_url}/sessions/{session_id}/snapshots").get("snapshots", [])
        turns_payload = api_get(f"{api_url}/sessions/{session_id}/turns")
        bundle["turns"] = turns_payload.get("turns", [])
        bundle["anchor_text"] = turns_payload.get("anchor_text", "")
    except Exception:
        pass
    return bundle


def extract_signal_df(snapshots: List[Dict[str, Any]]) -> pd.DataFrame:
    rows = []
    for idx, snap in enumerate(snapshots, start=1):
        rows.append(
            {
                "turn": idx,
                "drift": safe_float(snap.get("drift_score")),
                "threshold": safe_float(snap.get("threshold", {}).get("insistence_coefficient")),
                "coherence": safe_float(snap.get("coherence", {}).get("coherence_score")),
                "complementarity": safe_float(snap.get("complementarity", {}).get("complementarity_score")),
                "sps": safe_float(snap.get("semantic_possibility", {}).get("sps")),
                "cmr": safe_float(snap.get("semantic_possibility", {}).get("cmr")),
            }
        )
    return pd.DataFrame(rows)


def render_kpi(label: str, value: str, note: str) -> None:
    st.markdown(
        f"<div class='kpi'><div class='meta'>{escape(label)}</div><div class='hero-title' style='font-size:1.45rem'>{escape(str(value))}</div><div class='note'>{escape(note)}</div></div>",
        unsafe_allow_html=True,
    )


def render_signal_chart(df: pd.DataFrame) -> None:
    if df.empty:
        st.info("No snapshots yet.")
        return
    if PLOTLY_OK:
        fig = go.Figure()
        for name in ["drift", "threshold", "coherence", "complementarity", "sps", "cmr"]:
            fig.add_trace(go.Scatter(x=df["turn"], y=df[name], mode="lines+markers", name=name.upper()))
        fig.update_layout(height=360, margin=dict(l=10, r=10, t=10, b=10), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.line_chart(df.set_index("turn"), height=360)


def render_heatmap(values: List[float], prefix: str = "T") -> None:
    if not values:
        st.info("No history yet.")
        return
    cells = []
    for idx, value in enumerate(values, start=1):
        color = heat_color(safe_float(value))
        cells.append(f'<div class="heat-cell" style="background:{color};">{prefix}{idx}<br>{safe_float(value):.2f}</div>')
    st.markdown(f'<div class="heat-row">{"".join(cells)}</div>', unsafe_allow_html=True)


def render_envelope_heatmap(snapshots: List[Dict[str, Any]]) -> None:
    if not snapshots:
        st.info("No semantic envelope history yet.")
        return
    cells = []
    for idx, snap in enumerate(snapshots, start=1):
        envelope = snap.get("semantic_possibility", {})
        state_name = envelope.get("semantic_envelope_state", "unknown")
        sps = safe_float(envelope.get("sps"))
        cells.append(f'<div class="heat-cell" style="background:{envelope_color(state_name)};">T{idx}<br>{escape(state_name)}<br>{sps:.2f}</div>')
    st.markdown(f'<div class="heat-row">{"".join(cells)}</div>', unsafe_allow_html=True)


def render_reasoning(latest: Dict[str, Any], state: Dict[str, Any]) -> None:
    if not latest:
        st.info("No latest snapshot.")
        return
    drift_type = latest.get("drift_profile", {}).get("primary_type", "unknown")
    envelope = latest.get("semantic_possibility", {})
    env_state = envelope.get("semantic_envelope_state", "unknown")
    sps = safe_float(envelope.get("sps"))
    cmr = safe_float(envelope.get("cmr"))
    st.markdown(
        f"<div class='panel' style='min-height: 220px;'><div class='meta'>Decision</div>{badge(state.get('state', 'n/a'), state_color(state.get('state', 'n/a')))}{badge(state.get('action', 'n/a'), '#6c7a89')}{badge(env_state, envelope_color(env_state))}<div class='note' style='margin-top:8px'>Drift type: {escape(str(drift_type))}<br>SPS: {sps:.3f} | CMR: {cmr:.3f}<br>Confidence: {safe_float(state.get('confidence')):.2f}<br>Public observability summary for the current trajectory state.</div></div>",
        unsafe_allow_html=True,
    )


def render_snapshot_cards(snapshots: List[Dict[str, Any]], state_payload: Dict[str, Any]) -> None:
    if not snapshots:
        st.info("No decision snapshots yet.")
        return

    rows = [snapshots[idx:idx + 3] for idx in range(0, len(snapshots), 3)]
    for row in rows:
        cols = st.columns(3)
        for col_idx, col in enumerate(cols):
            with col:
                if col_idx >= len(row):
                    st.empty()
                    continue
                snap = row[col_idx]
                turn_no = snapshots.index(snap) + 1
                decision = snap.get("state", {}) or {}
                drift_profile = snap.get("drift_profile", {}) or {}
                threshold = snap.get("threshold", {}) or {}
                coherence = snap.get("coherence", {}) or {}
                envelope = snap.get("semantic_possibility", {}) or {}
                state_name = decision.get("state", "unknown")
                action_name = decision.get("action", "observe")
                drift_type = drift_profile.get("primary_type", "unknown")
                envelope_state = envelope.get("semantic_envelope_state", "unknown")
                metric_cards = [
                    ("Drift", f"{safe_float(snap.get('drift_score')):.2f}"),
                    ("Coherence", f"{safe_float(coherence.get('coherence_score')):.2f}"),
                    ("Threshold", f"{safe_float(threshold.get('insistence_coefficient')):.2f}"),
                    ("SPS / CMR", f"{safe_float(envelope.get('sps')):.2f} / {safe_float(envelope.get('cmr')):.2f}"),
                ]
                metric_html = "".join(
                    f"<div class='snapshot-metric'><div class='snapshot-metric-label'>{escape(label)}</div><div class='snapshot-metric-value'>{escape(value)}</div></div>"
                    for label, value in metric_cards
                )
                st.markdown(
                    f"<div class='snapshot-card'>"
                    f"<div class='meta'>Decision Snapshot</div>"
                    f"<div class='snapshot-title'>Turn T{turn_no}</div>"
                    f"{badge(state_name, state_color(state_name))}{badge(action_name, '#6c7a89')}{badge(envelope_state, envelope_color(envelope_state))}"
                    f"<div class='note' style='margin-top:10px'>Primary drift: <strong>{escape(str(drift_type))}</strong><br>"
                    f"Confidence: <strong>{safe_float(decision.get('confidence')):.2f}</strong></div>"
                    f"<div class='snapshot-metrics'>{metric_html}</div>"
                    f"</div>",
                    unsafe_allow_html=True,
                )


def render_metric_glossary(items: List[tuple[str, str]], title: str = "Metric Glossary") -> None:
    rows = []
    for code, desc in items:
        rows.append(
            f"<div style='margin-bottom:10px;'><span class='badge' style='background:rgba(96,165,250,0.16);color:#93c5fd;border-color:rgba(96,165,250,0.32);'>{escape(code)}</span>"
            f"<span class='note' style='display:block;margin-top:6px'>{escape(desc)}</span></div>"
        )
    st.markdown(
        f"<div class='panel'><div class='meta'>{escape(title)}</div>{''.join(rows)}</div>",
        unsafe_allow_html=True,
    )


def split_glossary_items(items: List[tuple[str, str]]) -> tuple[List[tuple[str, str]], List[tuple[str, str]]]:
    midpoint = (len(items) + 1) // 2
    return items[:midpoint], items[midpoint:]


def trajectory_signature(signal_df: pd.DataFrame) -> str:
    if signal_df.empty:
        return "empty"

    def q(value: float) -> str:
        if value >= 0.75:
            return "H"
        if value >= 0.45:
            return "M"
        return "L"

    d = "".join(q(v) for v in signal_df["drift"].tolist()[:8])
    c = "".join(q(v) for v in signal_df["coherence"].tolist()[:8])
    t = "".join(q(v) for v in signal_df["threshold"].tolist()[:8])
    e = "".join(q(v) for v in signal_df["sps"].tolist()[:8])
    return f"D:{d}|C:{c}|T:{t}|E:{e}"


def cluster_label(latest: Dict[str, Any]) -> str:
    drift = safe_float(latest.get("drift_score"))
    coherence = safe_float(latest.get("coherence", {}).get("coherence_score"))
    threshold = safe_float(latest.get("threshold", {}).get("insistence_coefficient"))
    envelope_state = latest.get("semantic_possibility", {}).get("semantic_envelope_state", "unknown")
    if envelope_state == "collapsed" or drift >= 0.85:
        return "unstable_cluster"
    if threshold >= 0.60:
        return "threshold_cluster"
    if coherence >= 0.72 and envelope_state == "healthy":
        return "symbiotic_cluster"
    if envelope_state in {"narrowing", "brittle"} or coherence >= 0.42:
        return "fragile_cluster"
    return "stable_cluster"


def build_graph(anchor_text: str, turns: List[Dict[str, Any]], snapshots: List[Dict[str, Any]]) -> graphviz.Digraph:
    dot = graphviz.Digraph()
    dot.attr(rankdir="LR", bgcolor="transparent")
    dot.attr("node", shape="box", style="rounded,filled", fontname="Arial", fontsize="10")
    dot.node("anchor", f"ANCHOR\n{escape(anchor_text[:72])}", fillcolor="#1f5b7a", color="#3ab6d0", fontcolor="white")
    previous = "anchor"
    snap_idx = 0
    for turn in turns:
        node_id = f"turn_{turn['turn_index']}"
        label = f"{turn['role'].upper()} #{turn['turn_index']}\n{turn['content'][:54]}"
        fill = "#314157" if turn["role"] == "user" else "#3b4657"
        border = "#23374d"
        if turn["role"] == "assistant" and snap_idx < len(snapshots):
            snap = snapshots[snap_idx]
            state_name = snap.get("state", {}).get("state", "no_analysis_yet")
            env_state = snap.get("semantic_possibility", {}).get("semantic_envelope_state", "unknown")
            label += f"\n[{state_name}]\nENV {env_state}"
            fill = state_color(state_name)
            snap_idx += 1
        dot.node(node_id, label, fillcolor=fill, color=border, fontcolor="white")
        dot.edge(previous, node_id, color="#8ba4c7")
        previous = node_id
    return dot


if "api_url" not in st.session_state:
    st.session_state.api_url = API_URL_DEFAULT
if "session_id" not in st.session_state:
    st.session_state.session_id = "demo_session"
if "anchor_text" not in st.session_state:
    st.session_state.anchor_text = "Maintain semantic stability across the dialogue trajectory."

with st.sidebar:
    st.markdown("## Connection")
    st.session_state.api_url = st.text_input("API Base URL", value=st.session_state.api_url)
    api_online = False
    try:
        api_online = requests.get(f"{st.session_state.api_url}/health", timeout=3).status_code == 200
    except Exception:
        api_online = False
    st.markdown(badge("API online", "#4be28f") if api_online else badge("API offline", "#ff8484"), unsafe_allow_html=True)

    session_items = fetch_sessions(st.session_state.api_url)
    session_ids = [item["session_id"] for item in session_items] or ["demo_session"]
    current_index = session_ids.index(st.session_state.session_id) if st.session_state.session_id in session_ids else 0
    st.session_state.session_id = st.selectbox("Known Sessions", session_ids, index=current_index)
    st.session_state.anchor_text = st.text_area("Anchor Intent", value=st.session_state.anchor_text, height=120)
    module = st.radio("View", ["ASA Overview", "Multi-Session Observatory", "Pattern Detection", "Trajectory Compression", "Session Monitor", "Trajectory Graph", "Audit & Research View"], label_visibility="collapsed")

bundle = fetch_session_bundle(st.session_state.api_url, st.session_state.session_id)
snapshots = bundle["snapshots"]
turns = bundle["turns"]
latest_state = bundle["state"] or {}
anchor_text = bundle["anchor_text"] or st.session_state.anchor_text
signal_df = extract_signal_df(snapshots)
latest = snapshots[-1] if snapshots else {}

drift_value = f"{safe_float(latest.get('drift_score')):.3f}" if latest else "n/a"
threshold_value = f"{safe_float(latest.get('threshold', {}).get('insistence_coefficient')):.3f}" if latest else "n/a"
coherence_value = f"{safe_float(latest.get('coherence', {}).get('coherence_score')):.3f}" if latest else "n/a"
comp_value = f"{safe_float(latest.get('complementarity', {}).get('complementarity_score')):.3f}" if latest else "n/a"
sps_value = f"{safe_float(latest.get('semantic_possibility', {}).get('sps')):.3f}" if latest else "n/a"
cmr_value = f"{safe_float(latest.get('semantic_possibility', {}).get('cmr')):.3f}" if latest else "n/a"
envelope_value = latest.get("semantic_possibility", {}).get("semantic_envelope_state", "n/a") if latest else "n/a"

st.markdown(
    f"<div class='hero'>"
    f"<div class='hero-kicker'>Human-AI stability research | ASA (Asymmetric Stability Architecture) & LTP | Adaptive Semantic Alignment | Drift -&gt; Coherence</div>"
    f"<div class='hero-title'>ASA Research Observatory</div>"
    f"<div class='note'>Public Research Edition. Observability for Human-AI dialogue stability, adaptive semantic alignment, drift lead-time detection, coherence tracking, and semantic envelope analysis.</div>"
    f"<div class='hero-strip'>"
    f"<span class='hero-pill'>Active session: {escape(st.session_state.session_id)}</span>"
    f"<span class='hero-pill'>Envelope: {escape(str(envelope_value))}</span>"
    f"<span class='hero-pill'>Drift: {escape(str(drift_value))}</span>"
    f"<span class='hero-pill'>SPS / CMR: {escape(str(sps_value))} / {escape(str(cmr_value))}</span>"
    f"</div>"
    f"<div class='live-ribbon'>"
    f"<span class='live-dot'></span>"
    f"<span class='live-label'>Live Analysis</span>"
    f"<div class='live-track'><span class='live-bar'></span></div>"
    f"<span class='live-meta'>semantic field active</span>"
    f"</div>"
    f"<div class='note' style='margin-top:10px;font-size:0.82rem;color:#8aa4c8;'>Created by Mieczyslaw Kusowski</div>"
    f"<div class='anchor'><strong>ACTIVE ANCHOR</strong><br>{escape(anchor_text)}</div>"
    f"</div>",
    unsafe_allow_html=True,
)

k1, k2, k3, k4, k5, k6, k7 = st.columns(7)
with k1:
    render_kpi("Drift", drift_value, "Anchor distance")
with k2:
    render_kpi("Threshold", threshold_value, "Insistence coefficient")
with k3:
    render_kpi("Coherence", coherence_value, "Shared-field estimate")
with k4:
    render_kpi("Complementarity", comp_value, "Human-AI balance")
with k5:
    render_kpi("SPS", sps_value, "Semantic possibility span")
with k6:
    render_kpi("CMR", cmr_value, "Counterfactual robustness")
with k7:
    render_kpi("Envelope", envelope_value, "Semantic envelope state")

if module == "ASA Overview":
    st.markdown("<div class='section-title'>Dialogue Trajectory Graph</div>", unsafe_allow_html=True)
    if turns:
        st.graphviz_chart(build_graph(anchor_text, turns, snapshots), use_container_width=True)
    else:
        st.info("No turns available.")
    st.markdown("<hr class='subtle-divider'>", unsafe_allow_html=True)
    left, right = st.columns([1.15, 1.0])
    with left:
        st.markdown("<div class='section-title'>Signal Timeline</div>", unsafe_allow_html=True)
        render_signal_chart(signal_df)
        st.markdown("<hr class='subtle-divider'>", unsafe_allow_html=True)
        heat_left, heat_right = st.columns(2)
        with heat_left:
            st.markdown("<div class='section-title'>Drift Heatmap</div>", unsafe_allow_html=True)
            render_heatmap(signal_df["drift"].tolist() if not signal_df.empty else [])
        with heat_right:
            st.markdown("<div class='section-title'>Semantic Envelope</div>", unsafe_allow_html=True)
            render_envelope_heatmap(snapshots)
    with right:
        st.markdown("<div class='section-title'>Why This Decision</div>", unsafe_allow_html=True)
        render_reasoning(latest, latest_state)
        st.markdown("<hr class='subtle-divider'>", unsafe_allow_html=True)
        st.markdown("<div class='section-title'>Trajectory Turn Table</div>", unsafe_allow_html=True)
        if turns:
            st.dataframe(pd.DataFrame(turns)[["turn_index", "role", "content"]], use_container_width=True, hide_index=True)
        else:
            st.info("No turn evidence available.")

elif module == "Multi-Session Observatory":
    summary_payload, summary_err = fetch_global_system_summary(st.session_state.api_url)
    if summary_err:
        st.warning(f"System summary unavailable: {summary_err}")
    else:
        features = summary_payload.get("features", [])
        clusters = summary_payload.get("clusters", {}).get("clusters", {})
        drift_field = summary_payload.get("drift_field", {})
        patterns = summary_payload.get("patterns", {})
        st.markdown(
            """
            <style>
            div[data-testid="stMetric"] {
                background: linear-gradient(180deg, rgba(18,31,52,0.96), rgba(12,22,38,0.96));
                border: 1px solid rgba(110,149,203,0.24);
                border-radius: 18px;
                padding: 8px 12px;
                box-shadow: 0 14px 32px rgba(0,0,0,0.16);
                min-height: 0;
                margin-bottom: 12px;
            }
            div[data-testid="stMetricLabel"] {
                color: #8aa4c8;
                font-weight: 700;
                text-transform: uppercase;
                letter-spacing: 0.08em;
                font-size: 0.70rem;
            }
            div[data-testid="stMetricValue"] {
                color: #f7fbff;
                font-weight: 800;
                font-size: 1.55rem;
                line-height: 1.1;
            }
            </style>
            """,
            unsafe_allow_html=True,
        )
        a, b, c, d = st.columns(4)
        a.metric("Sessions", summary_payload.get("sessions", 0))
        b.metric("Fragile", int(clusters.get("fragile", {}).get("count", 0)))
        c.metric("Unstable", int(clusters.get("unstable", {}).get("count", 0)))
        d.metric("Mean Drift", f"{pd.DataFrame(features)['avg_drift'].mean():.3f}" if features else "0.000")
        st.markdown("<div class='section-title'>Research Summary</div>", unsafe_allow_html=True)
        if features:
            st.dataframe(pd.DataFrame(features)[["session_id", "latest_state", "stability_class", "dominant_drift_type", "dominant_envelope_state", "avg_drift", "avg_coherence", "avg_sps", "avg_cmr"]], use_container_width=True, hide_index=True)
            st.markdown("<hr class='subtle-divider'>", unsafe_allow_html=True)
            st.markdown("<div class='section-title'>Research Visuals</div>", unsafe_allow_html=True)
            visual_left, visual_right = st.columns([1.25, 1.0])
            feature_df = pd.DataFrame(features)
            with visual_left:
                if PLOTLY_OK and not feature_df.empty:
                    fig_scatter = px.scatter(
                        feature_df,
                        x="avg_drift",
                        y="avg_cmr",
                        size="avg_sps",
                        color="stability_class",
                        hover_name="session_id",
                        color_discrete_map={
                            "stable": "#2e8b57",
                            "fragile": "#2563eb",
                            "unstable": "#d94b4b",
                        },
                        title="Session Stability Field",
                    )
                    fig_scatter.update_traces(marker=dict(line=dict(width=1, color="rgba(255,255,255,0.35)")))
                    fig_scatter.update_layout(
                        height=340,
                        margin=dict(l=10, r=10, t=40, b=10),
                        paper_bgcolor="rgba(0,0,0,0)",
                        plot_bgcolor="rgba(18,29,46,0.35)",
                        xaxis_title="Average Drift",
                        yaxis_title="Average CMR",
                    )
                    st.plotly_chart(fig_scatter, use_container_width=True)
                else:
                    st.dataframe(feature_df[["session_id", "avg_drift", "avg_cmr", "avg_sps"]], use_container_width=True, hide_index=True)
            with visual_right:
                drift_counts = (
                    feature_df["dominant_drift_type"].value_counts().reset_index()
                    if "dominant_drift_type" in feature_df.columns
                    else pd.DataFrame(columns=["index", "dominant_drift_type"])
                )
                if not drift_counts.empty:
                    drift_counts.columns = ["drift_type", "count"]
                if PLOTLY_OK and not drift_counts.empty:
                    fig_drift = px.bar(
                        drift_counts,
                        x="drift_type",
                        y="count",
                        color="drift_type",
                        title="Dominant Drift Signals",
                        color_discrete_sequence=["#60a5fa", "#34d399", "#f59e0b", "#f87171", "#a78bfa", "#22d3ee"],
                    )
                    fig_drift.update_layout(
                        height=340,
                        margin=dict(l=10, r=10, t=40, b=10),
                        paper_bgcolor="rgba(0,0,0,0)",
                        plot_bgcolor="rgba(18,29,46,0.35)",
                        showlegend=False,
                        xaxis_title="Drift Type",
                        yaxis_title="Sessions",
                    )
                    st.plotly_chart(fig_drift, use_container_width=True)
                elif not drift_counts.empty:
                    st.dataframe(drift_counts, use_container_width=True, hide_index=True)
        st.markdown("<hr class='subtle-divider'>", unsafe_allow_html=True)
        st.markdown("<div class='section-title'>Global Drift Map</div>", unsafe_allow_html=True)
        sessions = drift_field.get("sessions", [])
        if sessions:
            heat_df = pd.DataFrame([row["drift"] for row in sessions], index=[row["session_id"] for row in sessions])
            heat_df.columns = [f"T{idx}" for idx in range(1, len(heat_df.columns) + 1)]
            if PLOTLY_OK:
                fig = px.imshow(heat_df, aspect="auto", color_continuous_scale="RdYlGn_r", origin="lower", title="Sessions x Turns Drift Density")
                fig.update_layout(height=420, margin=dict(l=10, r=10, t=40, b=10), paper_bgcolor="rgba(0,0,0,0)")
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.dataframe(heat_df, use_container_width=True)
        st.markdown("<hr class='subtle-divider'>", unsafe_allow_html=True)
        st.markdown("<div class='section-title'>Dominant Envelope States</div>", unsafe_allow_html=True)
        env_counts = patterns.get("dominant_envelope_states", {})
        if env_counts:
            env_df = pd.DataFrame(list(env_counts.items()), columns=["envelope_state", "sessions"])
            if PLOTLY_OK:
                fig_env = px.bar(env_df, x="envelope_state", y="sessions", color="envelope_state", color_discrete_map={"healthy": "#2e8b57", "narrowing": "#2563eb", "brittle": "#d97706", "collapsed": "#d94b4b"}, title="Dominant Envelope Distribution")
                fig_env.update_layout(height=300, margin=dict(l=10, r=10, t=35, b=10), paper_bgcolor="rgba(0,0,0,0)")
                st.plotly_chart(fig_env, use_container_width=True)
            else:
                st.dataframe(env_df, use_container_width=True, hide_index=True)
        st.markdown("<hr class='subtle-divider'>", unsafe_allow_html=True)
        st.markdown("<div class='section-title'>Stability Clusters</div>", unsafe_allow_html=True)
        if clusters:
            cluster_rows = []
            for name, payload in clusters.items():
                count = payload.get("count", 0)
                if count <= 0:
                    continue
                cluster_rows.append({"cluster": name, "count": count, "session_ids": ", ".join(payload.get("session_ids", [])), "avg_drift": payload.get("avg_drift", 0.0), "avg_sps": payload.get("avg_sps", 0.0), "avg_cmr": payload.get("avg_cmr", 0.0)})
            if cluster_rows:
                st.dataframe(pd.DataFrame(cluster_rows), use_container_width=True, hide_index=True)
            else:
                st.info("No populated stability clusters yet.")

elif module == "Pattern Detection":
    payload, err = fetch_global_patterns(st.session_state.api_url)
    if err:
        st.warning(f"Pattern layer unavailable: {err}")
    else:
        rows = []
        for item in payload.get("items", []):
            for pattern in item.get("patterns", []):
                rows.append({"session_id": item.get("session_id"), "stability_class": item.get("stability_class"), "pattern": pattern})
        if rows:
            pattern_df = pd.DataFrame(rows)
            st.markdown("<div class='section-title'>Detected Pattern Events</div>", unsafe_allow_html=True)
            left, right = st.columns([1.15, 1.0])
            with left:
                st.dataframe(pattern_df, use_container_width=True, hide_index=True)
            with right:
                if PLOTLY_OK:
                    fig_pattern_map = px.sunburst(
                        pattern_df,
                        path=["stability_class", "pattern", "session_id"],
                        title="Pattern Topology Map",
                        color="stability_class",
                        color_discrete_map={
                            "stable": "#2e8b57",
                            "fragile": "#2563eb",
                            "unstable": "#d94b4b",
                        },
                    )
                    fig_pattern_map.update_layout(
                        height=380,
                        margin=dict(l=10, r=10, t=40, b=10),
                        paper_bgcolor="rgba(0,0,0,0)",
                    )
                    st.plotly_chart(fig_pattern_map, use_container_width=True)
        freq = payload.get("frequency", {})
        if freq and PLOTLY_OK:
            st.markdown("<hr class='subtle-divider'>", unsafe_allow_html=True)
            st.markdown("<div class='section-title'>Pattern Frequency Distribution</div>", unsafe_allow_html=True)
            fig = px.bar(
                pd.DataFrame(list(freq.items()), columns=["pattern", "count"]),
                x="pattern",
                y="count",
                title="Pattern Event Count",
                color="pattern",
                color_discrete_sequence=["#60a5fa", "#34d399", "#f59e0b", "#f87171", "#a78bfa", "#22d3ee", "#fb7185"],
            )
            fig.update_layout(height=320, margin=dict(l=10, r=10, t=35, b=10), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(18,29,46,0.35)", showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
        dominant_types = payload.get("dominant_drift_types", {})
        if dominant_types:
            st.markdown("<hr class='subtle-divider'>", unsafe_allow_html=True)
            st.markdown("<div class='section-title'>Dominant Drift Type Share</div>", unsafe_allow_html=True)
            drift_df = pd.DataFrame(list(dominant_types.items()), columns=["drift_type", "sessions"])
            glossary_items = [
                ("ICS", "Intent Compression Signal — narrowing of the original human intent space."),
                ("ADS", "Anchor Distance Signal — semantic distance from the original intent anchor."),
                ("CRS", "Correction Recovery Signal — recovery after user correction or clarification."),
                ("NRS", "Narrative Rigidity Signal — how strongly the dialogue reinforces one interpretation path."),
                ("SSR", "Semantic Substitution Risk — replacement of core concepts with nearby but different meaning."),
                ("ILS", "Interpretive Latency Signal — semantic recovery cost after drift begins."),
                ("RSR", "Re-anchor Success Rate — how effectively the dialogue returns to the original intent."),
                ("PFS", "Propagation Fidelity Score — baseline fidelity to the source meaning."),
                ("GDFS", "Graph Drift Fidelity Score — average source drift baseline across propagation nodes."),
                ("GDES", "Graph Divergence Escalation Score — maximum divergence pressure from the source node."),
                ("GLRS", "Graph Local Reinterpretation Score — average local reinterpretation intensity."),
                ("GAS", "Graph Amplification Stress — pressure created when drifting nodes branch further."),
                ("GNS", "Graph Narrative Stress — density of structurally unstable graph nodes."),
            ]
            glossary_left, glossary_right = split_glossary_items(glossary_items)
            left, center, right = st.columns([0.9, 1.2, 0.9])
            with left:
                render_metric_glossary(glossary_left, title="ASA Signals I")
            with center:
                if PLOTLY_OK:
                    fig_drift_types = px.pie(
                        drift_df,
                        names="drift_type",
                        values="sessions",
                        hole=0.55,
                        title="Drift Type Share by Session",
                        color="drift_type",
                        color_discrete_sequence=["#60a5fa", "#34d399", "#f59e0b", "#f87171", "#a78bfa", "#22d3ee"],
                    )
                    fig_drift_types.update_layout(
                        height=340,
                        margin=dict(l=10, r=10, t=40, b=10),
                        paper_bgcolor="rgba(0,0,0,0)",
                    )
                    st.plotly_chart(fig_drift_types, use_container_width=True)
                else:
                    st.dataframe(drift_df, use_container_width=True, hide_index=True)
            with right:
                render_metric_glossary(glossary_right, title="ASA Signals II")

elif module == "Trajectory Compression":
    st.markdown("<div class='section-title'>Trajectory Compression</div>", unsafe_allow_html=True)
    rows = []
    for session_id in session_ids:
        session_bundle = fetch_session_bundle(st.session_state.api_url, session_id)
        session_df = extract_signal_df(session_bundle["snapshots"])
        latest_snapshot = session_bundle["snapshots"][-1] if session_bundle["snapshots"] else {}
        rows.append({"session_id": session_id, "signature": trajectory_signature(session_df), "cluster": cluster_label(latest_snapshot), "final_drift": safe_float(latest_snapshot.get("drift_score")), "final_sps": safe_float(latest_snapshot.get("semantic_possibility", {}).get("sps")), "final_cmr": safe_float(latest_snapshot.get("semantic_possibility", {}).get("cmr"))})
    compression_df = pd.DataFrame(rows)
    top_left, top_right = st.columns([1.0, 1.2])
    with top_left:
        st.markdown("<div class='section-title'>Compressed Session Table</div>", unsafe_allow_html=True)
        st.dataframe(compression_df, use_container_width=True, hide_index=True)
        st.markdown("<hr class='subtle-divider'>", unsafe_allow_html=True)
        render_metric_glossary(
            [
                ("stable_cluster", "Low final drift and low semantic stress. The trajectory remains broadly recoverable."),
                ("fragile_cluster", "Meaning still holds, but under visible tension or narrowing."),
                ("symbiotic_cluster", "Coherent, balanced, and semantically healthy interaction field."),
                ("threshold_cluster", "Trajectory shaped by insistence or threshold pressure rather than pure drift."),
                ("unstable_cluster", "High drift or collapsed envelope at the end of the trajectory."),
            ],
            title="Cluster Glossary",
        )
    with top_right:
        if PLOTLY_OK and not compression_df.empty:
            fig_cluster = px.scatter(
                compression_df,
                x="final_drift",
                y="final_cmr",
                color="cluster",
                size="final_sps",
                hover_name="session_id",
                title="Compressed Trajectory Field",
                color_discrete_map={
                    "stable_cluster": "#2e8b57",
                    "fragile_cluster": "#2563eb",
                    "symbiotic_cluster": "#3f7df6",
                    "threshold_cluster": "#c8a43d",
                    "unstable_cluster": "#d94b4b",
                },
            )
            fig_cluster.update_traces(marker=dict(line=dict(width=1, color="rgba(255,255,255,0.35)")))
            fig_cluster.update_layout(
                height=360,
                margin=dict(l=10, r=10, t=40, b=10),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(18,29,46,0.35)",
                xaxis_title="Final Drift",
                yaxis_title="Final CMR",
            )
            st.plotly_chart(fig_cluster, use_container_width=True)
    if PLOTLY_OK and not compression_df.empty:
        st.markdown("<hr class='subtle-divider'>", unsafe_allow_html=True)
        st.markdown("<div class='section-title'>Compressed Cluster Profile</div>", unsafe_allow_html=True)
        bottom_left, bottom_right = st.columns([1.0, 1.0])
        cluster_share = compression_df["cluster"].value_counts().reset_index()
        cluster_share.columns = ["cluster", "count"]
        with bottom_left:
            fig_share = px.bar(
                cluster_share,
                x="cluster",
                y="count",
                color="cluster",
                title="Cluster Share",
                color_discrete_map={
                    "stable_cluster": "#2e8b57",
                    "fragile_cluster": "#2563eb",
                    "symbiotic_cluster": "#3f7df6",
                    "threshold_cluster": "#c8a43d",
                    "unstable_cluster": "#d94b4b",
                },
            )
            fig_share.update_layout(
                height=300,
                margin=dict(l=10, r=10, t=35, b=10),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(18,29,46,0.35)",
                showlegend=False,
            )
            st.plotly_chart(fig_share, use_container_width=True)
        with bottom_right:
            signature_counts = compression_df["signature"].value_counts().reset_index().head(6)
            signature_counts.columns = ["signature", "count"]
            fig_signature = px.bar(
                signature_counts,
                x="count",
                y="signature",
                orientation="h",
                color="count",
                color_continuous_scale=["#2563eb", "#22d3ee", "#34d399"],
                title="Top Trajectory Signatures",
            )
            fig_signature.update_layout(
                height=300,
                margin=dict(l=10, r=10, t=35, b=10),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(18,29,46,0.35)",
                yaxis_title="Signature",
                xaxis_title="Sessions",
                coloraxis_showscale=False,
            )
            st.plotly_chart(fig_signature, use_container_width=True)
    st.markdown("<div class='note'>This layer compresses full dialogue trajectories into symbolic signatures for cross-session comparison and demo-ready storytelling.</div>", unsafe_allow_html=True)

elif module == "Session Monitor":
    render_signal_chart(signal_df)
    st.markdown("<hr class='subtle-divider'>", unsafe_allow_html=True)
    left, right = st.columns([1.05, 0.95])
    with left:
        st.markdown("<div class='section-title'>Decision Forensics</div>", unsafe_allow_html=True)
        render_reasoning(latest, latest_state)
    with right:
        st.markdown("<div class='section-title'>Session Profile</div>", unsafe_allow_html=True)
        if latest:
            drift_level = "high drift pressure" if safe_float(latest.get("drift_score")) >= 0.75 else "moderate drift pressure"
            envelope_state = latest.get("semantic_possibility", {}).get("semantic_envelope_state", "unknown")
            drift_type = latest.get("drift_profile", {}).get("primary_type", "unknown")
            recoverability = "recoverable" if envelope_state in {"healthy", "narrowing"} else "fragile recovery"
            st.markdown(
                f"<div class='panel' style='min-height: 220px;'>"
                f"<div class='meta'>Session Snapshot</div>"
                f"<div class='note'>"
                f"Primary drift: <strong>{escape(str(drift_type))}</strong><br>"
                f"Envelope state: <strong>{escape(str(envelope_state))}</strong><br>"
                f"Pressure profile: <strong>{escape(drift_level)}</strong><br>"
                f"Recoverability: <strong>{escape(recoverability)}</strong><br>"
                f"Current SPS / CMR: <strong>{safe_float(latest.get('semantic_possibility', {}).get('sps')):.3f} / {safe_float(latest.get('semantic_possibility', {}).get('cmr')):.3f}</strong>"
                f"</div>"
                f"</div>",
                unsafe_allow_html=True,
            )
    st.markdown("<hr class='subtle-divider'>", unsafe_allow_html=True)
    upper_left, upper_right = st.columns([1.0, 1.0])
    with upper_left:
        st.markdown("<div class='section-title'>Envelope Timeline</div>", unsafe_allow_html=True)
        render_envelope_heatmap(snapshots)
    with upper_right:
        st.markdown("<div class='section-title'>State Density</div>", unsafe_allow_html=True)
        if snapshots:
            state_counts = pd.DataFrame([snap.get("state", {}).get("state", "unknown") for snap in snapshots], columns=["state"])
            state_counts = state_counts["state"].value_counts().reset_index()
            state_counts.columns = ["state", "count"]
            if PLOTLY_OK:
                fig_state_profile = px.bar(
                    state_counts,
                    x="state",
                    y="count",
                    color="state",
                    title="State Density",
                    color_discrete_map={
                        "stable_dialogue": "#2e8b57",
                        "fragile_coherence": "#8f63d2",
                        "drift_risk": "#d94b4b",
                        "listening_threshold": "#c8a43d",
                        "symbiotic_coherence": "#3f7df6",
                    },
                )
                fig_state_profile.update_layout(
                    height=250,
                    margin=dict(l=10, r=10, t=35, b=10),
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(18,29,46,0.35)",
                    showlegend=False,
                )
                st.plotly_chart(fig_state_profile, use_container_width=True)
            else:
                st.dataframe(state_counts, use_container_width=True, hide_index=True)

elif module == "Trajectory Graph":
    if turns:
        st.markdown("<div class='section-title'>Trajectory Structure</div>", unsafe_allow_html=True)
        st.graphviz_chart(build_graph(anchor_text, turns, snapshots), use_container_width=True)
        st.markdown("<hr class='subtle-divider'>", unsafe_allow_html=True)
        top_left, top_right = st.columns([0.95, 1.05])
        with top_left:
            st.markdown("<div class='section-title'>Decision Snapshots</div>", unsafe_allow_html=True)
            render_snapshot_cards(snapshots, latest_state)
            st.markdown("<hr class='subtle-divider'>", unsafe_allow_html=True)
            st.markdown("<div class='section-title'>Envelope Heatmap</div>", unsafe_allow_html=True)
            render_envelope_heatmap(snapshots)
        with top_right:
            st.markdown("<div class='section-title'>Final Decision</div>", unsafe_allow_html=True)
            render_reasoning(latest, latest_state)
            st.markdown("<hr class='subtle-divider'>", unsafe_allow_html=True)
            st.markdown("<div class='section-title'>Trajectory Turns</div>", unsafe_allow_html=True)
            st.dataframe(pd.DataFrame(turns)[["turn_index", "role", "content"]], use_container_width=True, hide_index=True)
    else:
        st.info("No turns available yet.")

elif module == "Audit & Research View":
    st.markdown(
        f"<div class='panel'><div class='meta'>Research Snapshot</div><div class='hero-title' style='font-size:1.25rem'>{escape(st.session_state.session_id)}</div><div class='note'>Interpretive summary and public forensic trace for the current Human-AI trajectory.</div></div>",
        unsafe_allow_html=True,
    )
    audit_left, audit_right = st.columns([1.05, 0.95])
    with audit_left:
        st.markdown("<div class='section-title'>Research Summary</div>", unsafe_allow_html=True)
        if latest:
            state_name = latest_state.get("state", latest.get("state", {}).get("state", "unknown"))
            action_name = latest_state.get("action", latest.get("state", {}).get("action", "observe"))
            confidence = safe_float(latest_state.get("confidence", latest.get("state", {}).get("confidence")))
            drift_type = latest.get("drift_profile", {}).get("primary_type", "unknown")
            env_state = latest.get("semantic_possibility", {}).get("semantic_envelope_state", "unknown")
            st.markdown(
                f"<div class='panel'>"
                f"<div class='meta'>Final Interpretation</div>"
                f"{badge(state_name, state_color(state_name))}{badge(action_name, '#6c7a89')}{badge(env_state, envelope_color(env_state))}"
                f"<div class='note' style='margin-top:10px'>"
                f"Confidence: <strong>{confidence:.2f}</strong><br>"
                f"Dominant drift: <strong>{escape(str(drift_type))}</strong><br>"
                f"SPS / CMR: <strong>{safe_float(latest.get('semantic_possibility', {}).get('sps')):.3f} / {safe_float(latest.get('semantic_possibility', {}).get('cmr')):.3f}</strong><br>"
                f"Coherence / Complementarity: <strong>{safe_float(latest.get('coherence', {}).get('coherence_score')):.3f} / {safe_float(latest.get('complementarity', {}).get('complementarity_score')):.3f}</strong>"
                f"</div>"
                f"</div>",
                unsafe_allow_html=True,
            )
            st.markdown(
                "<div class='panel'><div class='note'>This public edition exposes the current interpretive state, trajectory pressure, and core observability layers without revealing internal diagnostic detail.</div></div>",
                unsafe_allow_html=True,
            )
        else:
            st.info("No research snapshot available.")
    with audit_right:
        st.markdown("<div class='section-title'>Forensic Trace</div>", unsafe_allow_html=True)
        if latest:
            forensic_rows = [
                {"layer": "Drift", "signal": "primary_type", "value": latest.get("drift_profile", {}).get("primary_type", "unknown")},
                {"layer": "Envelope", "signal": "state", "value": latest.get("semantic_possibility", {}).get("semantic_envelope_state", "unknown")},
                {"layer": "Envelope", "signal": "SPS / CMR", "value": f"{safe_float(latest.get('semantic_possibility', {}).get('sps')):.3f} / {safe_float(latest.get('semantic_possibility', {}).get('cmr')):.3f}"},
                {"layer": "Threshold", "signal": "insistence", "value": f"{safe_float(latest.get('threshold', {}).get('insistence_coefficient')):.3f}"},
                {"layer": "Coherence", "signal": "score", "value": f"{safe_float(latest.get('coherence', {}).get('coherence_score')):.3f}"},
                {"layer": "Complementarity", "signal": "score", "value": f"{safe_float(latest.get('complementarity', {}).get('complementarity_score')):.3f}"},
            ]
            st.dataframe(pd.DataFrame(forensic_rows), use_container_width=True, hide_index=True)
            st.markdown("<hr class='subtle-divider'>", unsafe_allow_html=True)
            render_reasoning(latest, latest_state)
        else:
            st.info("No forensic payload available.")
    if turns:
        st.dataframe(pd.DataFrame(turns), use_container_width=True, hide_index=True)
