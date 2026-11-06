# ZKS ↔ Hermes initial integration (experimental)

**Status:** a read-only local knowledge adapter, not a live ChatGPT Library connector or an autonomous expert agent.

The skill lives at `optional-skills/research/zks-library/`. It works through Hermes' `terminal` tool; its helper uses only the Python standard library. It can list active module IDs, run a small lexical candidate search, read exact modules, and verify files against ZKS manifest SHA-256 hashes.

## First test on Windows

1. Set up Hermes on Windows from the official project instructions, or check out this fork and follow its `AGENTS.md`/developer setup.
2. Put the `zks-library` skill directory in the active Hermes profile's `skills/zks-library/` directory. Don't overwrite a different skill without preserving it.
3. Place an **authorized current ZKS snapshot** at `<installed-skill>/references/zks/` with the original `manifest.json` and relative module paths. **Do not commit personal ZKS documents to this public repository.** A ZIP of the snapshot can be transferred from a ChatGPT conversation to your computer and extracted locally.
4. With Python installed, invoke `python "<installed-skill>/scripts/zks.py" verify`.
5. Start a fresh Hermes session. Ask Hermes for a knowledge-dependent task, inspect whether it selects the skill, reads the right node, and applies it correctly.
6. To use Hermes from an iPhone, configure its supported messaging gateway (e.g. Telegram) on the Windows host; the host must remain online.

To point to a separately stored snapshot (no copying required): `python "<installed-skill>/scripts/zks.py" --root "C:\\path\\to\\ZKS" list`.

## Scope boundaries

- No API credentials, personal knowledge snapshot or passwords belong in this repository.
- `search` is lexical only, not a substitute for a well-evaluated retrieval pipeline.
- Do not infer that a validated snapshot is current, that the correct knowledge will be selected, or that a language model will apply it correctly.
- ZKS's canonical knowledge ownership and publication rules remain independent of Hermes.

## Offline tests

From the fork's root, run:

```powershell
python -m pytest tests/skills/test_zks_library_skill.py -q
```

The tests use synthetic data. They do not require access to ChatGPT Library or a model provider.

## Next measurable gate

Demonstrate with a real Hermes invocation: correct skill selection → correct knowledge read → source applicability check → correct answer, repeated against a no-ZKS baseline. Only then consider deeper context-engine integration or core agent-loop changes.
