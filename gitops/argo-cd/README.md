# Argo CD — PreSync vendor gate

[`presync-job.yaml`](./presync-job.yaml) runs a **PreSync** hook before your app syncs. It calls ServicePulse **`GET /api/v1/tracked-vendors`** with a token from a Kubernetes **Secret** and fails the hook (blocking sync) when vendors are unhealthy.

## Setup

1. Create a secret with your personal API token:

   ```bash
   kubectl create secret generic servicepulse-api -n your-namespace \
     --from-literal=token='sp_your_token'
   ```

2. Add the Job manifest to the same Argo CD app (or a dedicated “gate” app) and set **`namespace`** to your workload namespace.

3. Optionally set **`SERVICEPULSE_VENDOR_SLUGS`** to `stripe,snowflake` instead of checking every tracked vendor.

The inline Python matches [`scripts/check_stack.py`](../../scripts/check_stack.py).

## License

[MIT](../../LICENSE)
