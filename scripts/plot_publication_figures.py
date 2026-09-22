"""Create consistent, publication-quality DiracBench figures."""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.patches import Circle, FancyArrowPatch, FancyBboxPatch


COLORS = {
    "Shooting": "#173F5F",
    "Finite difference": "#D1495B",
    "Chebyshev": "#00798C",
    "DKB B-spline": "#EDAE49",
}
METHOD_COLUMNS = {
    "Shooting": "shooting",
    "Finite difference": "finite_difference",
    "Chebyshev": "chebyshev",
    "DKB B-spline": "dkb_bspline",
}
MARKERS = {"Shooting": "o", "Finite difference": "s", "Chebyshev": "^", "DKB B-spline": "D"}


def _style() -> None:
    mpl.rcParams.update(
        {
            "figure.dpi": 120,
            "savefig.dpi": 360,
            "font.family": "DejaVu Sans",
            "font.size": 9.5,
            "axes.titlesize": 10.5,
            "axes.labelsize": 9.5,
            "axes.linewidth": 0.8,
            "lines.linewidth": 1.8,
            "lines.markersize": 5.5,
            "xtick.labelsize": 8.5,
            "ytick.labelsize": 8.5,
            "legend.fontsize": 8.2,
            "mathtext.fontset": "stix",
            "axes.grid": True,
            "grid.linewidth": 0.45,
            "grid.alpha": 0.28,
            "grid.color": "#7A8793",
            "axes.facecolor": "#FBFCFD",
            "figure.facecolor": "white",
            "savefig.facecolor": "white",
        }
    )


def _panel_label(ax, label: str) -> None:
    ax.text(
        -0.14,
        1.04,
        f"({label})",
        transform=ax.transAxes,
        va="bottom",
        ha="left",
        fontsize=10.5,
        fontweight="bold",
        color="#23313D",
        clip_on=False,
    )


def _finish(fig, path: Path) -> None:
    fig.savefig(path.with_suffix(".pdf"), bbox_inches="tight", pad_inches=0.08)
    fig.savefig(path.with_suffix(".png"), dpi=360, bbox_inches="tight", pad_inches=0.08)
    plt.close(fig)


def _method_lines(ax, frame: pd.DataFrame, x: str, xlabel: str, ylabel: str) -> None:
    for label, column in METHOD_COLUMNS.items():
        ax.plot(
            frame[x],
            frame[column],
            color=COLORS[label],
            marker=MARKERS[label],
            label=label,
            markeredgecolor="white",
            markeredgewidth=0.55,
        )
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.legend(ncol=2, frameon=False, loc="best")


def _rounded_box(
    ax,
    center: tuple[float, float],
    width: float,
    height: float,
    title: str,
    body: str,
    face: str,
    edge: str,
    number: str | None = None,
    title_fontsize: float = 8.5,
    body_fontsize: float = 7.2,
    title_offset: float = 0.19,
    body_offset: float = -0.16,
    body_linespacing: float = 1.15,
    title_color: str = "#17212B",
    body_color: str = "#334155",
) -> None:
    """Draw a compact, vector-safe rounded box in axes coordinates."""

    x, y = center
    patch = FancyBboxPatch(
        (x - width / 2, y - height / 2),
        width,
        height,
        boxstyle="round,pad=0.012,rounding_size=0.025",
        transform=ax.transAxes,
        facecolor=face,
        edgecolor=edge,
        linewidth=1.35,
        clip_on=False,
    )
    ax.add_patch(patch)
    ax.text(
        x,
        y + height * title_offset,
        title,
        transform=ax.transAxes,
        ha="center",
        va="center",
        fontsize=title_fontsize,
        fontweight="bold",
        color=title_color,
    )
    ax.text(
        x,
        y + height * body_offset,
        body,
        transform=ax.transAxes,
        ha="center",
        va="center",
        fontsize=body_fontsize,
        linespacing=body_linespacing,
        color=body_color,
    )
    if number is not None:
        circle = Circle(
            (x - width / 2 + 0.035, y + height / 2 - 0.038),
            0.021,
            transform=ax.transAxes,
            facecolor=edge,
            edgecolor="white",
            linewidth=0.7,
            zorder=4,
        )
        ax.add_patch(circle)
        ax.text(
            x - width / 2 + 0.035,
            y + height / 2 - 0.039,
            number,
            transform=ax.transAxes,
            ha="center",
            va="center",
            fontsize=6.8,
            fontweight="bold",
            color="white",
            zorder=5,
        )


def make_workflow_figure(figures: Path) -> None:
    """Make the end-to-end campaign schematic inspired by the reference paper."""

    fig, ax = plt.subplots(figsize=(7.35, 2.35))
    ax.set_axis_off()
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.text(
        0.5,
        0.94,
        "DiracBench reproducibility workflow",
        transform=ax.transAxes,
        ha="center",
        va="center",
        fontsize=11.5,
        fontweight="bold",
        color="#17212B",
    )

    centers = [0.105, 0.303, 0.501, 0.699, 0.897]
    box_width = 0.166
    box_height = 0.43
    y = 0.53
    boxes = [
        ("Input", "$S_0,V_0,U_0$\n$R,a,\\kappa$\ndomain, resolution", "#DBEAFE", "#2563EB"),
        ("Equations", "radial Dirac system\nboundary data\nand units", "#DCFCE7", "#16A34A"),
        ("Four solvers", "shooting • FD\nChebyshev • DKB", "#F3E8FF", "#9333EA"),
        ("Diagnostics", "residuals • nodes\noverlap • domain", "#FFEDD5", "#EA580C"),
        ("Outputs", "CSV/JSON • PDF/PNG\npytest • CAS source", "#E0F2FE", "#0284C7"),
    ]
    for left, right in zip(centers[:-1], centers[1:]):
        arrow = FancyArrowPatch(
            (left + box_width / 2 + 0.006, y),
            (right - box_width / 2 - 0.006, y),
            transform=ax.transAxes,
            arrowstyle="-|>",
            mutation_scale=12,
            linewidth=1.25,
            color="#64748B",
            shrinkA=0,
            shrinkB=0,
            zorder=1,
        )
        ax.add_patch(arrow)
    for index, (center, (title, body, face, edge)) in enumerate(zip(centers, boxes), start=1):
        _rounded_box(ax, (center, y), box_width, box_height, title, body, face, edge, str(index))
    ax.text(
        0.5,
        0.12,
        "one benchmark specification  →  four independent numerical branches  →  auditable release products",
        transform=ax.transAxes,
        ha="center",
        va="center",
        fontsize=8.0,
        color="#475569",
    )
    _finish(fig, figures / "fig_diracbench_workflow")


def make_package_map_figure(figures: Path) -> None:
    """Make a compact map of the release structure for the reproducibility section."""

    fig, ax = plt.subplots(figsize=(7.35, 4.35))
    ax.set_axis_off()
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    _rounded_box(
        ax,
        (0.5, 0.93),
        0.36,
        0.13,
        "DiracBench",
        "reproducibility release",
        "#DCEBFF",
        "#1D4ED8",
        title_fontsize=11.5,
        body_fontsize=9.0,
        title_offset=0.22,
        body_offset=-0.18,
        body_linespacing=1.2,
        title_color="#123B69",
        body_color="#244B6B",
    )

    left = [
        (0.28, 0.74, "src/", "reusable solver module", "#CFE0FF", "#2563EB"),
        (0.28, 0.57, "data/", "CSV + JSON campaign record", "#BDF3E8", "#0F766E"),
        (0.28, 0.37, "tests/", "automated regression checks", "#FFE1C7", "#EA580C"),
        (0.28, 0.19, "docs/", "error definitions and limits", "#C9F4D5", "#16A34A"),
    ]
    right = [
        (0.72, 0.74, "run_campaign.py", "portable regeneration driver", "#E7D6FF", "#9333EA"),
        (0.72, 0.57, "figures/", "vector PDF + review PNG", "#CDEBFF", "#0284C7"),
        (0.72, 0.37, "notebook/", "Colab-ready walkthrough", "#FFEFB0", "#CA8A04"),
        (0.72, 0.19, "latex/", "CAS manuscript source", "#FFD8EA", "#DB2777"),
    ]
    for column in (left, right):
        for index, (x, y, title, body, face, edge) in enumerate(column):
            _rounded_box(
                ax,
                (x, y),
                0.36,
                0.14,
                title,
                body,
                face,
                edge,
                title_fontsize=10.2,
                body_fontsize=8.6,
                title_offset=0.22,
                body_offset=-0.18,
                body_linespacing=1.2,
                title_color=edge,
                body_color="#1E293B",
            )
            if index < len(column) - 1:
                arrow = FancyArrowPatch(
                    (x, y - 0.073),
                    (x, column[index + 1][1] + 0.073),
                    transform=ax.transAxes,
                    arrowstyle="-|>",
                    mutation_scale=12,
                    linewidth=2.0,
                    color="#475569",
                    zorder=1,
                )
                ax.add_patch(arrow)
    patch = FancyBboxPatch(
        (0.14, 0.015),
        0.72,
        0.06,
        boxstyle="round,pad=0.008,rounding_size=0.018",
        transform=ax.transAxes,
        facecolor="#EAF2FF",
        edgecolor="#64748B",
        linewidth=1.35,
        clip_on=False,
    )
    ax.add_patch(patch)
    ax.text(
        0.5,
        0.045,
        "requirements.txt  •  pyproject.toml  •  LICENSE  •  README.md",
        transform=ax.transAxes,
        ha="center",
        va="center",
        fontsize=8.6,
        fontweight="medium",
        color="#1E3A5F",
    )
    _finish(fig, figures / "fig_diracbench_package_map")


def make_publication_figures(root: str | Path) -> None:
    """Regenerate all paper figures from machine-readable campaign outputs."""

    _style()
    root = Path(root)
    data = root / "data"
    figures = root / "figures"
    figures.mkdir(parents=True, exist_ok=True)

    angular = pd.read_csv(data / "four_method_angular_channels.csv")
    parameter_sets = pd.read_csv(data / "four_method_parameter_sets.csv")
    tensor = pd.read_csv(data / "tensor_strength_sweep.csv")
    cutoff = pd.read_csv(data / "rmax_independence.csv")
    convergence = pd.read_csv(data / "resolution_convergence.csv")
    performance = pd.read_csv(data / "performance_benchmark.csv")
    errors = pd.read_csv(data / "error_analysis.csv")
    wave_metrics = pd.read_csv(data / "wavefunction_comparison.csv")
    wave = pd.read_csv(data / "wavefunction_profiles.csv")
    spurious = pd.read_csv(data / "spurious_state_profiles.csv")

    # Four-method agreement: energy levels and direct absolute errors.
    fig, axes = plt.subplots(1, 2, figsize=(7.35, 3.1), gridspec_kw={"wspace": 0.32})
    ax = axes[0]
    x = np.arange(len(angular))
    for label, column in METHOD_COLUMNS.items():
        ax.plot(
            x,
            angular[column],
            color=COLORS[label],
            marker=MARKERS[label],
            label=label,
            markeredgecolor="white",
            markeredgewidth=0.55,
        )
    ax.set_xticks(x, [rf"$\kappa={int(v)}$" for v in angular["kappa"]])
    ax.set_ylabel("Bound-state energy $E/m$")
    ax.set_title("Identified bound-state energies", pad=12)
    ax.legend(frameon=False, ncol=1, loc="lower right", borderaxespad=0.35, labelspacing=0.35)
    _panel_label(ax, "a")
    ax = axes[1]
    for label, column in list(METHOD_COLUMNS.items())[1:]:
        error = np.abs(angular[column] - angular["shooting"])
        ax.semilogy(
            x,
            error,
            color=COLORS[label],
            marker=MARKERS[label],
            label=label,
            markeredgecolor="white",
            markeredgewidth=0.55,
        )
    ax.set_xticks(x, [rf"$\kappa={int(v)}$" for v in angular["kappa"]])
    ax.set_ylabel("Absolute energy error")
    ax.set_title("Absolute error relative to shooting", pad=12)
    ax.legend(frameon=False, loc="best")
    _panel_label(ax, "b")
    fig.suptitle("DiracBench baseline agreement", y=1.02, fontsize=12, fontweight="bold")
    _finish(fig, figures / "fig_method_agreement")

    # Error-analysis dashboard: an annotated map plus convergence and stability views.
    fig, axes = plt.subplots(2, 2, figsize=(7.35, 5.55), gridspec_kw={"hspace": 0.52, "wspace": 0.55})
    ax = axes[0, 0]
    method_order = ["Finite difference", "Chebyshev", "DKB B-spline"]
    method_short = ["FD", "Chebyshev", "DKB"]
    error_rows: list[tuple[str, pd.Series]] = []
    for _, row in angular.iterrows():
        error_rows.append((rf"P1, $\kappa={int(row['kappa'])}$", row))
    for _, row in parameter_sets.iterrows():
        error_rows.append((f"{row['set']} family", row))
    error_matrix = np.array(
        [[abs(float(row[METHOD_COLUMNS[method]]) - float(row["shooting"])) for method in method_order] for _, row in error_rows]
    )
    log_matrix = np.log10(np.maximum(error_matrix, 1.0e-12))
    error_cmap = LinearSegmentedColormap.from_list(
        "diracbench_error",
        ["#1D4ED8", "#0EA5E9", "#FACC15", "#F97316", "#DC2626"],
    )
    im = ax.imshow(log_matrix, aspect="auto", cmap=error_cmap, vmin=-10, vmax=-4, interpolation="nearest")
    ax.set_xticks(np.arange(len(method_short)), method_short)
    ax.set_yticks(np.arange(len(error_rows)), [label for label, _ in error_rows])
    ax.set_xlabel("Independent method")
    ax.set_ylabel("Benchmark state")
    ax.set_title("Energy error map")
    for i in range(error_matrix.shape[0]):
        for j in range(error_matrix.shape[1]):
            text_color = "white" if log_matrix[i, j] < -7.0 or log_matrix[i, j] > -5.0 else "#17212B"
            ax.text(j, i, f"{error_matrix[i, j]:.1e}", ha="center", va="center", fontsize=7.0, color=text_color)
    cbar = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.05)
    cbar.set_label(r"$\log_{10}|E-E_{\mathrm{shoot}}|$", fontsize=8.0)
    cbar.ax.tick_params(labelsize=7.2)
    _panel_label(ax, "a")

    ax = axes[0, 1]
    convergence_labels = {"FD": "Finite difference", "Chebyshev": "Chebyshev", "DKB B-spline": "DKB B-spline"}
    for method, group in convergence.groupby("method", sort=False):
        label = convergence_labels[method]
        group = group.sort_values("resolution")
        ax.loglog(
            group["resolution"],
            group["abs_error"],
            marker=MARKERS[label],
            color=COLORS[label],
            label=label,
        )
    ax.axhline(1.0e-6, color="#64748B", linewidth=0.85, linestyle="--", label=r"$10^{-6}$ guide")
    ax.set_xlabel("Resolution / basis size")
    ax.set_ylabel("Absolute energy error", labelpad=11)
    ax.set_title("Resolution signatures")
    ax.legend(frameon=False, fontsize=7.0, loc="best")
    _panel_label(ax, "b")

    ax = axes[1, 0]
    pairs = wave_metrics["pair"].str.replace(" vs shooting", "", regex=False)
    bars = ax.bar(
        pairs,
        wave_metrics["L2_difference"],
        color=[COLORS["Finite difference"], COLORS["Chebyshev"]],
        width=0.58,
        alpha=0.92,
    )
    ax.set_ylabel("Two-component $L^2$ difference")
    ax.set_title("Wavefunction agreement")
    ax.tick_params(axis="x", rotation=18)
    ax.set_ylim(0, wave_metrics["L2_difference"].max() * 1.42)
    _panel_label(ax, "c")

    ax = axes[1, 1]
    cutoff_errors = errors.loc[errors["analysis"] == "domain"].copy().sort_values("case")
    x_domain = cutoff_errors["case"].astype(float).to_numpy()
    y_domain = np.maximum(cutoff_errors["relative_error"].to_numpy(), 1.0e-16)
    ax.semilogy(x_domain, y_domain, color=COLORS["Shooting"], marker="o", label="shooting")
    ax.axvspan(20, x_domain.max(), color="#16A34A", alpha=0.09, label=r"stable region $r_{\max}\geq20$")
    ax.axhline(1.0e-8, color="#64748B", linewidth=0.85, linestyle="--", label=r"$10^{-8}$ guide")
    ax.set_xlabel(r"Outer domain $r_{\max}$")
    ax.set_ylabel("Relative truncation error")
    ax.set_title("Domain locking")
    ax.legend(frameon=False, fontsize=7.0, loc="best")
    ax.text(0.03, 0.06, "zero shown at $10^{-16}$ floor", transform=ax.transAxes, ha="left", va="bottom", fontsize=6.8, color="#64748B")
    _panel_label(ax, "d")
    fig.suptitle("DiracBench error and convergence dashboard", y=0.995, fontsize=12, fontweight="bold")
    _finish(fig, figures / "fig_error_analysis")

    # Tensor sweep with a translucent method-spread envelope.
    fig, ax = plt.subplots(figsize=(7.0, 3.55))
    _method_lines(ax, tensor, "U0", r"Tensor strength $U_0$", r"Lowest $\kappa=-1$ energy $E$")
    spread = tensor["cross_method_spread"].to_numpy()
    center = tensor["shooting"].to_numpy()
    ax.fill_between(tensor["U0"], center - spread, center + spread, color="#6C757D", alpha=0.12, label="method-spread envelope")
    ax.set_title("Controlled tensor-strength response")
    ax.text(0.99, 0.04, f"max spread = {spread.max():.2e}", transform=ax.transAxes, ha="right", va="bottom", fontsize=8.5, color="#4D5964")
    ax.legend(frameon=False, ncol=1, loc="upper left", borderaxespad=0.25, labelspacing=0.3)
    _finish(fig, figures / "fig_tensor_sweep")

    # Domain independence.
    fig, ax = plt.subplots(figsize=(7.0, 3.55))
    _method_lines(ax, cutoff, "rmax", r"Outer domain $r_{\max}$", r"Lowest $\kappa=-1$ energy $E$")
    ax.set_title("Domain-locking and tail convergence")
    ax.axvspan(20, cutoff["rmax"].max(), color="#2A9D8F", alpha=0.08, label=r"stable region $r_{\max}\geq20$")
    ax.legend(frameon=False, ncol=1, loc="center left", bbox_to_anchor=(0.02, 0.55), borderaxespad=0.25, labelspacing=0.3)
    _finish(fig, figures / "fig_rmax_independence")

    # Resolution convergence.
    fig, ax = plt.subplots(figsize=(7.0, 3.55))
    for method, group in convergence.groupby("method", sort=False):
        label = {"FD": "Finite difference", "Chebyshev": "Chebyshev", "DKB B-spline": "DKB B-spline"}[method]
        ax.loglog(group["resolution"], group["abs_error"], marker=MARKERS[label], color=COLORS[label], label=label)
    ax.set_xlabel("Grid / collocation / basis resolution")
    ax.set_ylabel("Absolute energy error vs shooting")
    ax.set_title("Resolution dependence exposes method-specific convergence")
    ax.legend(frameon=False, ncol=1, loc="lower right", borderaxespad=0.25, labelspacing=0.3)
    _finish(fig, figures / "fig_resolution_convergence")

    # Two-component wavefunction comparison with a lower error panel.
    fig, axes = plt.subplots(2, 1, figsize=(7.0, 5.25), sharex=True, gridspec_kw={"height_ratios": [2.0, 1.0], "hspace": 0.08})
    axes[0].plot(wave["r"], wave["shooting_F"], color=COLORS["Shooting"], label="Shooting $F$")
    axes[0].plot(wave["r"], wave["finite_difference_F"], color=COLORS["Finite difference"], linestyle="--", label="FD $F$")
    axes[0].plot(wave["r"], wave["chebyshev_F"], color=COLORS["Chebyshev"], linestyle=":", label="Chebyshev $F$")
    axes[0].plot(wave["r"], wave["shooting_G"], color=COLORS["Shooting"], alpha=0.42, label="Shooting $G$")
    axes[0].set_ylabel("Normalized radial component")
    axes[0].set_title(r"Phase-aligned spinors for P1, $\kappa=-1$")
    axes[0].legend(frameon=False, ncol=1, loc="upper right", borderaxespad=0.25, labelspacing=0.3)
    axes[0].set_xlim(0, 16)
    axes[1].plot(wave["r"], np.abs(wave["finite_difference_F"] - wave["shooting_F"]), color=COLORS["Finite difference"], label=r"FD $|\Delta F|$")
    axes[1].plot(wave["r"], np.abs(wave["chebyshev_F"] - wave["shooting_F"]), color=COLORS["Chebyshev"], label=r"Chebyshev $|\Delta F|$")
    axes[1].set_xlabel("Radius $r$")
    axes[1].set_ylabel("Absolute difference")
    axes[1].legend(frameon=False, ncol=1, loc="upper right", borderaxespad=0.25, labelspacing=0.3)
    _panel_label(axes[0], "a")
    _panel_label(axes[1], "b")
    _finish(fig, figures / "fig_wavefunction_comparison")

    # Explicit centered-FD spurious-state diagnostic.
    fig, axes = plt.subplots(2, 1, figsize=(7.0, 4.75), sharex=True, gridspec_kw={"height_ratios": [2.0, 1.0], "hspace": 0.08})
    axes[0].plot(spurious["r"], spurious["physical_F"], color=COLORS["Chebyshev"], label="Physical branch")
    axes[0].plot(spurious["r"], spurious["oscillatory_F"], color=COLORS["Finite difference"], alpha=0.78, label="Grid-scale candidate")
    axes[0].set_ylabel("Scaled large component")
    axes[0].set_title("Centered finite differences: physical versus oscillatory branch")
    axes[0].set_xlim(0, 12)
    axes[0].legend(frameon=False, loc="upper right")
    axes[1].plot(spurious["r"], np.abs(np.diff(spurious["oscillatory_F"], prepend=spurious["oscillatory_F"].iloc[0])), color=COLORS["Finite difference"])
    axes[1].set_xlabel("Radius $r$")
    axes[1].set_ylabel("Step-to-step change")
    _panel_label(axes[0], "a")
    _panel_label(axes[1], "b")
    _finish(fig, figures / "fig_fd_spurious_diagnostic")

    # Runtime figure with direct value labels.
    fig, ax = plt.subplots(figsize=(7.0, 3.35))
    labels = performance["method"].replace({"Shooting": "Shooting", "FD": "FD", "Chebyshev": "Chebyshev", "DKB B-spline": "DKB B-spline"})
    colors = [COLORS.get(label, COLORS["Finite difference"]) for label in labels]
    bars = ax.bar(labels, performance["median_runtime_s"], color=colors, alpha=0.92, width=0.62)
    ax.set_ylabel("Median runtime (s)")
    ax.set_title(r"Reference runtime: one targeted P1, $\kappa=-1$ solve")
    ax.tick_params(axis="x", rotation=12)
    for bar, value in zip(bars, performance["median_runtime_s"]):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height(), f"{value:.3f}s", ha="center", va="bottom", fontsize=8)
    _finish(fig, figures / "fig_performance")

    make_workflow_figure(figures)
    make_package_map_figure(figures)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path("."))
    args = parser.parse_args()
    make_publication_figures(args.output)


if __name__ == "__main__":
    main()
