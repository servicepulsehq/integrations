# Shared CI script — `check_stack.py`

Single **stdlib-only** Python entrypoint used by:

- [GitHub Actions](../github-actions/vendor-gate/) (bundled from this repo)
- [GitLab CI](../gitlab-ci/) (fetched with `curl` or vendored)
- [Azure Pipelines](../azure-pipelines/) (same)

## Environment variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `SERVICEPULSE_TOKEN` | yes | — | Personal API token (`sp_…`) |
| `SERVICEPULSE_BASE_URL` | no | `https://servicepulse.dev` | API origin |
| `SERVICEPULSE_VENDOR_SLUGS` | no | *(empty = all tracked)* | Comma-separated slugs |
| `SERVICEPULSE_ALLOW_MAINTENANCE` | no | `false` | `true` / `1` / `yes` to allow maintenance |
| `SERVICEPULSE_ALLOW_UNKNOWN` | no | `false` | `true` to allow unknown status |

## Run locally

```bash
export SERVICEPULSE_TOKEN=sp_your_token
python3 scripts/check_stack.py
```

## Raw URL (pin a commit SHA in production)

```
https://raw.githubusercontent.com/servicepulsehq/integrations/main/scripts/check_stack.py
```

## License

[MIT](../LICENSE)
