# @servicepulsehq/client

TypeScript / Node **Personal API** client for **`GET /api/v1/tracked-vendors`** and **`assertStackHealthy`**, aligned with [`servicepulse-client`](../../servicepulse-client/) (Python).

**Requirements:** Node **18+** (global `fetch`).

## Install from Git

```bash
npm install "github:servicepulsehq/integrations#main:libraries/servicepulse-client-js"
```

If your npm version does not support the `:path` suffix, clone [servicepulsehq/integrations](https://github.com/servicepulsehq/integrations) and:

```bash
npm install ./libraries/servicepulse-client-js
```

## Usage

```ts
import { ServicePulseClient, StackNotHealthyError } from "@servicepulsehq/client";

const client = new ServicePulseClient(process.env.SERVICEPULSE_API_TOKEN!);

try {
  await client.assertStackHealthy(["stripe", "snowflake"]);
} catch (e) {
  if (e instanceof StackNotHealthyError) {
    console.error(e.message, e.unhealthy, e.missingSlugs);
    process.exit(1);
  }
  throw e;
}
```

Options on `assertStackHealthy(slugs, { allowMaintenance, allowUnknown, extraBadStatuses })` match the Python client.

## Build (maintainers)

```bash
npm install
npm run build
```

Published artifact is **`dist/`** (commit built output if you consume via git without a build step, or run `prepack` before packing).

## License

[MIT](../../LICENSE)
