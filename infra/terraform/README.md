# mynance — GCP Infrastructure (Terraform)

Production-quality, fully parametric Terraform for the **mynance** app
(FastAPI backend + React/Vite frontend) on Google Cloud.

## Architecture at a glance

```
                Internet
                   │
        Global external HTTP(S) LB  ── single static IP (always reserved)
        ┌──────────┴───────────┐
   app.<domain>            api.<domain>          (host-based routing)
        │                       │
 Cloud Run: frontend      Cloud Run: backend     (Cloud Run v2, ingress=INTERNAL_LB)
        │                       │
        └───── Direct VPC egress (subnet ENI) ────┘
                   │
                 VPC + subnet  (created here OR referenced from a Shared VPC)
                   │
        PSC endpoint (internal IP + forwarding rule)
                   │
        Cloud SQL Postgres (PSC-only, no public/private IP)
                   │
        DB password → Secret Manager → backend env via secret ref
```

Key design points:

- **Cloud Run v2** (`google_cloud_run_v2_service`), ingress
  `INGRESS_TRAFFIC_INTERNAL_LOAD_BALANCER` (reachable only via the LB).
- **Direct VPC egress** (`vpc_access.network_interfaces.subnetwork`), **no**
  Serverless VPC Access connector.
- **Cloud SQL via PSC**: instance has `ipv4_enabled = false`,
  `psc_config.psc_enabled = true`; a consumer PSC endpoint
  (`google_compute_address` + `google_compute_forwarding_rule`) lives in the
  VPC and the backend connects to its internal IP.
- **Certificate Manager** managed certs (DNS-authorized), **not** the legacy
  `google_compute_managed_ssl_certificate`.
- **GCS remote state** with a `bootstrap/` config to solve the chicken-and-egg.

## Prerequisites

- Terraform **>= 1.5** (developed/validated on 1.14.x).
- `gcloud` authenticated with Application Default Credentials:
  `gcloud auth application-default login`.
- A GCP project and billing enabled.
- IAM to create networks, Cloud Run, Cloud SQL, LB, Secret Manager, IAM,
  and to enable services.

### APIs enabled (parametrically, via `google_project_service`)

`run`, `sqladmin`, `compute`, `certificatemanager`, `secretmanager`,
`servicenetworking`, `dns` (optional), `iam`, `serviceusage`.
Toggle with `enable_apis` (default `true`).

## Bootstrap → init → apply (exact commands)

All commands are run from `infra/terraform/`.

### 1. Bootstrap the GCS state bucket (local state, run once)

```bash
cd infra/terraform/bootstrap
cp terraform.tfvars.example terraform.tfvars   # edit project_id + bucket name
terraform init
terraform apply
# note the output: state_bucket_name
cd ..
```

### 2. Initialize the root config against that bucket

```bash
terraform init \
  -backend-config="bucket=<state_bucket_name>" \
  -backend-config="prefix=mynance/root"
```

### 3. Configure variables and apply

```bash
cp terraform.tfvars.example terraform.tfvars   # edit project_id, region, ...
terraform apply
```

On the **first** apply you typically leave `domain = ""` → the LB comes up
**HTTP-only** so you can validate the static IP and routing. Then set the
domain and re-apply (see below).

## The "reserve IP now → set domain later → get the cert" flow

1. First apply with `domain = ""`. Read `terraform output lb_ip` — the static
   IP is reserved immediately and never changes.
2. Create DNS **A records** at your provider:
   - `app.<domain>` → `<lb_ip>`
   - `api.<domain>` → `<lb_ip>`
3. Set `domain = "example.com"` in `terraform.tfvars` and re-apply. This flips
   `local.enable_https = true` and provisions the Certificate Manager managed
   cert, certificate map, HTTPS proxy and the `:443` forwarding rule; `:80`
   becomes a redirect to `:443`.
4. Read `terraform output dns_authorization_record` and create the **CNAME**
   record it specifies (Certificate Manager DNS authorization). The managed
   cert validates and goes `ACTIVE` once both the CNAME and the A records
   resolve (can take several minutes to ~an hour).

## DNS records to create

| Type  | Name            | Value                                  |
|-------|-----------------|----------------------------------------|
| A     | `app`           | `lb_ip` output                         |
| A     | `api`           | `lb_ip` output                         |
| CNAME | (from output)   | `dns_authorization_record` output      |

## Frontend ↔ Backend wiring notes

- **Backend** receives DB settings as plain env (`POSTGRES_SERVER` = PSC IP,
  `POSTGRES_PORT`, `POSTGRES_DB`, `POSTGRES_USER`) and the password as a
  **Secret Manager** secret ref (`POSTGRES_PASSWORD`, never plaintext).
- `BACKEND_CORS_ORIGINS` (and `FRONTEND_HOST`) are set to
  `https://app.<domain>`. The app code (`backend/app/core/config.py`) reads
  these. Until the real domain is set these point at a placeholder host —
  re-apply after setting `domain`.
- **Frontend / Vite is BUILD-TIME**: `VITE_API_URL` is baked into the static
  bundle at build (`frontend/src/main.tsx` does
  `OpenAPI.BASE = import.meta.env.VITE_API_URL`). Terraform exposes a runtime
  `VITE_API_URL` env for completeness, **but you must build the frontend image
  with** `VITE_API_URL=https://api.<domain>` for the SPA to hit the API. A
  runtime env var will NOT change an already-built bundle.

## Variables (root) — name, default, purpose

| Variable | Default | Purpose |
|---|---|---|
| `project_id` | _(required)_ | GCP project ID |
| `region` | `europe-west1` | Region for regional resources |
| `name_prefix` | `mynance` | Resource name prefix |
| `enable_apis` | `true` | Enable required Google APIs |
| `network_self_link` | `""` | Existing VPC self link; empty ⇒ create |
| `subnet_self_link` | `""` | Existing subnet self link; empty ⇒ create |
| `host_project_id` | `""` | Shared VPC host project (informational) |
| `network_name` | `mynance-vpc` | VPC name when creating |
| `subnet_name` | `mynance-subnet` | Subnet name when creating |
| `subnet_cidr` | `10.10.0.0/24` | Subnet CIDR when creating |
| `db_instance_name` | `mynance-pg` | Cloud SQL instance name |
| `db_version` | `POSTGRES_16` | Postgres version |
| `db_tier` | `db-f1-micro` | SQL tier (cheapest; see caveat) |
| `db_disk_size` | `10` | SQL disk GB (PD_HDD, no autoresize) |
| `db_name` | `app` | Database name (`POSTGRES_DB`) |
| `db_user` | `mynance` | SQL user (`POSTGRES_USER`) |
| `db_password_secret_id` | `mynance-db-password` | Secret Manager secret id |
| `db_deletion_protection` | `false` | Instance deletion protection |
| `db_backups_enabled` | `false` | Automated backups (cost) |
| `db_port` | `5432` | `POSTGRES_PORT` for the backend |
| `cloudrun_min_instances` | `0` | Min instances (scale to zero) |
| `cloudrun_max_instances` | `2` | Max instances |
| `cloudrun_cpu` | `1` | CPU limit |
| `cloudrun_memory` | `512Mi` | Memory limit |
| `backend_image` | `…/cloudrun/container/hello` | Backend image |
| `frontend_image` | `…/cloudrun/container/hello` | Frontend image |
| `backend_container_port` | `8080` | Backend container port |
| `frontend_container_port` | `8080` | Frontend container port |
| `domain` | `""` | Base domain; empty ⇒ HTTP-only LB |
| `environment` | `production` | App `ENVIRONMENT` |
| `project_name` | `mynance` | App `PROJECT_NAME` |
| `extra_backend_env` | `{}` | Extra plain backend env (e.g. SECRET_KEY, SENTRY_DSN) |
| `extra_frontend_env` | `{}` | Extra plain frontend env |

### Bootstrap variables

| Variable | Default | Purpose |
|---|---|---|
| `project_id` | _(required)_ | Project owning the state bucket |
| `region` | `europe-west1` | Provider region |
| `state_bucket_name` | _(required)_ | Globally-unique state bucket name |
| `state_bucket_location` | `EU` | Bucket location |
| `state_version_retention` | `10` | Old state versions kept |
| `enable_apis` | `true` | Enable storage API |

## The two conditionals

1. **create-or-reference network** (`main.tf` locals):
   `local.create_network = var.network_self_link == ""`. The `network` module
   is called with `count = local.create_network ? 1 : 0`. Consumers use
   `local.network_self_link` / `local.subnet_self_link`, which resolve to the
   module output when created or the input variable when referenced.
2. **https-or-http LB** (`local.enable_https = var.domain != ""`): all
   Certificate Manager + HTTPS resources are gated with `count`. When disabled,
   only an HTTP target proxy + `:80` forwarding rule are created.

## Outputs

`lb_ip`, `https_enabled`, `dns_authorization_record`, `network_self_link`,
`subnet_self_link`, `network_created`, `cloudsql_instance_name`,
`cloudsql_connection_name`, `cloudsql_psc_ip`, `db_password_secret_id`,
`backend_service_uri`, `frontend_service_uri`, `backend_service_account`,
`frontend_service_account`.

## Caveats / TODO

- **`db-f1-micro` RAM**: shared-core, ~0.6 GB RAM. Fine for dev/smoke tests but
  will struggle under real load — bump `db_tier` (e.g. `db-custom-1-3840`) for
  staging/production.
- **`SECRET_KEY`** and other app secrets are NOT managed here. Feed them via
  `extra_backend_env` or extend the cloudsql/secrets pattern to add more
  Secret Manager-backed env vars. The app's `_check_default_secret` will fail
  on `changethis` in non-local environments.
- **Vite build-time env** (see wiring notes): rebuild the FE image when the
  domain changes.
- **CORS** is wired to `https://app.<domain>`; verify the app's allowed origins
  match once the domain is final.
- Backups disabled and deletion protection off by default — turn on for prod.
```
