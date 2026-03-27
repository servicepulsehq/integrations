# GitHub Actions — ServicePulse vendor gate

Composite action that calls **`GET /api/v1/tracked-vendors`** with your **personal API token** and fails the job if any selected vendor is not safe to proceed (same rules as [`servicepulse-client`](../servicepulse-client/)). It runs the shared script [`scripts/check_stack.py`](../scripts/check_stack.py) (also used by [GitLab CI](../gitlab-ci/) and [Azure Pipelines](../azure-pipelines/)).

## Use the composite action

From another repository (after this folder is available on `main` in [servicepulsehq/integrations](https://github.com/servicepulsehq/integrations)):

```yaml
name: Deploy
on:
  push:
    branches: [main]

jobs:
  gate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: ServicePulse vendor gate
        uses: servicepulsehq/integrations/github-actions/vendor-gate@main
        with:
          token: ${{ secrets.SERVICEPULSE_API_TOKEN }}
          # vendor_slugs: "stripe,snowflake"   # optional; default = all tracked
          # allow_maintenance: "true"
          # base_url: "https://servicepulse.dev"

  deploy:
    needs: [gate]
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      # ... your deploy steps
```

Create **`SERVICEPULSE_API_TOKEN`** (or any name you prefer) in **Repository secrets** with a ServicePulse personal token (`sp_…`).

### Pinning

Prefer a **commit SHA** or **tag** instead of `@main` once you rely on this in production.

## Monorepo path

If you copy only this tree, the action path is `github-actions/vendor-gate` relative to the repo root.

## License

[MIT](../LICENSE)
