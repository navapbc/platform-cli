#!/usr/bin/env bash

source "$(realpath "$(dirname "${BASH_SOURCE[0]}")")/lib.sh"

export CMD="${CMD:-nava-platform}"

export PROJECT_NAME="${PROJECT_DIR:-foo}"
export PROJECT_DIR=${PROJECT_DIR:-$(mk_temp_dir "test-platform-project")}

init_project_dir() {
    rm -rf "${PROJECT_DIR}"
    # vast majority of the time we are expecting to be working against an existing
    # project (or at least an empty, but git-initialized project directory)
    mkdir -p "${PROJECT_DIR}"
    git init "${PROJECT_DIR}"
}
