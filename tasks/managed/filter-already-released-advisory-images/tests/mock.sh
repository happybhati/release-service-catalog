#!/usr/bin/env bash
set -ex

# Mock kubectl command
function kubectl() {
  if [[ "$*" == "get internalrequest "*"-o=jsonpath={.status.results}" ]]; then
    # Get the test case from the environment
    TEST_CASE=${TEST_CASE:-"success"}
    
    case $TEST_CASE in
      "success")
        echo '{
          "result": "Success",
          "filtered_snapshot": "{\"application\":\"myapp\",\"components\":[{\"name\":\"comp2\",\"repository\":\"quay.io/redhat-prod/another\",\"containerImage\":\"quay.io/redhat-prod/another@sha256:xyz\",\"tags\":[\"v2.0\"]}]}"
        }'
        ;;
      "base_image")
        echo '{
          "result": "Success",
          "filtered_snapshot": "{\"application\":\"myapp\",\"components\":[{\"name\":\"comp1\",\"repository\":\"quay.io/redhat-prod/base\",\"containerImage\":\"quay.io/redhat-prod/base@sha256:base123\",\"tags\":[\"latest\"],\"baseImage\":true},{\"name\":\"comp2\",\"repository\":\"quay.io/redhat-prod/another\",\"containerImage\":\"quay.io/redhat-prod/another@sha256:xyz\",\"tags\":[\"v2.0\"]}]}"
        }'
        ;;
      "error")
        echo '{
          "result": "Error",
          "message": "Failed to filter images"
        }'
        ;;
      *)
        echo '{
          "result": "Success",
          "filtered_snapshot": "{\"application\":\"myapp\",\"components\":[]}"
        }'
        ;;
    esac
  else
    /usr/bin/kubectl "$@"
  fi
}

# Mock git command
function git() {
  if [[ "$*" == *"clone"* ]]; then
    # Get the test case from the environment
    TEST_CASE=${TEST_CASE:-"success"}
    
    case $TEST_CASE in
      "success"|"base_image")
        mkdir -p "$(workspaces.data.path)/data/advisories/test-origin/2024/1234"
        cat > "$(workspaces.data.path)/data/advisories/test-origin/2024/1234/advisory.json" << EOF
{
  "images": [
    {
      "name": "comp1",
      "image": "quay.io/redhat-prod/release@sha256:prod123",
      "digest": "sha256:prod123"
    }
  ]
}
EOF
        ;;
      "multiple_advisories")
        mkdir -p "$(workspaces.data.path)/data/advisories/test-origin/2024/1234"
        mkdir -p "$(workspaces.data.path)/data/advisories/test-origin/2024/5678"
        cat > "$(workspaces.data.path)/data/advisories/test-origin/2024/1234/advisory.json" << EOF
{
  "images": [
    {
      "name": "comp1",
      "image": "quay.io/redhat-prod/release@sha256:prod123",
      "digest": "sha256:prod123"
    }
  ]
}
EOF
        cat > "$(workspaces.data.path)/data/advisories/test-origin/2024/5678/advisory.json" << EOF
{
  "images": [
    {
      "name": "comp1",
      "image": "quay.io/redhat-prod/release@sha256:prod123",
      "digest": "sha256:prod123"
    }
  ]
}
EOF
        ;;
      *)
        # For error cases, don't create any advisory files
        ;;
    esac
  fi
}

# Mock find command
function find() {
  if [[ "$*" == *"data/advisories"* ]]; then
    # Get the test case from the environment
    TEST_CASE=${TEST_CASE:-"success"}
    
    case $TEST_CASE in
      "multiple_advisories")
        echo "$(workspaces.data.path)/data/advisories/test-origin/2024/1234"
        echo "$(workspaces.data.path)/data/advisories/test-origin/2024/5678"
        ;;
      *)
        echo "$(workspaces.data.path)/data/advisories/test-origin/2024/1234"
        ;;
    esac
  fi
}
