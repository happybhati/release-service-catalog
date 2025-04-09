#!/usr/bin/env bash
set -ex

function kubectl() {
  if [[ "$*" == "get internalrequest "*"-o=jsonpath={.status.results}" ]]; then
    echo '{
      "result": "Success",
      "filtered_snapshot": "{\"application\":\"myapp\",\"components\":[{\"name\":\"comp2\",\"repository\":\"quay.io/redhat-prod/another\",\"containerImage\":\"quay.io/redhat-prod/another@sha256:xyz\",\"tags\":[\"v2.0\"]}]}"
    }'
  else
    /usr/bin/kubectl "$@"
  fi
}
