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
- User wants to post cost information to a PR before merging
- Part of the ship workflow to track PR costs

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

### Step 2: Check for Open PR and Post Cost Information (Optional)

If running as part of a ship workflow or when a PR exists, post cost information to the PR:

```bash
# Check if there's an open PR for current branch
CURRENT_BRANCH=$(git branch --show-current)
PR_NUMBER=$(gh pr list --head "$CURRENT_BRANCH" --json number --jq '.[0].number' 2>/dev/null)

if [ -n "$PR_NUMBER" ]; then
    echo "Found PR #$PR_NUMBER - posting cost information..."
    
    # Get current cost data
    COST_DATA=$(./scripts/cost-check.sh)
    
    # Parse current cost (remove $ and convert to number)
    CURRENT_COST=$(echo "$COST_DATA" | jq -r '.total_cost' | sed 's/[^0-9.]//g')
    
    # Check for previous cost checkpoint (stored in git notes or file)
    PREVIOUS_COST_FILE=".cost-checkpoint"
    PREVIOUS_COST=""
    COST_DELTA=""
    
    if [ -f "$PREVIOUS_COST_FILE" ]; then
        PREVIOUS_COST=$(cat "$PREVIOUS_COST_FILE" | sed 's/[^0-9.]//g')
        
        # Calculate delta
        if command -v bc &> /dev/null; then
            COST_DELTA=$(echo "$CURRENT_COST - $PREVIOUS_COST" | bc)
        else
            # Fallback without bc
            COST_DELTA="N/A (bc not available)"
        fi
    fi
    
    # Build cost report
    INPUT_TOKENS=$(echo "$COST_DATA" | jq -r '.input_tokens')
    OUTPUT_TOKENS=$(echo "$COST_DATA" | jq -r '.output_tokens')
    CACHE_READ=$(echo "$COST_DATA" | jq -r '.cache_read')
    CACHE_WRITE=$(echo "$COST_DATA" | jq -r '.cache_write')
    
    COST_REPORT="## Cost Report

**Current Session Costs:**
- Total Cost: $(echo "$COST_DATA" | jq -r '.total_cost')
- Input Tokens: $INPUT_TOKENS
- Output Tokens: $OUTPUT_TOKENS
- Cache Read: $CACHE_READ
- Cache Write: $CACHE_WRITE
"
    
    # Add delta if available
    if [ -n "$COST_DELTA" ] && [ "$COST_DELTA" != "N/A (bc not available)" ]; then
        COST_REPORT="$COST_REPORT
**PR Cost (Delta from last checkpoint):** \$$COST_DELTA
"
    fi
    
    # Post to PR as comment
    gh pr comment $PR_NUMBER --body "$COST_REPORT"
    echo "Cost information posted to PR #$PR_NUMBER"
    
    # Save current cost as checkpoint for next time
    echo "$CURRENT_COST" > "$PREVIOUS_COST_FILE"
    echo "Cost checkpoint saved: \$$CURRENT_COST"
else
    echo "No open PR found for current branch - skipping PR cost post"
fi
```

### Step 3: Display Results

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
