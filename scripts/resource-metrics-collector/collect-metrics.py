#!/usr/bin/env python3
"""
Collect CPU and Memory metrics for Tekton task steps from Konflux clusters.

This script queries Prometheus to get resource usage data for task steps,
which can be used to set appropriate CPU/Memory requests and limits.

Usage:
    1. Create a file with oc login commands (one per line)
    2. Run: python3 collect-metrics.py --logins logins.txt --namespace <namespace>

Output:
    - CSV files with CPU (95th percentile) and Memory (max) per step
    - One file per cluster + combined file

Requirements:
    - Python 3.6+
    - requests library: pip install requests
    - oc CLI installed and in PATH
"""

import subprocess
import requests
import urllib3
import csv
import os
import sys
import argparse
from datetime import datetime

# Disable SSL warnings for self-signed certs
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def run_cmd(cmd):
    """Run a shell command and return output."""
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.stdout.strip()


def get_prometheus_route():
    """Get the Prometheus route URL for current cluster."""
    try:
        result = run_cmd("oc -n openshift-monitoring get route prometheus-k8s -o jsonpath='{.spec.host}'")
        return result.strip("'")
    except:
        return None


def get_token():
    """Get the current OC token."""
    return run_cmd("oc whoami -t")


def get_cluster_name():
    """Get a short name for current cluster context."""
    context = run_cmd("oc config current-context")
    # Extract meaningful name from context
    server = run_cmd("oc whoami --show-server")
    if server:
        # Extract cluster name from server URL
        parts = server.replace("https://", "").replace("http://", "").split(".")
        if len(parts) > 1:
            return parts[0].replace("api-", "").replace("api", "")
    return context[:30] if context else "unknown"


def query_prometheus(prom_url, token, query):
    """Execute a PromQL query against Prometheus."""
    url = f"https://{prom_url}/api/v1/query"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}",
    }
    params = {"query": query}
    
    try:
        response = requests.get(url, headers=headers, params=params, verify=False, timeout=60)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"    Error querying Prometheus: {e}")
        return None


def parse_results(data):
    """Parse Prometheus response into dict of container -> value."""
    results = {}
    if data and data.get("status") == "success":
        for item in data.get("data", {}).get("result", []):
            container = item.get("metric", {}).get("container", "unknown")
            step_name = container.replace("step-", "")
            value = float(item.get("value", [0, 0])[1])
            results[step_name] = value
    return results


def format_cpu(cores):
    """Format CPU cores to Kubernetes format (e.g., 250m, 1, 2)."""
    if cores == 0:
        return "0"
    elif cores < 1:
        return f"{int(cores * 1000)}m"
    else:
        return f"{cores:.2f}"


def format_memory(bytes_val):
    """Format bytes to Kubernetes format (e.g., 128Mi, 1Gi)."""
    if bytes_val == 0:
        return "0"
    gi = bytes_val / (1024 ** 3)
    mi = bytes_val / (1024 ** 2)
    if gi >= 1:
        return f"{gi:.1f}Gi"
    else:
        return f"{int(mi)}Mi"


def login_to_cluster(login_cmd):
    """Login to a cluster using oc login command."""
    # Extract server URL for display (hide token)
    server = "unknown"
    if "--server=" in login_cmd:
        server = login_cmd.split("--server=")[1].split()[0]
    print(f"\nLogging into: {server}")
    
    result = subprocess.run(login_cmd, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"  Login failed: {result.stderr}")
        return False
    print(f"  Login successful")
    return True


def collect_metrics(namespace, lookback_days):
    """Collect CPU and Memory metrics for a cluster."""
    print(f"  Getting Prometheus route...")
    prom_url = get_prometheus_route()
    if not prom_url:
        print(f"    Could not get Prometheus route")
        return None
    
    print(f"  Prometheus: {prom_url}")
    print(f"  Namespace: {namespace}")
    print(f"  Lookback: {lookback_days} days")
    
    token = get_token()
    if not token:
        print(f"    Could not get token")
        return None
    
    # CPU Query - 95th percentile
    cpu_query = f'''
        quantile by (container) (
            0.95,
            max_over_time(
                node_namespace_pod_container:container_cpu_usage_seconds_total:sum_irate{{
                    namespace="{namespace}",
                    container=~"step-.*"
                }}[{lookback_days}d]
            )
        )
    '''
    
    # Memory Query - max
    mem_query = f'''
        max by (container) (
            max_over_time(
                container_memory_working_set_bytes{{
                    namespace="{namespace}",
                    container=~"step-.*"
                }}[{lookback_days}d]
            )
        )
    '''
    
    print(f"  Querying CPU metrics (95th percentile)...")
    cpu_data = query_prometheus(prom_url, token, cpu_query)
    cpu_results = parse_results(cpu_data)
    print(f"    Found {len(cpu_results)} steps with CPU data")
    
    print(f"  Querying Memory metrics (max)...")
    mem_data = query_prometheus(prom_url, token, mem_query)
    mem_results = parse_results(mem_data)
    print(f"    Found {len(mem_results)} steps with Memory data")
    
    # Combine results
    all_steps = set(cpu_results.keys()) | set(mem_results.keys())
    
    results = []
    for step in sorted(all_steps):
        cpu_val = cpu_results.get(step, 0)
        mem_val = mem_results.get(step, 0)
        results.append({
            "step_name": step,
            "cpu_cores": cpu_val,
            "cpu_formatted": format_cpu(cpu_val),
            "memory_bytes": mem_val,
            "memory_formatted": format_memory(mem_val),
        })
    
    print(f"  Total: {len(results)} unique steps")
    return results


def save_to_csv(results, filename, include_cluster=False, cluster_name=None):
    """Save results to CSV file."""
    if not results:
        return
    
    os.makedirs(os.path.dirname(filename) if os.path.dirname(filename) else ".", exist_ok=True)
    
    fieldnames = list(results[0].keys())
    if include_cluster and cluster_name:
        for r in results:
            r['cluster'] = cluster_name
        fieldnames = ['cluster'] + fieldnames
    
    with open(filename, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)
    
    print(f"  Saved to: {filename}")


def main():
    parser = argparse.ArgumentParser(
        description="Collect CPU/Memory metrics for Tekton task steps from Konflux clusters",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Collect from clusters listed in logins.txt for namespace 'my-tenant'
    python3 collect-metrics.py --logins logins.txt --namespace my-tenant

    # With custom lookback period and output directory
    python3 collect-metrics.py --logins logins.txt --namespace my-tenant --days 30 --output ./metrics

    # Single cluster (already logged in)
    python3 collect-metrics.py --namespace my-tenant --skip-login
        """
    )
    parser.add_argument("--logins", help="File containing oc login commands (one per line)")
    parser.add_argument("--namespace", required=True, help="Kubernetes namespace to query")
    parser.add_argument("--days", type=int, default=14, help="Lookback period in days (default: 14)")
    parser.add_argument("--output", default="./metrics-output", help="Output directory for CSV files")
    parser.add_argument("--skip-login", action="store_true", help="Skip login, use current context")
    args = parser.parse_args()
    
    print("=" * 60)
    print("Resource Metrics Collector for Konflux Tasks")
    print("=" * 60)
    print(f"Namespace: {args.namespace}")
    print(f"Lookback: {args.days} days")
    print(f"Output: {args.output}/")
    
    # Determine clusters to query
    login_commands = []
    if args.skip_login:
        login_commands = [None]  # Use current context
    elif args.logins:
        if not os.path.exists(args.logins):
            print(f"Error: Login file '{args.logins}' not found")
            sys.exit(1)
        with open(args.logins, 'r') as f:
            login_commands = [line.strip() for line in f if line.strip().startswith("oc login")]
        print(f"Found {len(login_commands)} cluster(s) in login file")
    else:
        print("Error: Either --logins or --skip-login is required")
        sys.exit(1)
    
    os.makedirs(args.output, exist_ok=True)
    all_results = []
    
    for login_cmd in login_commands:
        if login_cmd:
            if not login_to_cluster(login_cmd):
                continue
        
        cluster_name = get_cluster_name()
        print(f"  Cluster: {cluster_name}")
        
        results = collect_metrics(args.namespace, args.days)
        
        if results:
            # Save individual cluster file
            csv_file = f"{args.output}/{cluster_name}-metrics.csv"
            save_to_csv(results, csv_file)
            
            # Add to combined results
            for r in results:
                r_copy = r.copy()
                r_copy['cluster'] = cluster_name
                all_results.append(r_copy)
    
    # Save combined results
    if all_results:
        combined_file = f"{args.output}/all-clusters-combined.csv"
        with open(combined_file, 'w', newline='') as f:
            fieldnames = ['cluster', 'step_name', 'cpu_cores', 'cpu_formatted', 'memory_bytes', 'memory_formatted']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(all_results)
        print(f"\nCombined results saved to: {combined_file}")
        
        # Print summary
        print("\n" + "=" * 60)
        print("SUMMARY")
        print("=" * 60)
        print(f"Clusters queried: {len(set(r['cluster'] for r in all_results))}")
        print(f"Total step metrics: {len(all_results)}")
        
        # Top CPU consumers
        all_results.sort(key=lambda x: x['cpu_cores'], reverse=True)
        print(f"\nTop 10 CPU consumers:")
        for r in all_results[:10]:
            print(f"  {r['step_name']:<40} {r['cpu_formatted']:<10} ({r['cluster']})")
    else:
        print("\nNo metrics collected")


if __name__ == "__main__":
    main()

