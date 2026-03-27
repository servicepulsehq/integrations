# Recipe: Node / TypeScript client

Use [`@servicepulsehq/client`](../libraries/servicepulse-client-js/) from a clone or Git dependency:

```bash
npm install ../path/to/integrations/libraries/servicepulse-client-js
```

```ts
import { ServicePulseClient } from "@servicepulsehq/client";
await new ServicePulseClient(process.env.SERVICEPULSE_API_TOKEN!).assertStackHealthy(
  ["stripe"],
  { allowMaintenance: false }
);
```

See the package [README](../libraries/servicepulse-client-js/README.md).
