# dash_app.py
from datetime import datetime, timedelta, timezone
from pathlib import Path
import pandas as pd
from dash import Dash, dcc, html
import plotly.graph_objects as go

from log_parser import read_latest_in_folder

app = Dash(__name__)

def serve_layout():
    latest_path, df = read_latest_in_folder(Path("data"))
    now = datetime.now(timezone.utc)
    if not df.empty:
        df = df[df["ts"] >= now - timedelta(minutes=10)]
    fig = go.Figure()
    if not df.empty:
        fig.add_trace(go.Scatter(x=df["ts"], y=df["power_kW"], mode="lines"))
    fig.update_layout(title="Power (kW) — last 10 min", height=360)
    return html.Div([
        html.H2("PUR-1 Dashboard (Dash — Starter)"),
        html.Div(f"Source: data/ → {latest_path.name if latest_path else '—'}"),
        dcc.Graph(figure=fig, id="power_chart"),
        dcc.Interval(id="tick", interval=3000, n_intervals=0)
    ])

app.layout = serve_layout

if __name__ == "__main__":
    app.run_server(debug=True)
