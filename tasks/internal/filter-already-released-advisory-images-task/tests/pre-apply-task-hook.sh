#!/usr/bin/env bash

# $1 is the path to the Task YAML
TASK_PATH="$1"
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

# Add mocks.sh content at the beginning of the task's first step script
yq -i '.spec.steps[0].script = load_str("'$SCRIPT_DIR'/mocks.sh") + .spec.steps[0].script' "$TASK_PATH"

# No need to create any Kubernetes secrets for this task
echo "Injected mocks.sh into the Task script successfully"
