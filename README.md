# YAML Composer

A **template-based YAML generator** for composing reusable templates with parameterized functions. Works with any YAML-based configuration system including Docker Compose, Kubernetes, Helm, Terraform, application configs, and more.

**Key Benefit:** Write templates once, reuse them across environments, projects, and contexts by simply changing configuration overrides.

[![GitHub](https://img.shields.io/badge/GitHub-nilayjoshi89%2Fyaml__composer-blue?logo=github)](https://github.com/nilayjoshi89/yaml_composer)
[![Docker Hub](https://img.shields.io/badge/Docker%20Hub-nilayjoshi89%2Fyaml__composer-blue?logo=docker)](https://hub.docker.com/r/nilayjoshi89/yaml_composer)
![Docker Pulls](https://img.shields.io/docker/pulls/nilayjoshi89/yaml_composer)
![Docker Image Size](https://img.shields.io/docker/image-size/nilayjoshi89/yaml_composer/dev-v0.1)
![Python](https://img.shields.io/badge/python-3.11+-blue)
![License](https://img.shields.io/github/license/nilayjoshi89/yaml_composer)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v2.json)](https://github.com/astral-sh/uv)

---

## Table of Contents

1. [Quick Start](#quick-start)
2. [Quick Reference](#quick-reference)
3. [Core Concepts](#core-concepts)
4. [Simple Examples](#simple-examples)
5. [Advanced Examples](#advanced-examples)
6. [Real-World Examples](#real-world-examples)
7. [Architecture](#architecture)
8. [API Reference](#api-reference)
9. [Best Practices](#best-practices)
10. [Troubleshooting](#troubleshooting)
11. [Running Tests](#running-tests)
12. [Contributing](#contributing)

---

## Quick Start

### Installation

This project uses [uv](https://docs.astral.sh/uv/) for dependency management. `pip install` is not supported — the build backend is `uv_build`.

```bash
git clone https://github.com/nilayjoshi89/yaml_composer.git
cd yaml_composer

# Install all dependencies (including dev group) and create .venv
uv sync --group dev
```

The virtual environment is created at `.venv/`. On Windows the interpreter is at `.venv\Scripts\python`.

### Basic Usage

```bash
# Generate YAML from a template
py-yaml-composer my_template.yml -w /path/to/workspace

# Output is written to the path specified in the template's X-OUTPUT field
```

**Using Docker:**
```bash
# Pull the image
docker pull nilayjoshi89/yaml_composer:dev-v0.1

# Run against a local workspace
docker run --rm \
  -v ./repo:/yaml_workspace \
  nilayjoshi89/yaml_composer:dev-v0.1 \
  ./stack/pg_db_admin/pg_db_admin_app_stack.yml
```

Image on Docker Hub: [nilayjoshi89/yaml_composer](https://hub.docker.com/r/nilayjoshi89/yaml_composer)

### Minimal Template

```yaml
X-OUTPUT: generated/config.yml
X-OVERRIDE:
  X-REF-MyConfig:
    name: example
    enabled: true

config:
  X-REF-MyConfig: null
```

**Output:**
```yaml
config:
  name: example
  enabled: true
```

---

## Quick Reference

| Tag | Role | Example |
|-----|------|---------|
| `X-OUTPUT` | Where to write the generated file | `X-OUTPUT: generated/docker-compose.yml` |
| `X-INCLUDE` | Load external template files | `X-INCLUDE: [templates/base.yml]` |
| `X-OVERRIDE` | Define or override named references locally | `X-OVERRIDE: {X-REF-DB: {host: localhost}}` |
| `X-REF-Name` | Inline reference marker (replaced at generation) | `X-REF-Database: null` |
| `X-REF-Name('a','b')` | Parameterized function call | `X-REF-Service('v2', 'prod'): null` |
| `{X-ARG-N}` | Argument placeholder inside a template (1-based) | `image: "{X-ARG-1}"` |

**Evaluation order:** `X-INCLUDE` files load first → `X-OVERRIDE` values take precedence → function calls expand → references resolve.

---

## Core Concepts

### 1. Template Includes (`X-INCLUDE`)

Load external template files to share components across configurations.

```yaml
X-INCLUDE:
  - templates/base.yml
  - templates/components.yml
```

**templates/base.yml:**
```yaml
X-REF-BASE-CONFIG:
  enabled: true
  timeout: 30
  retry_policy:
    max_attempts: 3
    backoff: exponential
```

### 2. Template Overrides (`X-OVERRIDE`)

Define or replace reference values locally. These take precedence over anything loaded via `X-INCLUDE`.

```yaml
X-OVERRIDE:
  X-REF-Database:
    type: postgresql
    version: "15"
    host: db.example.com
  X-REF-Cache:
    type: redis
    version: "7.2"
    host: cache.example.com
```

### 3. References (`X-REF-*`)

Place a reference marker anywhere in your YAML. It is replaced in-place with the matching template value.

```yaml
infrastructure:
  databases:
    X-REF-Database: null   # replaced with Database template
  caches:
    X-REF-Cache: null      # replaced with Cache template
```

### 4. Parameterized Functions (`X-REF-Name()` + `{X-ARG-N}`)

Define a template with argument placeholders, then call it like a function.

**Template definition:**
```yaml
X-REF-GENERIC-COMPONENT:
  type: "{X-ARG-1}"
  name: "{X-ARG-2}"
  config:
    timeout: "{X-ARG-3}"
```

**Call site:**
```yaml
components:
  api-handler:
    X-REF-GENERIC-COMPONENT('handler', 'api-processor', '30'): null
```

**Output:**
```yaml
components:
  api-handler:
    type: handler
    name: api-processor
    config:
      timeout: "30"
```

### 5. Output Location (`X-OUTPUT`)

Required on every template. Specifies where the generated file is written (relative to the workspace).

```yaml
X-OUTPUT: generated/config.yml
```

---

## Simple Examples

### Example 1: Basic Reference Replacement

**Input:**
```yaml
X-OUTPUT: output.yml
X-OVERRIDE:
  X-REF-Node2:
    name: ServiceB
    value: ValueB

Node1: ValueA
X-REF-Node2: null
```

**Output:**
```yaml
Node1: ValueA
name: ServiceB
value: ValueB
```

---

### Example 2: Nested References

**Input:**
```yaml
X-OUTPUT: output.yml
X-OVERRIDE:
  X-REF-DatabaseConfig:
    connection_string: postgresql://localhost:5432
    pool_size: 20
  X-REF-CacheConfig:
    connection_string: redis://localhost:6379
    ttl: 3600

application:
  database:
    X-REF-DatabaseConfig: null
  cache:
    X-REF-CacheConfig: null
```

**Output:**
```yaml
application:
  database:
    connection_string: postgresql://localhost:5432
    pool_size: 20
  cache:
    connection_string: redis://localhost:6379
    ttl: 3600
```

---

### Example 3: Function with Single Argument

**Input:**
```yaml
X-OUTPUT: output.yml
X-OVERRIDE:
  X-REF-ServiceTemplate:
    version: "{X-ARG-1}"
    enabled: true

services:
  api:
    X-REF-ServiceTemplate('v2.1'): null
```

**Output:**
```yaml
services:
  api:
    version: v2.1
    enabled: true
```

---

### Example 4: Function with Multiple Arguments

**Input:**
```yaml
X-OUTPUT: output.yml
X-OVERRIDE:
  X-REF-ApiEndpoint:
    path: "{X-ARG-1}"
    method: "{X-ARG-2}"
    auth_required: "{X-ARG-3}"

endpoints:
  users:
    X-REF-ApiEndpoint('/api/users', 'GET', 'true'): null
```

**Output:**
```yaml
endpoints:
  users:
    path: /api/users
    method: GET
    auth_required: "true"
```

---

### Example 5: List Substitution

**Input:**
```yaml
X-OUTPUT: output.yml
X-OVERRIDE:
  X-REF-PERMISSIONS:
    - read
    - write
    - delete

roles:
  admin:
    permissions:
      X-REF-PERMISSIONS: null
```

**Output:**
```yaml
roles:
  admin:
    permissions:
      - read
      - write
      - delete
```

---

## Advanced Examples

### Example 6: Template Inheritance with Base Config

**templates/base.yml:**
```yaml
X-REF-BASE-CONFIG:
  timeout: 30
  retry: 3
  logging_level: INFO
```

**templates/components.yml:**
```yaml
X-REF-API-COMPONENT:
  X-REF-BASE-CONFIG: null  # inherit base config
  endpoint: /api/v1
  rate_limit: 1000
```

**Main template:**
```yaml
X-INCLUDE:
  - templates/base.yml
  - templates/components.yml

X-OUTPUT: config.yml

components:
  api:
    X-REF-API-COMPONENT: null
```

**Output:**
```yaml
components:
  api:
    timeout: 30
    retry: 3
    logging_level: INFO
    endpoint: /api/v1
    rate_limit: 1000
```

---

### Example 7: Environment-Specific Overrides

Same template, different overrides per environment.

**templates/database.yml:**
```yaml
X-REF-DATABASE-CONFIG:
  name: "{X-ARG-1}"
  host: "{X-ARG-2}"
  credentials:
    user: "{X-ARG-3}"
    password: "{X-ARG-4}"
```

**dev-config.yml:**
```yaml
X-INCLUDE:
  - templates/database.yml

X-OUTPUT: generated/dev/config.yml
X-OVERRIDE:
  X-REF-DB-NAME: dev_db
  X-REF-DB-HOST: localhost
  X-REF-DB-USER: dev_user
  X-REF-DB-PASSWORD: dev_password

database:
  X-REF-DATABASE-CONFIG(X-REF-DB-NAME, X-REF-DB-HOST, X-REF-DB-USER, X-REF-DB-PASSWORD): null
```

**prod-config.yml:**
```yaml
X-INCLUDE:
  - templates/database.yml

X-OUTPUT: generated/prod/config.yml
X-OVERRIDE:
  X-REF-DB-NAME: prod_db
  X-REF-DB-HOST: db.prod.internal
  X-REF-DB-USER: prod_user
  X-REF-DB-PASSWORD: ${PROD_DB_PASSWORD:?error}

database:
  X-REF-DATABASE-CONFIG(X-REF-DB-NAME, X-REF-DB-HOST, X-REF-DB-USER, X-REF-DB-PASSWORD): null
```

---

### Example 8: Composite Arguments (String Interpolation)

Combine fixed text with argument placeholders inside a single value.

**Template:**
```yaml
X-OVERRIDE:
  X-REF-ServiceDef:
    service_id: "{X-ARG-1}-{X-ARG-2}"
    registry: mycompany/{X-ARG-1}:{X-ARG-3}

services:
  processor:
    X-REF-ServiceDef('data', 'prod', 'v2.1'): null
```

**Output:**
```yaml
services:
  processor:
    service_id: data-prod
    registry: mycompany/data:v2.1
```

---

## Real-World Examples

### Use Case 1: Docker Compose Stacks (PostgreSQL + PgAdmin)

#### Folder Structure

```
repo/
├── templates/
│   ├── core.yml              # Base service configuration
│   ├── image_version.yml     # Centralized image versions
│   ├── postgres.yml          # PostgreSQL service template
│   └── pg_admin.yml          # PgAdmin service template
├── stack/
│   └── pg_db_admin/
│       └── pg_db_admin_app_stack.yml
└── services/
    └── pg_db_admin_service.yml   # Generated output
```

**templates/core.yml:**
```yaml
X-REF-BASE-TEMPLATE:
  restart: unless-stopped
  security_opt:
    - no-new-privileges:true
  pids_limit: 100
  mem_limit: 512m
  cpus: "1.0"
```

**templates/image_version.yml:**
```yaml
X-REF-IMAGE-POSTGRES: postgres:18.3-alpine
X-REF-IMAGE-PG-ADMIN4: dpage/pgadmin4
```

**templates/postgres.yml:**
```yaml
X-REF-FUNCT-TEMPLATE-POSTGRES:
  X-REF-BASE-TEMPLATE: null
  image: X-REF-IMAGE-POSTGRES
  container_name: "{X-ARG-1}"
  shm_size: 128mb
  environment: "{X-ARG-2}"
  ports: "{X-ARG-3}"
  volumes: "{X-ARG-4}"
  healthcheck:
    test: ["CMD-SHELL", "pg_isready -U $$POSTGRES_USER -d $$POSTGRES_DB"]
    interval: 10s
    timeout: 5s
    retries: 5
    start_period: 15s
```

**templates/pg_admin.yml:**
```yaml
X-REF-FUNCT-TEMPLATE-PG-ADMIN:
  X-REF-BASE-TEMPLATE: null
  image: X-REF-IMAGE-PG-ADMIN4
  container_name: "{X-ARG-1}"
  environment: "{X-ARG-2}"
  ports:
    - "{X-ARG-3}"
  volumes: "{X-ARG-4}"
```

**stack/pg_db_admin/pg_db_admin_app_stack.yml:**
```yaml
X-INCLUDE:
  - templates/core.yml
  - templates/image_version.yml
  - templates/postgres.yml
  - templates/pg_admin.yml

X-OUTPUT: services/pg_db_admin_service.yml

X-OVERRIDE:
  X-REF-DB1-CONTAINER-NAME: db1
  X-REF-DB1-ENV:
    - POSTGRES_DB=mydb1
    - POSTGRES_USER=user
    - POSTGRES_PASSWORD=password
  X-REF-DB1-PORTS: []
  X-REF-DB1-VOLUME:
    - ${PG_DB_ADMIN_DATA:?}\db1:/var/lib/postgresql

  X-REF-DB2-CONTAINER-NAME: db2
  X-REF-DB2-ENV:
    - POSTGRES_DB=mydb2
    - POSTGRES_USER=user
    - POSTGRES_PASSWORD=password
  X-REF-DB2-PORTS: []
  X-REF-DB2-VOLUME:
    - ${PG_DB_ADMIN_DATA:?}\db2:/var/lib/postgresql

  X-REF-PGADMIN-CONTAINER-NAME: pg_admin
  X-REF-PGADMIN-ENV:
    - PGADMIN_DEFAULT_EMAIL=admin@admin.com
    - PGADMIN_DEFAULT_PASSWORD=password
  X-REF-PGADMIN-PORTS: 8080:80
  X-REF-PGADMIN-VOLUME:
    - ${PG_DB_ADMIN_DATA:?}\pgadmin\data:/var/lib/pgadmin
    - ${PG_DB_ADMIN_DATA:?}\pgadmin\servers.json:/pgadmin4/servers.json

services:
  db-one:
    X-REF-FUNCT-TEMPLATE-POSTGRES(X-REF-DB1-CONTAINER-NAME,X-REF-DB1-ENV,X-REF-DB1-PORTS,X-REF-DB1-VOLUME): null
    networks:
      - pg_service_network

  db-two:
    X-REF-FUNCT-TEMPLATE-POSTGRES(X-REF-DB2-CONTAINER-NAME,X-REF-DB2-ENV,X-REF-DB2-PORTS,X-REF-DB2-VOLUME): null
    networks:
      - pg_service_network

  pg_admin:
    X-REF-FUNCT-TEMPLATE-PG-ADMIN(X-REF-PGADMIN-CONTAINER-NAME,X-REF-PGADMIN-ENV,X-REF-PGADMIN-PORTS,X-REF-PGADMIN-VOLUME): null
    networks:
      - pg_service_network

networks:
  pg_service_network:
    driver: bridge
```

**Generate and run:**
```bash
py-yaml-composer stack/pg_db_admin/pg_db_admin_app_stack.yml -w repo

cd services
docker-compose -f pg_db_admin_service.yml up -d
# Access PgAdmin at http://localhost:8080  (admin@admin.com / password)
```

---

### Use Case 2: Kubernetes Configuration Management

**templates/k8s-deployment.yml:**
```yaml
X-REF-K8S-DEPLOYMENT:
  apiVersion: apps/v1
  kind: Deployment
  metadata:
    name: "{X-ARG-1}"
    namespace: "{X-ARG-2}"
  spec:
    replicas: "{X-ARG-3}"
    template:
      metadata:
        labels:
          app: "{X-ARG-1}"
      spec:
        containers:
        - name: app
          image: "{X-ARG-4}"
          ports:
          - containerPort: "{X-ARG-5}"
```

**k8s-prod-config.yml:**
```yaml
X-INCLUDE:
  - templates/k8s-deployment.yml

X-OUTPUT: generated/k8s-prod.yml
X-OVERRIDE:
  X-REF-APP-NAME: myapp
  X-REF-NAMESPACE: production
  X-REF-REPLICAS: "3"
  X-REF-IMAGE: myrepo/myapp:v1.2.3
  X-REF-PORT: "8080"

deployments:
  - X-REF-K8S-DEPLOYMENT(X-REF-APP-NAME, X-REF-NAMESPACE, X-REF-REPLICAS, X-REF-IMAGE, X-REF-PORT): null
```

**Output:**
```yaml
deployments:
  - apiVersion: apps/v1
    kind: Deployment
    metadata:
      name: myapp
      namespace: production
    spec:
      replicas: "3"
      template:
        metadata:
          labels:
            app: myapp
        spec:
          containers:
          - name: app
            image: myrepo/myapp:v1.2.3
            ports:
            - containerPort: "8080"
```

---

### Use Case 3: Application Configuration

**templates/app-settings.yml:**
```yaml
X-REF-APP-CONFIG:
  server:
    host: "{X-ARG-1}"
    port: "{X-ARG-2}"
  database:
    host: "{X-ARG-3}"
    pool_size: "{X-ARG-4}"
  cache:
    enabled: "{X-ARG-5}"
    ttl: "{X-ARG-6}"
```

**app-dev-config.yml:**
```yaml
X-INCLUDE:
  - templates/app-settings.yml

X-OUTPUT: generated/dev/settings.yml
X-OVERRIDE:
  X-REF-SERVER-HOST: localhost
  X-REF-SERVER-PORT: "3000"
  X-REF-DB-HOST: localhost
  X-REF-DB-POOL: "5"
  X-REF-CACHE-ENABLED: "false"
  X-REF-CACHE-TTL: "300"

application:
  X-REF-APP-CONFIG(X-REF-SERVER-HOST, X-REF-SERVER-PORT, X-REF-DB-HOST, X-REF-DB-POOL, X-REF-CACHE-ENABLED, X-REF-CACHE-TTL): null
```

**app-prod-config.yml:**
```yaml
X-INCLUDE:
  - templates/app-settings.yml

X-OUTPUT: generated/prod/settings.yml
X-OVERRIDE:
  X-REF-SERVER-HOST: 0.0.0.0
  X-REF-SERVER-PORT: "8080"
  X-REF-DB-HOST: db.prod.internal
  X-REF-DB-POOL: "50"
  X-REF-CACHE-ENABLED: "true"
  X-REF-CACHE-TTL: "3600"

application:
  X-REF-APP-CONFIG(X-REF-SERVER-HOST, X-REF-SERVER-PORT, X-REF-DB-HOST, X-REF-DB-POOL, X-REF-CACHE-ENABLED, X-REF-CACHE-TTL): null
```

---

### Use Case 4: Infrastructure-as-Code (Terraform)

**templates/terraform-vars.yml:**
```yaml
X-REF-TF-VARIABLES:
  region: "{X-ARG-1}"
  environment: "{X-ARG-2}"
  instance_type: "{X-ARG-3}"
  instance_count: "{X-ARG-4}"
  tags:
    - project: myproject
    - managed_by: terraform
```

**infrastructure-staging.yml:**
```yaml
X-INCLUDE:
  - templates/terraform-vars.yml

X-OUTPUT: generated/terraform-staging.tfvars.yml
X-OVERRIDE:
  X-REF-REGION: us-east-1
  X-REF-ENV: staging
  X-REF-INSTANCE-TYPE: t3.medium
  X-REF-INSTANCE-COUNT: "2"

terraform:
  X-REF-TF-VARIABLES(X-REF-REGION, X-REF-ENV, X-REF-INSTANCE-TYPE, X-REF-INSTANCE-COUNT): null
```

---

## Architecture

### Data Flow

```
Template YAML
    │
    ├─ X-INCLUDE files loaded   (ref_data built)
    ├─ X-OVERRIDE values merged (local takes precedence)
    │
    ▼
YamlFunctionAction              expand X-REF-Name() calls
    │
    ▼
YamlTraverser (DFS)
    ├─ YamlXRefAction           resolve X-REF-* markers
    └─ YamlSortAction           reorder Docker Compose keys
    │
    ▼
Save to X-OUTPUT path
```

### Component Responsibilities

| Component | Purpose |
|-----------|---------|
| `YamlGenerator` | Orchestrates the pipeline: loads templates, manages action execution |
| `YamlFileHelper` | I/O: loads/saves YAML files with workspace path resolution |
| `YamlTraverser` | Depth-first traversal; applies actions at each node |
| `YamlFunctionAction` | Expands parameterized function calls before traversal |
| `YamlXRefAction` | Resolves `X-REF-*` markers and merges template data |
| `YamlSortDockerComposeNodeAction` | Sorts Docker Compose keys into standard order |
| `ActionContext` | Carries reference data through the action pipeline |

---

## API Reference

### Command Line

```
py-yaml-composer TEMPLATE_FILE [-w WORKSPACE]

Arguments:
  TEMPLATE_FILE         Path to YAML template (relative to workspace or absolute)

Options:
  -w, --workspace PATH  Workspace root for file resolution (default: /yaml_workspace)
  -h, --help            Show this help message
```

### YAML Metadata Tags

| Tag | Purpose | Type | Required |
|-----|---------|------|----------|
| `X-OUTPUT` | Output file path | `str` | Yes |
| `X-INCLUDE` | External template files to load | `list[str]` | No |
| `X-OVERRIDE` | Local reference definitions | `dict` | No |
| `X-REF-*` | Reference marker (replaced at generation) | `any` | — |
| `{X-ARG-N}` | Function argument placeholder (1-based) | `str` | — |

### Merge Behavior

When a reference key already exists in the target, values are merged rather than replaced:

| Existing type | Incoming type | Result |
|---|---|---|
| `dict` | `dict` | Deep merge (incoming wins on conflict) |
| `list` | `list` | Lists are concatenated |
| any | `str` | Overwrite |
| missing | any | Insert |

---

## Best Practices

### 1. Organize Templates by Concern

```
templates/
├── base.yml              # Common base configurations
├── versions.yml          # Centralized image/package versions
├── infrastructure/
│   ├── database.yml
│   ├── cache.yml
│   └── messaging.yml
└── environments.yml      # Environment-specific defaults
```

### 2. Centralize Versions

```yaml
# templates/versions.yml
X-REF-VERSION-POSTGRES: postgres:18.3-alpine
X-REF-VERSION-REDIS: redis:7.2-alpine

# Component template references version by name
X-REF-DATABASE:
  image: X-REF-VERSION-POSTGRES
```

### 3. Use Descriptive Reference Names

```yaml
# Good
X-REF-DB1-CONTAINER-NAME: db1
X-REF-DB1-ENV: [...]

# Avoid
X-REF-A: db1
X-REF-B: [...]
```

### 4. Separate Config from Templates

Keep templates generic. Put environment-specific values in `X-OVERRIDE` inside stack files, not in the template files themselves.

### 5. Use Environment Variables for Secrets

```yaml
X-REF-DB-PASSWORD: ${DB_PASSWORD:?error - DB_PASSWORD not set}
X-REF-API-KEY: ${API_KEY:?error}
```

### 6. Document Template Parameters

```yaml
# templates/component.yml
#
# Parameters:
#   ARG-1: Component name
#   ARG-2: Environment (dev/staging/prod)
#   ARG-3: Memory limit (e.g. 512m, 2Gi)
#
X-REF-COMPONENT:
  name: "{X-ARG-1}"
  environment: "{X-ARG-2}"
  resources:
    memory: "{X-ARG-3}"
```

### 7. Validate Generated Output

```bash
# YAML syntax
python -c "import yaml, sys; yaml.safe_load(open(sys.argv[1]))" generated/config.yml

# Docker Compose
docker-compose -f services/docker-compose.yml config

# Kubernetes
kubectl apply -f generated/k8s-config.yml --dry-run=client

# Terraform
terraform validate generated/
```

### 8. Version Control Strategy

```
.gitignore:
  generated/    # generated files — do not commit
  data/         # runtime data
  .env          # secrets

Commit:
  templates/    # reusable templates
  stacks/       # stack definitions
  .env.example  # example vars (no secrets)
```

---

## Troubleshooting

### "Output file path not specified in the template"
The `X-OUTPUT` key is missing or empty in your template. Every template must have it.

### "File does not exist"
An `X-INCLUDE` entry points to a file that can't be found. Check that the path is correct relative to the workspace root, and that you're passing the right `-w` value.

```bash
# Debug: print resolved workspace path
py-yaml-composer template.yml -w /absolute/path/to/repo
```

### "Reference not found"
An `X-REF-*` marker in your template has no matching definition in `X-OVERRIDE` or any `X-INCLUDE` file.

```yaml
# This will fail if X-REF-MyThing is not defined anywhere:
service:
  X-REF-MyThing: null
```

Check spelling — reference names are case-sensitive.

### "Value must be dict"
A reference used as a dict key (e.g. `X-REF-Foo: null` where `Foo` expands into a dict's children) resolved to a non-dict value. Ensure the reference definition is a YAML mapping, not a scalar or list.

### "Invalid Function argument index"
The `{X-ARG-N}` index in a template is out of range for the number of arguments passed in the function call. Count the arguments in the call and the `{X-ARG-N}` placeholders — they must match.

```yaml
# Template has {X-ARG-1} and {X-ARG-2} — must pass exactly 2 args:
X-REF-Svc('value1', 'value2'): null
```

### Generation appears to hang
This can happen if two references form a circular chain (A includes B, B includes A). There is currently no cycle detection — terminate the process and review your reference graph.

---

## Running Tests

```bash
# Run all tests
uv run pytest tests

# With coverage report
uv run pytest tests --cov=src --cov-report=html

# Single test
uv run pytest tests/py_yaml_composer_tests/test_yaml_refs.py::TestYamlReferences::test_simple_yaml_generation
```

### Linting and Type Checking

```bash
# Lint
uv run ruff check .

# Type check
uv run mypy . --config-file pyproject.toml
```

**In VS Code:** the default build task (`Ctrl+Shift+B`) runs both ruff and mypy in sequence ("Complete check"). Tasks are defined in [.vscode/tasks.json](.vscode/tasks.json).

The VS Code Test Explorer is pre-configured to discover and run pytest tests via [.vscode/settings.json](.vscode/settings.json).

---

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Write tests for new functionality
4. Ensure all checks pass: `uv run ruff check . && uv run mypy . --config-file pyproject.toml && uv run pytest tests`
5. Open a pull request

---

## License

MIT License — see [LICENSE](LICENSE) for details.
s

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test
pytest tests/py_yaml_composer_tests/test_yaml_refs.py::TestYamlReferences::test_simple_yaml_generation
```

---

## Contributing

Contributions welcome! Please:

1. Fork repository
2. Create feature branch: `git checkout -b feature/your-feature`
3. Write tests for new functionality
4. Ensure all tests pass and type checking passes: `mypy . && ruff check .`
5. Create pull request

---

## License

[Your License Here]

---

## Resources

- [YAML Specification](https://yaml.org/spec/1.2/spec.html) - Official YAML format specification
- [Docker Compose Reference](https://docs.docker.com/compose/compose-file/) - Docker Compose YAML schema
- [Kubernetes API Reference](https://kubernetes.io/docs/reference/kubernetes-api/) - K8s YAML structures
- [Terraform Configuration](https://www.terraform.io/language/syntax/configuration) - Terraform file formats
- [pytest Documentation](https://docs.pytest.org/) - Python testing framework
- [Python argparse](https://docs.python.org/3/library/argparse.html) - Command-line interface creation

---
s

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test
pytest tests/py_yaml_composer_tests/test_yaml_refs.py::TestYamlReferences::test_simple_yaml_generation
```

---

## Contributing

Contributions welcome! Please:

1. Fork repository
2. Create feature branch: `git checkout -b feature/your-feature`
3. Write tests for new functionality
4. Ensure all tests pass and type checking passes: `mypy . && ruff check .`
5. Create pull request

---

## License

[Your License Here]

---

## Resources

- [YAML Specification](https://yaml.org/spec/1.2/spec.html) - Official YAML format specification
- [Docker Compose Reference](https://docs.docker.com/compose/compose-file/) - Docker Compose YAML schema
- [Kubernetes API Reference](https://kubernetes.io/docs/reference/kubernetes-api/) - K8s YAML structures
- [Terraform Configuration](https://www.terraform.io/language/syntax/configuration) - Terraform file formats
- [pytest Documentation](https://docs.pytest.org/) - Python testing framework
- [Python argparse](https://docs.python.org/3/library/argparse.html) - Command-line interface creation

---
