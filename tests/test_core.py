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


if __name__ == "__main__":
    unittest.main()

