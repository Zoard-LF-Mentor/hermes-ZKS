#!/usr/bin/env python3
"""Read-only verified snapshot discovery for ZKS; stdlib only."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from pathlib import Path

STOP = frozenset("a an and are at be by can do for from how i in is it my of on or our the their this to use we what when which with you".split())


def root_dir(cli_root: str | None) -> Path:
    if cli_root:
        return Path(cli_root).expanduser().resolve()
    if os.getenv("ZKS_ROOT"):
        return Path(os.environ["ZKS_ROOT"]).expanduser().resolve()
    return (Path(__file__).resolve().parents[1] / "references" / "zks").resolve()


def manifest(root: Path) -> dict:
    path = root / "manifest.json"
    if not path.is_file():
        raise ValueError(f"Missing ZKS manifest at {path}; supply --root or ZKS_ROOT")
    m = json.loads(path.read_text(encoding="utf-8"))
    if m.get("system") != "ZKS" or not isinstance(m.get("modules"), list):
        raise ValueError("Not a ZKS manifest")
    return m


def verified_source(root: Path, entry: dict) -> str:
    rel = entry["path"]
    target = (root / rel).resolve()
    if not target.is_relative_to(root) or target == root:
        raise ValueError("Manifest path escapes the snapshot root")
    data = target.read_bytes()
    if hashlib.sha256(data).hexdigest() != entry["sha256"]:
        raise ValueError(f"SHA-256 mismatch: {rel}")
    return data.decode("utf-8")


def terms(s: str) -> set[str]:
    return {w for w in re.findall(r"[a-z0-9]+", s.casefold()) if len(w) > 2 and w not in STOP}


def score(q: set[str], entry: dict, source: str) -> int:
    if not q:
        return 0
    # Lexical locator, not semantic relevance/authority; avoid ranking by full body length.
    metadata = source.split("\n---\n", 1)[0]
    title = source.split("\n# ", 1)[1].splitlines()[0] if "\n# " in source else ""
    return (6 * len(q & terms(entry["id"] + " " + title))
            + 3 * len(q & terms(metadata))
            + len(q & terms(source[:20000])))


def run(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Inspect a verified ZKS snapshot (read-only)")
    parser.add_argument("--root", help="Local ZKS folder containing manifest.json")
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("verify")
    commands.add_parser("list")
    read = commands.add_parser("read")
    read.add_argument("module_id")
    search = commands.add_parser("search")
    search.add_argument("query", nargs="+")
    search.add_argument("--all", action="store_true", help="Include SYSTEM modules")
    search.add_argument("--limit", type=int, default=5)
    args = parser.parse_args(argv)
    root = root_dir(args.root)
    m = manifest(root)
    entries = m["modules"]

    if args.command == "verify":
        for e in entries + m.get("integrity_files", []):
            verified_source(root, e)
        print(f"PASS: ZKS {m['system_version']}; {len(entries)} modules verified")
        return 0
    if args.command == "list":
        for e in entries:
            print(f"{e['id']}\t{e['path']}")
        return 0
    if args.command == "read":
        entry = next((e for e in entries if e["id"].casefold() == args.module_id.casefold()), None)
        if entry is None:
            print("Unknown active module ID; try list", file=sys.stderr)
            return 2
        print(f"ZKS {m['system_version']} | {entry['id']} | checksum verified", file=sys.stderr)
        print(verified_source(root, entry))
        return 0
    q = terms(" ".join(args.query))
    results = []
    for e in entries:
        if not args.all and not e["id"].startswith("KNOW-"):
            continue
        s = score(q, e, verified_source(root, e))
        if s:
            results.append((s, e))
    results.sort(key=lambda pair: (-pair[0], pair[1]["id"]))
    if not results:
        print("No lexical matches; do not infer that knowledge is absent. Try an exact ID or inspect the manifest.")
    else:
        print(f"ZKS {m['system_version']} — lexical candidates, NOT verified relevance")
        for s, e in results[:max(1, min(args.limit, 20))]:
            print(f"score={s:2}\t{e['id']}\t{e['path']}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(run())
    except (OSError, ValueError, KeyError, UnicodeError, json.JSONDecodeError) as exc:
        print(f"ZKS read-only adapter: {exc}", file=sys.stderr)
        raise SystemExit(1)
