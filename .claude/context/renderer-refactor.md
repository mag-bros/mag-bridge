# Renderer Refactor Context

Working file for `src/renderer/renderer.py` refactoring.

## Constraints

- **Backward compatible** — notebook call site unchanged (same params, same behavior)
- **camelCase** on all public params (RDKit convention, kept for compat)
- **Minimal** — no new dependencies, no over-engineering
- `Theme` stays in `src/utils/ui.py`
- All renderer code moves from `src/utils/` → `src/renderer/`

## Only Call Site (must keep working)

```python
Renderer(Theme.LoFi).GetMoleculesGridImg(
    mols=[m.ToRDKit() for m in mols],
    highlightAtomLists=[r.highlightAtomList for r in results],
    highlightAtomGroupsPerMol=[r.highlightAtomGroups for r in results],
    matchesCountersPerMol=[r.matchesCounter for r in results],
    size=(888, 500),
    mols_per_row=1,
    label="Bonds matched in compound visualization.",
    showLegend=True,
)
```

---

## Target State — File Structure

```
src/
├── ui/
│   ├── __init__.py
│   ├── highlight.py       ← NEW: pure color logic, no RDKit/PIL
│   └── renderer.py        ← MOVED + refactored from src/renderer/renderer.py
└── utils/
    ├── exceptions.py
    └── ui.py              ← Theme stays here (unchanged)
```

---

## Target State — Architecture

```
                    ┌─────────────────────────────────────────────┐
                    │              src/renderer/highlight.py            │
                    │                                             │
                    │  HighlightScheme                           │
                    │  ┌─────────────────────────────────────┐   │
                    │  │ .atomColors  list[dict[int, RGB]]   │   │
                    │  │ .formulaColor  dict[str, RGB]        │   │
                    │  │                                     │   │
                    │  │ fromGroups()   ← main path          │   │
                    │  │ fromAtomLists() ← legacy fallback   │   │
                    │  └─────────────────────────────────────┘   │
                    │  (owns palette math + luminance helpers)    │
                    └──────────────────┬──────────────────────────┘
                                       │ atomColors, formulaColor
                                       ▼
┌──────────────────────────────────────────────────────────────────┐
│                      src/renderer/renderer.py                          │
│                                                                  │
│  GridRenderConfig                  Renderer(theme)               │
│  ┌───────────────────┐             ┌────────────────────────┐    │
│  │ size              │             │ GetMoleculesGridImg()  │    │
│  │ molsPerRow        │   uses      │ GetMoleculeImg()       │    │
│  │ label             │ ──────────► │                        │    │
│  │ showLegend        │             │ internal pipeline:     │    │
│  │ sepWidth          │             │  align inputs          │    │
│  │ labelHeight       │             │  → HighlightScheme     │    │
│  └───────────────────┘             │  → bond colors (RDKit) │    │
│                                    │  → MolsToGridImage     │    │
│  ImageAdapter                      │  → theme background    │    │
│  ┌───────────────────┐             │  → grid lines          │    │
│  │ RDKit/numpy/PIL   │             │  → label               │    │
│  │ → PIL.Image       │             │  → legend              │    │
│  └───────────────────┘             └────────────────────────┘    │
└──────────────────────────────────────────────────────────────────┘
```

### Component responsibilities

| Component | File | Responsibility |
|---|---|---|
| `HighlightScheme` | `highlight.py` | Chemistry data → color mappings. No PIL, no RDKit mols. |
| `GridRenderConfig` | `renderer.py` | Layout parameters in one place. Extensible without touching method signature. |
| `Renderer` | `renderer.py` | Orchestrates the full pipeline: inputs → colors → RDKit render → PIL post-processing. |
| `ImageAdapter` | `renderer.py` | Converts RDKit/numpy/IPython image types to PIL. Unchanged. |

---

## Status

- [x] Analysis complete
- [x] Questions answered
- [x] Implementation plan written
- [x] Refactor implemented

---

## Next: Replace PIL Drawing Layer with matplotlib

**Decision (2026-03-22):** matplotlib replaces hand-rolled PIL pixel math for post-processing.

**Why matplotlib:** Already in ecosystem (Jupyter/scientific Python). Eliminates layout math entirely — legend, grid, text map to native primitives. Exports PNG/JPEG, displays in Jupyter natively.

**Rejected:** RDKit MolDraw2DSVG (no custom legend/label API), drawsvg/svgwrite (same manual math in SVG), pycairo (system C dep, same low-level drawing).

### What changes

Replace these 4 PIL methods in `renderer.py` (~100 LOC):
- `_apply_theme_background` — numpy pixel swap → matplotlib figure facecolor
- `_add_grid_lines` — ImageDraw lines → axes grid/borders
- `_add_label` — ImageDraw text → figure suptitle or text
- `_add_legend` — complex pixel-math swatch layout → matplotlib legend with custom patches

### Constraints (unchanged)
1. RDKit `MolsToGridImage` rendering untouched — only post-processing layer changes
2. Public API unchanged — `Renderer.GetMoleculesGridImg` signature and behavior stay backward-compatible
3. Output: PNG/JPEG required, SVG is a bonus. Must display in Jupyter
4. Composable layout — legend, label, grid overlay as independent concerns
