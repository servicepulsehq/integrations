# Recipe: Azure Pipelines vendor gate

1. Create a **secret** pipeline variable **`SERVICEPULSE_API_TOKEN`** (your `sp_…` token).
2. Use a **Verify** stage that runs the bash step from [`../azure-pipelines/azure-pipelines.example.yml`](../azure-pipelines/azure-pipelines.example.yml) (downloads [`scripts/check_stack.py`](../scripts/check_stack.py) then `python3`).
3. Set **`dependsOn: Verify`** (and `condition: succeeded()`) on deploy stages.

Pin the script URL to a **commit SHA** instead of `main` when this is load-bearing.

Full notes: [`../azure-pipelines/README.md`](../azure-pipelines/README.md).
