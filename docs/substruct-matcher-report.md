# Substruct Matcher -- Architecture Report

> AI-generated analysis of `src/core/substruct_matcher.py` and its dependencies.
> Cross-referenced against RDKit C++ source via jCodeMunch index.

---

## Confidence Ratings

| Dimension | Score | What I verified | What I can't verify |
|-----------|-------|-----------------|---------------------|
| **Code structure** | 8/10 | Overlap pipeline, dispatch strategies, dummy rings, injection pattern -- all read line-by-line | `MBAtom` internals, Boost.Python binding layer, test coverage mapping |
| **Chemistry** | 5/10 | Pascal's additivity concept, SMARTS syntax (e.g. `[C;X3,X2;!$([c])]=[C]` = aliphatic C=C excluding aromatics) | Why correction constants have specific values (cyclohexene=6.9 vs cyclohexane=3.0), whether SMARTS exclusions are chemically complete, magnetic susceptibility reasoning behind overlap thresholds |

**For the chemist:** I can read the SMARTS and trace the code logic, but I cannot judge whether the patterns are *chemically correct*. A domain expert should validate the exclusion clauses and constitutive correction values independently.

---

## 1. Purpose

- Implements **Pascal's additivity scheme** -- each bond type carries a constitutive correction constant (C=C -> 5.5, benzene -> -1.4) for diamagnetic susceptibility
- ~48 bond types defined in `bond_types.py`, each with a hand-crafted SMARTS pattern encoding chemical exclusions
- Wraps RDKit's C++ `GetSubstructMatches()` but adds **overlap resolution** -- deciding which bond type "wins" when patterns claim the same atoms
- Entry point: `MBSubstructMatcher.GetMatches()` at line 57
- Output serves both analysis (which bond types matched where) and visualization (atom highlights for the frontend)

## 2. Architecture

- **`MBMolecule`** wraps RDKit's `Mol` with `__getattr__` fallback -- keeps domain logic decoupled from RDKit internals
- **Two-phase overlap pipeline** (the core innovation):
  - Phase 1 -- `_FilterSelfOverlaps` (line 116): conflicts *within* one bond type
  - Phase 2 -- `_FilterCrossOverlaps` (line 231): conflicts *between* different bond types, priority-ordered
- **5 overlap strategies** dispatched via `match/case` on `OverlapGroup`:

  | Strategy | Shared atom threshold |
  |----------|----------------------|
  | `BICYCLIC_STRUCTURES` | 3+ atoms |
  | `DOUBLE_BONDS` | 1+ atom |
  | `CARBONYL_BOND_TYPES` | 2+ atoms + double-bond check |
  | `Ar_N_BOND_TYPES` | 3+ atoms |
  | `DEFAULT` | per-formula rules (halogens, aromatics) |

- **`CrossOverlapComparator`** sorts candidates by group priority, then intra-group specificity (e.g. RC(=O)NH2 > RCOOR > RCOOH > C=O)
- **`InjectDerivedMatches()`** (line 329): when a complex pattern is rejected, it decomposes into simpler matches (e.g. rejected cyclohexene -> injected C=C bonds)

## 3. Complexity Hotspots

- **`DEFAULT` self-overlap handler** (lines 161-220): special-cased Cl/Br dihalide C-C detection and aromatic Ar-OR/Ar-NR2 duplicate bond injection with nested `_get_duplicate_bonds` closure
- **`rule_Cl_CR2_CR2_Cl`** (line 364): manual subgraph decomposition -- finds free Cl atoms, checks C neighbors for single bonds, injects `C-Cl` replacements. RDKit knows nothing about this logic.
- **Dummy rings** (ids 14-16: thia/oxa/azacyclopropane): exist only to force correct bicyclic overlap resolution for 5-membered rings; filtered out at line 300
- **SMARTS complexity**: e.g. `C=O` (bond id 19) has 5 nested exclusion clauses preventing overlap with amides, esters, acids, aryl ketones, alkynyl ketones -- all in one pattern
- **Order-dependent state mutation**: `InjectDerivedMatches` modifies match lists in-place during iteration -- `CrossOverlapComparator.sort_matches()` ordering is load-bearing for correctness

