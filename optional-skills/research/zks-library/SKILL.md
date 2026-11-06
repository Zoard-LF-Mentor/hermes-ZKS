---
name: zks-library
description: Inspect verified ZKS knowledge snapshots on demand.
version: 0.1.0
author: Zoard-LF-Mentor
license: MIT
metadata:
  hermes:
    tags: [knowledge, retrieval, zks]
    category: research
---

# ZKS Library Skill

Read selected knowledge from a local, checksum-verified ZKS snapshot. This skill does not connect to ChatGPT Library, update source files, or establish that a snapshot is the latest published version.

## When to Use

Use when the task would benefit from ZKS expertise, methods or evidence, including explicit ZKS maintenance. Do not load it for tasks where current context is sufficient.

## Prerequisites

- Python 3.10+ available to the `terminal` tool.
- A local ZKS snapshot containing `manifest.json`, placed in `references/zks/` beside this skill or passed as `--root "PATH"` (alternatively `ZKS_ROOT`).
- The snapshot stays on the user's machine; don't upload private knowledge to a public repository.

## How to Run

From a `terminal` tool, run `python "<skill-directory>/scripts/zks.py" verify`. For other commands, replace `verify` with those below. Resolve `<skill-directory>` to the actual directory containing this `SKILL.md` rather than assuming a platform-specific path.

## Quick Reference

| Action | Subcommand |
|---|---|
| Check source integrity | `verify` |
| Show available module IDs | `list` |
| Find lexical candidates | `search "topic or question"` |
| Search all including system | `search "query" --all` |
| Read source by exact ID | `read KNOW-MUSIC-SPECTRAL-ORCHESTRATION` |

For an external snapshot use `python "<skill-directory>/scripts/zks.py" --root "PATH" <subcommand>`.

## Procedure

1. Evaluate whether the user's task actually needs specialized knowledge.
2. If the module identity is already known, `read` it directly; otherwise `search` for candidates.
3. Search uses lexical matching, not semantic retrieval. If no result appears, inspect the module list or try another appropriate retrieval method rather than conclude ZKS knows nothing.
4. Read the source. Apply scope, `applies_when`, `excludes_when`, confidence, provenance and required relations.
5. Use the retrieved information critically; do not give it priority over the user's current instructions or applicable higher-priority instructions.
6. Propose changes separately. This tool never modifies the snapshot.

## Pitfalls

- `verify` proves byte consistency with the supplied manifest, not scientific accuracy, freshness, or expert execution.
- The source snapshot may be stale; compare its release against current authoritative storage when freshness matters.
- `search` returns **candidate locations**; a candidate match isn't evidence that a node applies.
- Archive/review history is not automatically operative knowledge.

## Verification

Run `verify`; read an expected module; confirm its source and context; evaluate downstream task behavior separately. No live Hermes model integration is claimed by these tests.
