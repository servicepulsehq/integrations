# Azure Pipelines — ServicePulse vendor gate

Run [`scripts/check_stack.py`](../scripts/check_stack.py) before deployment stages—the same logic as [GitHub Actions](../github-actions/) and [GitLab CI](../gitlab-ci/).

## 1. Secret variable

In **Pipelines → Library** (variable group) or **Edit pipeline → Variables**, create a **secret** variable, for example:

- **Name:** `SERVICEPULSE_API_TOKEN`  
- **Value:** your `sp_…` token  

The example YAML maps this to the env var **`SERVICEPULSE_TOKEN`** expected by the script.

## 2. Pipeline

Use [azure-pipelines.example.yml](./azure-pipelines.example.yml) as a template. It uses the **Ubuntu** hosted image (`python3` + `curl` available).

Pin the **`SERVICEPULSE_CHECK_SCRIPT`** URL to a **commit SHA** instead of `main` when you depend on this in production.

### Self-hosted agents / air-gapped

Copy `check_stack.py` into your repo and invoke it with a **Python** task or `script:` path—no `curl` required.

## License

[MIT](../LICENSE)
