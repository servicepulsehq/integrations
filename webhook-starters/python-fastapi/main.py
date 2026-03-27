"""
ServicePulse outbound webhook — FastAPI starter.
Verifies X-Signature (HMAC-SHA256 hex of raw body) or X-ServicePulse-Signature: sha256=<hex>.
"""

from __future__ import annotations

import hashlib
import hmac
import os
import re
from fastapi import FastAPI, Header, HTTPException, Request, Response

SECRET = (os.environ.get("SERVICEPULSE_WEBHOOK_SECRET") or "").encode("utf-8")

app = FastAPI(title="ServicePulse webhook receiver")


def _expected_sig(raw: bytes) -> str:
    return hmac.new(SECRET, raw, hashlib.sha256).hexdigest()


def _extract_sig(x_signature: str | None, x_sp: str | None) -> str:
    if x_signature:
        return x_signature.strip()
    if x_sp:
        m = re.match(r"^sha256=(.+)$", x_sp.strip(), re.I)
        return (m.group(1) if m else x_sp).strip()
    return ""


def _const_eq(a: str, b: str) -> bool:
    return hmac.compare_digest(a.encode("utf-8"), b.encode("utf-8"))


@app.post("/webhooks/servicepulse")
async def servicepulse(
    request: Request,
    x_signature: str | None = Header(default=None, alias="X-Signature"),
    x_servicepulse_signature: str | None = Header(default=None, alias="X-ServicePulse-Signature"),
) -> Response:
    if not SECRET:
        raise HTTPException(500, "Set SERVICEPULSE_WEBHOOK_SECRET")
    raw = await request.body()
    got = _extract_sig(x_signature, x_servicepulse_signature)
    if not got or not _const_eq(got, _expected_sig(raw)):
        raise HTTPException(401, "Invalid signature")
    # Parse only after verify
    import json

    try:
        payload = json.loads(raw.decode("utf-8"))
    except json.JSONDecodeError as e:
        raise HTTPException(400, "Invalid JSON") from e
    print("Verified ServicePulse webhook:", payload.get("trigger"), (payload.get("vendor") or {}).get("slug"))
    return Response(status_code=204)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
