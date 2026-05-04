# YAML Composer 🎼

A **template-based YAML generator** for composing reusable templates with parameterized functions. Works with any YAML-based configuration system including Docker Compose, Kubernetes, Helm, Terraform, application configs, and more.

**Key Benefit:** Write templates once, reuse them across environments, projects, and contexts by simply changing configuration overrides.

---

## 📋 Table of Contents

1. [Quick Start](#quick-start)
2. [Core Concepts](#core-concepts)
3. [Simple Examples](#simple-examples)
4. [Advanced Examples](#advanced-examples)
5. [Real-World Examples](#real-world-examples)
6. [Architecture](#architecture)
7. [API Reference](#api-reference)
8. [Best Practices](#best-practices)

---

## Quick Start

### Installation

```bash
# Clone repository
git clone <repo-url>
cd yaml_composer

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -e ".[dev]"
```

### Basic Usage

```bash
# Generate YAML from template
py-yaml-composer my_template.yml -w /path/to/workspace

# Output is written to location specified in template's X-OUTPUT field
```

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

## Core Concepts

### 1. **Template Includes** (`X-INCLUDE`)

Load external template files to organize reusable components across your YAML configurations.

```yaml
X-INCLUDE:
  - templates/base.yml
  - templates/components.yml
  - templates/common.yml
```

**File: templates/base.yml**
```yaml
X-REF-BASE-CONFIG:
  enabled: true
  timeout: 30
  retry_policy:
    max_attempts: 3
    backoff: exponential
```

### 2. **Template Overrides** (`X-OVERRIDE`)

Define template variables and reference implementations locally for your specific context.

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

### 3. **References** (`X-REF-*`)

Reference templates to include them in your configuration at specific locations.

```yaml
infrastructure:
  databases:
    X-REF-Database: null        # Marker to replace with Database template
  
  caches:
    X-REF-Cache: null           # Marker to replace with Cache template
```

### 4. **Parameterized Functions** (`X-REF-FUNC()` + `{X-ARG-N}`)

Define templates with parameters for maximum reusability across different configurations.

**Template Definition:**
```yaml
X-REF-GENERIC-COMPONENT:
  type: "{X-ARG-1}"
  name: "{X-ARG-2}"
  config:
    timeout: "{X-ARG-3}"
```

**Function Call:**
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

### 5. **Output Location** (`X-OUTPUT`)

Specify where the generated YAML should be saved.

```yaml
X-OUTPUT: generated/config.yml
```

---

## Simple Examples

These examples work with any YAML-based system (configs, APIs, infrastructure, etc.).

### Example 1: Basic Reference Replacement

**Input Template:**
```yaml
X-OUTPUT: output.yml
X-OVERRIDE:
  X-REF-Node2:
    name: ServiceB
    value: ValueB

Node1: ValueA
X-REF-Node2: null  # Marker for replacement
```

**Generated Output:**
```yaml
Node1: ValueA
name: ServiceB
value: ValueB
```

---

### Example 2: Nested References

**Input Template:**
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

**Generated Output:**
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

**Input Template:**
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

**Generated Output:**
```yaml
services:
  api:
    version: v2.1
    enabled: true
```

---

### Example 4: Function with Multiple Arguments

**Input Template:**
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

**Generated Output:**
```yaml
endpoints:
  users:
    path: /api/users
    method: GET
    auth_required: "true"
```

---

### Example 5: List Substitution

**Input Template:**
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

**Generated Output:**
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

**File: templates/base.yml**
```yaml
X-REF-BASE-CONFIG:
  timeout: 30
  retry: 3
  logging_level: INFO
```

**File: templates/components.yml**
```yaml
X-REF-API-COMPONENT:
  X-REF-BASE-CONFIG: null  # Inherit base config
  endpoint: /api/v1
  rate_limit: 1000
```

**Main Template:**
```yaml
X-INCLUDE:
  - templates/base.yml
  - templates/components.yml

X-OUTPUT: config.yml

components:
  api:
    X-REF-API-COMPONENT: null
```

**Generated Output:**
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

Demonstrate the same template used for different environments.

**File: templates/database.yml**
```yaml
X-REF-DATABASE-CONFIG:
  name: "{X-ARG-1}"
  host: "{X-ARG-2}"
  credentials:
    user: "{X-ARG-3}"
    password: "{X-ARG-4}"
```

**File: dev-config.yml** (Development)
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

**File: prod-config.yml** (Production)
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

Combine fixed text with parameters in function arguments.

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

**Generated Output:**
```yaml
services:
  processor:
    service_id: data-prod
    registry: mycompany/data:v2.1
```

---

## Real-World Examples

YAML Composer works with any YAML-based system. Here are several use cases:

### Use Case 1: Docker Compose Stacks (PostgreSQL + PgAdmin)

This demonstrates a practical, production-ready setup with multiple PostgreSQL databases and PgAdmin management interface.

#### Folder Structure

```
repo/
├── templates/
│   ├── core.yml              # Base configuration templates
│   ├── image_version.yml     # Centralized image versions
│   ├── postgres.yml          # PostgreSQL service template
│   └── pg_admin.yml          # PgAdmin service template
├── stack/
│   └── pg_db_admin/
│       └── pg_db_admin_app_stack.yml  # Main stack definition
└── services/
    └── pg_db_admin_service.yml        # Generated output
```

### Step 1: Define Base Templates

**File: templates/core.yml**
```yaml
# Common configuration for all services
X-REF-BASE-TEMPLATE:
  environment:
    - TZ=Asia/Singapore
  restart: unless-stopped
  security_opt:
    - no-new-privileges:true
  pids_limit: 100
  mem_limit: 512m
  cpus: "1.0"

X-REF-BASE-READONLY-TEMPLATE:
  environment:
    - TZ=Asia/Singapore
  restart: unless-stopped
  read_only: true
  security_opt:
    - no-new-privileges:true
```

---

### Step 2: Define Service-Specific Templates

**File: templates/image_version.yml**
```yaml
# Centralize image versions for easy updates
X-REF-IMAGE-POSTGRES: postgres:18.3-alpine
X-REF-IMAGE-PG-ADMIN4: dpage/pgadmin4
```

**File: templates/postgres.yml**
```yaml
# PostgreSQL template with parameterized configuration
X-REF-FUNCT-TEMPLATE-POSTGRES:
  # Inherit base template
  X-REF-BASE-TEMPLATE: null
  
  image: X-REF-IMAGE-POSTGRES  # Reference image version
  container_name: "{X-ARG-1}"  # DB container name
  shm_size: 128mb
  
  environment:
    - "{X-ARG-2}"              # DB environment variables
  
  ports:
    - "{X-ARG-3}"              # Port mapping
  
  volumes:
    - "{X-ARG-4}"              # Volume mount
  
  healthcheck:
    test: ["CMD-SHELL", "pg_isready -U $$POSTGRES_USER -d $$POSTGRES_DB"]
    interval: 10s
    timeout: 5s
    retries: 5
    start_period: 15s
```

**File: templates/pg_admin.yml**
```yaml
# PgAdmin template (lightweight, for read-only operations)
X-REF-FUNCT-TEMPLATE-PG-ADMIN:
  X-REF-BASE-TEMPLATE: null
  
  image: X-REF-IMAGE-PG-ADMIN4
  container_name: "{X-ARG-1}"          # PgAdmin container name
  environment: "{X-ARG-2}"             # Environment variables
  ports:
    - "{X-ARG-3}"                      # Web UI port
  volumes:
    - "{X-ARG-4}"                      # Data volumes
```

---

### Step 3: Create Stack Definition

**File: stack/pg_db_admin/pg_db_admin_app_stack.yml**
```yaml
# Include all templates
X-INCLUDE:
  - templates/core.yml
  - templates/image_version.yml
  - templates/postgres.yml
  - templates/pg_admin.yml

# Output location
X-OUTPUT: services/pg_db_admin_service.yml

# Environment-specific overrides
X-OVERRIDE:
  # Database 1 Configuration
  X-REF-DB1-CONTAINER-NAME: db1
  X-REF-DB1-ENV:
    - POSTGRES_DB=mydb1
    - POSTGRES_USER=user
    - POSTGRES_PASSWORD=password
  X-REF-DB1-PORTS: []  # No public port exposure
  X-REF-DB1-VOLUME:
    - ${PG_DB_ADMIN_DATA:?}\db1:/var/lib/postgresql

  # Database 2 Configuration
  X-REF-DB2-CONTAINER-NAME: db2
  X-REF-DB2-ENV:
    - POSTGRES_DB=mydb2
    - POSTGRES_USER=user
    - POSTGRES_PASSWORD=password
  X-REF-DB2-PORTS: []
  X-REF-DB2-VOLUME:
    - ${PG_DB_ADMIN_DATA:?}\db2:/var/lib/postgresql

  # PgAdmin Configuration
  X-REF-PGADMIN-CONTAINER-NAME: pg_admin
  X-REF-PGADMIN-ENV:
    - PGADMIN_DEFAULT_EMAIL=admin@admin.com
    - PGADMIN_DEFAULT_PASSWORD=password
  X-REF-PGADMIN-PORTS: 8080:80
  X-REF-PGADMIN-VOLUME:
    - ${PG_DB_ADMIN_DATA:?}\pgadmin\data:/var/lib/pgadmin
    - ${PG_DB_ADMIN_DATA:?}\pgadmin\servers.json:/pgadmin4/servers.json

# Service composition
services:
  db-one:
    # Function call with parameters
    X-REF-FUNCT-TEMPLATE-POSTGRES(X-REF-DB1-CONTAINER-NAME,X-REF-DB1-ENV,X-REF-DB1-PORTS,X-REF-DB1-VOLUME): null
    networks:
      - pg_service_network

  db-two:
    # Function call with parameters
    X-REF-FUNCT-TEMPLATE-POSTGRES(X-REF-DB2-CONTAINER-NAME,X-REF-DB2-ENV,X-REF-DB2-PORTS,X-REF-DB2-VOLUME): null
    networks:
      - pg_service_network

  pg_admin:
    # PgAdmin service
    X-REF-FUNCT-TEMPLATE-PG-ADMIN(X-REF-PGADMIN-CONTAINER-NAME,X-REF-PGADMIN-ENV,X-REF-PGADMIN-PORTS,X-REF-PGADMIN-VOLUME): null
    networks:
      - pg_service_network

networks:
  pg_service_network:
    driver: bridge
```

---

### Step 4: Generate and Run

```bash
# Set workspace to repo folder
export PG_DB_ADMIN_DATA=/var/lib/pgadmin

# Generate docker-compose.yml
py-yaml-composer stack/pg_db_admin/pg_db_admin_app_stack.yml -w repo

# View generated output
cat services/pg_db_admin_service.yml

# Start services
cd services
docker-compose -f pg_db_admin_service.yml up -d

# Access PgAdmin
# Open browser: http://localhost:8080
# Login: admin@admin.com / password
```

---

### Generated Output

```yaml
services:
  db-one:
    environment:
      - TZ=Asia/Singapore
    restart: unless-stopped
    security_opt:
      - no-new-privileges:true
    pids_limit: 100
    mem_limit: 512m
    cpus: "1.0"
    image: postgres:18.3-alpine
    container_name: db1
    shm_size: 128mb
    environment:
      - POSTGRES_DB=mydb1
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=password
    ports: []
    volumes:
      - ${PG_DB_ADMIN_DATA:?}\db1:/var/lib/postgresql
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U $$POSTGRES_USER -d $$POSTGRES_DB"]
      interval: 10s
      timeout: 5s
      retries: 5
      start_period: 15s
    networks:
      - pg_service_network

  db-two:
    # ... similar to db-one with db2 configuration

  pg_admin:
    image: dpage/pgadmin4
    container_name: pg_admin
    environment:
      - PGADMIN_DEFAULT_EMAIL=admin@admin.com
      - PGADMIN_DEFAULT_PASSWORD=password
    ports:
      - 8080:80
    volumes:
      - ${PG_DB_ADMIN_DATA:?}\pgadmin\data:/var/lib/pgadmin
      - ${PG_DB_ADMIN_DATA:?}\pgadmin\servers.json:/pgadmin4/servers.json
    networks:
      - pg_service_network

networks:
  pg_service_network:
    driver: bridge
```

---

### Use Case 2: Kubernetes Configuration Management

Use YAML Composer to manage multiple Kubernetes deployment configurations across environments.

**File: templates/k8s-deployment.yml**
```yaml
X-REF-K8S-DEPLOYMENT:
  apiVersion: apps/v1
  kind: Deployment
  metadata:
    name: \"{X-ARG-1}\"
    namespace: \"{X-ARG-2}\"
  spec:
    replicas: \"{X-ARG-3}\"
    template:
      metadata:
        labels:
          app: \"{X-ARG-1}\"
      spec:
        containers:
        - name: app
          image: \"{X-ARG-4}\"
          ports:
          - containerPort: \"{X-ARG-5}\"
```

**File: k8s-prod-config.yml**
```yaml
X-INCLUDE:
  - templates/k8s-deployment.yml

X-OUTPUT: generated/k8s-prod.yml
X-OVERRIDE:
  X-REF-APP-NAME: myapp
  X-REF-NAMESPACE: production
  X-REF-REPLICAS: \"3\"
  X-REF-IMAGE: myrepo/myapp:v1.2.3
  X-REF-PORT: \"8080\"

deployments:
  - X-REF-K8S-DEPLOYMENT(X-REF-APP-NAME, X-REF-NAMESPACE, X-REF-REPLICAS, X-REF-IMAGE, X-REF-PORT): null
```

**Generated Output:**
```yaml
deployments:
  - apiVersion: apps/v1
    kind: Deployment
    metadata:
      name: myapp
      namespace: production
    spec:
      replicas: \"3\"
      template:
        metadata:
          labels:
            app: myapp
        spec:
          containers:
          - name: app
            image: myrepo/myapp:v1.2.3
            ports:
            - containerPort: \"8080\"
```

---

### Use Case 3: Application Configuration

Manage application configuration files with environment-specific overrides.

**File: templates/app-settings.yml**
```yaml
X-REF-APP-CONFIG:
  server:
    host: \"{X-ARG-1}\"
    port: \"{X-ARG-2}\"
  database:
    host: \"{X-ARG-3}\"
    pool_size: \"{X-ARG-4}\"
  cache:
    enabled: \"{X-ARG-5}\"
    ttl: \"{X-ARG-6}\"
```

**File: app-dev-config.yml**
```yaml
X-INCLUDE:
  - templates/app-settings.yml

X-OUTPUT: generated/dev/settings.yml
X-OVERRIDE:
  X-REF-SERVER-HOST: localhost
  X-REF-SERVER-PORT: \"3000\"
  X-REF-DB-HOST: localhost
  X-REF-DB-POOL: \"5\"
  X-REF-CACHE-ENABLED: \"false\"
  X-REF-CACHE-TTL: \"300\"

application:
  X-REF-APP-CONFIG(X-REF-SERVER-HOST, X-REF-SERVER-PORT, X-REF-DB-HOST, X-REF-DB-POOL, X-REF-CACHE-ENABLED, X-REF-CACHE-TTL): null
```

**File: app-prod-config.yml**
```yaml
X-INCLUDE:
  - templates/app-settings.yml

X-OUTPUT: generated/prod/settings.yml
X-OVERRIDE:
  X-REF-SERVER-HOST: 0.0.0.0
  X-REF-SERVER-PORT: \"8080\"
  X-REF-DB-HOST: db.prod.internal
  X-REF-DB-POOL: \"50\"
  X-REF-CACHE-ENABLED: \"true\"
  X-REF-CACHE-TTL: \"3600\"

application:
  X-REF-APP-CONFIG(X-REF-SERVER-HOST, X-REF-SERVER-PORT, X-REF-DB-HOST, X-REF-DB-POOL, X-REF-CACHE-ENABLED, X-REF-CACHE-TTL): null
```

---

### Use Case 4: Infrastructure-as-Code (Terraform)

Generate Terraform variable files and configurations.

**File: templates/terraform-vars.yml**
```yaml
X-REF-TF-VARIABLES:
  region: \"{X-ARG-1}\"
  environment: \"{X-ARG-2}\"
  instance_type: \"{X-ARG-3}\"
  instance_count: \"{X-ARG-4}\"
  tags:
    - project: myproject
    - managed_by: terraform
```

**File: infrastructure-staging.yml**
```yaml
X-INCLUDE:
  - templates/terraform-vars.yml

X-OUTPUT: generated/terraform-staging.tfvars.yml
X-OVERRIDE:
  X-REF-REGION: us-east-1
  X-REF-ENV: staging
  X-REF-INSTANCE-TYPE: t3.medium
  X-REF-INSTANCE-COUNT: \"2\"

terraform:
  X-REF-TF-VARIABLES(X-REF-REGION, X-REF-ENV, X-REF-INSTANCE-TYPE, X-REF-INSTANCE-COUNT): null
```

---

## Architecture

### Data Flow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│ User Input: YAML Template with X-INCLUDE, X-OVERRIDE, etc.     │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
              ┌────────────────────────┐
              │  YamlGenerator.start() │  Load template & ref data
              └────────────┬───────────┘
                           │
         ┌─────────────────┼─────────────────┐
         │                 │                 │
         ▼                 ▼                 ▼
  ┌────────────┐  ┌────────────────┐  ┌──────────────┐
  │ Load YAML  │  │ Load X-INCLUDE │  │ Load X-OVERRIDE
  │   file     │  │   ref files    │  │   references
  └────────────┘  └────────────────┘  └──────────────┘
         │                 │                 │
         └─────────────────┼─────────────────┘
                           │
                           ▼
              ┌─────────────────────────────────┐
              │  ActionContext (ref_data setup) │
              └─────────────┬───────────────────┘
                            │
                            ▼
            ┌────────────────────────────────────┐
            │  YamlFunctionAction                │
            │  Replace X-REF-FuncName() calls    │
            └────────────┬───────────────────────┘
                         │
                         ▼
            ┌────────────────────────────────────┐
            │  YamlTraverser (DFS)               │  For each node:
            │  - YamlXRefAction                  │  - Resolve X-REF-* refs
            │  - YamlSortDockerComposeAction    │  - Sort docker-compose keys
            └────────────┬───────────────────────┘
                         │
                         ▼
              ┌───────────────────────┐
              │ Save to X-OUTPUT path │
              └───────────────────────┘
                         │
                         ▼
            ┌──────────────────────────────────┐
            │ Generated YAML ready for use     │
            │ (e.g., docker-compose.yml)      │
            └──────────────────────────────────┘
```

### Component Responsibilities

| Component | Purpose |
|-----------|---------|
| **YamlGenerator** | Orchestrates the pipeline: loads templates, manages action execution |
| **YamlFileHelper** | I/O operations: loads/saves YAML files with workspace path resolution |
| **YamlTraverser** | Depth-first traversal of YAML structure; applies actions to each node |
| **YamlFunctionAction** | Replaces parameterized function calls with actual values |
| **YamlXRefAction** | Resolves `X-REF-*` references and merges templates |
| **YamlSortDockerComposeNodeAction** | Sorts docker-compose keys in standard order |
| **ActionContext** | Passes reference data through the action pipeline |

---

## API Reference

### Command Line

```bash
py-yaml-composer TEMPLATE_FILE [OPTIONS]

Arguments:
  TEMPLATE_FILE  Path to YAML template (absolute or relative to workspace)

Options:
  -w, --workspace PATH  Workspace root for loading/saving files (default: /yaml_workspace)
  -h, --help            Show help message
```

### YAML Metadata Tags

| Tag | Purpose | Value Type | Example |
|-----|---------|-----------|---------|
| `X-INCLUDE` | Load external template files | List[str] | `X-INCLUDE: [base.yml, services.yml]` |
| `X-OVERRIDE` | Define templates & overrides | Dict | `X-OVERRIDE: {X-REF-MyService: {...}}` |
| `X-OUTPUT` | Output file path | str | `X-OUTPUT: generated/docker-compose.yml` |
| `X-REF-*` | Template reference marker | any | `X-REF-Service: null` or `X-REF-Func('arg'): null` |
| `{X-ARG-N}` | Function parameter placeholder | str | `image: "{X-ARG-1}"` (1-based indexing) |

### Function Syntax

```
X-REF-FunctionName('arg1', 'arg2', 'arg3'): null
```

- **Function name:** Custom identifier after `X-REF-`
- **Arguments:** Comma-separated, quoted strings
- **Placeholder format:** `{X-ARG-1}`, `{X-ARG-2}`, etc. (1-based indexing)

---

## Best Practices

### 1. **Organize Templates by Concern**

```
templates/
├── base.yml              # Common base configurations
├── common.yml            # Shared settings/policies
├── infrastructure/
│   ├── database.yml      # Database component templates
│   ├── cache.yml         # Cache component templates
│   ├── messaging.yml     # Message broker templates
│   └── security.yml      # Security/auth templates
├── versions.yml          # Centralized version references
└── environments.yml      # Environment-specific defaults
```

---

### 2. **Centralize Versions & References**

**Good:**
```yaml
# templates/versions.yml
X-REF-VERSION-POSTGRES: postgres:18.3-alpine
X-REF-VERSION-REDIS: redis:7.2-alpine
X-REF-VERSION-K8S-API: v1.28
X-REF-VERSION-TERRAFORM: 1.5.0

# Reference in component template
X-REF-DATABASE:
  image: X-REF-VERSION-POSTGRES
```

**Why:** Easy to update versions globally; single source of truth across all configurations.

---

### 3. **Use Descriptive Reference Names**

**Good:**
```yaml
X-REF-DB1-CONTAINER-NAME: db1
X-REF-DB1-ENV: [...]
X-REF-DB1-PORTS: [...]
X-REF-DB1-VOLUME: [...]
```

**Avoid:**
```yaml
X-REF-A: db1
X-REF-B: [...]
```

---

### 4. **Separate Configuration from Templates**

**Good:**
```yaml
# templates/component.yml
X-REF-APP-SERVICE:
  name: "{X-ARG-1}"
  version: X-REF-VERSION-APP
  config: "{X-ARG-2}"

# stack/prod-config.yml
X-OVERRIDE:
  X-REF-APP-NAME: myapp
  X-REF-APP-CONFIG: {log_level: INFO, timeout: 60}
X-REF-APP-SERVICE(X-REF-APP-NAME, X-REF-APP-CONFIG): null
```

**Why:** Templates stay generic; overrides contain environment-specific values.

---

### 5. **Use Environment Variables for Secrets**

**Good:**
```yaml
X-REF-DB-PASSWORD: ${DB_PASSWORD:?error - DB_PASSWORD not set}
X-REF-API-KEY: ${API_KEY:?error}
```

**Why:** Never commit secrets to version control.

---

### 6. **Document Template Parameters**

```yaml
# templates/component-template.yml
###
# Service Configuration Template
# 
# Parameters:
#   ARG-1: Component name (string)
#   ARG-2: Environment tier (dev/staging/prod)
#   ARG-3: Resource allocation (string, e.g., '512m', '2Gi')
#   ARG-4: Instance count (integer as string)
#
# Example usage:
#   X-REF-COMPONENT('api', 'prod', '2Gi', '3'):
###
X-REF-COMPONENT:
  name: "{X-ARG-1}"
  environment: "{X-ARG-2}"
  resources:
    memory: "{X-ARG-3}"
  replicas: "{X-ARG-4}"
```

---

### 7. **Validate Generated Output**

```bash
# Generate
py-yaml-composer stack/prod-config.yml -w repo

# Validate YAML syntax
python -m yaml generated/config.yml

# For Docker Compose:
docker-compose -f services/docker-compose.yml config

# For Kubernetes:
kubectl apply -f generated/k8s-config.yml --dry-run=client

# For Terraform:
terraform validate generated/
```

**Why:** Catch configuration errors before deployment.

---

### 8. **Version Control Strategy**

```
repo/
├── .gitignore            # Ignore generated/ and .env
├── templates/            # ✓ Commit: reusable templates
├── stacks/               # ✓ Commit: stack definitions
├── configs/              # ✓ Commit: stack configs (dev, prod, etc.)
├── generated/            # ✗ Ignore: generated files
├── data/                 # ✗ Ignore: runtime data
└── .env.example          # ✓ Commit: example vars (NO secrets)
```

**.gitignore:**
```
generated/
data/
.env
*.local
*.tmp
__pycache__/
.pytest_cache/
.mypy_cache/
*.pyc
```

**Why:** Keep repository clean; templates are portable; generated configs are environment-specific.

---

## Troubleshooting

### Issue: "File does not exist"
**Cause:** X-INCLUDE references a file that doesn't exist or wrong workspace path.
```bash
# Solution: Verify file exists and use correct -w workspace path
py-yaml-composer template.yml -w /absolute/path/to/repo
```

---

### Issue: "Reference not found"
**Cause:** X-REF-* marker references undefined template.
```yaml
# Check: Is this defined in X-OVERRIDE or X-INCLUDE files?
X-REF-undefined-ref: null  # ERROR: X-REF-undefined-ref not defined
```

---

### Issue: Function arguments mismatch
**Cause:** Number of `{X-ARG-N}` placeholders doesn't match function arguments.
```yaml
# WRONG: 2 placeholders, 3 arguments provided
X-REF-Service('{X-ARG-1}', '{X-ARG-2}', 'extra_arg'): null

# WRONG: 3 placeholders in template, only 2 arguments provided
X-REF-Service('value1', 'value2'): null

# RIGHT: Number of placeholders matches arguments
X-REF-Service('value1', 'value2', 'value3'): null
```

**Solution:** Count `{X-ARG-N}` placeholders in template definition and ensure function calls provide matching number of arguments.

---

## Running Tests

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
