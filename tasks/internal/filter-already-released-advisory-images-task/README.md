# filter-already-released-advisory-images-task

This internal Tekton task filters out images from a snapshot if they have already
been published in an advisory stored in a GitLab repository. It supports idempotency
for the `rh-advisories` pipeline by ensuring that previously released images are not
included in subsequent release operations.

## Parameters

| Name                        | Description                                                                 |
|-----------------------------|-----------------------------------------------------------------------------|
| `snapshot_json`             | String containing the full JSON representation of the snapshot spec        |
| `origin`                    | The origin workspace for the release CR (used to locate advisories)        |
| `advisory_secret_name`      | Name of the secret containing GitLab repo and token information             |
| `internalRequestPipelineRunName` | UID of the PipelineRun that invoked the InternalRequest                    |

## Results

| Name                          | Description                                                         |
|-------------------------------|---------------------------------------------------------------------|
| `result`                      | `Success` or a detailed error message                               |
| `filtered_snapshot`           | Snapshot JSON string containing only images not already released    |
| `internalRequestPipelineRunName` | The PipelineRun UID that triggered this task                        |
| `internalRequestTaskRunName`  | The TaskRun name of this internal task instance                     |
