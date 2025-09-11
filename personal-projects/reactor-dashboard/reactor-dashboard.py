# simulator.py
# ------------------------------------------------------------
# Simple reactor-like data generator (for dashboards/demos).
# Think of it as a fake reactor that writes a CSV log
# every N seconds with power, temperatures, flow, and rods.
# It also has a few optional scenarios to make the data
# do interesting things such as power spike, loss of flow, rod stuck.
# ------------------------------------------------------------

import csv, time, math, random, argparse
from datetime import datetime, timezone, timedelta
from pathlib import Path

# CSV column order (header row)
COLUMNS = ["ts","power_kW","core_temp_C","pool_temp_C","flow_lps","rod_bank_pct","scram","msg"]

def bounded(val, lo, hi):
    """
    Keep 'val' within [lo, hi]. If it goes below lo, return lo.
    If it goes above hi, return hi. Otherwise return val.
    """
    return max(lo, min(hi, val))

def simulate_step(state, dt_s, scenario=None, t_elapsed_s=0.0):
    """
    Move the plant state forward by one time step (dt_s seconds).

    This is a *very* simple "toy" model just to produce realistic-looking trends:
      - Power (kW) moves slowly toward a setpoint, plus a little random noise.
      - Core temperature follows power and flow (more power -> hotter; more flow -> cooler).
      - Pool temperature drifts slowly (big water tank, so changes are small).
      - Flow stays near a nominal value unless a scenario alters it.
      - Rod bank (%) roughly tracks power demand (unless "rod_stuck" scenario).
      - If power gets too high, trigger a SCRAM (simple safety trip).

    Parameters
    ----------
    state : dict
        The current values for p_sp (setpoint), power_kW, core_temp_C,
        pool_temp_C, flow_lps, rod_bank_pct.
    dt_s : float
        Time step in seconds.
    scenario : str or None
        Optional special behavior: "power_spike", "loss_of_flow", "rod_stuck", or None.
    t_elapsed_s : float
        How many seconds since the simulation started. Used to time scenarios.

    Returns
    -------
    state : dict
        Updated state after one step.
    msg : str
        Human-friendly note about what happened this step.
    scram : int
        1 if a trip happened this step, else 0.
    """
    # shorthand
    sp = state["p_sp"]            # power setpoint (kW)
    p  = state["power_kW"]        # current power (kW)
    flow = state["flow_lps"]      # coolant flow (liters per second)
    rods = state["rod_bank_pct"]  # control rods position (%)
    coreT = state["core_temp_C"]  # core temperature (°C)
    poolT = state["pool_temp_C"]  # pool temperature (°C)
    scram = 0                     # 0 = normal, 1 = tripped
    msg   = "normal"              # note for the log

    # ------------------------------
    # Scenario scheduling (time windows)
    # This is where we temporarily change setpoints/values to
    # create realistic-looking events in the data.
    # ------------------------------
    if scenario == "power_spike":
        # From 20s to 50s, push setpoint high, before/after keep it lower.
        if 20 <= t_elapsed_s < 50:
            sp = 13.5
            msg = "scenario: power_spike"
        else:
            sp = 7.0 if t_elapsed_s < 15 else 10.0

    elif scenario == "loss_of_flow":
        # Between 25s and 80s, slowly reduce flow; then recover.
        if 25 <= t_elapsed_s < 80:
            flow = max(0.5, state["flow_lps"] * 0.98)  # small bleed every step
            msg = "scenario: loss_of_flow"
        else:
            flow = min(12.0, state["flow_lps"] + 0.1)  # ramp back up

    elif scenario == "rod_stuck":
        # From 15s to 120s, raise setpoint but let rods move very slowly (sticky).
        if 15 <= t_elapsed_s < 120:
            sp = 10.5
            rods = min(99.0, rods + 0.05)  # tiny creep upward
            msg = "scenario: rod_stuck"
        else:
            sp = 9.0
            rods = max(5.0, rods - 0.2)    # relax back down

    # ------------------------------
    # 1) Power dynamics:
    # Move power towards setpoint with a time constant (tau_p) + small noise.
    # ------------------------------
    tau_p = 6.0  # seconds (how quickly power moves toward setpoint)
    p += (sp - p) * (dt_s / tau_p) + random.gauss(0, 0.03)
    p = bounded(p, 0.0, 14.0)  # cap at [0, 14] kW (toy TRIGA-like numbers)

    # ------------------------------
    # 2) Rods track commanded power (unless scenario overrides above).
    # Here "p * 8.5" is just a rough map from kW to %.
    # ------------------------------
    if scenario != "rod_stuck":
        rods += (min(100.0, max(0.0, p * 8.5)) - rods) * 0.05 + random.gauss(0, 0.05)
    rods = bounded(rods, 0.0, 100.0)

    # ------------------------------
    # 3) Flow returns toward nominal unless the scenario changed it.
    # ------------------------------
    if scenario != "loss_of_flow":
        flow += (10.0 - flow) * 0.05 + random.gauss(0, 0.03)
    flow = bounded(flow, 0.0, 15.0)

    # ------------------------------
    # 4) Temperatures:
    # Core temp goes up with power and down with flow; pool changes slowly.
    # Numbers are tuned to "look right", not to be physically exact.
    # ------------------------------
    coreT += (22.0 + 2.8 * p - 0.8 * flow - coreT) * 0.06 + random.gauss(0, 0.05)
    poolT += (22.0 + 0.15 * p - poolT) * 0.005 + random.gauss(0, 0.01)
    coreT = bounded(coreT, 15.0, 95.0)
    poolT = bounded(poolT, 15.0, 60.0)

    # ------------------------------
    # 5) Simple trip (SCRAM) rule:
    # If power is very high, we trip and force power downward fast.
    # ------------------------------
    if p >= 13.0:
        scram = 1
        p = 0.8 * p  # drop power quickly after trip
        msg = "SCRAM (overpower)"
        rods = min(100.0, rods + 5.0)  # rods insert further

    # Save values back into the state dict
    state.update(dict(
        p_sp=sp, power_kW=p, flow_lps=flow, rod_bank_pct=rods,
        core_temp_C=coreT, pool_temp_C=poolT
    ))
    return state, msg, scram

def main():
    """
    Command-line entry point. Creates/updates a CSV file that logs the
    simulated values every --interval seconds until you stop it (Ctrl+C)
    or until --duration seconds have passed.
    """
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=Path("data/live_log.csv"),
                    help="Path to CSV file to write (will be created if missing)")
    ap.add_argument("--interval", type=float, default=1.0,
                    help="Seconds between samples (e.g., 0.5, 1, 2...)")
    ap.add_argument("--seed", type=int, default=None,
                    help="Random seed for reproducible runs (optional)")
    ap.add_argument("--scenario", type=str, default=None,
                    choices=[None,"power_spike","loss_of_flow","rod_stuck"],
                    help="Optional behavior to make the data 'interesting'")
    ap.add_argument("--duration", type=float, default=0.0,
                    help="Stop after N seconds (0 = run forever)")
    args = ap.parse_args()

    # Fix random numbers if seed is given (useful for testing or demos)
    if args.seed is not None:
        random.seed(args.seed)

    # Make sure the output folder exists; check if we need to write header row
    args.out.parent.mkdir(parents=True, exist_ok=True)
    write_header = not args.out.exists()

    # Initial "plant" state (picked to be reasonable starting values)
    state = dict(
        p_sp=9.0,            # power setpoint (kW)
        power_kW=8.5,        # current power (kW)
        core_temp_C=28.0,    # core temp (°C)
        pool_temp_C=24.0,    # pool temp (°C)
        flow_lps=10.0,       # flow (liters/second)
        rod_bank_pct=40.0,   # rod position (%)
    )

    t0 = time.time()  # when we started
    next_t = t0       # next sample time
    elapsed = 0.0     # seconds since start

    # Open the CSV once and keep appending rows
    with args.out.open("a", newline="") as f:
        w = csv.writer(f)
        if write_header:
            w.writerow(COLUMNS)

        # Main loop: run until stopped or until --duration is reached
        while True:
            now = time.time()
            # Sleep a little if we arrived early (keeps steady interval)
            if now < next_t:
                time.sleep(max(0.0, next_t - now))
                continue

            dt = args.interval
            elapsed = now - t0

            # Advance the state by one step
            state, msg, scram = simulate_step(state, dt, args.scenario, elapsed)

            # Build one CSV row with the new values
            row = [
                datetime.now(timezone.utc).isoformat(), # timestamp in UTC
                round(state["power_kW"], 3),
                round(state["core_temp_C"], 3),
                round(state["pool_temp_C"], 3),
                round(state["flow_lps"], 3),
                round(state["rod_bank_pct"], 2),
                scram,  # 0 or 1
                msg,    # text description for humans
            ]
            w.writerow(row)
            f.flush()  # make sure it's written to disk

            # Stop if we hit the requested duration (if provided)
            if args.duration and elapsed >= args.duration:
                break

            # Schedule next sample time
            next_t = now + args.interval

if __name__ == "__main__":
    main()
