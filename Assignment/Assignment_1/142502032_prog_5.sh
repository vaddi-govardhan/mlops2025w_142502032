#!/bin/bash

echo -n "Enter a string: "
read str

# Reverse the string using rev command
rev_str=$(echo "$str" | rev)

echo "Reversed string: $rev_str"

