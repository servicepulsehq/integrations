# Recipe: OpenAPI client generation

The machine-readable spec ships with the main app: `public/openapi/servicepulse.yaml`.

1. Clone the **ServicePulse application** repo (not only `integrations`).
2. Follow [`../openapi/README.md`](../openapi/README.md) and [`../openapi/generate-clients.example.sh`](../openapi/generate-clients.example.sh).
3. Commit generated code to **your** internal repo, or regenerate in CI.

Hand-maintained SDKs for the common “gate” use case remain [`servicepulse-client`](../servicepulse-client/) (Python), [`@servicepulsehq/client`](../libraries/servicepulse-client-js/), and [Go](../libraries/servicepulse-client-go/).
