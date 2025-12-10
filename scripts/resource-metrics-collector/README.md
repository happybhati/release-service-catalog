# Resource Metrics Collector for Konflux Tasks

Collects CPU and Memory usage metrics for Tekton task steps from Prometheus across multiple Konflux clusters.

## What It Collects

| Metric | Query Type | Description |
|--------|-----------|-------------|
| CPU | 95th percentile | node_namespace_pod_container:container_cpu_usage_seconds_total:sum_irate |
| Memory | Maximum | container_memory_working_set_bytes |

## Prerequisites

```bash
# Python 3.6+
python3 --version

# Install requests library
pip3 install requests

# oc CLI must be installed and in PATH
oc version
```

## Usage

### Step 1: Create a Login File

Create a file (e.g., logins.txt) with oc login commands for each cluster:

```
oc login --token=<token1> --server=https://api.cluster1.example.com:6443
oc login --token=<token2> --server=https://api.cluster2.example.com:6443
```

SECURITY NOTE: Delete this file after use. Never commit tokens to git.

### Step 2: Run the Script

```bash
# Basic usage
python3 collect-metrics.py --logins logins.txt --namespace rhtap-releng-tenant

# With custom lookback period (30 days)
python3 collect-metrics.py --logins logins.txt --namespace rhtap-releng-tenant --days 30

# Custom output directory
python3 collect-metrics.py --logins logins.txt --namespace rhtap-releng-tenant --output ./my-metrics

# Single cluster (if already logged in)
python3 collect-metrics.py --namespace rhtap-releng-tenant --skip-login
```

### Step 3: Review Output

The script creates:
- cluster-name-metrics.csv - Per-cluster data
- all-clusters-combined.csv - Combined data from all clusters

### Step 4: Clean Up

```bash
# Delete the login file (contains tokens!)
rm logins.txt
```

## Output Format

```csv
cluster,step_name,cpu_cores,cpu_formatted,memory_bytes,memory_formatted
stone-prd-rh01,push-snapshot,7.38,7.38,524288000,500Mi
stone-prd-rh01,create-pyxis-image,2.76,2.76,268435456,256Mi
```

## CLI Options

| Option | Required | Default | Description |
|--------|----------|---------|-------------|
| --logins | Yes* | - | File with oc login commands |
| --namespace | Yes | - | Kubernetes namespace to query |
| --days | No | 14 | Lookback period in days |
| --output | No | ./metrics-output | Output directory |
| --skip-login | No | - | Use current oc context |

*Not required if --skip-login is used

## Namespaces

| Namespace | Use Case |
|-----------|----------|
| rhtap-releng-tenant | Managed release pipelines (external clusters) |
| internal-services | Internal release tasks (internal clusters) |

## Related Jira

- RELEASE-2035: Consider setting limit.cpu=request.cpu in task resources
- KONFLUX-6712: Define resources for more tasks (build-definitions)

## Credits

Based on scripts shared by the Performance Team for KONFLUX-6712.

