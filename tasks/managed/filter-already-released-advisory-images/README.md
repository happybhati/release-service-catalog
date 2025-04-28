# Filter Already Released Advisory Images

This task filters out the images from a snapshot that have already been published in advisories.  
It is a **managed Tekton task** that triggers an **internal task** using an InternalRequest, and returns a filtered snapshot JSON containing only **unpublished images**.

## Parameters

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `snapshotPath` | string | Yes | - | Path to the JSON file of the Snapshot spec in the workspace |
| `releasePlanAdmissionPath` | string | Yes | - | Path to the JSON file of the ReleasePlanAdmission in the workspace |
| `resultsDirPath` | string | Yes | - | Path to the results directory within the workspace |
| `request` | string | No | `filter-already-released-advisory-images-task` | The name of the internal task to be triggered |
| `synchronously` | string | No | `true` | Whether the task should wait for the InternalRequest to complete |
| `pipelineRunUid` | string | Yes | - | UID of the current pipelineRun, used as a label on the InternalRequest |
| `taskGitUrl` | string | Yes | - | Git URL of the release-service-catalog containing internal task logic |
| `taskGitRevision` | string | Yes | - | Git revision or branch name used to run the internal task |

## Workspaces

| Name | Description |
|------|-------------|
| `data` | A shared workspace containing the input files and to store InternalRequest results |

## Results

| Name | Description |
|------|-------------|
| `filtered_snapshot` | JSON string of the snapshot with already-published images removed |
| `result` | String containing `"Success"` or an error message if something went wrong |
