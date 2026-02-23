---
name: cost-check
description: Gets the current total cost and token usage from opencode stats
---

# Cost Check Skill

This skill retrieves the current cost and token usage statistics from the opencode stats command.

## When to Use

- User asks to check costs
- User wants to see token usage
- User needs to monitor spending
- User wants to see cache usage statistics

## Prerequisites

- The `opencode` command must be available and executable
- Must have access to run `opencode stats`

## Instructions

### Step 1: Run Cost Check Script

Execute the cost-check script to get current statistics:

```bash
./scripts/cost-check.sh
```

This script will:
1. Check if `opencode` command exists
2. Run `opencode stats` to get current statistics
3. Parse and output the relevant cost and token information

### Output Format

The script outputs JSON with the following fields:
- `total_cost`: Total cost in dollars
- `input_tokens`: Number of input tokens used
- `output_tokens`: Number of output tokens used
- `cache_read`: Cache read statistics
- `cache_write`: Cache write statistics

### Example Output

```json
{
  "total_cost": "$3.24",
  "input_tokens": "1.4M",
  "output_tokens": "125.5K",
  "cache_read": "41.2M",
  "cache_write": "302.5K"
}
```

### Step 2: Display Results

Present the cost information to the user in a clear format:

```bash
# Run the script and capture output
COST_DATA=$(./scripts/cost-check.sh)

# Display to user
echo "Current Cost and Token Usage:"
echo "=============================="
echo "$COST_DATA" | jq -r '
  "Total Cost: \(.total_cost)",
  "Input Tokens: \(.input_tokens)",
  "Output Tokens: \(.output_tokens)",
  "Cache Read: \(.cache_read)",
  "Cache Write: \(.cache_write)"
'
```

## Error Handling

- If `opencode` command is not found, the script returns: `{"error": "opencode command not found"}`
- If stats cannot be retrieved, the script returns: `{"error": "Failed to get opencode stats"}`

## Important Notes

- This skill currently only supports the `opencode` tool
- The script is designed to be easily extended for other tools in the future
- Cost data is retrieved in real-time from the opencode stats command
- Cache statistics help understand context usage and efficiency
