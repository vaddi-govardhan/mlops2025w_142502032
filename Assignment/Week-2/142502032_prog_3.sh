#!/bin/bash

# Check if filename is provided
if [ $# -eq 0 ]; then
    echo "Usage: $0 filename"
    exit 1
fi

file="$1"

# Add line numbers with pr, sort them in reverse order,
# then cut out the line numbers to keep only text
pr -t -n "$file" | sort -k1,1nr | cut -f2-

