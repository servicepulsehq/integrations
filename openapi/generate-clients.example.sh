#!/usr/bin/env bash
# Example: run from a checkout of the ServicePulse *app* repo (contains public/openapi/servicepulse.yaml).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
SPEC="$ROOT/public/openapi/servicepulse.yaml"
if [[ ! -f "$SPEC" ]]; then
  echo "Expected OpenAPI spec at: $SPEC"
  echo "Run from the ServicePulse app monorepo (contains public/openapi/). This script lives in integrations/openapi/."
  exit 1
fi
docker run --rm -v "$ROOT:/local" openapitools/openapi-generator-cli:v7.10.0 generate \
  -i /local/public/openapi/servicepulse.yaml \
  -g go \
  -o /local/tmp-sp-go \
  --additional-properties=packageName=servicepulseapi
echo "Generated under ${ROOT}/tmp-sp-go (adjust -g and Docker output path as needed)."
