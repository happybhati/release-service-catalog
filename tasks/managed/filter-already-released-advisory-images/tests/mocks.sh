#!/bin/bash
set -ex

# Mock internal-request command
function internal-request() {
  local rando=$RANDOM
  echo "Creating InternalRequest with label test-id=$rando"
  
  # Create a mock InternalRequest
  cat > /tmp/mock-internal-request.yaml << EOF
apiVersion: appstudio.redhat.com/v1alpha1
kind: InternalRequest
metadata:
  name: mock-internal-request-$rando
  labels:
    internal-services.appstudio.openshift.io/test-id: "$rando"
spec:
  request: |
    {
      "snapshotPath": "$(params.snapshotPath)",
      "origin": "$(params.origin)",
      "advisory_secret_name": "$(params.advisory_secret_name)"
    }
status:
  conditions:
    - type: Succeeded
      status: "True"
      reason: "Succeeded"
      message: "Task completed successfully"
  results:
    - name: filteredSnapshotPath
      value: "filtered-snapshot.json"
EOF

  # Apply the mock InternalRequest
  kubectl apply -f /tmp/mock-internal-request.yaml
  
  # Wait for the mock InternalRequest to complete
  echo "Waiting for mock InternalRequest to complete..."
  sleep 1
  
  # Create a mock filtered snapshot
  cat > $(workspaces.tests-workspace.path)/filtered-snapshot.json << EOF
{
  "components": [
    {
      "name": "new-component",
      "containerImage": "quay.io/test/new-image:v2.0.0",
      "version": "2.0.0"
    }
  ]
}
EOF
}

# Mock kubectl command
function kubectl() {
  if [[ "$*" == "get internalrequest "*"-o=jsonpath={.status.results}" ]]; then
    echo '{
      "result": "Success",
      "filtered_snapshot": "{\"components\":[{\"name\":\"new-component\",\"containerImage\":\"quay.io/test/new-image:v2.0.0\",\"version\":\"2.0.0\"}]}"
    }'
  else
    /usr/bin/kubectl "$@"
  fi
}

# Main script
internal-request 