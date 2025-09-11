# log_parser.py
from __future__ import annotations
from pathlib import Path
from typing import Optional, Tuple
import pandas as pd

COL_DT = "ts"

def read_csv_safely(path: Path) -> pd.DataFrame:
    """
    Robust CSV reader that tolerates partial writes (skip bad lines).
    """
    try:
        df = pd.read_csv(path)
    except pd.errors.EmptyDataError:
        return pd.DataFrame()
    except Exception:
        # Attempt a more forgiving read
        df = pd.read_csv(path, on_bad_lines="skip", engine="python")
    # Normalize
    if df.empty:
        return df
    if COL_DT in df.columns:
        df[COL_DT] = pd.to_datetime(df[COL_DT], errors="coerce", utc=True)
        df = df.dropna(subset=[COL_DT]).sort_values(COL_DT)
    return df

def read_latest_in_folder(folder: Path, filename_hint: str = ".csv") -> Tuple[Optional[Path], pd.DataFrame]:
    """
    From a folder, pick the newest CSV (by modified time) matching `filename_hint`.
    """
    cands = list(folder.glob(f"*{filename_hint}"))
    if not cands:
        return None, pd.DataFrame()
    latest = max(cands, key=lambda p: p.stat().st_mtime)
    return latest, read_csv_safely(latest)

def within_time_range(df: pd.DataFrame, start=None, end=None) -> pd.DataFrame:
    if df.empty or "ts" not in df.columns:
        return df
    if start is not None:
        df = df[df["ts"] >= pd.to_datetime(start, utc=True)]
    if end is not None:
        df = df[df["ts"] <= pd.to_datetime(end, utc=True)]
    return df.reset_index(drop=True)

def humanize(n: float, unit: str) -> str:
    return f"{n:.2f} {unit}"
