# ServicePulse outbound webhook — FastAPI starter

Verifies **`X-Signature`** (hex HMAC-SHA256 of the raw JSON body) the same way as the [Express starter](../nodejs-express/).

## Run

```bash
pip install -r requirements.txt
set SERVICEPULSE_WEBHOOK_SECRET=your_webhook_secret
uvicorn main:app --host 0.0.0.0 --port 8000
```

Webhook URL: `http://localhost:8000/webhooks/servicepulse`

## License

[MIT](../../LICENSE)
