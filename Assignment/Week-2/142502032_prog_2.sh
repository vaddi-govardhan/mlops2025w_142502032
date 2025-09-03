#!/bin/bash

traverse() {
    local dir="$1"

    # Print current directory
    echo "Directory: $dir"

    # List contents of current directory
    ls -l "$dir"

    # Loop through subdirectories
    for sub in "$dir"/*; do
        if [ -d "$sub" ]; then
            traverse "$sub"
        fi
    done
}

traverse "/"

