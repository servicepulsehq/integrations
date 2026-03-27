# Recipe: GitHub Actions vendor gate

Block deploy jobs when ServicePulse shows an outage on vendors you care about.

1. Add a **repository secret** `SERVICEPULSE_API_TOKEN` with your `sp_…` token.
2. Reference the composite action from [servicepulsehq/integrations](https://github.com/servicepulsehq/integrations):

```yaml
jobs:
  gate:
    runs-on: ubuntu-latest
    steps:
      - uses: servicepulsehq/integrations/github-actions/vendor-gate@main
        with:
          token: ${{ secrets.SERVICEPULSE_API_TOKEN }}
          vendor_slugs: stripe,snowflake
```

3. Add `needs: [gate]` to downstream jobs.

The composite action runs [`../scripts/check_stack.py`](../scripts/check_stack.py). The same script powers [GitLab CI](./gitlab-ci-vendor-gate.md) and [Azure Pipelines](./azure-devops-vendor-gate.md).

Full notes: [`../github-actions/README.md`](../github-actions/README.md).
