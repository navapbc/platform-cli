#!/usr/bin/env bash

mk_temp_dir() {
    local name="${1:-platform-cli-test-e2e}"
    # macOS returns a symlink for $TMPDIR, so resolve to the actual path
    realpath "$(mktemp -d "${TMPDIR:-/tmp}/${name}.XXXXXXXXX")"
}
