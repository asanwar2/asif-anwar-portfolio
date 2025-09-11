# Real-Time Reactor Data Dashboard (Python + Dash/Streamlit)

This project implements a **real-time reactor monitoring dashboard** that visualizes live or simulated log data from a research reactor (PUR-1). The system parses streaming logs (power, temperatures, flow, control rod position, etc.) and displays **time-series plots, color-coded alerts, and historical data** in a user-friendly web interface.

---

## Objective
To design and build an interactive dashboard that:
- **Streams** live or simulated reactor data in real time  
- **Visualizes** power, core/pool temperatures, coolant flow, and rod positions  
- **Implements alerts** for abnormal events (e.g., overpower, loss of flow, rod stuck)  
- **Provides playback** and historical browsing of logged CSV data  

---

## Methods
- **Backend log generator (`simulator.py`)**  
  - Produces CSV logs of reactor variables at regular intervals  
  - Supports scenarios: `power_spike`, `loss_of_flow`, `rod_stuck`, plus scram events  
- **Dashboard (`dash_app.py` or `streamlit_app.py`)**  
  - Reads log file in real time and updates plots dynamically  
  - Displays **line charts** of key parameters vs time  
  - Color-coded alerts when conditions exceed thresholds  
- **Data handling (`log_parser.py`)**  
  - Parses CSV logs into structured time-series for plotting and alerts  

---

## Contents
- `simulator.py` — generates reactor-like log data (CSV)  
- `dash_app.py` — interactive dashboard with live charts (Dash)  
- `streamlit_app.py` — alternative dashboard in Streamlit  
- `log_parser.py` — helper functions for reading/parsing logs  
- `alerting.py` — simple safety checks and alert messages  
- `data/` — folder where CSV logs are written  

---

## File Index

| File Name          | Description                                                     |
|--------------------|-----------------------------------------------------------------|
| `simulator.py`     | Fake reactor plant simulator (CSV logger, scenarios, scram)     |
| `dash_app.py`      | Dashboard app (plots, alerts, historical browsing)              |
| `streamlit_app.py` | Alternative Streamlit dashboard                                 |
| `log_parser.py`    | Reads/parses CSV logs into Python structures for plotting       |
| `alerting.py`      | Checks for abnormal conditions and raises alerts                |
| `data/`            | Contains generated logs (`live_log.csv`)                        |

---

## How to Run

### Environment Setup
```bash
python -m venv .venv
source .venv/bin/activate      # On Windows: .venv\Scripts\activate
pip install dash streamlit numpy pandas matplotlib
```

### Start the Log Simulator
Run the simulator to generate a live CSV log:
```bash
python simulator.py --out data/live_log.csv --interval 1 --scenario power_spike --duration 120
```

- `--interval` sets seconds between samples  
- `--scenario` can be `power_spike`, `loss_of_flow`, `rod_stuck`, or none  
- `--duration` sets total runtime (0 = run forever)  

### Launch the Dashboard
For Dash:
```bash
python dash_app.py
```
Then open your browser at [http://127.0.0.1:8050](http://127.0.0.1:8050).

For Streamlit:
```bash
streamlit run streamlit_app.py
```
Then open the local Streamlit URL shown in terminal.

---

## Example Outputs
- **Line Charts** of power, core temp, pool temp, flow, and rods over time  
- **Alerts** when thresholds are exceeded (e.g., SCRAM triggered, low flow, rod stuck)  
- **Scenario Visualization**:  
  - *Power Spike*: power rises rapidly, SCRAM triggered above 13 kW  
  - *Loss of Flow*: coolant flow decreases, core temp rises  
  - *Rod Stuck*: setpoint increases but rods lag, unstable power  

---

## Why It Matters
- Demonstrates how **real-time data systems** are built for reactors.  
- Shows integration of **simulation + visualization + alerting**.  
- Provides a lightweight tool for **educational demos**, **training**, and **CS–nuclear integration**.  

---

## Extensions / Future Work
- **Database integration** for long-term log storage (SQLite, InfluxDB)  
- **Web deployment** for remote access to the dashboard  
- **Machine learning anomaly detection** on reactor sensor data  
- **3D visualizations** of core and control rod positions  

---

## Tools & Libraries
- Python 3.10+  
- Dash / Plotly  
- Streamlit  
- NumPy  
- Pandas  
- Matplotlib  

