# Skills

A collection of agent skills for AI coding assistants.

## Available Skills

### commit

Creates a signed commit in the local repository. If on main or master branch,
creates a new branch first. Fails if GPG signing is not configured.

## Installation

### From GitHub

```bash
npx skills add adaptivekind/skills
```

Or to install globally:

```bash
npx skills add -g adaptivekind/skills
```

### From local clone

```bash
git clone https://github.com/adaptivekind/skills.git /path/to/skills
cd /path/to/skills
npx skills add .
```

## Usage

The agent will automatically use these skills when relevant tasks are detected.
For example, when you ask to "commit changes", the agent will load the commit
skill and follow its instructions to create a signed commit.
