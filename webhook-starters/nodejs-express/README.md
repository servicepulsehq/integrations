# ServicePulse outbound webhook — Express starter

Minimal **Express** server that accepts ServicePulse **Team** outbound webhooks and verifies **`X-Signature`** (HMAC-SHA256 of the raw JSON body, hex digest). The product also sends **`X-Timestamp`** (ISO time) for your own replay protection if you want to add it.

## Run

```bash
npm install
set SERVICEPULSE_WEBHOOK_SECRET=your_webhook_secret
npm start
```

Point ServicePulse **Settings → Notifications → Outbound webhook** at `https://your-host/webhooks/servicepulse`.

## Signature details

- Header **`X-Signature`**: `HMAC_SHA256(secret, raw_body_utf8)` as **lowercase hex** (this matches the current sender).
- Some documentation may show **`X-ServicePulse-Signature: sha256=<hex>`**; this starter accepts either form.

## License

[MIT](../../LICENSE)
