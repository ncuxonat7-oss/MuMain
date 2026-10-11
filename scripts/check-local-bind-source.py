#!/usr/bin/env python3
"""Pinned-source applicability checks only; does not compile or execute C#.

Usage: python scripts/check-local-bind-source.py /path/to/sparse-or-full/pinned-source
No downloads, builds, baseline tests or source-tree mutations.
"""

import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile


REPO = Path(__file__).resolve().parents[1]
PATCH = REPO / "patches/openmu-local-only-bind.patch"


def require(condition, message):
    if not condition:
        raise ValueError(message)


def check(source):
    provenance = json.loads(
        (REPO / "patches/openmu-local-only-bind-provenance.json").read_text()
    )
    for name, digest in provenance["sourceSha256"].items():
        require(hashlib.sha256((source / name).read_bytes()).hexdigest() == digest,
                f"Pinned source mismatch: {name}")
    money = REPO / "patches/openmu-trade-money.patch"
    require(hashlib.sha256(money.read_bytes()).hexdigest() == provenance["moneyPatchSha256"],
            "Money patch changed")
    bind_targets = patch_targets(PATCH)
    require(bind_targets == {"src/Network/Listener.cs", "src/Network/LocalOnlyBinding.cs"},
            "Unexpected patch targets")
    require(bind_targets.isdisjoint(patch_targets(money)), "Bind patch overlaps Money patch")
    with tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary)
        target = root / "src/Network/Listener.cs"
        target.parent.mkdir(parents=True)
        original = (source / "src/Network/Listener.cs").read_bytes()
        target.write_bytes(original)
        subprocess.run(["git", "init", "-q", str(root)], check=True)
        subprocess.run(["git", "apply", "--check", str(PATCH)], cwd=root, check=True)
        subprocess.run(["git", "apply", str(PATCH)], cwd=root, check=True)
        expected = original.replace(
            b"new TcpListener(IPAddress.Any, this._port)",
            b"new TcpListener(LocalOnlyBinding.GetAddress(), this._port)",
        )
        require(target.read_bytes() == expected, "Unexpected Listener modification")
        require((root / "src/Network/LocalOnlyBinding.cs").is_file(), "Missing bind helper")
        changed = {p.relative_to(root).as_posix() for p in (root / "src").rglob("*.cs")}
        require(changed == {"src/Network/Listener.cs", "src/Network/LocalOnlyBinding.cs"},
                "Patch scope exceeds shared TCP listener")
        subprocess.run(["git", "apply", "--reverse", str(PATCH)], cwd=root, check=True)
        require(target.read_bytes() == original, "Patch reversal lost original bytes")
    print("PASS (SOURCE ONLY): pinned bytes, Money patch integrity, patch application, "
          "exact Listener change, scope and reversible application. C#/Windows: NOT_RUN.")


def patch_targets(patch):
    result = subprocess.run(["git", "apply", "--numstat", str(patch)],
                            check=True, capture_output=True, text=True)
    return {line.split("\t", 2)[2] for line in result.stdout.splitlines()}


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    check(Path(sys.argv[1]).resolve())
