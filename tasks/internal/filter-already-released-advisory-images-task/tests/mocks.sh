#!/usr/bin/env bash
set -euo pipefail

# --- Mock gitlab-functions ---
gitlab_init() {
  echo "Mock gitlab_init called"
}

# --- Mock git-functions ---
git_functions_init() {
  echo "Mock git_functions_init called"
}

# --- Mock git_clone_and_checkout ---
git_clone_and_checkout() {
  echo "Mock git_clone_and_checkout called"

  mkdir -p /tmp/data/advisories/stage/20240426-123456/
  cat <<EOF > /tmp/data/advisories/stage/20240426-123456/advisory.yaml
spec:
  content:
    images:
      - containerImage: quay.io/example/image1@sha256:aaa
        tags: ["latest"]
        repository: quay.io/example
EOF
}

# --- Mock find command ---
find() {
  echo "Mock find called with: $*" >&2
  if echo "$*" | grep -q "/data/advisories/stage"; then
    echo "1712012345.0 /tmp/data/advisories/stage/20240426-123456"
  else
    echo "Error: Unexpected find command: $*" >&2
    exit 1
  fi
}

# --- Mock yq command ---
yq() {
  echo "Mock yq called with: $*" >&2
  if [[ "$2" == ".spec.content.images // []" ]]; then
    # Return the advisory image we injected
    echo '[{"containerImage":"quay.io/example/image1@sha256:aaa","tags":["latest"],"repository":"quay.io/example"}]'
  else
    echo "Error: Unexpected yq query: $2" >&2
    exit 1
  fi
}
