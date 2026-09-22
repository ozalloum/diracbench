# DiracBench

DiracBench is a reproducible four-method framework for bound states of the
spherical radial Dirac equation with scalar, vector, and radial tensor
interactions. It combines adaptive two-sided Runge-Kutta shooting, centered
finite-difference diagonalization, Chebyshev collocation, and a
dual-kinetic-balance B-spline Galerkin method.

The benchmark campaign uses original dimensionless Woods-Saxon parameter
families. Published parameters, energy tables, and wavefunctions are not
copied. The package is intended as a transparent numerical benchmark and
diagnostic framework, not as a production nuclear-structure code.

## Quick start

Python 3.10 or newer is supported.

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
python run_campaign.py --output generated_campaign
```

The campaign accepts an arbitrary output directory. It creates or refreshes
only its known `src/`, `data/`, and `figures/` products and does not delete the
directory or unrelated files. To regenerate the included products in place, use
`python run_campaign.py --output .`.

The reusable solver can also be installed as a Python module:

```bash
python -m pip install -e .
python -c "import diracbench_svt; print(diracbench_svt.__name__)"
```

## Numerical campaign

The package includes:

- three original Woods-Saxon parameter families;
- four independent numerical methods;
- angular-channel and tensor-strength sweeps;
- domain-size and resolution studies;
- phase-aligned wavefunction comparisons;
- centered-finite-difference spurious-state diagnostics;
- runtime measurements;
- publication-quality PDF/PNG figures, including an annotated error/convergence dashboard, workflow schematic, and archive-structure map;
- machine-readable CSV tables and JSON metadata;
- a Colab-ready notebook and the LaTeX manuscript source.
- the supplied Elsevier CAS class/style files and a compiled PDF render.

The independent methods agree to the few-parts-in-
`10^5` level for the reported smooth benchmark states. The package retains two
important limitations explicitly: centered finite differences exhibit a
grid-scale oscillatory branch, and the DKB B-spline refinement is not strictly
monotonic on every tested basis sequence.

## Error analysis

`data/error_analysis.csv` separates energy error relative to two-sided
shooting, cross-method spread, wavefunction L2 difference and overlap,
outer-domain sensitivity, and the finite-difference alternation diagnostic.
`data/error_analysis_summary.json` contains the aggregate extrema. The
definitions and interpretation are documented in
[`docs/ERROR_ANALYSIS.md`](docs/ERROR_ANALYSIS.md).

## Reproducibility layout

```text
src/diracbench_svt.py       reusable numerical methods
run_campaign.py             portable campaign driver
scripts/                    error analysis and figure generation
tests/                      automated regression tests
data/                       CSV outputs and JSON metadata
figures/                    publication PDF/PNG figures
notebook/                   Google Colab notebook
latex/                      CAS source, class files, and compiled PDF
docs/ERROR_ANALYSIS.md      metric definitions and interpretation
```

The campaign driver no longer uses a hard-coded `/mnt/data` directory, does
not remove an existing output tree, and does not reconstruct the reusable
solver by slicing its own source code.

## Scope and limitations

The smooth benchmark campaign is dimensionless and uses finite Woods-Saxon
fields. It is not a fit to a specific nucleus. The centered finite-difference
method is retained as a reproducible counterexample because it can generate
grid-scale spurious states. DKB basis refinement remains a development target;
its non-monotonic behavior is reported rather than hidden. The singular
point-Coulomb DKB case is not used to support the smooth-potential claims.

## License

DiracBench is distributed under the MIT License. See `LICENSE`.
