# OpenAPI — generated clients

The canonical **OpenAPI 3** document for the public HTTP API lives in the main **ServicePulse** application repository:

- Path: `public/openapi/servicepulse.yaml`
- Raw (example): `https://raw.githubusercontent.com/ethomasii/servicepulse/main/public/openapi/servicepulse.yaml`  
  (swap org/branch as needed)

This folder only documents how to generate **extra** clients beyond the hand-written SDKs in [`../libraries/`](../libraries/).

## Generate (example)

Install [OpenAPI Generator](https://openapi-generator.tech/) (CLI or Docker), then:

```bash
# From a clone of the ServicePulse app repo (not this integrations mirror):
openapi-generator-cli generate \
  -i public/openapi/servicepulse.yaml \
  -g go \
  -o /tmp/sp-go-client \
  --additional-properties=packageName=servicepulseapi
```

Repeat with `-g csharp`, `java`, `ruby`, etc. Regenerate when the YAML changes.

See also [`generate-clients.example.sh`](./generate-clients.example.sh).

## License

[MIT](../LICENSE)
