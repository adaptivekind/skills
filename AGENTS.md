# AGENTS.md

This file provides guidance to AI coding agents working on this skills repository.

## Project Overview

This is a skills package containing reusable agent skills that can be installed and used by AI coding assistants.

## Skills

### commit
- **Location**: `skills/commit/SKILL.md`
- **Scripts**: `skills/commit/scripts/pre-commit.sh`
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

## Creating Deterministic Scripts

When a skill involves complex, deterministic logic, extract it into scripts:

1. Create a `scripts/` directory under your skill
2. Write executable scripts for deterministic operations:
   - Scripts should be self-contained with clear error handling
   - Include helpful error messages and edge case handling
   - Use relative paths from the skill root
3. Reference scripts in SKILL.md:
   ```markdown
   Run the setup script:
   ```bash
   ./scripts/setup.sh
   ```
   ```

Benefits:
- **Deterministic**: Scripts produce consistent, testable results
- **Reusable**: Can be run independently of the skill
- **Maintainable**: Easier to test and debug than inline commands
- **Clear separation**: Logic in scripts, orchestration in SKILL.md

## Testing Skills

When testing skills:
- Verify the skill works with real commands
- Ensure error handling is proper
- Test with various edge cases
- If the skill has scripts, test scripts independently
