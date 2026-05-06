## Substructure Queries
## Appendix 1. Constitutive corrections (&lambda;<sub>i</sub>) - bond type query

The diamagnetic contribution for a given compound may be estimated by summing atomic susceptibilities (**&chi;<sub>Di</sub>**) and *constitutive corrections* (**&lambda;<sub>i</sub>**):

$$
\chi_D = \sum_i \chi_{Di} + \sum_i \lambda_i \quad
$$

<p align="right">
 <span id="eq1"> (A.1)</span>
</p>

where **&lambda;<sub>i</sub>** takes into account the structural factors. A single **&lambda;<sub>i</sub>** constant can account for either an individual bond between a pair of atoms or larger structural fragments of a molecule (e.g., rings, functional groups, or conjugated systems), collectively referred to as *bond types*.

There is confusion regarding the &lambda;<sub>i</sub> and &chi;<sub>Di</sub> constants, arising from conflicting values reported across different sources. To avoid inconsistencies in the data used in MagBridge, the constitutive corrections implemented in the software were taken exclusively from the article by G. A. Bain et al.[<a href="#ref1">1</a>], which provides a valuable clarification of this issue. Because constitutive corrections have been tabulated for only a limited number of bond types, they do not adequately capture the enormous structural diversity of organic and inorganic compounds. In turn, this may reduce the accuracy of calculating the overall diamagnetic contribution for certain compounds when using MagBrdige.

>[!NOTE]
>Due to the scarcity of the literature constitutive correction data, the assignment of available bond types for certain molecules was nontrivial and required several assumptions, which are discussed herein. Two opposite approaches could be made to overcome this issue. The first is a strict approach, applying &lambda;<sub>i</sub> to exactly corresponding bond types. The second is a more flexible approach, in which a given constitutive correction is assumed to also apply to structurally similar fragments. During software development, we chose to follow the second approach. However, in a future iteration of the software, the user will be able to decide whether the automatic application of constitutive corrections for a studied compound is appropriate and, if necessary, adjust them manually during postprocessing.

## Assumptions made 

### Linear Conjugated Polyenes

<p align="center">
<img src="https://github.com/user-attachments/assets/0d276288-0355-408d-b37f-a242f224b623" alt="Image" width="600">
</p>
<p align="center">
  <b>Figure A.1</b> An example of bond type assignment for a linear conjugated polyene.
</p>

To account for linear conjugated polyene fragments containing three or more conjugated C=C bonds, we assumed that the constitutive correction for such a fragment can be approximated as the sum of the corrections for the relevant, available bond types C=C, Ar-C=C, and/or C=C-C=C (Figure A.1).

### Carboxyl group

The available constitutive corrections account only for Ar-COOH and RCOOH carboxyl fragments, with the carboxyl group in its neutral form. However, in ligands of paramagnetic coordination compounds, the carboxyl group is usually deprotonated. For these reasons, we assumed that the literature constitutive correction of $\lambda_{RCOOH} = -5.0 \times 10^{-6} \ \mathrm{cm^3 \ mol^{-1}}$ for RCOOH fragment can also be applied to the deprotonated fragment RCOO-. Analogously, the $\lambda_{Ar-COOH} = -1.5 \times 10^{-6} \ \mathrm{cm^3 \ mol^{-1}}$ was assumed to be relevant for Ar-COO- fragment.

### Phenol group
As with the carboxyl group, the Ar–OH constitutive correction was also assumed to represent the deprotonated phenolate (Ar–O<sup>-</sup>) group.

### N-heterocyclic rings
For the reasons explained for the carboxyl group, constitutive correction for a given ring in its neutral protonation state was also assumed to be relevant for other common protonation states of the ring. The relevant rings are: imidazole, pyrazine, pyrimidine, pyridine, pyrrole, 1,3,5-triazine, thiazole, pyrrolidine, piperidine and piperazine. 

It is important to note that for some rings (including saturated ones), the constitutive corrections are unavailable.

### Ester group
Two relevant constitutive corrections &lambda;<sub>i</sub> are available, one corresponding to RCOOR and the second to the Ar-COOR group. We permitted &lambda;<sub>RCOOR</sub> to also be applied when the R group bonded to oxygen atom is substituted with aryl groups or N, O, or Si atoms. The same assumption was made for the &lambda;<sub>Ar-COOR</sub> of Ar-COOR group.

Another dilemma was the acid anhydride R-C(=O)-O-C(=O)-R' fragment, which has no associated constitutive correction. To address this issue, we decided to use two constitutive corrections corresponding to ester bond types (RCOOR or Ar-COOR), as these have the closest structural resemblance among the available bond types (Figure A.2). Omitting R-C(=O)-O-C(=O)-R' fragment without applying any &lambda;<sub>i</sub> constant would presumably result in a greater systematic error than applying the constitutive correction of a similar bond type.

<p align="center">
<img  src="https://github.com/user-attachments/assets/aa5ff399-fe72-44ff-88df-4a7f195edf16" alt="Image" width="200">
</p>
<p align="center">
  <b>Figure A.2</b> Two &lambda;<sub>i</sub> constants corresponding to ester group are used to account for acid anhydride R-C(=O)-O-C(=O)-R' fragment.
</p>

### Amide group
Two relevant constitutive corrections &lambda;<sub>i</sub> are available, one corresponding to RCONH2 and the second to the Ar-CONH2 group. However, molecules containing an amide group in which the nitrogen is bonded to one or two aliphatic or aryl groups are far more common. Taking this into account, we assumed that the constitutive correction for RCONH2 also applies to RCONHR'R'' fragment, where R' and R'' are aliphatic or aryl groups. The same assumption was made for Ar-CONH2 constitutive correction.

A similar dilemma to that of the acid anhydride was presented by the imide R-C(=O)-NH-C(=O)-R' fragment. Due to a lack of associated &lambda;<sub>i</sub> constant for this group, we assumed the use of two amide-group constitutive corrections.

<p align="center">
<img src="https://github.com/user-attachments/assets/b2d7c6fc-0e76-48e2-b068-d1a90f585920"  alt="Image" width="200">
</p>
<p align="center">
<b>Figure A.3</b> Two &lambda;<sub>i</sub> constants corresponding to the amide group are used to account for imide R-C(=O)-NH-C(=O)-R' fragment.
</p>

### Bicyclic fragments

<p align="center">
<img src="https://github.com/user-attachments/assets/cd1f52bc-f3d4-4460-a90e-2a402b80b957" alt="Image" width="250" >
</p>
<p align="center">
<b>Figure A.4</b> Bicyclo[2.2.1]heptane structure with an atom-numbering scheme. 
</p>

In general, three fused rings can be identified within a bicyclic structure. By examining Figure A.4 of the bicyclo[2.2.1]heptane structure, we can identify three rings with the following atomic indices: 1<sup>st</sup> cyclopentane ring (C1,C2,C3,C4,C7), 2<sup>nd</sup> cyclopentane ring (C1,C6,C5,C4,C7) and the cyclohexane ring (C1,C2,C3,C4,C5,C6). Because these rings share at least two C-C bonds, the application of three constitutive corrections accounting for all three rings would lead to an overestimation of the diamagnetic contribution of a molecule. (In this particular case, this is not relevant as &lambda;<sub>i</sub> of cyclopentane ring equals $0.0 \times 10^{-6} \ \mathrm{cm^3 \ mol^{-1}}$). To address this issue, we introduced *ring seniority* rules, according to which only the constitutive correction of one of the rings is considered. The seniority of the rings was defined based on the ring's &lambda;<sub>i</sub> value, as shown in Figure A.5.

<p align="center">
<img src="https://github.com/user-attachments/assets/5c8bda57-6180-4d2d-8ada-78b76bceaa40" alt="Image" width="550">
</p>
<b>Figure A.5</b> Ring seniority within bicyclic structure. The two dummy rings have no associated  &lambda;<sub>i</sub> values and were introduced solely for code implementation purposes.

### X-CR2-CR2-X bond type (X = Cl or Br)

For the Cl-CR2-CR2-Cl and Br-CR2-CR2-Br fragments, constitutive corrections &lambda;<sub>Cl-CR2-CR2-Cl</sub> and &lambda;<sub>Br-CR2-CR2-Br</sub> are available [<a href="#ref1">1</a>]. However, applying these constants was forbidden in the case when Cl-CR2-CR2-Cl or Br-CR2-CR2-Br shared three C-C bonds with a ring. To avoid the problem with overlapping bond types, in this particular case, two &lambda;<sub>C-Cl</sub> or &lambda;<sub>C-Br</sub> constants are used, together with given ring's &lambda;<sub>i</sub> value, instead of a single &lambda;<sub>Cl-CR2-CR2-Cl</sub> or &lambda;<sub>Br-CR2-CR2-Br</sub> constant along with ring's &lambda;<sub>i</sub>.


### Amines

Only the constitutive correction of the Ar-NR2 fragment is available. We assumed that this constant can also be applied to the following structurally similar bond types: Ar-NH2, Ar-NHR, Ar-NH-Ar and Ar-N-Ar2. For each of these bond types &lambda;<sub>Ar-NR2</sub> value is applied once.

### Aryl ethers 

The only relevant available constitutive correction is associated with the Ar-OR bond type. We assumed to extend this constant over the Ar-O-Ar bond type, where, in this case, &lambda;<sub>Ar-OR</sub> is applied only once.

### Fused ring systems

To account for fused ring systems, we assumed that the constitutive correction for such fragments can be approximated as the sum of the corrections for the relevant, single aromatic rings. Note that this is a rough approximation, as the aromaticity of such fused fragments may differ significantly from that of individual aromatic rings.

&nbsp;

>[!NOTE]
>These are only the most important assumptions made for bond type assignment and, consequently, for the application of constitutive corrections. For more detailed information, users are referred to the results of 400 tests covering bond type assignment for a wide range of organic molecules, most of which were sourced from the PubChem database.

&nbsp;

## Literature references <a id="literature-references"></a>
> <a id="ref1"></a>[1] G. A. Bain, J. F. Berry, J. Chem. Educ., 2008, 85, 532-536. DOI: https://doi.org/10.1021/ed085p532.


# Substruct Matcher Architecture

Reference document for `src/core/substruct_matcher.py` and `src/overlap_rules.py`.

## Core Files

| File | Role |
|---|---|
| `src/core/substruct_matcher.py` | Orchestrator: `GetMatches → _Postprocess → _FilterSelfOverlaps → _FilterCrossOverlaps` |
| `src/overlap_rules.py` | Strategy tables: `SelfOverlapRules`, `CrossOverlapRules`, `OverlapInjector`, `OVERLAP_RULES_CONFIG` |
| `src/constants/bond_types.py` | Bond type definitions, `OverlapGroup` enum — SMARTS patterns are frozen |
| `src/core/cross_overlap_comparator.py` | Priority sorting used by `_FilterCrossOverlaps` and `CrossOverlapRules._check_carbonyl` |

---

## Data Types

```python
BondMatchCandidate      # BondType + matched atom indices (from RDKit substructure hit)
RejectedCandidate       # candidate + reason str + conflicting_with: BondMatchCandidate (1:1)
InjectedCandidate       # candidate + parent: RejectedCandidate + rule: str (1:1)
```

---

## Self-Overlaps

### `_FilterSelfOverlaps` — 3-Phase Pipeline

Filters candidates within the same formula group. Input/output: `dict[formula, list[BondMatchCandidate]]`.

```
grouped_candidates
        │
        ▼
┌─────────────────────────────────────────────────────┐
│  Phase 1: Classify                                  │
│  SelfOverlapRules.check_overlap()                   │
│  → accepted: dict[str, list[BondMatchCandidate]]    │
│  → rejected: dict[str, list[RejectedCandidate]]     │
└──────────────────┬──────────────────────────────────┘
                   │
        ┌──────────┴──────────┐
        ▼                     ▼
   accepted               rejected
        │                     │
        │          ┌──────────┘
        │          ▼
        │  ┌──────────────────────────────────────────┐
        │  │  Phase 2: Inject on rejection            │
        │  │  OverlapInjector.inject_on_reject(       │
        │  │      trigger="on_self_reject")            │
        │  └──────────────────────────────────────────┘
        │
        ▼
┌─────────────────────────────────────────────────────┐
│  Phase 3: Inject on accept                          │
│  OverlapInjector.inject_on_reject(trigger="on_accept") │
│  (Ar-OR / Ar-NR2 aromatic duplication)              │
└──────────────────┬──────────────────────────────────┘
                   │
                   ▼
            dict(accepted)
```

**Phase 2 isolation:** `occupied = list(accepted[cand_key])` — inject rules may append foreign-type entries to this copy (for `exclude_idx` computation), but those writes must not contaminate `accepted[cand_key]`.

**Phase 3 `seen` list:** Each accepted candidate is processed against `seen` (candidates earlier in the same group). `seen` grows per iteration; extras are written directly to `accepted[formula]`.

### `SelfOverlapRules` — classifier

Group-level callable per `OverlapGroup`. Returns `RejectedCandidate` on overlap, `None` to accept.

| Method | Group | Threshold | Extra condition |
|---|---|---|---|
| `_check_bicyclic` | BICYCLIC_STRUCTURES | ≥ 3 shared atoms | — |
| `_check_double_bonds` | DOUBLE_BONDS | ≥ 1 shared atom | — |
| `_check_carbonyl` | CARBONYL_BOND_TYPES | ≥ 2 shared atoms | both in C=O double bond |
| `_check_default` | DEFAULT | ≥ 3 shared atoms | only for dihalide formulas (`Cl-CR2-CR2-Cl`, `R2CCl2`, `Br-CR2-CR2-Br`) |

---

## Cross-Overlaps

### `_FilterCrossOverlaps` — Priority-Sorted Pipeline

Filters candidates across different formula groups using priority ordering from `OVERLAP_RULES_CONFIG`.

```
grouped_candidates
        │
        ▼
┌─────────────────────────────────────────────────────┐
│  Sort all candidates by group priority              │
│  CrossOverlapComparator.sort_matches()              │
└──────────────────┬──────────────────────────────────┘
                   │
                   │  ↻ one bmc at a time, in sorted order
                   ▼
┌─────────────────────────────────────────────────────┐
│  Check bmc against occupied                         │
│  CrossOverlapRules.check_overlap()                  │
│  → approve / reject                                 │
└──────────────────┬──────────────────────────────────┘
                   │
        ┌──────────┴──────────────────────────────────────────────┐
        ▼                                                         ▼
┌───────────────────────────────┐  ┌──────────────────────────────────┐
│  approve                      │  │  reject                          │
│                               │  │                                  │
│  bmc → accepted               │  │  OverlapInjector                 │
│  bmc → occupied               │  │  .inject_on_reject(              │
│                               │  │    trigger="on_cross_reject")    │
│                               │  │  → may append to accepted +      │
│                               │  │    occupied                      │
└──────────────┬────────────────┘  └────────────────┬─────────────────┘
               │                                    │
               └─────────────────┬──────────────────┘
                                 │  (occupied updated
                                 │   before next bmc) ↺

         (after all iterations)
┌─────────────────────────────────────────────────────┐
│  Strip dummy rings + dummy bond types               │
└──────────────────┬──────────────────────────────────┘
                   │
                   ▼
            dict(accepted)
```

### Cross-Overlap Structural Requirements

- **Candidates must be processed in group priority order** — each decision reads `occupied` built by all prior iterations; group priority determines which formulas "claim" atoms first.
- **OverlapInjector must fire in the same iteration as the rejection** — injected candidates (e.g. a C=C from a rejected cyclohexene) compute free atoms from the current `occupied` snapshot; deferring it to after the loop would expand that snapshot and produce wrong or missing injections.
- **Check-overlap methods only return a decision** — writing to `accepted` or `occupied` always happens at the caller level, keeping rule methods consistent with `SelfOverlapRules`.

### `CrossOverlapRules` — classifier

Group-level callable per `OverlapGroup`. Returns `True` to approve, `False` to reject. Dispatched via `OVERLAP_RULES_CONFIG["cross_overlap_rule"]`. All methods use a `{group}_approved` accumulator — custom logic per group, uniform interface.

| Method | Group | Threshold | Extra condition |
|---|---|---|---|
| `_check_bicyclic` | BICYCLIC_STRUCTURES | ≥ 3 shared atoms with any accepted | — |
| `_check_double_bonds` | DOUBLE_BONDS | ≥ 1 shared atom with any accepted double-bond | — |
| `_check_carbonyl` | CARBONYL_BOND_TYPES | ≥ 2 shared atoms with accepted carbonyl | priority comparison via `CrossOverlapComparator`; last-wins (see docstring) |
| `_check_ar_n` | Ar_N_BOND_TYPES | ≥ 3 shared atoms with any accepted Ar-N | — |

**Return type asymmetry vs `SelfOverlapRules`:** `CrossOverlapRules` returns `bool` rather than `RejectedCandidate | None` because cross-overlap conflicts are many-to-one and relational — the 1:1 `conflicting_with` model of `RejectedCandidate` does not apply.

---

## Overlap Injector

### `OverlapInjector` — side-effect rules

Fires when a rejected candidate can produce a valid alternative match. All rule methods receive `trigger: str` as last parameter — available in debugger, not used by logic.

| Method | Trigger | Condition | Action |
|---|---|---|---|
| `_inject_bicyclic` | `on_cross_reject` | formula == "cyclohexene" | Add C=C double bond matches from free atoms |
| `_inject_default` | `on_self_reject` | formula == "Cl-CR2-CR2-Cl" | Inject free C-Cl bonds for each free Cl from unoccupied atoms |
| `_inject_aromatic` | `on_accept` | formula in `{"Ar-OR", "Ar-NR2"}`, no 1-atom conflict | Append (aromatic C count − 1) duplicate copies |

### `inject_on_reject()` dispatch

```python
trigger == "on_accept"
    → OVERLAP_RULES_CONFIG[group]["on_accept"]              # group-level callable

trigger == "on_self_reject" | "on_cross_reject"
    → OVERLAP_RULES_CONFIG[group]["inject_rules"][formula]  # formula-level dict
```

**`_inject_aromatic` formula guard:** DEFAULT is a catch-all group — without an internal check, `_inject_aromatic` would fire for `benzene` and any DEFAULT formula with aromatic C. Guard: `if bmc.formula not in {"Ar-OR", "Ar-NR2"}: return False`.

---

## `OVERLAP_RULES_CONFIG` Structure

Defined in `overlap_rules.py` after all class definitions (method references resolve at module level). Wires all three domains — self-overlap rule, cross-overlap rule, inject rules, and on-accept hook — into one config per group.

---

## Import Chain (no circular imports)

```
bond_types.py               ← stdlib only
    ↑
cross_overlap_comparator.py ← imports bond_types
    ↑
overlap_rules.py            ← imports bond_types, cross_overlap_comparator, src.core.molecule
    ↑
substruct_matcher.py        ← imports overlap_rules, cross_overlap_comparator
```

---
