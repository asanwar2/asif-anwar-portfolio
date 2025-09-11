# alerting.py
from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Any

@dataclass
class Thresholds:
    power_warn: float = 11.5
    power_crit: float = 12.2
    coreT_warn: float = 50.0
    coreT_crit: float = 60.0
    poolT_warn: float = 35.0
    poolT_crit: float = 40.0
    flow_warn: float = 5.0
    flow_crit: float = 3.0
    rod_warn: float  = 90.0   # effective with high power
    rod_crit: float  = 95.0

def classify(value: float, warn: float, crit: float, reverse: bool = False) -> str:
    """
    Returns one of: 'OK', 'WARN', 'CRIT'.
    If reverse=True, thresholds are reversed (e.g., flow where lower is worse).
    """
    if value is None:
        return "OK"
    if reverse:
        if value <= crit: return "CRIT"
        if value <= warn: return "WARN"
        return "OK"
    else:
        if value >= crit: return "CRIT"
        if value >= warn: return "WARN"
        return "OK"

def rollup_status(parts):
    if "CRIT" in parts: return "CRIT"
    if "WARN" in parts: return "WARN"
    return "OK"

def evaluate_row(row: Dict[str, Any], th: Thresholds = Thresholds()) -> Dict[str, str]:
    power = float(row.get("power_kW", 0.0))
    coreT = float(row.get("core_temp_C", 0.0))
    poolT = float(row.get("pool_temp_C", 0.0))
    flow  = float(row.get("flow_lps", 0.0))
    rods  = float(row.get("rod_bank_pct", 0.0))
    scram = int(row.get("scram", 0))

    s_power = classify(power, th.power_warn, th.power_crit, reverse=False)
    s_coreT = classify(coreT, th.coreT_warn, th.coreT_crit, reverse=False)
    s_poolT = classify(poolT, th.poolT_warn, th.poolT_crit, reverse=False)
    s_flow  = classify(flow, th.flow_warn,  th.flow_crit,  reverse=True)

    # Rods rules couple to power
    s_rods = "OK"
    if power >= 11.0 and rods >= th.rod_crit:
        s_rods = "CRIT"
    elif power >= 10.0 and rods >= th.rod_warn:
        s_rods = "WARN"

    parts = [s_power, s_coreT, s_poolT, s_flow, s_rods]
    if scram:
        parts.append("CRIT")

    return {
        "power": s_power,
        "core_temp": s_coreT,
        "pool_temp": s_poolT,
        "flow": s_flow,
        "rods": s_rods,
        "overall": "CRIT" if "CRIT" in parts else ("WARN" if "WARN" in parts else "OK"),
    }
