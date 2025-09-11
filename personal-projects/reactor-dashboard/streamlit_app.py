# streamlit_app.py
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from pathlib import Path
from datetime import datetime, timedelta, timezone

from log_parser import read_latest_in_folder
from alerting import evaluate_row, Thresholds

st.set_page_config(page_title="PUR-1 Reactor Dashboard (Demo)", layout="wide")

# ------------- Sidebar Controls -------------
st.sidebar.header("Data Source")
mode = st.sidebar.radio("Mode", ["Simulated Live (in-app)", "CSV Folder"])

refresh = st.sidebar.slider("Refresh every (s)", 1, 10, 3, help="Auto-refresh interval")
history_min = st.sidebar.slider("History window (minutes)", 1, 60, 10)

if mode == "CSV Folder":
    folder = st.sidebar.text_input("Folder path", "data")
else:
    folder = None

st.sidebar.markdown("---")
st.sidebar.header("Accident Scenarios (Simulated)")
scenario = st.sidebar.selectbox("Inject scenario", ["none", "power_spike", "loss_of_flow", "rod_stuck"])

st.sidebar.markdown("---")
st.sidebar.caption("This dashboard is for demo/educational use only — not a safety system.")

# ------------- Data Acquisition -------------
def simulate_data(minutes=10, scenario="none"):
    import random, math
    cols = ["ts","power_kW","core_temp_C","pool_temp_C","flow_lps","rod_bank_pct","scram","msg"]
    t0 = datetime.now(timezone.utc) - timedelta(minutes=minutes)
    p, coreT, poolT, flow, rods = 8.5, 28.0, 24.0, 10.0, 40.0
    out = []
    for i in range(minutes * 60):
        t = t0 + timedelta(seconds=i)
        sp = 9.0
        msg = "normal"
        if scenario == "power_spike" and 60 < i < 120:
            sp = 13.5; msg = "scenario: power_spike"
        elif scenario == "loss_of_flow" and 80 < i < 200:
            flow = max(0.5, flow * 0.995); msg = "scenario: loss_of_flow"
        elif scenario == "rod_stuck" and 40 < i < 300:
            rods = min(99.0, rods + 0.03); sp = 10.5; msg = "scenario: rod_stuck"
        else:
            flow += (10.0 - flow) * 0.02

        p += (sp - p) * 0.12 + random.gauss(0, 0.02)
        rods += (min(100.0, max(0.0, p * 8.5)) - rods) * 0.02 + random.gauss(0, 0.03)
        coreT += (22.0 + 2.8 * p - 0.8 * flow - coreT) * 0.04 + random.gauss(0, 0.03)
        poolT += (22.0 + 0.12 * p - poolT) * 0.003 + random.gauss(0, 0.01)

        scram = 1 if p >= 13.0 else 0
        if scram:
            p *= 0.8; rods = min(100.0, rods + 2.0); msg = "SCRAM (overpower)"

        out.append([t.isoformat(), p, coreT, poolT, flow, rods, scram, msg])

    df = pd.DataFrame(out, columns=cols)
    df["ts"] = pd.to_datetime(df["ts"], utc=True)
    return df

if mode == "CSV Folder":
    latest_path, df_raw = read_latest_in_folder(Path(folder))
    src_desc = f"Folder: `{folder}`" + (f" → `{latest_path.name}`" if latest_path else " (no CSV found)")
else:
    df_raw = simulate_data(minutes=max(3, history_min), scenario=(scenario if scenario!="none" else None))
    src_desc = f"Simulated (scenario = {scenario})"

# Filter to recent window for live view
now = datetime.now(timezone.utc)
df = df_raw.copy()
if not df.empty:
    df = df[df["ts"] >= now - timedelta(minutes=history_min)].reset_index(drop=True)

# ------------- Header / KPIs / Status -------------
st.title("Real-Time Reactor Data Dashboard — PUR-1 (Demo)")
st.caption(src_desc)

if df.empty:
    st.warning("No data available yet. If using CSV mode, point to a folder with a live CSV (e.g., `data/live_log.csv`). If using simulation, wait a moment for samples to populate.")
    st.stop()

latest = df.iloc[-1].to_dict()
status = evaluate_row(latest, Thresholds())

def status_chip(label, value, unit, state):
    color = {"OK":"#16a34a","WARN":"#f59e0b","CRIT":"#ef4444"}[state]
    st.markdown(f"""
    <div style="border-radius: 14px; padding: 12px; background: #0b1020; border: 1px solid rgba(255,255,255,.08)">
      <div style="display:flex; align-items:center; gap:10px;">
        <div style="width:10px;height:10px;border-radius:50%;background:{color}"></div>
        <div style="font-size:0.9rem;opacity:.8">{label}</div>
      </div>
      <div style="font-size:1.6rem;font-weight:700;margin-top:6px">{value} <span style="font-size:0.9rem;opacity:.7">{unit}</span></div>
      <div style="font-size:0.8rem;opacity:.7;margin-top:6px">{state}</div>
    </div>
    """, unsafe_allow_html=True)

c1, c2, c3, c4, c5 = st.columns(5)
with c1: status_chip("Power", f"{latest['power_kW']:.2f}", "kW", status["power"])
with c2: status_chip("Core Temp", f"{latest['core_temp_C']:.1f}", "°C", status["core_temp"])
with c3: status_chip("Pool Temp", f"{latest['pool_temp_C']:.1f}", "°C", status["pool_temp"])
with c4: status_chip("Flow", f"{latest['flow_lps']:.2f}", "L/s", status["flow"])
with c5: status_chip("Rod Bank", f"{latest['rod_bank_pct']:.1f}", "%", status["rods"])

# Overall banner
overall_color = {"OK":"#052e16","WARN":"#451a03","CRIT":"#3b0d0d"}[status["overall"]]
overall_text = {"OK":"All systems nominal", "WARN":"Attention required", "CRIT":"Critical condition"}[status["overall"]]
st.markdown(f"""
<div style="margin-top:8px;border-radius:16px;padding:14px 16px;background:{overall_color};border:1px solid rgba(255,255,255,.15)">
  <strong>System Status:</strong> {overall_text} — latest @ {pd.to_datetime(latest['ts']).strftime('%H:%M:%S UTC')}
</div>
""", unsafe_allow_html=True)

# ------------- Charts -------------
def add_threshold_band(fig, y_warn, y_crit, name):
    fig.add_hrect(y0=y_warn, y1=y_crit, fillcolor="orange", opacity=0.08, line_width=0, annotation_text=f"{name} WARN", annotation_position="top left")
    fig.add_hrect(y0=y_crit, y1=max(df[name].max(), y_crit), fillcolor="red", opacity=0.08, line_width=0, annotation_text=f"{name} CRIT", annotation_position="top left")

tab1, tab2 = st.tabs(["Live Trends", "Alert Log / Table"])

with tab1:
    th = Thresholds()
    # Power
    fig_p = go.Figure()
    fig_p.add_trace(go.Scatter(x=df["ts"], y=df["power_kW"], mode="lines", name="Power (kW)"))
    add_threshold_band(fig_p, th.power_warn, th.power_crit, "power_kW")
    fig_p.update_layout(title="Power vs Time", xaxis_title="Time (UTC)", yaxis_title="kW", height=320, margin=dict(l=20,r=20,t=40,b=20))
    st.plotly_chart(fig_p, use_container_width=True)

    # Temperatures
    fig_t = go.Figure()
    fig_t.add_trace(go.Scatter(x=df["ts"], y=df["core_temp_C"], mode="lines", name="Core Temp (°C)"))
    fig_t.add_trace(go.Scatter(x=df["ts"], y=df["pool_temp_C"], mode="lines", name="Pool Temp (°C)"))
    fig_t.add_hrect(y0=th.coreT_warn, y1=th.coreT_crit, fillcolor="orange", opacity=0.06, line_width=0)
    fig_t.add_hrect(y0=th.coreT_crit, y1=max(df["core_temp_C"].max(), th.coreT_crit), fillcolor="red", opacity=0.06, line_width=0)
    fig_t.update_layout(title="Temperatures vs Time", xaxis_title="Time (UTC)", yaxis_title="°C", height=320, margin=dict(l=20,r=20,t=40,b=20))
    st.plotly_chart(fig_t, use_container_width=True)

    # Flow & Rods
    fig_fr = go.Figure()
    fig_fr.add_trace(go.Scatter(x=df["ts"], y=df["flow_lps"], mode="lines", name="Flow (L/s)"))
    fig_fr.add_trace(go.Scatter(x=df["ts"], y=df["rod_bank_pct"], mode="lines", name="Rod Bank (%)", yaxis="y2"))
    fig_fr.update_layout(title="Flow & Rod Bank vs Time", xaxis_title="Time (UTC)",
                         yaxis=dict(title="Flow (L/s)"),
                         yaxis2=dict(title="Rod Bank (%)", overlaying="y", side="right"),
                         height=320, margin=dict(l=20,r=20,t=40,b=20))
    st.plotly_chart(fig_fr, use_container_width=True)

with tab2:
    # Compute per-row status for table
    df_tbl = df.copy()
    sts = df_tbl.apply(lambda r: evaluate_row(r.to_dict()), axis=1, result_type="expand")
    df_tbl = pd.concat([df_tbl, sts], axis=1)
    st.dataframe(df_tbl.tail(200), use_container_width=True, height=420)

# Footer / Help
st.markdown("---")
st.markdown("""
**How to use:**  
- For truly live data, run `python simulator.py --out data/live_log.csv` in another terminal (or point the CSV mode to a log your lab writes).  
- Use the **Accident Scenarios** dropdown to see how alerting responds.  
- Adjust the **history window** for a tighter or broader view.
""")
