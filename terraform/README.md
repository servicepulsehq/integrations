# Terraform — ServicePulse

- **[`modules/stack_health`](./modules/stack_health/)** — calls **`GET /api/v1/tracked-vendors`** during plan/apply and **fails** if your stack is unhealthy (Terraform **check** block; requires Terraform **≥ 1.5**).

A full **Terraform provider** is not shipped here yet; the HTTP module covers the common “block apply when Stripe is down” pattern without maintaining provider binaries. See [`providers/README.md`](./providers/README.md) for notes if you want to build one.

## License

[MIT](../LICENSE)
