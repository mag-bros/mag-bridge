## Substruct Matching Task
Use this file `.claude/context/substruct-matching.md` to write down key context that should be peristed within sessions. It will be handed over to other agents after your session finishes.

## What is Substructure Matching?
In RDKit, substructure matching is a graph-based search operation used to locate a specific chemical pattern—often defined by a `SMARTS` query—within a larger target molecule.  It leverages subgraph isomorphism algorithms to identify and return the exact atom indices where the query fragment exists.

## Motivation
RDKit creators clearly stated that they do not support Substruct Matching Overlaps. When querying molecules for SMARTS patterns, RDKit does the heavy-lifting to find ALL matches. Our use case requires domain-specific overlap rules, that are complex to implement.

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

## Review Notes `src/core/substruct_matcher.py`
todo