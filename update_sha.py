#!/usr/bin/env python3
import json
import re
import sys
import urllib.request
from functools import lru_cache
from pathlib import Path

USES_RE = re.compile(r"^(\s*-?\s*uses:\s*)([A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+)@([^\s#]+)(.*)$")


def github_json(url: str) -> dict:
    req = urllib.request.Request(
        url,
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": "update-github-actions",
        },
    )
    with urllib.request.urlopen(req) as resp:
        return json.load(resp)


@lru_cache
def latest_release(owner_repo: str) -> tuple[str, str]:
    release = github_json(f"https://api.github.com/repos/{owner_repo}/releases/latest")
    tag = release["tag_name"]

    ref = github_json(f"https://api.github.com/repos/{owner_repo}/git/ref/tags/{tag}")

    sha = ref["object"]["sha"]

    # Dereference annotated tags.
    if ref["object"]["type"] == "tag":
        tag_obj = github_json(f"https://api.github.com/repos/{owner_repo}/git/tags/{sha}")
        sha = tag_obj["object"]["sha"]

    return tag, sha


def process_file(path: Path, cache: dict[str, tuple[str, str]]) -> None:
    changed = False
    output: list[str] = []

    for line in path.read_text(encoding="utf-8").splitlines(keepends=True):
        match = USES_RE.match(line)
        if not match:
            output.append(line)
            continue

        prefix, repo, _, suffix = match.groups()

        # Ignore local actions.
        if repo.startswith("./"):
            output.append(line)
            continue

        try:
            tag, sha = cache.setdefault(repo, latest_release(repo))
        except Exception as exc:
            print(f"{path}: failed to update {repo}: {exc}", file=sys.stderr)
            output.append(line)
            continue

        new_line = f"{prefix}{repo}@{sha} # {tag}\n"

        if new_line != line:
            print(f"{path}: {repo} -> {tag} ({sha[:12]})")
            changed = True

        output.append(new_line)

    if changed:
        path.write_text("".join(output), encoding="utf-8")


def main() -> None:
    root = Path.cwd().parent / repo
    cache: dict[str, tuple[str, str]] = {}

    for path in root.rglob("*"):
        if path.suffix.lower() not in {".yml", ".yaml"}:
            continue
        process_file(path, cache)


if __name__ == "__main__":
    repo = sys.argv[1] if len(sys.argv) == 2 else "actions"
    main()
