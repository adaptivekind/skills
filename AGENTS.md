# AGENTS.md

This file provides guidance to AI coding agents working on this skills repository.

## Project Overview

This is a skills package containing reusable agent skills that can be installed and used by AI coding assistants.

## Skills

### commit
- **Location**: `skills/commit/SKILL.md`
- **Purpose**: Creates signed commits in local git repositories
- **Usage**: Triggered when user asks to commit changes

## Adding New Skills

To add a new skill:

1. Create a directory under the skill name (e.g., `my-skill/`)
2. Create `SKILL.md` with YAML frontmatter:
   ```yaml
   ---
   name: my-skill
   description: Brief description of what this skill does
   ---
   ```
3. Add skill instructions in markdown format

## Testing Skills

When testing skills:
- Verify the skill works with real commands
- Ensure error handling is proper
- Test with various edge cases
