# Recipe: Verify outbound webhooks

ServicePulse (Team) can POST incident payloads to your URL with an HMAC.

- Prefer header **`X-Signature`**: lowercase **hex** digest of the **raw** JSON body using your webhook secret.
- Some docs mention **`X-ServicePulse-Signature: sha256=<hex>`**; accept both for forward compatibility.

Starters:

- [Express](../webhook-starters/nodejs-express/)
- [FastAPI](../webhook-starters/python-fastapi/)

Always verify **before** parsing JSON, using the raw body bytes.
