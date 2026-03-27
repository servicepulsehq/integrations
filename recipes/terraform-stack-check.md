# Recipe: Terraform stack check

Use the [`stack_health`](../terraform/modules/stack_health/) module so **`terraform apply`** fails when vendors are unhealthy.

```hcl
module "servicepulse" {
  source = "github.com/servicepulsehq/integrations//terraform/modules/stack_health?ref=main"

  api_token    = var.servicepulse_api_token
  vendor_slugs = ["stripe", "snowflake"]
}
```

Export `TF_VAR_servicepulse_api_token` in CI or use a secrets backend — never commit the token.

Requires Terraform **≥ 1.5** and the **http** provider **≥ 3.4**.
