# Manuscript build

`main.tex` is the submission source for Elsevier's CAS `cas-dc` document
class, following the supplied spherical-electrostatics manuscript template.
The archive includes the required CAS class, common style, bibliography style,
and thumbnail assets, so it can be compiled directly with pdfLaTeX:

```bash
pdflatex -interaction=nonstopmode main.tex
pdflatex -interaction=nonstopmode main.tex
```

The local algorithm style files are included so the pseudocode renders
without additional project-specific files. The figure-generation script
regenerates the publication PDF/PNG assets, including the full-width annotated
error/convergence dashboard, workflow schematic, and reproducibility-package
map. Run pdfLaTeX twice after changing the source so cross-references settle.
