"""
Example DAG: gate expensive work on ServicePulse vendor health.

Requires: servicepulse-airflow (see README in this folder).
"""

from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.bash import BashOperator
# Install: pip install …/libraries/airflow-servicepulse (see examples/airflow/README.md).
from servicepulse_airflow import ServicePulseVendorGateOperator

VENDOR_SLUGS = ["stripe", "snowflake"]

with DAG(
    dag_id="servicepulse_vendor_gate_example",
    start_date=datetime(2024, 1, 1),
    schedule="@daily",
    catchup=False,
    default_args={"owner": "data-platform", "retries": 1, "retry_delay": timedelta(minutes=5)},
    tags=["servicepulse", "example"],
) as dag:
    gate = ServicePulseVendorGateOperator(
        task_id="assert_vendors_operational",
        vendor_slugs=VENDOR_SLUGS,
    )

    downstream = BashOperator(
        task_id="expensive_job_placeholder",
        bash_command='echo "Replace with real workload"',
    )

    gate >> downstream
