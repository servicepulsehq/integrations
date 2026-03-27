# Flux CD — vendor gate patterns

Flux does not use Argo-style sync hooks. Equivalent options:

1. **Terraform + `stack_health` module** — run `terraform apply` in a Flux **`Terraform`** object or in CI before you bump image tags.
2. **GitHub Actions (or other CI)** — use [`../../github-actions/vendor-gate`](../../github-actions/vendor-gate) on the PR or release pipeline that updates the Flux `GitRepository` / `Kustomization`.
3. **Init container / admission** — run the same check as an init container before your main workload starts (similar cost to PreSync, but at pod schedule time).

For a **Kubernetes Job** triggered manually or from a CI system, you can reuse the Job spec from [`../argo-cd/presync-job.yaml`](../argo-cd/presync-job.yaml) without Argo annotations.

## License

[MIT](../../LICENSE)
