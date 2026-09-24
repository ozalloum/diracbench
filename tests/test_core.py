from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import diracbench_svt as db  # noqa: E402


class TestDiracBenchCore(unittest.TestCase):
    def setUp(self) -> None:
        self.parameters = {"S0": -0.60, "V0": 0.20, "U0": 0.0, "R": 5.0, "a": 0.60}

    def test_potentials_are_finite_at_the_origin(self) -> None:
        values = db.pots(np.array([0.0, 1.0e-8, 1.0, 10.0]), self.parameters)
        for value in values:
            self.assertTrue(np.isfinite(value).all())

    def test_four_methods_agree_on_a_targeted_state(self) -> None:
        reference = db.shoot(-1, self.parameters, 0.75, 0.85)
        finite_difference = db.near(db.fd(-1, self.parameters, N=180, sigma=reference)[0], reference)
        chebyshev = db.near(db.cheb(-1, self.parameters, N=40)[0], reference)
        dkb = db.near(db.dkb(-1, self.parameters, n=24)[0], reference)
        for value in (finite_difference, chebyshev, dkb):
            self.assertLess(abs(value - reference), 2.0e-3)

    def test_shooting_wavefunction_is_normalized_and_finite(self) -> None:
        reference = db.shoot(-1, self.parameters, 0.75, 0.85)
        grid = np.linspace(1.0e-3, 20.0, 500)
        grid, large, small = db.shoot_wave(reference, -1, self.parameters, rmax=20.0, grid=grid)
        norm = np.trapezoid(large * large + small * small, grid)
        self.assertAlmostEqual(norm, 1.0, places=3)
        self.assertTrue(np.isfinite(large).all())
        self.assertTrue(np.isfinite(small).all())

    def test_campaign_cli_is_portable_and_non_destructive(self) -> None:
        script = (ROOT / "run_campaign.py").read_text(encoding="utf-8")
        self.assertNotIn("/mnt/data", script)
        self.assertNotIn("shutil.rmtree", script)
        result = subprocess.run(
            [sys.executable, str(ROOT / "run_campaign.py"), "--help"],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("--output", result.stdout)

    def test_error_analysis_artifact_has_required_columns(self) -> None:
        path = ROOT / "data" / "error_analysis.csv"
        self.assertTrue(path.exists())
        header = path.read_text(encoding="utf-8").splitlines()[0]
        for field in ("analysis", "metric", "value", "absolute_error", "relative_error"):
            self.assertIn(field, header)

    def test_release_metadata_is_consistent(self) -> None:
        pyproject = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
        citation = (ROOT / "CITATION.cff").read_text(encoding="utf-8")
        campaign = (ROOT / "run_campaign.py").read_text(encoding="utf-8")
        metadata = (ROOT / "data" / "campaign_metadata.json").read_text(encoding="utf-8")
        self.assertIn('version = "1.0.0"', pyproject)
        self.assertIn("version: 1.0.0", citation)
        self.assertIn("PACKAGE_VERSION = '1.0.0'", campaign)
        self.assertIn('"version": "1.0.0"', metadata)
        self.assertNotIn("version = \"0.", pyproject)
        self.assertNotIn("version: 0.", citation)
        self.assertNotIn("/workspace/", metadata)

    def test_jupyter_notebook_and_publication_plot_contract(self) -> None:
        notebooks = list((ROOT / "notebook").glob("*.ipynb"))
        self.assertTrue(any("Jupyter" in path.name for path in notebooks))
        plotter = (ROOT / "scripts" / "plot_publication_figures.py").read_text(encoding="utf-8")
        self.assertNotIn("set_title", plotter)
        self.assertNotIn("suptitle", plotter)

    def test_publication_figures_are_regenerated(self) -> None:
        required = (
            "fig_diracbench_package_map.pdf",
            "fig_diracbench_workflow.pdf",
            "fig_error_analysis.pdf",
            "fig_method_agreement.pdf",
            "fig_performance.pdf",
            "fig_resolution_convergence.pdf",
            "fig_rmax_independence.pdf",
            "fig_tensor_sweep.pdf",
            "fig_wavefunction_comparison.pdf",
        )
        for filename in required:
            path = ROOT / "figures" / filename
            self.assertTrue(path.exists(), filename)
            self.assertGreater(path.stat().st_size, 1000, filename)


if __name__ == "__main__":
    unittest.main()
