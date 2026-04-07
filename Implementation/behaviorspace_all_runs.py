import csv
from typing import Any, Dict, List


def _coerce(value: str) -> Any:
    if value == "":
        return value
    v = value.strip()
    if v.lower() == "true":
        return True
    if v.lower() == "false":
        return False
    try:
        return int(v)
    except ValueError:
        try:
            return float(v)
        except ValueError:
            return v


def load_behaviorspace_all_runs(csv_path: str) -> List[Dict[str, Any]]:
    """
    Hard-coded loader for NetLogo Wolf–Sheep Predation BehaviorSpace CSV.

    Expected per-run reporter columns (repeated for each run):
    [ [step], count sheep, count wolves, count patches with [pcolor = green] ]
    """
    with open(csv_path, newline="", encoding="utf-8") as f:
        rows = list(csv.reader(f))

    # Find key section markers robustly
    run_number_idx = next(i for i, r in enumerate(rows) if r and r[0] == "[run number]")
    reporter_idx = next(i for i, r in enumerate(rows) if r and r[0] == "[reporter]")
    all_data_idx = next(i for i, r in enumerate(rows) if r and r[0] == "[all run data]")

    reporter_row = rows[reporter_idx]
    num_cols = len(reporter_row)

    # Wolf–Sheep has 4 reporter columns per run in this dataset
    COLS_PER_RUN = 4
    num_runs = (num_cols - 1) // COLS_PER_RUN

    # Parameter rows are between [run number] and [reporter]
    params_rows = rows[run_number_idx + 1 : reporter_idx]

    runs: List[Dict[str, Any]] = []

    for run_index in range(num_runs):
        offset = 1 + COLS_PER_RUN * run_index

        # ---- parameters ----
        params: Dict[str, Any] = {}
        for r in params_rows:
            key = r[0]
            if not key or key.startswith("["):
                continue
            if offset < len(r) and r[offset] != "":
                params[key] = _coerce(r[offset])

        # Helpful metadata (optional, safe)
        params.setdefault("model", "NetLogo Wolf–Sheep Predation")

        # ---- time series ----
        data = {
            "step": [],
            "count_sheep": [],
            "count_wolves": [],
            "count_green_patches": [],
        }

        for row in rows[all_data_idx + 1 :]:
            # Stop when this run's block ends
            if len(row) <= offset or row[offset] == "":
                break

            data["step"].append(_coerce(row[offset]))
            data["count_sheep"].append(_coerce(row[offset + 1]))
            data["count_wolves"].append(_coerce(row[offset + 2]))
            data["count_green_patches"].append(_coerce(row[offset + 3]))

        runs.append(
            {
                "run_index": run_index,
                "params": params,
                "data": data,
            }
        )

    return runs
