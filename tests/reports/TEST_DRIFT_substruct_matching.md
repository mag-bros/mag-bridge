# TEST_DRIFT Report

## Configuration

| Parameter | Value |
|---|---|
| **Timestamp** | `2026-03-08 02:54:41` |
| **Target** | `tests/core/test_substruct_matching.py::test_substruct_matches` |
| **Baseline Ref** | `bondtype-match-query-tool (9245985)` |
| **Current Ref** | `working tree (9245985)` |

## Summary

| Metric | Baseline | Current | Delta |
|---|---|---|---|
| **Total Tests** | 397 | 397 | +0 |
| **Passed** | 359 | 359 | +0 |
| **Failed** | 36 | 36 | +0 |
| **Skipped** | 2 | 2 | +0 |

## Consistently Failing (36 tests)

| Test Node | Error |
|---|---|
| `test_substruct_matches[<148> C1CSCCN1NC(=O)N(CCCl)N=O]` | `AssertionError: assert Counter({'RC(...1, 'C-Cl': 1}) == Counter({'RC(... 1, 'N=O': 1})` |
| `test_substruct_matches[<150> CCOC1=NC2=CC=CC(=C2N1CC3=CC=C(C=C3)C4=CC=CC=C4C5=NNN=N5)C(=O)OC(C)OC(=O)OC6CCCCC6]` | `AssertionError: assert Counter({'ben...midazole': 1}) == Counter({'ben...midazole': 1})` |
| `test_substruct_matches[<151> CCC(=O)OCC(=O)[C@]1(CC[C@@H]2[C@@]1(C[C@@H]([C@H]3[C@H]2CCC4=CC(=O)C=C[C@]34C)O)C)OC(=O)OCC]` | `AssertionError: assert Counter({'cyc...opentane': 1}) == Counter({'C=O...opentane': 1})` |
| `test_substruct_matches[<161> CN(C(=O)N)N=O]` | `AssertionError: assert Counter({'N=O...C(=O)NH2': 1}) == Counter({'RC(... 2, 'N=O': 1})` |
| `test_substruct_matches[<18> CCCC(C)C1(C(=O)NC(=O)NC1=O)CC=C]` | `AssertionError: assert Counter({'RC(...=CH-CH2-': 1}) == Counter({'RC(...=CH-CH2-': 1})` |
| `test_substruct_matches[<199> CCOC(=O)CCC(=O)CC1(C2(C3(C4(C1(C5(C2(C3(C(C45Cl)(Cl)Cl)Cl)Cl)Cl)Cl)Cl)Cl)Cl)O]` | `AssertionError: assert Counter() == Counter({'Cl-..., 'RCOOR': 1})` |
| `test_substruct_matches[<200> C1C2C3C4C1C5(C2C6(C3(C(C4(C56Cl)Cl)(Cl)Cl)Cl)Cl)O]` | `AssertionError: assert Counter() == Counter({'Cl-... 'R2CCl2': 1})` |
| `test_substruct_matches[<203> C1(=C(C2(C3(C(C1(C2(Cl)Cl)Cl)(C(=C(C3(Cl)Cl)Cl)Cl)Cl)Cl)Cl)Cl)Cl]` | `AssertionError: assert Counter({'C-C... 1, 'C=C': 1}) == Counter({'C-C... 1, 'C=C': 1})` |
| `test_substruct_matches[<204> C12C3C(C4C1C5(C(C3(C4(C5(Cl)Cl)Cl)Cl)Cl)Cl)C6C2O6]` | `AssertionError: assert Counter({'C-C... 'R2CCl2': 1}) == Counter({'cyc... 'R2CCl2': 1})` |
| `test_substruct_matches[<205> C1C2C=CC1(C3(C2C4(CC3(C(=C4Cl)Cl)Cl)Cl)Cl)Cl]` | `AssertionError: assert Counter({'C-C...lohexene': 2}) == Counter({'C-C...2-CR2-Cl': 2})` |
| `test_substruct_matches[<211> CC1(C2(CC(C1(C3CC3(Cl)Cl)Cl)(C(C2)(Cl)Cl)Cl)Cl)C]` | `AssertionError: assert Counter({'C-C...lohexane': 1}) == Counter({'R2C...2-CR2-Cl': 1})` |
| `test_substruct_matches[<212> C1C2C3C4C1C5C2C6(C3(C4(C5(C6(Cl)Cl)Cl)Cl)Cl)Cl]` | `AssertionError: assert Counter() == Counter({'Cl-... 'R2CCl2': 1})` |
| `test_substruct_matches[<213> C12(C3(C4(C1(C5(C2(C3(C45Cl)F)F)Cl)F)F)F)F]` | `AssertionError: assert Counter({'cyc...6, 'C-Cl': 2}) == Counter({'cyc...2-CR2-Cl': 1})` |
| `test_substruct_matches[<217> C1C2(C1(C3(CC3(C4(C2=CC=CC4Cl)Cl)Cl)Cl)Cl)Cl]` | `AssertionError: assert Counter({'C-C...lohexane': 1}) == Counter({'cyc...'C=C-C=C': 1})` |
| `test_substruct_matches[<219> C1CC2(CC1=C3C2(C(C(C3(Cl)Cl)(Cl)Cl)(Cl)Cl)Cl)Cl]` | `AssertionError: assert Counter({'R2C...lohexane': 1}) == Counter({'R2C...2-CR2-Cl': 1})` |
| `test_substruct_matches[<223> C1C(C2CC(C3(C2C1C4C3(C4(Cl)Cl)Cl)Cl)(Cl)Cl)C=O]` | `AssertionError: assert Counter({'cyc... 1, 'C=O': 1}) == Counter({'cyc...2-CR2-Cl': 1})` |
| `test_substruct_matches[<230> C12(C3(C4(C1(C5(C2(C3(C45Cl)Cl)Cl)Cl)Cl)Cl)Cl)Cl]` | `AssertionError: assert Counter({'C-C...lobutane': 6}) == Counter({'Cl-...lobutane': 6})` |
| `test_substruct_matches[<232> ClC(C)(C)C(C)(Cl)C(C)(Cl)C(C)(Cl)C(C)(Cl)C]` | `AssertionError: assert Counter({'Cl-...2, 'C-Cl': 2}) == Counter({'Cl-CR2-CR2-Cl': 4})` |
| `test_substruct_matches[<251> C1CCC2(CCCCC2(C1)Br)Br]` | `AssertionError: assert Counter({'C-B...lohexane': 2}) == Counter({'cyc...2-CR2-Br': 1})` |
| `test_substruct_matches[<252> C12(C3(C4(C1(C5(C2(C3(C45Br)Br)Br)Br)Br)Br)Br)Br]` | `AssertionError: assert Counter({'C-B...lobutane': 6}) == Counter({'Br-...lobutane': 6})` |
| `test_substruct_matches[<254> C(C(C)(C(C)(C(C)(Br)C(C)(Br)C)Br)Br)(C)(Br)C]` | `AssertionError: assert Counter({'Br-...2, 'C-Br': 1}) == Counter({'Br-CR2-CR2-Br': 4})` |
| `test_substruct_matches[<260> C1(=C(C(=C(C(=C1Br)Br)Br)Br)Br)OC2=C(C(=C(C(=C2Br)Br)Br)Br)Br]` | `AssertionError: assert Counter({'Ar-...'benzene': 2}) == Counter({'Ar-..., 'Ar-OR': 1})` |
| `test_substruct_matches[<264> C1=CC=C2C(=C1)C3=CC=CC=C3[I+]2]` | `AssertionError: assert Counter({'benzene': 2}) == Counter({'ben..., 'Ar-Ar': 1})` |
| `test_substruct_matches[<275> CNCCCN1C2=CC=CC=C2CCC3=CC=CC=C31]` | `AssertionError: assert Counter({'ben... 'Ar-NR2': 2}) == Counter({'ben... 'Ar-NR2': 1})` |
| `test_substruct_matches[<313> C1CC1C2(C3=C(C=CC(=C3)Br)NC(=O)N2)C#CC4=CN=CN=C4]` | `AssertionError: assert Counter({'ben...rimidine': 1}) == Counter({'RC(...rimidine': 1})` |
| `test_substruct_matches[<316> CC1([C@H]([C@H]1C(=O)O[C@H](C#N)C2=CC(=CC=C2)OC3=CC=CC=C3)C=C(Br)Br)C]` | `AssertionError: assert Counter({'Ar-..., 'RCOOR': 1}) == Counter({'C-B... 1, 'C=C': 1})` |
| `test_substruct_matches[<328> CC1=CC(=C(C2=C1C(=O)OC3=C(O2)C4=C(C(=C3C)O)C(=O)OC4O)C=O)OC]` | `AssertionError: assert Counter({'Ar-..., 'Ar-OH': 1}) == Counter({'Ar-..., 'Ar-OH': 1})` |
| `test_substruct_matches[<330> C1=CC=C2C(=C1)C(=O)OC23C4=C(C=C(C=C4)O)OC5=C3C=CC(=C5)[O-]]` | `AssertionError: assert Counter({'ben...'Ar-COOR': 1}) == Counter({'ben..., 'Ar-OR': 1})` |
| `test_substruct_matches[<332> CN1CCN(CC1)CCCN2C3=CC=CC=C3SC4=C2C=C(C=C4)C(Cl)(Br)I]` | `AssertionError: assert Counter({'ben... 1, 'R-I': 1}) == Counter({'ben... 1, 'C-I': 1})` |
| `test_substruct_matches[<361> CCC1=C(C(=CC=C1)/C(=N/N=C(\\C)/C2=CC=CCC2(C)C)/C=C=C)F]` | `AssertionError: assert Counter({'C=C...'benzene': 1}) == Counter({'R2C... 1, 'C=C': 1})` |
| `test_substruct_matches[<370> CC(=O)C#CC(=O)C]` | `AssertionError: assert Counter({'RC#... 1, 'C=O': 1}) == Counter({'RC#C-C(=O)R': 2})` |
| `test_substruct_matches[<371> CC(C)(C)C#CC(=O)C#CC(C)(C)C]` | `AssertionError: assert Counter({'C#C...C-C(=O)R': 1}) == Counter({'RC#C-C(=O)R': 2})` |
| `test_substruct_matches[<374> C#CC(=O)C#C]` | `AssertionError: assert Counter({'C#C...C-C(=O)R': 1}) == Counter({'RC#C-C(=O)R': 2})` |
| `test_substruct_matches[<394> C1=CC=C(C=C1)N(C2=CC=CC=C2)C3=NC(=NC(=N3)N)CCl]` | `AssertionError: assert Counter({'Ar-...1, 'C-Cl': 1}) == Counter({'ben...triazine': 1})` |
| `test_substruct_matches[<395> C1=C(C=C(C(=C1Br)OC2=NC(=NC(=N2)OC3=C(C=C(C=C3Br)Br)Br)OC4=C(C=C(C=C4Br)I)I)I)I]` | `AssertionError: assert Counter({'Ar-...triazine': 1}) == Counter({'Ar-...triazine': 1})` |
| `test_substruct_matches[<5> CC1(C(C1C(=O)OC(C#N)C2=CC(=CC=C2)OC3=CC=CC=C3)C=C(Cl)Cl)C]` | `AssertionError: assert Counter({'C-C... 1, 'C=C': 1}) == Counter({'C-C... 1, 'C=C': 1})` |

