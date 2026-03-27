# Recipe: GitLab CI vendor gate

1. Add **`SERVICEPULSE_TOKEN`** (masked) under **Settings → CI/CD → Variables**.
2. Copy the job from [`../gitlab-ci/.gitlab-ci.example.yml`](../gitlab-ci/.gitlab-ci.example.yml) into your `.gitlab-ci.yml`.
3. Make deploy jobs **`needs: [servicepulse_vendor_gate]`** (or your job name).

The job downloads [`scripts/check_stack.py`](../scripts/check_stack.py) from GitHub raw—**pin a commit SHA** in `SERVICEPULSE_CHECK_SCRIPT` for production.

Full notes: [`../gitlab-ci/README.md`](../gitlab-ci/README.md).
