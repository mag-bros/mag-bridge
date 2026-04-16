# Renderer Module

Molecule grid rendering pipeline. Wraps RDKit drawing with theme support, formula-based highlighting, and matplotlib post-processing.

## Files

| File | Responsibility |
|---|---|
| `highlight.py` | Chemistry data → color mappings. No PIL, no RDKit mols. |
| `renderer.py` | Full pipeline: inputs → colors → RDKit render → matplotlib composition. |

---

## Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                   src/renderer/highlight.py                  │
│                                                              │
│  HighlightScheme                                             │
│  ┌────────────────────────────────────────────────────────┐  │
│  │ .atomColors     list[dict[int, RGBf]]                  │  │
│  │ .formulaColor   dict[str, RGBf]                        │  │
│  │                                                        │  │
│  │ fromGroups()    stable color per formula across mols   │  │
│  │                RGB blending for shared/overlap atoms   │  │
│  │ fromAtomLists() legacy fallback — one color per mol    │  │
│  └────────────────────────────────────────────────────────┘  │
│  _contrasting_palette()   golden-ratio HSV, max contrast     │
└─────────────────────────────────┬────────────────────────────┘
                                  │ .atomColors  .formulaColor
                                  ▼
┌──────────────────────────────────────────────────────────────────┐
│                      src/renderer/renderer.py                    │
│                                                                  │
│  GridRenderConfig               Renderer(theme)                  │
│  ┌──────────────────────┐       ┌──────────────────────────────┐ │
│  │ size                 │       │ GetMoleculeImg()             │ │
│  │ molsPerRow           │       │ GetMoleculesGridImg()        │ │
│  │ label                │ uses  │                              │ │
│  │ showLegend           │──────►│  _align_inputs()             │ │
│  │ showAtomIndexes      │       │  HighlightScheme             │ │
│  │ highlightAlpha       │       │  _build_bond_colors()        │ │
│  │ sepWidth             │       │  MolsToGridImage() ──────────────► RDKit
│  └──────────────────────┘       │  _compose_figure()           │ │
│                                 └──────────────┬───────────────┘ │
│  ImageAdapter                                  │ PIL Image       │
│  ┌──────────────────────┐                      ▼                 │
│  │ RDKit / numpy / PIL  │    matplotlib post-processing:         │
│  │ → PIL.Image.Image    │    numpy pixel swap  → theme.Surface   │
│  └──────────────────────┘    Figure + FigureCanvasAgg            │
│                              ax.imshow          → molecule grid  │
│                              ax.axvline/axhline → grid lines     │
│                              ax.text            → label          │
│                              ax.legend          → formula legend │
│                              savefig + numpy round-trip          │
│                              → PIL.Image (RGB, no metadata)      │
└──────────────────────────────────────────────────────────────────┘
```

### Components

**`HighlightScheme`** (`highlight.py`)
- `fromGroups()` — main path. Assigns one stable color per formula across all molecules. Atoms in multiple groups get an **RGB-averaged blend** of all their group colors, making shared nodes visually distinct.
- `fromAtomLists()` — legacy fallback, one color per molecule.
- Uses golden-ratio HSV palette for maximum color contrast.

**`GridRenderConfig`** (`renderer.py`)
- All layout params in one place. Adding new display options goes here — the method signature stays stable.

**`Renderer`** (`renderer.py`)
- `GetMoleculeImg()` — single molecule, SMILES legend.
- `GetMoleculesGridImg()` — full grid pipeline. Public API, backward-compatible.

**`ImageAdapter`** (`renderer.py`)
- Normalizes RDKit / numpy / IPython image types to `PIL.Image`. Unchanged.

---

## Post-processing: matplotlib (not PIL)

RDKit renders the molecule grid. Everything after that is matplotlib:

| What | How |
|---|---|
| Theme background (outer) | `Figure(facecolor=theme.Background)` |
| Theme surface (molecule cells) | numpy pixel swap: near-white → `theme.Surface` before `ax.imshow()` |
| Grid lines | `ax.axvline/axhline` in imshow pixel-exact data coordinates |
| Label | `ax.text(..., transform=ax.transAxes)` — below axes at `y=-0.02` |
| Legend | `ax.legend(Patch[], bbox_to_anchor)` — below label at `y=-0.08` |
| Output | `fig.savefig(BytesIO, bbox_inches='tight')` → numpy round-trip → `PIL.Image` |

**Why numpy round-trip on output:** matplotlib embeds DPI as a `tuple` in PNG metadata. RDKit's IPython display hook calls `.encode()` on all metadata values and crashes. The `Image.fromarray(np.array(...convert("RGB")))` strips all metadata and normalizes to RGB.

**Why `FigureCanvasAgg` explicitly:** `Figure` created without `pyplot` has no canvas. Attaching `FigureCanvasAgg` makes `fig.savefig()` work without a display or backend conflicts with Jupyter.

---

## `GetMoleculesGridImg` parameters

| Parameter | Default | Notes |
|---|---|---|
| `mols` | — | `list[Mol]` |
| `highlightAtomLists` | `None` | per-mol atom index lists |
| `highlightAtomGroupsPerMol` | `None` | per-mol `{formula: [atom_idxs]}` — enables formula coloring |
| `matchesCountersPerMol` | `None` | per-mol `Counter[formula]` — populates legend counts |
| `size` | `(300, 300)` | per-cell pixel size |
| `mols_per_row` | `4` | |
| `label` | `None` | caption below grid |
| `showLegend` | `False` | formula color legend below label |
| `showAtomIndexes` | `False` | RDKit atom index overlay (`rdMolDraw2D.addAtomIndices`) |
| `highlightAlpha` | `0.6` | RGBA alpha for atom/bond highlights — lower = more transparent |

---

## Notebook Control

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
      showAtomIndexes=True,
      highlightAlpha=0.5,
)
```
