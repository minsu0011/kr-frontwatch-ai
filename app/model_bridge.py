"""Hash-gated bridge from the Desktop API shell to the Laptop frozen KR model.

This endpoint replays the 12 frozen feature-capsule rows only. It is not live
inference, training, or a fallback for an unsupported security/date.
"""
from functools import lru_cache
from hashlib import sha256
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
RUNTIME = ROOT / "model_runtime"
MANIFEST = RUNTIME / "MODEL_RUNTIME_MANIFEST.json"


def _sha(path: Path) -> str:
    h = sha256()
    with path.open("rb") as f:
        while block := f.read(4 * 1024 * 1024):
            h.update(block)
    return h.hexdigest()


def _verify() -> dict:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8-sig"))
    if manifest.get("schema") != "KR_FRONTWATCH_MODEL_RUNTIME_MANIFEST_V1":
        raise RuntimeError("Unexpected model runtime manifest")
    for item in manifest["files"]:
        target = (RUNTIME / item["relative_path"]).resolve()
        if not target.is_relative_to(RUNTIME.resolve()) or not target.is_file():
            raise RuntimeError("Unsafe or missing model runtime file")
        if target.stat().st_size != item["bytes"] or _sha(target) != item["sha256"]:
            raise RuntimeError("Model runtime integrity mismatch")
    return manifest


@lru_cache(maxsize=1)
def _loaded() -> tuple[dict, dict[str, dict]]:
    manifest = _verify()
    runtime_text = str(RUNTIME)
    if runtime_text not in sys.path:
        sys.path.insert(0, runtime_text)
    from submission_final.replay import replay
    rows = replay(RUNTIME)
    index = {row["security_code"]: row for row in rows}
    if len(index) != 12:
        raise RuntimeError("Unexpected frozen model replay geometry")
    return manifest, index


def status() -> dict:
    manifest, index = _loaded()
    return {
        "ready": True,
        "mode": "FROZEN_FEATURE_CAPSULE_REPLAY_ONLY",
        "codes": sorted(index),
        "analysis_date": "2023-12-28",
        "model_sha256": manifest["model_sha256"],
        "adapter_sha256": manifest["adapter_sha256"],
        "live_inference_enabled": False,
        "training_enabled": False,
    }


def replay_code(code: str, frozen_row: dict | None) -> dict:
    if not re.fullmatch(r"[0-9]{6}", code):
        raise ValueError("EXACT_SIX_DIGIT_SECURITY_CODE_REQUIRED")
    manifest, index = _loaded()
    if code not in index:
        raise KeyError("MODEL_CAPSULE_CODE_NOT_AVAILABLE")
    result = index[code]
    if frozen_row is None or frozen_row.get("analysis_date") != "2023-12-28":
        raise KeyError("FROZEN_CACHE_BINDING_NOT_AVAILABLE")
    keys = ["risk_index", "confidence_index", "kr_market_anomaly", "activation_index", "us_donor_support_effective", "risk_level"]
    parity = all(
        result[k] == frozen_row[k] if isinstance(result[k], str)
        else abs(float(result[k]) - float(frozen_row[k])) <= 1e-8
        for k in keys
    )
    if not parity:
        raise RuntimeError("MODEL_TO_FROZEN_API_PARITY_MISMATCH")
    return {
        "security_code": code,
        "analysis_date": "2023-12-28",
        "mode": "FROZEN_FEATURE_CAPSULE_REPLAY_ONLY",
        "model_output": result,
        "frozen_api_parity": True,
        "live_inference_enabled": False,
        "training_performed": False,
        "model_sha256": manifest["model_sha256"],
        "adapter_sha256": manifest["adapter_sha256"],
        "scientific_validation_pass": False,
        "production_qualified": False,
    }
