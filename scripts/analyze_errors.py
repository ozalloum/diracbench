"""Generate machine-readable error-analysis products for DiracBench.

The analysis deliberately separates three ideas that are often conflated:
energy disagreement between methods, domain/resolution sensitivity, and
wavefunction agreement.  The resulting CSV is intended both for the paper
and for independent inspection by a reviewer.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd


METHODS = ["finite_difference", "chebyshev", "dkb_bspline"]
METHOD_LABELS = {
    "finite_difference": "Finite difference",
    "chebyshev": "Chebyshev",
    "dkb_bspline": "DKB B-spline",
}


def _energy_rows(frame: pd.DataFrame, scope: str, case_column: str) -> list[dict]:
    rows: list[dict] = []
    for record in frame.to_dict(orient="records"):
        reference = float(record["shooting"])
        case = str(record[case_column])
        for method in METHODS:
            value = float(record[method])
            absolute = abs(value - reference)
            relative = absolute / max(abs(reference), np.finfo(float).tiny)
            rows.append(
                {
                    "analysis": "energy",
                    "scope": scope,
                    "case": case,
                    "method": METHOD_LABELS[method],
                    "metric": "relative_error_vs_shooting",
                    "value": value,
                    "reference": "shooting",
                    "reference_value": reference,
                    "absolute_error": absolute,
                    "relative_error": relative,
                }
            )
        spread = float(record["cross_method_spread"])
        rows.append(
            {
                "analysis": "energy",
                "scope": scope,
                "case": case,
                "method": "All methods",
                "metric": "cross_method_spread",
                "value": spread,
                "reference": "max(method energy)-min(method energy)",
                "reference_value": np.nan,
                "absolute_error": spread,
                "relative_error": np.nan,
            }
        )
    return rows


def analyze_error_outputs(root: str | Path) -> dict:
    """Write error-analysis CSV/JSON products and return summary metrics."""

    root = Path(root)
    data = root / "data"
    angular = pd.read_csv(data / "four_method_angular_channels.csv")
    parameter = pd.read_csv(data / "four_method_parameter_sets.csv")
    tensor = pd.read_csv(data / "tensor_strength_sweep.csv")
    wave = pd.read_csv(data / "wavefunction_comparison.csv")
    convergence = pd.read_csv(data / "resolution_convergence.csv")
    cutoff = pd.read_csv(data / "rmax_independence.csv")
    spurious = pd.read_csv(data / "fd_spurious_state_diagnostic.csv")

    rows: list[dict] = []
    rows.extend(_energy_rows(angular, "angular_channels", "kappa"))
    rows.extend(_energy_rows(parameter, "parameter_sets", "set"))
    rows.extend(_energy_rows(tensor, "tensor_strength_sweep", "U0"))

    for record in wave.to_dict(orient="records"):
        rows.append(
            {
                "analysis": "wavefunction",
                "scope": "P1_kappa_minus_1",
                "case": str(record["pair"]),
                "method": str(record["pair"]),
                "metric": "L2_difference",
                "value": float(record["L2_difference"]),
                "reference": "shooting",
                "reference_value": float(record["overlap"]),
                "absolute_error": float(record["L2_difference"]),
                "relative_error": float(1.0 - record["overlap"]),
            }
        )

    reference_energy = float(
        angular.loc[angular["kappa"] == -1, "shooting"].iloc[0]
    )
    for record in convergence.to_dict(orient="records"):
        if record["method"] == "FD":
            method = "Finite difference"
        elif record["method"] == "Chebyshev":
            method = "Chebyshev"
        else:
            method = "DKB B-spline"
        rows.append(
            {
                "analysis": "resolution",
                "scope": "P1_kappa_minus_1",
                "case": str(record["resolution"]),
                "method": method,
                "metric": "absolute_error_vs_shooting",
                "value": float(record["abs_error"]),
                "reference": "shooting",
                "reference_value": reference_energy,
                "absolute_error": float(record["abs_error"]),
                "relative_error": float(record["abs_error"] / abs(reference_energy)),
            }
        )

    cutoff_reference = float(cutoff.loc[cutoff["rmax"] == cutoff["rmax"].max(), "shooting"].iloc[0])
    for record in cutoff.to_dict(orient="records"):
        absolute = abs(float(record["shooting"]) - cutoff_reference)
        rows.append(
            {
                "analysis": "domain",
                "scope": "P1_kappa_minus_1",
                "case": str(record["rmax"]),
                "method": "Shooting",
                "metric": "absolute_error_vs_rmax_35",
                "value": float(record["shooting"]),
                "reference": "shooting at largest rmax",
                "reference_value": cutoff_reference,
                "absolute_error": absolute,
                "relative_error": absolute / abs(cutoff_reference),
            }
        )

    for record in spurious.to_dict(orient="records"):
        rows.append(
            {
                "analysis": "spurious_state",
                "scope": "P1_kappa_minus_1_centered_FD",
                "case": str(record["energy"]),
                "method": "Finite difference",
                "metric": "alternation_fraction",
                "value": float(record["alternation_fraction"]),
                "reference": "zero for smooth physical branch",
                "reference_value": 0.0,
                "absolute_error": float(record["alternation_fraction"]),
                "relative_error": np.nan,
            }
        )

    analysis = pd.DataFrame(rows)
    analysis = analysis[
        [
            "analysis",
            "scope",
            "case",
            "method",
            "metric",
            "value",
            "reference",
            "reference_value",
            "absolute_error",
            "relative_error",
        ]
    ]
    analysis.to_csv(data / "error_analysis.csv", index=False, float_format="%.12g")

    energy_errors = analysis.loc[
        (analysis["analysis"] == "energy")
        & (analysis["metric"] == "relative_error_vs_shooting")
    ]
    spreads = analysis.loc[analysis["metric"] == "cross_method_spread", "value"]
    summary = {
        "max_energy_relative_error": float(energy_errors["relative_error"].max()),
        "max_cross_method_spread": float(spreads.max()),
        "max_wavefunction_L2_difference": float(wave["L2_difference"].max()),
        "minimum_wavefunction_overlap": float(wave["overlap"].min()),
        "maximum_domain_relative_error": float(
            analysis.loc[analysis["analysis"] == "domain", "relative_error"].max()
        ),
        "maximum_fd_alternation_fraction": float(spurious["alternation_fraction"].max()),
    }
    (data / "error_analysis_summary.json").write_text(
        json.dumps(summary, indent=2) + "\n", encoding="utf-8"
    )
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path("."))
    args = parser.parse_args()
    summary = analyze_error_outputs(args.output)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()

