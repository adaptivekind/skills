#!/bin/bash
#
# cost-check.sh - Get cost and token usage from opencode stats
#
# This script retrieves the current total cost and token usage statistics
# from the opencode stats command.
#
# Usage: ./scripts/cost-check.sh
#
# Output: JSON formatted cost and token information
#

set -e

# Check if opencode command exists
if ! command -v opencode &> /dev/null; then
    echo '{"error": "opencode command not found"}'
    exit 1
fi

# Get stats from opencode
STATS=$(opencode stats 2>/dev/null)

if [ -z "$STATS" ]; then
    echo '{"error": "Failed to get opencode stats"}'
    exit 1
fi

# Parse and output the relevant information
echo "$STATS" | awk '
BEGIN {
    print "{"
    first = 1
}
/Total Cost/ {
    gsub(/\|/, "")
    gsub(/^[ \t]+/, "")
    gsub(/[ \t]+$/, "")
    split($0, a, /[ \t]+/)
    cost = a[3]
    if (!first) print ","
    printf "  \"total_cost\": \"%s\"", cost
    first = 0
}
/Input/ {
    gsub(/\|/, "")
    gsub(/^[ \t]+/, "")
    gsub(/[ \t]+$/, "")
    split($0, a, /[ \t]+/)
    input = a[2]
    if (!first) print ","
    printf "  \"input_tokens\": \"%s\"", input
    first = 0
}
/Output/ {
    gsub(/\|/, "")
    gsub(/^[ \t]+/, "")
    gsub(/[ \t]+$/, "")
    split($0, a, /[ \t]+/)
    output = a[2]
    if (!first) print ","
    printf "  \"output_tokens\": \"%s\"", output
    first = 0
}
/Cache Read/ {
    gsub(/\|/, "")
    gsub(/^[ \t]+/, "")
    gsub(/[ \t]+$/, "")
    split($0, a, /[ \t]+/)
    cache_read = a[3]
    if (!first) print ","
    printf "  \"cache_read\": \"%s\"", cache_read
    first = 0
}
/Cache Write/ {
    gsub(/\|/, "")
    gsub(/^[ \t]+/, "")
    gsub(/[ \t]+$/, "")
    split($0, a, /[ \t]+/)
    cache_write = a[3]
    if (!first) print ","
    printf "  \"cache_write\": \"%s\"", cache_write
    first = 0
}
END {
    print ""
    print "}"
}
'
