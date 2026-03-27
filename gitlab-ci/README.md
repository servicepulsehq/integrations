# GitLab CI — ServicePulse vendor gate

Run the shared [`scripts/check_stack.py`](../scripts/check_stack.py) before deploy stages. Same behavior as [GitHub Actions](../github-actions/) and [Azure Pipelines](../azure-pipelines/).

## 1. CI/CD variable

In **Settings → CI/CD → Variables**, add:

- **Key:** `SERVICEPULSE_TOKEN`
- **Value:** your `sp_…` personal API token  
- Masked + (recommended) **Protected** if only protected branches deploy

Optional variables (unprotected or same scope):

- `SERVICEPULSE_VENDOR_SLUGS` — e.g. `stripe,snowflake` (empty = all tracked)
- `SERVICEPULSE_ALLOW_MAINTENANCE` — `true` / `false`
- `SERVICEPULSE_ALLOW_UNKNOWN` — `true` / `false`
- `SERVICEPULSE_BASE_URL` — default `https://servicepulse.dev`

## 2. Pipeline

See [`.gitlab-ci.example.yml`](./.gitlab-ci.example.yml). It downloads the script from GitHub raw (pin a **commit SHA** in the URL for supply-chain stability) and runs `python3`.

### Vendoring the script

If runners cannot reach GitHub, copy `scripts/check_stack.py` into your repo and run:

```yaml
script:
  - python3 ci/servicepulse/check_stack.py
```

## License

[MIT](../LICENSE)
