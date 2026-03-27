# servicepulse-probe — poll internal HTTP/DB, ping ServicePulse heartbeats
# Build: docker build -t servicepulse-probe:local .
# Run:   docker run --rm -v /path/to/config.json:/config.json:ro -e SERVICEPULSE_HEARTBEAT_API=... servicepulse-probe:local --config /config.json

FROM python:3.12-slim-bookworm

WORKDIR /app

# Postgres, MySQL, Snowflake, Databricks, SQL Server, Oracle (image is larger but turnkey)
COPY requirements-db.txt requirements-warehouse.txt requirements-sqlalchemy.txt pyproject.toml README.md ./
COPY src ./src
RUN pip install --no-cache-dir -r requirements-db.txt \
    && pip install --no-cache-dir -r requirements-warehouse.txt \
    && pip install --no-cache-dir -r requirements-sqlalchemy.txt \
    && pip install --no-cache-dir .

ENTRYPOINT ["servicepulse-probe"]
CMD ["--help"]
