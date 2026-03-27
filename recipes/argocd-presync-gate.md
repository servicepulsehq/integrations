# Recipe: Argo CD PreSync gate

Before Argo syncs your app, run a Job that calls ServicePulse:

1. Copy [`../gitops/argo-cd/presync-job.yaml`](../gitops/argo-cd/presync-job.yaml) into your manifests.
2. Create the `servicepulse-api` secret with key `token` = `sp_…`.
3. Set `namespace` and optional `SERVICEPULSE_VENDOR_SLUGS`.

If the hook fails, the sync stops and you avoid rolling out during a dependency outage.

See [`../gitops/argo-cd/README.md`](../gitops/argo-cd/README.md).
