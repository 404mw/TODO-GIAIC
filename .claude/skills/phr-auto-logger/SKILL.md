---
name: phr-auto-logger
description: Automatically creates Prompt History Records (PHRs) after every user interaction. Use after completing requests to create detailed logs of prompts, responses, and outcomes. Follows CLAUDE.md routing rules.
allowed-tools: Read, Write, Grep, Glob, Bash(.specify/scripts/bash/create-phr.sh:*)
---

# PHR Auto-Logger

## Purpose

Enforce CLAUDE.md requirement: "Record every user input verbatim in a Prompt History Record (PHR) after every user message."

## PHR Routing (from CLAUDE.md)

All PHRs go under `history/prompts/`:
- **Constitution** → `history/prompts/constitution/`
- **Feature-specific** → `history/prompts/<feature-name>/`
- **General** → `history/prompts/general/`

## Stages

- `constitution` - Work on constitution.md
- `spec` - Specification work
- `plan` - Planning/architecture
- `tasks` - Task generation
- `red` - TDD Red phase (tests)
- `green` - TDD Green phase (implementation)
- `refactor` - TDD Refactor phase
- `explainer` - Explanations/documentation
- `misc` - Feature-related but doesn't fit other stages
- `general` - Not tied to a specific feature

## Instructions

### After Every User Interaction

When a request is completed:

1. **Detect if PHR is needed**
   - Skip only for `/sp.phr` command itself
   - All other interactions require PHR

2. **Identify stage**
   - Analyze what work was done
   - Map to appropriate stage
   - See: `.claude/skills/phr-auto-logger/stage-detection.md` for logic

3. **Generate title**
   - 3-7 words summarizing the work
   - Convert to slug (lowercase, hyphens)

4. **Determine route**
   - Constitution work → `history/prompts/constitution/`
   - Feature stages → `history/prompts/<feature-name>/`
   - General → `history/prompts/general/`

5. **Use agent-native flow first**
   - Read PHR template from `.specify/templates/phr-template.prompt.md`
   - Allocate ID (increment from existing PHRs)
   - Fill all placeholders
   - Write file using Write tool

6. **Fallback to bash script if needed**
   - If template not found or agent-native fails
   - Run `.specify/scripts/bash/create-phr.sh`

7. **Validate PHR**
   - No unresolved placeholders
   - Title and stage match
   - PROMPT_TEXT is complete (not truncated)
   - File exists and is readable

## PHR Template Structure

```yaml
---
id: [ID]
title: [TITLE]
stage: [STAGE]
date: [DATE_ISO]
surface: agent
model: [MODEL]
feature: [FEATURE or "none"]
branch: [BRANCH]
user: [USER]
command: [COMMAND]
labels: [[\"label1\", \"label2\"]]
links:
  spec: [URL or \"null\"]
  ticket: [URL or \"null\"]
  adr: [URL or \"null\"]
  pr: [URL or \"null\"]
files:
  - [file1]
  - [file2]
tests:
  - [test1]
  - [test2]
---

# [TITLE]

## Prompt

[FULL USER PROMPT - NOT TRUNCATED]

## Response

[KEY ASSISTANT OUTPUT - CONCISE BUT REPRESENTATIVE]

## Outcome

[WHAT WAS ACCOMPLISHED]

## Evaluation

[QUALITY CHECK - CONSTITUTIONAL COMPLIANCE, COMPLETENESS]
```

## Response Format

### When Creating PHR

```
📝 CREATING PROMPT HISTORY RECORD

Stage: [stage]
Title: [title]
Route: history/prompts/[route]/

ID: [allocated ID]
File: history/prompts/[route]/[ID]-[slug].[stage].prompt.md

✅ PHR Created Successfully

Recorded:
- Prompt: [first 50 chars...]
- Response: [key points]
- Files: [list of files]
- Tests: [list of tests]

Validations Passed:
✓ No unresolved placeholders
✓ Title and stage match
✓ Prompt text complete
✓ File readable
```

## Sub-Modules (Progressive Disclosure)

When you need detailed information, read these files:

- **Stage Detection Logic**: `.claude/skills/phr-auto-logger/stage-detection.md`
  - Python code for detecting stage from context
  - Feature detection from branch or file paths

- **Detailed Examples**: `.claude/skills/phr-auto-logger/examples.md`
  - Constitution work example
  - Feature spec work example
  - Implementation work example
  - General/explainer work example

## Quick Reference

**Mandatory**: PHR creation is required after every interaction (except `/sp.phr` itself)

**Verbatim**: User prompts must be recorded verbatim (not truncated)

**Routing**:
- Constitution → `history/prompts/constitution/`
- Feature work → `history/prompts/<feature-name>/`
- General → `history/prompts/general/`

**Validation**: All placeholders must be filled before finalizing

**Agent-native preferred**: Use Write tool over bash script when possible

**Non-blocking**: PHR creation failures should warn but not block main work

## Notes

- **Read sub-modules on-demand** to avoid context bloat
- PHR files use `.prompt.md` extension
- Filename format: `[ID]-[slug].[stage].prompt.md`
- ID is auto-incremented per directory
- Stage must match one of the defined stages
