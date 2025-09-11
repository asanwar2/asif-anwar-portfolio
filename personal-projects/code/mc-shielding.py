# simulator.py
import csv, time, math, random, argparse
from datetime import datetime, timezone, timedelta
from pathlib import Path

COLUMNS = ["ts","power_kW","core_temp_C","pool_temp_C","flow_lps","rod_bank_pct","scram","msg"]

def bounded(val, lo, hi):
    return max(lo, min(hi, val))

def simulate_step(state, dt_s, scenario=None, t_elapsed_s=0.0):
    """
    Very simple dynamics:
    - Power tends toward setpoint with a small random walk
    - Core temp follows power and flow with lag
    - Pool temp drifts slowly
    - Flow mostly constant unless 'loss_of_flow' scenario
    - Rod bank tracks setpoint; may stick in 'rod_stuck'
    """
    sp = state["p_sp"]  # kW setpoint
    p  = state["power_kW"]
    flow = state["flow_lps"]
    rods = state["rod_bank_pct"]
    coreT = state["core_temp_C"]
    poolT = state["pool_temp_C"]
    scram = 0
    msg   = "normal"

    # Scenario scheduling windows
    if scenario == "power_spike":
        # Inject spike 20s–50s, then revert
        if 20 <= t_elapsed_s < 50:
            sp = 13.5
            msg = "scenario: power_spike"
        else:
            sp = 7.0 if t_elapsed_s < 15 else 10.0

    elif scenario == "loss_of_flow":
        if 25 <= t_elapsed_s < 80:
            flow = max(0.5, state["flow_lps"] * 0.98)  # bleed flow
            msg = "scenario: loss_of_flow"
        else:
            # recover
            flow = min(12.0, state["flow_lps"] + 0.1)

    elif scenario == "rod_stuck":
        if 15 <= t_elapsed_s < 120:
            # setpoint rises but rods lag (stickiness)
            sp = 10.5
            rods = min(99.0, rods + 0.05)  # creep upward
            msg = "scenario: rod_stuck"
        else:
            sp = 9.0
            rods = max(5.0, rods - 0.2)

    # Power dynamics toward setpoint + noise
    tau_p = 6.0
    p += (sp - p) * (dt_s / tau_p) + random.gauss(0, 0.03)
    p = bounded(p, 0.0, 14.0)

    # Rods loosely track power demand (unless set by scenario)
    if scenario != "rod_stuck":
        rods += (min(100.0, max(0.0, p * 8.5)) - rods) * 0.05 + random.gauss(0, 0.05)
    rods = bounded(rods, 0.0, 100.0)

    # Flow relaxes toward nominal unless scenario altered it
    if scenario != "loss_of_flow":
        flow += (10.0 - flow) * 0.05 + random.gauss(0, 0.03)
    flow = bounded(flow, 0.0, 15.0)

    # Temps: core increases with power/flow; pool is slow reservoir
    coreT += (22.0 + 2.8 * p - 0.8 * flow - coreT) * 0.06 + random.gauss(0, 0.05)
    poolT += (22.0 + 0.15 * p - poolT) * 0.005 + random.gauss(0, 0.01)
    coreT = bounded(coreT, 15.0, 95.0)
    poolT = bounded(poolT, 15.0, 60.0)

    # Simple scram logic if way over nominal
    if p >= 13.0:
        scram = 1
        p = 0.8 * p  # drop quickly
        msg = "SCRAM (overpower)"
        rods = min(100.0, rods + 5.0)

    state.update(dict(
        p_sp=sp, power_kW=p, flow_lps=flow, rod_bank_pct=rods,
        core_temp_C=coreT, pool_temp_C=poolT
    ))
    return state, msg, scram

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=Path("data/live_log.csv"))
    ap.add_argument("--interval", type=float, default=1.0, help="seconds between samples")
    ap.add_argument("--seed", type=int, default=None)
    ap.add_argument("--scenario", type=str, default=None, choices=[None,"power_spike","loss_of_flow","rod_stuck"])
    ap.add_argument("--duration", type=float, default=0.0, help="stop after N seconds (0=run forever)")
    args = ap.parse_args()

    if args.seed is not None:
        random.seed(args.seed)

    args.out.parent.mkdir(parents=True, exist_ok=True)
    write_header = not args.out.exists()

    state = dict(
        p_sp=9.0,
        power_kW=8.5,
        core_temp_C=28.0,
        pool_temp_C=24.0,
        flow_lps=10.0,
        rod_bank_pct=40.0,
    )

    t0 = time.time()
    next_t = t0
    elapsed = 0.0

    with args.out.open("a", newline="") as f:
        w = csv.writer(f)
        if write_header:
            w.writerow(COLUMNS)

        while True:
            now = time.time()
            if now < next_t:
                time.sleep(max(0.0, next_t - now))
                continue

            dt = args.interval
            elapsed = now - t0
            state, msg, scram = simulate_step(state, dt, args.scenario, elapsed)

            row = [
                datetime.now(timezone.utc).isoformat(),
                round(state["power_kW"], 3),
                round(state["core_temp_C"], 3),
                round(state["pool_temp_C"], 3),
                round(state["flow_lps"], 3),
                round(state["rod_bank_pct"], 2),
                scram,
                msg,
            ]
            w.writerow(row)
            f.flush()

            if args.duration and elapsed >= args.duration:
                break

            next_t = now + args.interval

if __name__ == "__main__":
    main()
