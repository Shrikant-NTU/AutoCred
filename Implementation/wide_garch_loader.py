import pandas as pd
from typing import Any, Dict, List


def load_wide_timestamp_returns_csv(csv_path: str) -> List[Dict[str, Any]]:
  
    
    df = pd.read_csv(csv_path)

    if df.shape[1] % 2 != 0:
        raise ValueError(
            f"Expected an even number of columns (timestamp/returns pairs), got {df.shape[1]}"
        )

    n_runs = df.shape[1] // 2
    all_runs: List[Dict[str, Any]] = []

    for run_idx in range(n_runs):
        t_col = df.columns[2 * run_idx]
        r_col = df.columns[2 * run_idx + 1]

        # Basic sanity check (helps catch accidental column order issues)
        if "time" not in str(t_col).lower():
            raise ValueError(
                f"Column {2*run_idx} ('{t_col}') does not look like a timestamp column."
            )
        if "return" not in str(r_col).lower():
            raise ValueError(
                f"Column {2*run_idx+1} ('{r_col}') does not look like a returns column."
            )

        # Convert to numeric and drop NaNs consistently (if any)
        t = pd.to_numeric(df[t_col], errors="coerce")
        r = pd.to_numeric(df[r_col], errors="coerce")
        valid = t.notna() & r.notna()

        run_data = {
            # Use 'step' to match your existing framework convention
            "step": t[valid].astype(int).tolist(),
            "returns": r[valid].astype(float).tolist(),
        }

        run_obj = {
            "run_index": run_idx,   # 0-based, matches your framework
            "params": {},           # no params in the CSV (by your requirement)
            "data": run_data,
        }

        all_runs.append(run_obj)

    return all_runs


