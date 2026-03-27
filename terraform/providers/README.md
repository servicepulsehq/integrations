# Terraform provider (not shipped)

A first-party **`terraform-provider-servicepulse`** could expose data sources (e.g. `servicepulse_tracked_vendors`) and resources for advanced automation. That requires:

- Go, HashiCorp **terraform-plugin-framework**, release signing, and registry publishing.
- Ongoing compatibility with API versioning.

Until then, use the [**HTTP `stack_health` module**](../modules/stack_health/) or call **`GET /api/v1/tracked-vendors`** from a `local-exec` / CI step.

Community template: [Terraform Plugin Framework scaffolding](https://developer.hashicorp.com/terraform/plugin/framework).

## License

[MIT](../../LICENSE)
