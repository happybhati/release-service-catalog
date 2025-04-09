#!/usr/bin/env bash
set -ex

function kubectl() {
  if [[ "$*" == "get internalrequest "*"-o=jsonpath={.status.results}" ]]; then
    echo '{
      "result": "Success",
      "filtered_snapshot": "{\"application\":\"myapp\",\"components\":[{\"name\":\"comp1\",\"repository\":\"quay.io/redhat-prod/repo\"}]}"
    }' 
  else
    /usr/bin/kubectl $*
  fi
}
