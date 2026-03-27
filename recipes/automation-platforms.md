# Recipe: Zapier, n8n, Make, Pipedream

ServicePulse already supports native notification channels for several of these (see in-app **Settings → Notifications** on eligible plans). For **custom** flows:

1. **HTTP request** — call `GET https://servicepulse.dev/api/v1/tracked-vendors` with header `Authorization: Bearer sp_…`, then branch on JSON (e.g. loop vendors, test `currentStatus`).
2. **Outbound webhook** — point ServicePulse at an **n8n Webhook** or **Zapier Catch Hook** node; verify the signature using the same rules as [outbound-webhook-signature.md](./outbound-webhook-signature.md).
3. **Inbound (push)** — forward vendor status formats to ServicePulse [push ingest](https://servicepulse.dev/docs) if you centralize events elsewhere.

Keep secrets in the platform’s vault; rotate personal API tokens if a flow leaks.
