# stack_health

Terraform **≥ 1.5** module: fetch tracked vendors and **fail** plan/apply when any selected vendor is not safe (same semantics as `servicepulse-client`).

## Usage

```hcl
module "servicepulse_gate" {
  source = "github.com/servicepulsehq/integrations//terraform/modules/stack_health?ref=main"

  api_token      = var.servicepulse_api_token # sp_… from TF_VAR_ or a secrets backend
  vendor_slugs   = ["stripe", "snowflake"]
  # allow_maintenance = true
}
```

Pass the token via environment (e.g. `TF_VAR_servicepulse_api_token`) or remote state / Vault — **do not** commit it.

## Requirements

- Provider **hashicorp/http** ≥ 3.4 (custom request headers).

## License

[MIT](../../../LICENSE)
