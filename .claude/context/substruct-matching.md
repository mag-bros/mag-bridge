## Substruct Matching Task
Use this file `.claude/context/substruct-matching.md` to write down key context that should be peristed within sessions. It will be handed over to other agents after your session finishes.

## What is Substructure Matching?
In RDKit, substructure matching is a graph-based search operation used to locate a specific chemical pattern—often defined by a `SMARTS` query—within a larger target molecule.  It leverages subgraph isomorphism algorithms to identify and return the exact atom indices where the query fragment exists.

## Motivation
RDKit creators clearly stated that they do not support Substruct Matching Overlaps. When querying molecules for SMARTS patterns, RDKit does the heavy-lifting to find ALL matches. Our use case requires domain-specific overlap rules, that are complex to implement.

## Principles

- **SMARTS patterns are frozen, chemist-owned contracts.** The SMARTS patterns in `bond_types.py` are the product of 3 months of iterative domain-expert design and must not be modified by code-side refactoring. The improvement boundary is strictly in the Python overlap resolution layer — SMARTS define *what* matches, Python decides *which matches survive* when they compete for the same atoms.

## Task status
This task roughly estimated at 95% done in terms of effort. The last 5% is very challenging, that is the exact reason why we need you. The code has gone to a place where it is very difficult to extend new complex chemical logic.

## Core Files Map
- `src/core/substruct_matcher.py` - most important file for the whole task. Contains very complex chemical project-tailored graph-based matching features.
- `src/constants/bond_types.py` - a list of relevant bond types used for matching molecule substructures.
- `tests/reports/TEST_DRIFT_substruct_matching.md` - **Test Drift Report**

## Tests
- `tests/core/test_substruct_matching.py` - The ONLY test that matters for this task is defined inside this file: `def test_substruct_matches(...)`
- `tests/data/substruct_matching_tests.py` - The only test data used by this test - it follows "Python as Configuration" concept, has 2.5k+ lines, but the structure is fully templated via `class SubstructMatchTest` - you should not **Edit** this file without permission. For **Read** operations please find an optimized search algoritm. One effective way was to simply cltr+f **id=<test_id>** - these IDs are consistent with `tests/core/test_substruct_matching.py` **@parametrize**.
- **Run Test Drift: Substruct Matching** - `.vscode/tasks.json` (script not extracted to a standalone form) - custom test automation test. It was introduced to streamline TDD, very handy, fast to use and delivers key benchmark that answers the question "where are we in comparison to the `bondtype-match-query-tool` branch (parent branch that we compare our new features against). The main reason why it was introduced was because when changing `src/core/substruct_matcher.py` or related files, there was a **test drift** - some tests started to fail, while others started to pass, so we were losing the track of what happened. This tool effectively fixes this issue and ultimately produces a minimized source of truth report: `tests/reports/TEST_DRIFT_substruct_matching.md`

## Open Tasks
1. [ ] Review **substruct matcher** code: `src/core/substruct_matcher.py`. Seek for: code smells, repetitions, broader context patterns, unused variables, contracts consistency / usage coverage in various places. As a part of this analysis, you should compare our implementation against RDKit native features. We have a feeling that we kind of reinvented the wheel in some places - it would be great if you were able to propose tradeoffs and identify hot spots were we could remove some of our custom **rdkit-wrapping** concepts/logic to favor native possibilities of the RDKit API.

## Remaining Substruct Matching Challenges
Source: `docs/remaining_substruct_matching_challenges.pdf`

### 1. [x] RCONH2 overlap restriction
- RCONH2 can overlap only by N atom, not by carbonyl C=O fragment.
- **Solution:** On self-overlap, recognize carbonyl C=O group. If C=O is matched twice, forbid self-overlap. Otherwise allow.

### 2. [x] RC(=O)OR overlap restriction
- RC(=O)OR can overlap only by O atom, not by carbonyl C=O fragment.
- Analogous conditions as for #1, plus: C=O cannot match for RO-C(=O)-OR fragment.
- **Solution:** Same as #1 — recognize carbonyl C=O in self-overlap; if C=O matched twice, forbid.

### 3. [x] Seniority rule
- Priority order: RCONH2 > Ar-CONH2 > RCOOR > Ar-COOR > COOH > Ar-COOH > C=O

### 4. [ ] Fix Cl-CR2-CR2-Cl and R2CCl2
- Self-overlap allowed via one C-C bond (same rule for R2CCl2).
- Cl-CR2-CR2-Cl and R2CCl2 (cross-type) are allowed to match only via one C-C bond.
- Ring and Cl-CR2-CR2-Cl overlap allowed only via two C-C bonds (same rule for R2CCl2).
- **Solution:** On self-overlap, recognize C-C pair (two C connected by single bond). Allow only one such pair between two same bond types. Cross-type overlap (R2CCl2 vs Cl-CR2-CR2-Cl) resolved by SMARTS. Ring overlap resolved by checking how many atoms belong to the same ring — if more than 2, exclude matching.

### 5. [ ] Fix Br-CR2-CR2-Br
- Self-overlap allowed via one C-C bond only.
- Ring and Br-CR2-CR2-Br overlap allowed only via two C-C bonds.
- **Solution:** Reuse solutions from #4.

### 6. [x] Fix Ar-NR2
- If one R = Ar, assign two Ar-NR2 bond types; for two R = Ar, match three Ar-NR2.
- For [N+]-Ar4, match four Ar-NR2.
- **Solution:** When Ar-NR2 is matched, check how many carbon atoms are aromatic. The number of matched groups must equal the number of aromatic C atoms.

### 7. [x] Fix Ar-OR
- If Ar = R, match two Ar-OR bonds.
- **Solution:** Analogous to #6.

### 8. [ ] C=C=C issue
- Current SMARTS logic excludes matching of two C=C bond types in C=C=C (allene).
- **Solution:** Add additional condition — use SMARTS to convey the structural pattern to exclude from the rule, or: if one C atom forms two double bonds with other C atoms, allow C=C self-overlap.

### 9. [ ] Fix self-overlap of RC#C-C(=O)R
- Two possibilities of self-overlap: via C#C-C fragment, or via C(=O)C.
- **Solution:** Allow self-overlap via C-C exclusively. Recognize single-bonded C atoms (C-C). Only this pair is allowed to overlap. Otherwise forbid self-overlap.

## Review Notes `src/core/substruct_matcher.py`
todo