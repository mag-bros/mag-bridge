# Test Report: `test_substruct_matching.py`

**Baseline commit:** `2502c688fd7bfe911c2380ef3b6e0c9b14defa26`
**Current state:** working tree (sort migration + CROSS_OVERLAP_RULES restructure)

---

## Summary

| | Baseline | Current |
|---|---|---|
| Passed | 353 | 354 |
| Failed | 40 | 39 |
| Skipped | 2 | 2 |

**Net change: +1 passing**

---

## Test Fixed (baseline failing → current passing)

| ID | SMILES |
|---|---|
| `<151>` | `CCC(=O)OCC(=O)[C@]1(CC[C@@H]2[C@@]1(C[C@@H]([C@H]3[C@H]2CCC4=CC(=O)C=C[C@]34C)O)C)OC(=O)OCC` |

---

## Tests Failing in Both Baseline and Current (39 tests)

| ID | SMILES |
|---|---|
| `<5>` | `CC1(C(C1C(=O)OC(C#N)C2=CC(=CC=C2)OC3=CC=CC=C3)C=C(Cl)Cl)C` |
| `<18>` | `CCCC(C)C1(C(=O)NC(=O)NC1=O)CC=C` |
| `<61>` | `C1C2C1(C(=O)NC2=O)C3=CC=CC=C3` |
| `<150>` | `CCOC1=NC2=CC=CC(=C2N1CC3=CC=C(C=C3)C4=CC=CC=C4C5=NNN=N5)C(=O)OC(C)OC(=O)OC6CCCCC6` |
| `<152>` | `C[C@@]12[C@H]3CC[C@@H]([C@@]1(C(=O)OC2=O)C)O3` |
| `<155>` | `CC(C)[C@H]1C(=O)OC(=O)N1C(=O)OCC2=CC=CC=C2` |
| `<156>` | `COC(=O)N1CC(=O)OC1=O` |
| `<199>` | `CCOC(=O)CCC(=O)CC1(C2(C3(C4(C1(C5(C2(C3(C(C45Cl)(Cl)Cl)Cl)Cl)Cl)Cl)Cl)Cl)Cl)O` |
| `<200>` | `C1C2C3C4C1C5(C2C6(C3(C(C4(C56Cl)Cl)(Cl)Cl)Cl)Cl)O` |
| `<203>` | `C1(=C(C2(C3(C(C1(C2(Cl)Cl)Cl)(C(=C(C3(Cl)Cl)Cl)Cl)Cl)Cl)Cl)Cl)Cl` |
| `<204>` | `C12C3C(C4C1C5(C(C3(C4(C5(Cl)Cl)Cl)Cl)Cl)Cl)C6C2O6` |
| `<205>` | `C1C2C=CC1(C3(C2C4(CC3(C(=C4Cl)Cl)Cl)Cl)Cl)Cl` |
| `<211>` | `CC1(C2(CC(C1(C3CC3(Cl)Cl)Cl)(C(C2)(Cl)Cl)Cl)Cl)C` |
| `<212>` | `C1C2C3C4C1C5C2C6(C3(C4(C5(C6(Cl)Cl)Cl)Cl)Cl)Cl` |
| `<213>` | `C12(C3(C4(C1(C5(C2(C3(C45Cl)F)F)Cl)F)F)F)F` |
| `<217>` | `C1C2(C1(C3(CC3(C4(C2=CC=CC4Cl)Cl)Cl)Cl)Cl)Cl` |
| `<219>` | `C1CC2(CC1=C3C2(C(C(C3(Cl)Cl)(Cl)Cl)(Cl)Cl)Cl)Cl` |
| `<223>` | `C1C(C2CC(C3(C2C1C4C3(C4(Cl)Cl)Cl)Cl)(Cl)Cl)C=O` |
| `<230>` | `C12(C3(C4(C1(C5(C2(C3(C45Cl)Cl)Cl)Cl)Cl)Cl)Cl)Cl` |
| `<232>` | `ClC(C)(C)C(C)(Cl)C(C)(Cl)C(C)(Cl)C(C)(Cl)C` |
| `<243>` | `C(C(=O)OC(=O)C(Cl)Cl)(Cl)Cl` |
| `<251>` | `C1CCC2(CCCCC2(C1)Br)Br` |
| `<252>` | `C12(C3(C4(C1(C5(C2(C3(C45Br)Br)Br)Br)Br)Br)Br)Br` |
| `<254>` | `C(C(C)(C(C)(C(C)(Br)C(C)(Br)C)Br)Br)(C)(Br)C` |
| `<260>` | `C1(=C(C(=C(C(=C1Br)Br)Br)Br)Br)OC2=C(C(=C(C(=C2Br)Br)Br)Br)Br` |
| `<264>` | `C1=CC=C2C(=C1)C3=CC=CC=C3[I+]2` |
| `<275>` | `CNCCCN1C2=CC=CC=C2CCC3=CC=CC=C31` |
| `<295>` | `C1=CC=C(C=C1)C(=O)OOC(=O)C2=CC=CC=C2` |
| `<296>` | `C1=CC=C2C(=C1)C(=O)OC2=O` |
| `<316>` | `CC1([C@H]([C@H]1C(=O)O[C@H](C#N)C2=CC(=CC=C2)OC3=CC=CC=C3)C=C(Br)Br)C` |
| `<328>` | `CC1=CC(=C(C2=C1C(=O)OC3=C(O2)C4=C(C(=C3C)O)C(=O)OC4O)C=O)OC` |
| `<330>` | `C1=CC=C2C(=C1)C(=O)OC23C4=C(C=C(C=C4)O)OC5=C3C=CC(=C5)[O-]` |
| `<332>` | `CN1CCN(CC1)CCCN2C3=CC=CC=C3SC4=C2C=C(C=C4)C(Cl)(Br)I` |
| `<361>` | `CCC1=C(C(=CC=C1)/C(=N/N=C(\\C)/C2=CC=CCC2(C)C)/C=C=C)F` |
| `<370>` | `CC(=O)C#CC(=O)C` |
| `<371>` | `CC(C)(C)C#CC(=O)C#CC(C)(C)C` |
| `<374>` | `C#CC(=O)C#C` |
| `<394>` | `C1=CC=C(C=C1)N(C2=CC=CC=C2)C3=NC(=NC(=N3)N)CCl` |
| `<395>` | `C1=C(C=C(C(=C1Br)OC2=NC(=NC(=N2)OC3=C(C=C(C=C3Br)Br)Br)OC4=C(C=C(C=C4Br)I)I)I)I` |
