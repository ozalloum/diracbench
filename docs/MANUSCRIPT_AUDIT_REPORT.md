# Manuscript audit and revision record

This report records the structured audit of the DiracBench submission package.
It is an audit trail for the author and
is not intended to replace the manuscript, the source archive, or the journal
submission metadata.

## 1. Materials inventory and evidence limits

| Item | Evidence used | Disposition |
|---|---|---|
| CAS manuscript source | `manuscript/DiracBench_CPC_Manuscript.tex` and bundled CAS class/style files | Revised and compiled |
| Compiled manuscript | `manuscript/DiracBench_CPC_Manuscript.pdf` | Rebuilt from the revised source |
| Numerical source | `src/diracbench_svt.py`, `run_campaign.py` | Preserved and audited |
| Campaign outputs | `data/*.csv`, `data/*.json` | Regenerated |
| Publication figures | `figures/` PDF and PNG products | Regenerated and visually inspected |
| Figure scripts | `scripts/analyze_errors.py`, `scripts/plot_publication_figures.py` | Revised and tested |
| Tests | `tests/test_core.py` | Expanded to 8 passing tests |
| Jupyter notebook | `notebook/DiracBench_Original_SVT_Jupyter.ipynb` | Renamed and retained |
| Metadata | `pyproject.toml`, `requirements.txt`, `CITATION.cff`, `LICENSE` | Normalized |
| Review specification | Structured manuscript and reproducibility audit | Applied as the audit specification |

The archive contained a current manuscript together with a duplicate
versioned software tree, an older manuscript PDF, and stale machine-specific
campaign metadata. The current manuscript and verified campaign products were
therefore consolidated into one clean root layout. No claim is made here about
hardware-independent runtime, an independent clean-room reproduction on
another operating system, or a future archival DOI.

## 2. Classification and activated audit modules

DiracBench is classified as a computational-physics software and numerical
benchmark paper with a reproducibility package. The activated modules were:

1. materials inventory and evidence limits;
2. numerical-method and algorithm audit;
3. validation and error analysis;
4. software quality, dependency, and portability audit;
5. figure and caption audit;
6. reference and DOI audit;
7. CPC-specific submission audit;
8. simulated editorial and peer review;
9. final build, test, and visual verification.

The paper is not framed as a new physical interaction model. Its contribution
is a reproducible cross-method benchmark and diagnostic framework.

## 3. Stage 1 diagnostic audit

The main pre-revision risks were:

- duplicate manuscript and software layers in the supplied archive;
- stale release metadata and a machine-specific output path;
- a campaign driver whose behavior was not explicit about output preservation;
- a test command that was not portable under standard `unittest` discovery;
- ordinary plot titles that competed with the manuscript captions;
- inconsistent figure layout and legend placement;
- five references without DOI links;
- missing explicit declarations;
- a stale future-release statement for the staggered-grid work.

The principal strengths were already substantial: four independent numerical
routes, machine-readable outputs, an explicit finite-difference spurious-state
diagnostic, a domain-lock study, wavefunction comparisons, a portable driver,
and automated tests.

## 4. Executive publication diagnosis

**Pre-revision diagnosis:** promising but not submission-clean because the
archive and metadata were not a single reproducible release.

**Post-revision readiness score:** 90/100.

**Verdict:** technically submit-ready after the author completes the
author-controlled checks in Section 29. The remaining items are portal
metadata, author confirmation, and optional independent-environment
reproduction rather than unresolved compilation or figure blockers.

## 5. Section-by-section audit

| Manuscript component | Result | Action |
|---|---|---|
| Title and highlights | Clear numerical/software identity | Shortened title to avoid layout pressure |
| Abstract | Quantitative and limitation-aware | Removed release-process lead-in and retained measured results |
| Program summary | CPC-compatible software description | Kept repository link and clarified post-acceptance library record |
| Introduction | Motivates spurious states and cross-method checking | Retained CPC and relativistic-method context |
| Formulation | Defines common conventions and operators | Preserved |
| Algorithms | Five algorithms are described | Preserved and checked against code structure |
| Validation | Residual, normalization, overlap, nodes, and domain tests | Preserved and cross-linked to outputs |
| Numerical results | Four-method tables and sweeps | Regenerated from the campaign |
| Error analysis | Dedicated CSV/JSON product and dashboard | Retained and made central |
| Reproducibility | Driver, dependencies, tests, notebook, figures | Rewritten for portability and Jupyter naming |
| Limitations | FD artifact and DKB non-monotonic refinement | Strengthened and kept explicit |
| Declarations | Funding, conflicts, data/code, and tool statement | Added |
| Data and code availability | Public repository and release are named | DOI promise removed |
| References | 36 records, including CPC, related methods, and one complementary quantum-simulation study | DOI links made clickable |

## 6. Core scientific audit

The scientific narrative now distinguishes:

- agreement for the tested smooth dimensionless Woods--Saxon benchmarks;
- a centered-finite-difference branch that deliberately exposes a grid-scale
  oscillatory candidate;
- a DKB B-spline branch that reaches few-parts-in-\(10^6\) accuracy on the
  tested smooth cases but is not uniformly monotone under basis refinement;
- validation evidence from energies, residuals, nodes, overlaps, and domain
  variation.

The manuscript does not generalize these results to singular Coulomb fields,
all potentials, all angular channels, or production nuclear-structure
calculations.

## 7. Novelty assessment

The strongest defensible novelty statement is methodological and
reproducibility-focused:

> DiracBench supplies an independently parameterized scalar--vector--tensor
> benchmark campaign in which four numerically distinct radial Dirac solvers
> are evaluated with shared energy, wavefunction, node, residual, domain, and
> spurious-state diagnostics, and the complete evidence chain is released as
> machine-readable data and regenerable figures.

The paper does not claim to introduce DKB, finite differences, Chebyshev
collocation, or shooting as new algorithms.

## 8. Major claim verification

| Claim | Evidence in package | Status |
|---|---|---|
| Four methods are implemented | `run_campaign.py`, `src/diracbench_svt.py`, Algorithms 1--5 | Supported |
| P1 angular-channel spread is at most \(1.22\times10^{-5}\) | `data/four_method_angular_channels.csv` | Supported |
| Tensor sweep spread is at most \(8.39\times10^{-6}\) | `data/tensor_strength_sweep.csv` | Supported |
| Domain sensitivity is below \(10^{-7}\) after locking | `data/rmax_independence.csv` | Supported for the tested setup |
| FD and Chebyshev overlaps are 0.999990 and 0.999514 | `data/wavefunction_comparison.csv` | Supported |
| FD exposes a grid-scale oscillatory candidate | `data/fd_spurious_state_diagnostic.csv`, Figure 8 | Supported |
| DKB refinement is not uniformly monotone | `data/resolution_convergence.csv`, Figure 6 | Supported |
| The release is portable | relative output path, `--output`, no destructive cleanup | Supported by code audit; author should repeat on a clean machine |

## 9. Specialized numerical and software findings

### Numerical methods

The four branches share benchmark definitions but retain separate
discretization logic. The DKB branch is presented as a prototype/benchmark
route, not as a universal production solver. The centered FD branch is kept
because its failure mode is scientifically informative.

### Validation

The package reports energy differences relative to shooting, pairwise spreads,
wavefunction \(L^2\) differences and overlaps, domain variation, residual and
node diagnostics, and the FD alternation fraction.

### Software

Dependencies are declared in both `requirements.txt` and
`pyproject.toml`. The campaign driver accepts an arbitrary output
directory, preserves unrelated files, records relative output provenance, and
exposes `--help`.

### Reproducibility

The Jupyter notebook is also Colab-compatible. The repository and the public
release are recorded in the manuscript, README, and citation metadata. No
pre-acceptance archival DOI is asserted.

## 10. Validation audit

The supplied campaign was regenerated in the clean package root. The resulting
summary extrema were:

| Metric | Value |
|---|---:|
| Maximum relative energy error | \(1.2047\times10^{-5}\) |
| Maximum cross-method spread | \(1.2235\times10^{-5}\) |
| Maximum tensor-sweep spread | \(8.3854\times10^{-6}\) |
| Maximum wavefunction \(L^2\) difference | \(1.3753\times10^{-3}\) |
| Minimum wavefunction overlap | 0.999514 |
| Maximum domain relative error | \(6.9084\times10^{-8}\) |
| Maximum FD alternation fraction | 1.0 |

The last value is not a quality score; it is the expected diagnostic signature
of the retained oscillatory FD candidate.

## 11. Reproducibility audit

**Rating: 9/10 for the supplied package.**

The package contains source, data, figures, notebook, dependencies, license,
tests, citation metadata, and a buildable CAS manuscript. The remaining point
is withheld because a clean external environment, hardware record, and complete
independent rerun were not available as evidence in this workspace.

## 12. Writing, notation, and consistency audit

- “Jupyter notebook” is used consistently, with Colab compatibility stated
  only as a compatibility property.
- The manuscript uses one release identifier, `1.0.0`, in package metadata and
  release links.
- The paper distinguishes benchmark evidence from future work.
- Scalar, vector, tensor, FD, DKB, overlap, residual, and domain terminology is
  used consistently.
- The long code command is line-broken so it does not exceed the column width.
- The CAS source compiles with the available TeX fonts; microtype expansion is
  disabled because the local class falls back to non-scalable fonts.

## 13. Figure and table audit

All ten figures are generated by package scripts and provided as PDF and PNG.

- Figure 1 is full-width; its panel labels are outside the axes and its
  panel-(a) legend is vertical in the lower-right corner.
- Figure 2 is full-width; panel-(b) has additional left padding and the
  zero-floor annotation is moved away from the curve.
- Figure 3 uses a full-width workflow schematic with text contained in boxes.
- Figures 4--9 are full-width and use readable legend blocks.
- Figure 10 is a full-width archive map with visible borders, deliberate
  vertical spacing, and orthogonal colored arrows.
- Scientific plot titles were removed from the plotting layer and transferred
  to captions/section context.

## 14. Caption and title report

Captions now identify the plotted quantity, benchmark condition, comparison
reference, and the principal interpretation. Figure 6 explicitly states the
non-monotonic DKB refinement behavior. Figure 8 identifies the physical and
grid-scale candidates. Figure 10 explains the archive structure without
requiring a plot title.

## 15. Reference and DOI audit

The manuscript contains 35 references, including CPC software papers,
relativistic basis/kinetic-balance literature, spectral-pollution work,
scientific-Python references, reproducibility guidance, and the closely
related scalar--vector--tensor study.

All 35 DOI records are rendered as clickable `https://doi.org/...` links in
the LaTeX source. Five high-priority records were independently checked
against publisher or primary records during this audit:

- Shabaev et al., DOI `10.1103/PhysRevLett.93.130405`;
- Li et al., DOI `10.1103/n376-m3nf`;
- Fillion-Gourdeau et al., DOI `10.1103/PhysRevA.85.022506`;
- Froese Fischer and Zatsarinny, DOI `10.1016/j.cpc.2008.12.010`;
- Dyall and Fægri, DOI `10.1016/0009-2614(90)85321-3`.

No DOI was invented. The author should perform a final spot-check of the
remaining supplied DOI strings when preparing the portal metadata.

## 16. CPC-specific review

The manuscript is best positioned as a Computer Physics Communications
computational-physics paper centered on numerical methods, software
implementation, validation, and reproducibility. The Program Summary is
retained because it is useful for CPC software-oriented submissions. The
introduction emphasizes the general numerical problem and the significance of
cross-method diagnostics before narrowing to the benchmark application.

The submission should link the public GitHub repository and exact release
asset in the portal. An archival DOI can be added later if and when the
authors create an accepted-version archive.

## 17. Simulated editorial and reviewer reports

### Editor

The paper is potentially suitable for CPC after minor author-side
confirmation. Its strongest asset is the complete evidence chain. The main
editorial risk is overinterpreting a smooth dimensionless campaign as a
general-purpose relativistic solver.

### Numerical-analysis reviewer

The cross-method checks, overlap diagnostics, and spurious-state example are
valuable. The reviewer would request a clearer distinction between the
reference shooting solution and an exact solution, plus explicit statements
about grid, basis, tolerances, and hardware. Those qualifications are now
present where supported; the author should add any missing runtime hardware
details before submission.

### Software/reproducibility reviewer

The package structure, MIT license, dependency metadata, tests, notebook,
portable driver, machine-readable outputs, and release link are appropriate.
The reviewer would rerun the command in a clean environment and inspect the
reported output path. The current package is prepared for that check.

### Physics reviewer

The paper should be evaluated as a numerical benchmark, not as a new nuclear
interaction model. The limitations section now makes that scope explicit and
separates the centered-FD counterexample and DKB development target from the
positive agreement claims.

## 18. Prioritized author plan

### Before submission

1. Confirm author spelling, affiliation, email, and ORCID.
2. Confirm that the public repository and exact release asset are accessible.
3. Repeat the 8-test command and campaign command in a clean environment.
4. Record the runtime hardware and Python/NumPy/SciPy versions if CPC asks for
   a machine-specific performance context.
5. Spot-check the remaining DOI links.
6. Prepare the CPC cover letter and portal program summary.

### After acceptance

1. Add the accepted-version archival DOI if desired.
2. Update the manuscript's CPC library record if CPC supplies one.
3. Freeze the repository release asset and preserve the tested commit.

## 19. Complete revised manuscript

The complete revised manuscript is the source-controlled file
`manuscript/DiracBench_CPC_Manuscript.tex`. The compiled PDF is
`manuscript/DiracBench_CPC_Manuscript.pdf`; it was rebuilt after
the source edits and all figures were regenerated from the campaign outputs.

## 20. Corrected reference list

The authoritative corrected list is the 35-entry `thebibliography` in
`manuscript/DiracBench_CPC_Manuscript.tex`. It includes 21 CPC records and related primary/methodological
references. DOI links are explicit and clickable rather than bare DOI labels.

## 21. Change log

- Consolidated the current manuscript and software into one clean package root.
- Removed the stale duplicate manuscript PDF from the deliverable.
- Standardized metadata and campaign provenance on `1.0.0`.
- Added repository and release URLs to `pyproject.toml` and `CITATION.cff`.
- Made campaign outputs relative-path and non-destructive.
- Added solver `__version__` metadata.
- Renamed the notebook to a Jupyter-oriented filename.
- Removed ordinary scientific plot titles from generated figures.
- Reworked legends, panel labels, dashboard spacing, and archive-map geometry.
- Added declarations and tightened the limitations language.
- Replaced the pre-acceptance archival-DOI promise with a public repository and
  release statement.
- Converted all reference DOI fields to clickable URLs and filled five missing
  DOI records.
- Expanded automated tests from 5 to 8 checks.
- Regenerated data, figures, metadata, and the manuscript PDF.

## 22. Submission-ready text components

### Suggested title

**DiracBench: Reproducible Relativistic Bound-State Benchmarks**

### Keywords

Dirac equation; radial eigenvalue problem; kinetic balance; B-splines;
Chebyshev collocation; finite differences; reproducibility.

### Data/code statement

All source code, dependency metadata, the MIT license, automated tests, the
Jupyter notebook (Colab-compatible), CSV outputs, error-analysis products,
publication figures, and figure-generation scripts used for the
scalar--vector--tensor campaign are included in the accompanying
reproducibility archive. The source repository is publicly available at
<https://github.com/ozalloum/diracbench>, and the exact reproducibility package
is archived in the public release at
<https://github.com/ozalloum/diracbench/releases/tag/1.0.0>.

## 23. Cover-letter and submission strategy

Present the work as a reproducible numerical-methods and software paper. Lead
with the cross-method falsification design, the explicit spurious-state
diagnostic, and the machine-readable release. State that the benchmark fields
are independent dimensionless Woods--Saxon tests and that the package is not
being presented as a production nuclear-structure code.

## 24. Likely objections and responses

| Objection | Response prepared in manuscript/package |
|---|---|
| The fields are dimensionless | The scope is stated explicitly; the goal is method benchmarking |
| FD has a spurious state | It is intentionally retained as a diagnostic and is quantified |
| DKB is not monotone | The refinement limitation is shown, not concealed |
| Runtime is hardware-dependent | Runtime is labeled as a reproducible baseline |
| No archival DOI yet | The public GitHub repository and exact release are supplied; DOI is deferred |
| Results may be overgeneralized | Limitations restrict claims to tested smooth benchmarks and channels |

## 25. Response-to-reviewers framework

For any revision, answer in the order: reviewer claim, exact manuscript
location, code/data evidence, change made, and residual limitation. Do not
answer a request for a new physical claim by extrapolating beyond the current
benchmark data. Add new results only through the campaign driver and preserve
the machine-readable error-analysis products.

## 26. Final checklist

- [x] Single clean package root
- [x] CAS source and compiled PDF
- [x] License
- [x] Dependency metadata
- [x] Public repository and release links
- [x] Jupyter notebook
- [x] Portable driver
- [x] Automated tests
- [x] Regenerated data and figures
- [x] Error-analysis CSV and JSON
- [x] Explicit limitations
- [x] Declarations
- [x] 35 references with clickable DOI links
- [x] No pre-acceptance archival DOI promise
- [ ] Author confirmation of portal metadata
- [ ] Optional clean-machine reproduction by the author

## 27. Stage 3 verification

| Verification | Result |
|---|---|
| Campaign regeneration | Passed |
| Unit/regression tests | 8 passed |
| Driver help | Passed |
| LaTeX compilation | Passed twice with the available CAS class |
| Figures readable at review resolution | Passed by visual inspection |
| Figure placement before limitations section | Passed |
| Release metadata consistency | Passed |
| Stale absolute campaign path | Removed from generated metadata |
| Repository/release links | Present in README, manuscript, and citation metadata |

## 28. Final assessment

The package is a strong CPC submission candidate after author confirmation.
Its scientific strength is the combination of independent discretizations and
failure-aware diagnostics. Its remaining risk is not hidden numerical
behavior; it is the normal need to reproduce the run in the author's final
environment, confirm all portal fields, and avoid broad claims beyond the
tested smooth benchmark domain.

## 29. Author action checklist

Before uploading to CPC, the author should:

- open `manuscript/DiracBench_CPC_Manuscript.pdf` and confirm the author metadata and page proofs;
- run `python -m unittest discover -s tests -t . -v`;
- run `python run_campaign.py --output clean_campaign`;
- confirm that the GitHub repository and release asset are public;
- check the five highlighted DOI records and spot-check the remaining links;
- provide the actual runtime hardware if retaining the performance paragraph;
- upload the manuscript source/PDF and the exact release package requested by
  the CPC portal;
- keep the archival DOI sentence out of the pre-acceptance manuscript unless
  an archival record has actually been created.
