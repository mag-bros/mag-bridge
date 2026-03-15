# Substruct Matcher Architecture Report

## Accuracy Self-Assessment

- **Structural understanding: 8/10** -- The two-phase overlap pipeline, five dispatch strategies, dummy ring mechanism, and injection-on-rejection pattern are all verified line-by-line against source; the architectural picture is reliable.
- **Chemical knowledge: 5/10** -- I understand that Pascal's additivity scheme decomposes molecular diamagnetic susceptibility into atomic increments plus constitutive correction terms for specific bond types and ring systems, and I can read SMARTS notation well enough to see that e.g. `[C;X3,X2;!$([c])]=[C]` targets aliphatic sp2/sp carbon double bonds while excluding aromatics. However, I do not understand *why* specific constitutive correction values are what they are (e.g. why cyclohexene is 6.9 but cyclohexane is 3.0), I cannot independently verify whether the SMARTS exclusion clauses are chemically complete (e.g. whether the C=O pattern correctly excludes all carbonyl-containing functional groups that should be counted separately), and I have no intuition for when two overlap groups should share atoms vs. reject -- I only know the thresholds because the code says so, not because I understand the underlying magnetic susceptibility reasoning.
- **Coverage gaps: not rated** -- Did not investigate `MBAtom` internals, oxidation state assignment, or how the ~400 test cases map to real chemical edge cases; a chemist reviewing the SMARTS patterns and overlap rules would be needed to validate correctness beyond what code structure alone can confirm.

## Section 1: What It Does (Domain Purpose)

- Implements **Pascal's additivity scheme** for molecular diamagnetic susceptibility -- each recognized bond type carries a `constitutive_corr` constant (e.g., C=C -> 5.5, benzene -> -1.4) that feeds into the final calculation in `MBMolecule.CalcDiamagContr()`
- Defines **66 bond types** in `src/constants/bond_types.py` as `BondType` dataclasses, each with a hand-crafted SMARTS pattern encoding precise chemical exclusions (e.g., C=C excludes aromatic carbons, cyclohexene, and aryl-bound carbons)
- The entry point `MBSubstructMatcher.GetMatches()` at `src/core/substruct_matcher.py:57` runs every SMARTS pattern against a molecule, producing renderer-ready highlight data and match counts
- Wraps RDKit's `Mol.GetSubstructMatches()` (which calls the C++ `SubstructMatch` at `Code/GraphMol/Substruct/SubstructMatch.cpp:525`) but adds a critical post-processing layer that RDKit doesn't provide: **overlap resolution between competing bond type assignments**
- The output `SubstructMatchResult` serves dual purposes -- analytical (which bond types matched where) and visual (atom highlight lists for the frontend renderer)

## Section 2: How It Works (Architecture)

- `MBMolecule` at `src/core/molecule.py:14` wraps RDKit's `Mol` with a `__getattr__` fallback, parsing SMARTS via `MolFromSmarts(smarts, mergeHs=True)` and delegating to RDKit's C++ substruct engine -- the thin wrapper keeps the domain logic decoupled from RDKit internals
- A **two-phase overlap pipeline** is the core innovation: Phase 1 (`_FilterSelfOverlaps`, line 116) resolves conflicts *within* a single bond type; Phase 2 (`_FilterCrossOverlaps`, line 231) resolves conflicts *between* different bond types using priority-ordered processing
- Overlap resolution uses **5 distinct strategies** dispatched via Python `match/case` on `OverlapGroup`: `BICYCLIC_STRUCTURES` (3+ shared atoms), `DOUBLE_BONDS` (1+ shared atoms), `CARBONYL_BOND_TYPES` (2+ shared atoms with double-bond check), `Ar_N_BOND_TYPES` (3+ shared atoms), and `DEFAULT` (complex per-formula rules for halogens and aromatics)
- `CrossOverlapComparator` at `src/core/cross_overlap_comparator.py:4` sorts candidates by group priority then intra-group ordering (e.g., within carbonyls: RC(=O)NH2 > RCOOR > RCOOH > C=O), ensuring higher-specificity patterns claim atoms first
- `OverlapRules.InjectDerivedMatches()` at line 329 handles **decomposition on rejection** -- when a complex pattern like cyclohexene is rejected due to bicyclic overlap, it injects simpler derived matches (e.g., C=C double bonds from the unclaimed atoms)

## Section 3: What's Tricky (Complexity & Risk)

- The `DEFAULT` overlap group in `_FilterSelfOverlaps` (lines 161-220) contains the most intricate logic -- special-cased handling for `Cl-CR2-CR2-Cl`, `Br-CR2-CR2-Br` (C-C detection with bond-type checking) and `Ar-OR`/`Ar-NR2` (aromatic carbon counting for duplicate bond injection), with a nested `_get_duplicate_bonds` closure
- The `rule_Cl_CR2_CR2_Cl` at line 364 performs atom-level graph traversal (finding free Cl atoms, checking their C neighbors for single bonds) to inject `C-Cl` replacements when the full `Cl-CR2-CR2-Cl` pattern is rejected -- this is essentially a **manual subgraph decomposition** that RDKit's built-in `SubstructMatch` knows nothing about
- Dummy rings (`dummy_ring=True`) like thiacyclopropane/oxacyclopropane/azacyclopropane (ids 14-16) exist solely to force correct bicyclic overlap resolution for 5-membered rings in bicyclo[3.1.0] systems -- they're filtered out at the end of `_FilterCrossOverlaps` (line 300)
- The SMARTS patterns themselves encode significant domain complexity -- e.g., `C=O` at bond id 19 has 5 nested exclusion clauses preventing overlap with amides, esters, acids, aryl ketones, and specific alkynyl ketones, all within a single SMARTS string
- State mutation during iteration: both `accepted_candidates` and `filtered`/`final_hits_by_formula` are modified in-place by `InjectDerivedMatches`, meaning the overlap resolution is **order-dependent** -- the `CrossOverlapComparator.sort_matches()` ordering is load-bearing for correctness
