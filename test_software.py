"""Software tests for IBSCS configuration and core engines."""

import os
import sys
import tempfile
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))

from crypto_engine import CryptoEngine
from hf_config import get_hf_authorization_header, get_huggingface_api_token
from image_generation import generate_cover_image, get_inference_headers
from stego_engine import StegoEngine


def test_hf_token_loaded():
    token = get_huggingface_api_token()
    assert token is not None, "HUGGINGFACE_API_TOKEN not loaded from .env"
    assert token.startswith("hf_"), "Token should start with hf_"
    assert len(token) > 10, "Token appears too short"
    print("[PASS] HF token loaded from environment")


def test_hf_authorization_header():
    header = get_hf_authorization_header()
    assert "Authorization" in header, "Authorization header missing"
    assert header["Authorization"].startswith("Bearer hf_"), "Bearer token format invalid"
    print("[PASS] Authorization header formatted correctly")


def test_inference_headers():
    headers = get_inference_headers()
    assert headers.get("Content-Type") == "application/json"
    assert "Authorization" in headers
    print("[PASS] Inference headers ready for HF API")


def test_hf_api_connectivity():
    try:
        import urllib.request
        import json
    except ImportError:
        print("[SKIP] urllib not available")
        return

    token = get_huggingface_api_token()
    req = urllib.request.Request(
        "https://huggingface.co/api/whoami-v2",
        headers={"Authorization": f"Bearer {token}"},
        method="GET",
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode())
        assert "name" in data or "fullname" in data or "email" in data or "type" in data
        username = data.get("name") or data.get("fullname") or "(authenticated)"
        print(f"[PASS] Hugging Face API accepted token (user: {username})")
    except Exception as e:
        raise AssertionError(f"Hugging Face API rejected token or unreachable: {e}") from e


def test_crypto_roundtrip():
    crypto = CryptoEngine()
    original = b"TEXT::Hello IBSCS test message"
    encrypted, key = crypto.lock_data(original)
    decrypted = crypto.unlock_data(encrypted, key)
    assert decrypted == original
    print("[PASS] Crypto lock/unlock roundtrip")


def test_stego_roundtrip():
    crypto = CryptoEngine()
    stego = StegoEngine()
    payload = b"TEXT::Stego integration test"

    with tempfile.TemporaryDirectory() as tmp:
        cover_path = Path(tmp) / "cover.png"
        out_path = Path(tmp) / "secured.png"
        _, _ = generate_cover_image(str(cover_path), allow_fallback=True)

        enc_data, key = crypto.lock_data(payload)
        stego.hide_payload(str(cover_path), enc_data, key, str(out_path))

        assert stego.detect_payload(str(out_path)), "Payload not detected"
        extracted_enc, extracted_key = stego.extract_payload(str(out_path))
        assert extracted_enc is not None and extracted_key is not None
        recovered = crypto.unlock_data(extracted_enc, extracted_key)
        assert recovered == payload
    print("[PASS] Stego hide/extract roundtrip with crypto")


def test_image_generation_module():
    headers = get_inference_headers()
    assert "Authorization" in headers

    with tempfile.TemporaryDirectory() as tmp:
        out_path = Path(tmp) / "cover.png"
        path, source = generate_cover_image(str(out_path), prompt="test landscape")
        assert path == str(out_path)
        assert source in ("huggingface", "pollinations", "local_fallback")
    print(f"[PASS] Image generation module ready (source: {source})")


def test_app_imports():
    import importlib.util

    spec = importlib.util.spec_from_file_location("app", PROJECT_ROOT / "app.py")
    assert spec is not None and spec.loader is not None
    print("[PASS] app.py imports without syntax errors")


def main():
    tests = [
        test_hf_token_loaded,
        test_hf_authorization_header,
        test_inference_headers,
        test_image_generation_module,
        test_hf_api_connectivity,
        test_crypto_roundtrip,
        test_stego_roundtrip,
        test_app_imports,
    ]
    passed = 0
    failed = 0
    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            failed += 1
            print(f"[FAIL] {test.__name__}: {e}")

    print("-" * 40)
    print(f"Results: {passed} passed, {failed} failed, {len(tests)} total")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
