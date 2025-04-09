#!/usr/bin/env sh
set -eux

# mocks to be injected into task step scripts
function git() {
  if [[ "$*" == *"clone"* ]]; then
    gitRepo=$(echo "$*" | cut -f5 -d/ | cut -f1 -d.)
    mkdir -p "$gitRepo/data/advisories/test-origin/2024/1234"
    cat > "$gitRepo/data/advisories/test-origin/2024/1234/advisory.yaml" << EOF
content:
  images:
    - image: quay.io/test/released-image:1.0.0
      repository: test/released-image
      tags:
        - 1.0.0
EOF
  fi
  if [[ "$*" == "init"* ]]; then
    /usr/bin/git $*
  fi
  if [[ "$*" == "add"* ]]; then
    /usr/bin/git $*
  fi
  if [[ "$*" == "status"* ]]; then
    /usr/bin/git $*
  fi
  if [[ "$*" == "commit"* ]]; then
    /usr/bin/git "$@"
  fi
  if [[ "$*" == "config"* ]]; then
    /usr/bin/git "$@"
  fi
}

function yq() {
  if [[ "$*" == *"select(.image == \"quay.io/test/released-image:1.0.0\")"* ]]; then
    echo "quay.io/test/released-image:1.0.0"
    exit 0
  elif [[ "$*" == *"select(.image == \"quay.io/test/new-image:1.0.0\")"* ]]; then
    exit 1
  fi
  /usr/bin/yq "$@"
}

function find() {
  echo "Mock find called with: $*" >&2

  if echo "$*" | grep -q "data/advisories/test-origin"; then
    # Simulate directories with timestamps
    echo "1712012345.0 data/advisories/test-origin/2024/1234"
  else
    echo "Error: Unexpected find command: $*" >&2
    exit 1
  fi
} 