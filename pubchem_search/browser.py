from __future__ import annotations

import json
import random
from dataclasses import dataclass
from typing import Literal, Optional, cast
from urllib.parse import urlencode
from urllib.request import Request, urlopen

import pubchempy as pcp


class PubChemSearchError(RuntimeError):
    pass


@dataclass(frozen=True)
class PubSearchResult:
    """Result of a PubChem SMARTS search (one call)."""

    smarts: str
    kind: str
    limit: int
    randomize: bool
    oversample: int
    requested_cids: int
    returned_smiles: list[str]

    def __str__(self) -> str:
        n = len(self.returned_smiles)

        lines = "\n".join(
            f"  {i + 1:>4}. {s}" for i, s in enumerate(self.returned_smiles)
        )

        return (
            "PubSearchResult(\n"
            f"  kind={self.kind!r}, limit={self.limit}, randomize={self.randomize}, oversample={self.oversample}\n"
            f"  requested_cids={self.requested_cids}, returned_smiles={n}\n"
            f"  smarts={self.smarts!r}\n"
            "  matching_smiles=\n"
            f"{lines}\n"
            ")"
        )

    def __repr__(self) -> str:
        # Make notebooks show the pretty format too.
        return str(self)


class PubChemSearch:
    _BASE = "https://pubchem.ncbi.nlm.nih.gov/rest/pug"

    def lookup_matching_smiles(
        self,
        smarts: str,
        *,
        limit: int = 100,
        kind: Literal["ConnectivitySMILES", "IsomericSMILES"] = "ConnectivitySMILES",
        randomize: bool = False,
        oversample: int = 2000,
    ) -> PubSearchResult:
        if limit < 1:
            raise PubChemSearchError(f"Limit must be more than 1")

        fetch_n = oversample if randomize else limit
        cids = self._fastsubstructure_smarts_to_cids(smarts, max_records=fetch_n)
        if not cids:
            raise PubChemSearchError(
                f"No matches - no Compound ID (CID) was matched for given smarts: {smarts}"
            )

        if randomize:
            if len(cids) > limit:
                cids = random.sample(cids, k=limit)
            else:
                random.shuffle(cids)

        cid_args = cast(list[str | int], list(cids))
        props_raw = pcp.get_properties([kind], cid_args, namespace="cid") or []
        props = cast(list[dict[str, object]], props_raw)

        cid_to_smiles: dict[int, str] = {}
        for row in props:
            cid_val = row.get("CID")
            s_val = row.get(kind)
            if isinstance(cid_val, int) and isinstance(s_val, str) and s_val:
                cid_to_smiles[cid_val] = s_val

        smiles = [cid_to_smiles[cid] for cid in cids if cid in cid_to_smiles]

        return PubSearchResult(
            smarts=smarts,
            kind=kind,
            limit=limit,
            randomize=randomize,
            oversample=oversample,
            requested_cids=len(cids),
            returned_smiles=smiles,
        )

    def _fastsubstructure_smarts_to_cids(
        self, smarts: str, *, max_records: int
    ) -> list[int]:
        url = (
            f"{self._BASE}/compound/fastsubstructure/smarts/cids/JSON"
            f"?{urlencode({'MaxRecords': str(int(max_records))})}"
        )
        body = urlencode({"smarts": smarts}).encode("utf-8")

        req = Request(url, data=body, method="POST")
        req.add_header("Content-Type", "application/x-www-form-urlencoded")

        try:
            with urlopen(req, timeout=60) as resp:
                payload = json.loads(resp.read().decode("utf-8"))
        except Exception as e:
            raise PubChemSearchError(f"SMARTS search failed: {e}") from e

        raw = payload.get("IdentifierList", {}).get("CID", []) or []
        out: list[int] = []
        for x in raw:
            try:
                cid = int(x)
            except (TypeError, ValueError):
                continue
            if cid > 0:
                out.append(cid)
        return out
