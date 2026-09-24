# DiracBench error analysis

The release reports numerical disagreement and sensitivity in separate
categories. This prevents a small eigenvalue difference from being interpreted
as a complete validation of the corresponding spinor.

## Generated products

Running `python run_campaign.py --output generated_campaign` writes:

- `data/error_analysis.csv`: one row per energy, wavefunction, domain, and
  centered-finite-difference diagnostic;
- `data/error_analysis_summary.json`: aggregate maxima and minima used by the
  manuscript;
- `fig_error_analysis.pdf` and `figures/fig_error_analysis.png`: publication figure summarizing
  the numerical reliability envelope.

## Definitions

For a matrix-method energy (E_i) and the independently obtained two-sided
shooting energy (E_s), the absolute and relative errors are

\[
  \Delta E_i = |E_i-E_s|, \qquad
  \varepsilon_i = \frac{|E_i-E_s|}{|E_s|}.
\]

The cross-method spread is the largest minus the smallest energy among the
four reported methods for one identified state. It is not a statistical
uncertainty; it measures numerical agreement between discretizations.

For common-grid spinors, the global sign is chosen to make the overlap

\[
  O_{ij}=\int(F_iF_j+G_iG_j)\,dr
\]

positive. The reported (L^2) difference is then the norm of the two-component
difference after this phase alignment. The overlap deficit (1-O_{ij}) is
reported alongside it.

The domain error compares the shooting energy at each (r_{\max}) with the
largest tested domain, (r_{\max}=35). It measures finite-domain sensitivity,
not uncertainty in the physical model.

The centered finite-difference alternation fraction is the fraction of adjacent
large-component samples with opposite signs. A value near one, together with a
large node count and disagreement with independent methods, flags the
grid-scale branch documented in the paper.

## Interpretation

The shooting calculation is an independent numerical reference for the smooth
Woods-Saxon benchmarks, not an exact solution. The four-method spread, shooting
cross-check, resolution study, domain study, and wavefunction overlap should be
read together. The DKB refinement curve is intentionally retained even when it
is non-monotonic, and the centered-FD spurious branch is retained as a
diagnostic rather than silently removed.
