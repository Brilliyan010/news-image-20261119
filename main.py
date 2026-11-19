#!/usr/bin/env python3
"""news-image-20261119 safety entry.

Copies the pre-rendered front page (entry.png, drawn programmatically
with PIL in the build session) to the make.fun output directory.
Standard library only; deterministic: the same bytes every run.
"""
import os
import shutil
import sys

MAX_BYTES = 1_048_576
PNG_MAGIC = b"\x89PNG\r\n\x1a\n"


def main() -> int:
    here = os.path.dirname(os.path.abspath(__file__))
    src = os.path.join(here, "entry.png")
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    dst = os.path.join(out_dir, "entry.png")

    with open(src, "rb") as fh:
        data = fh.read()
    if data[:8] != PNG_MAGIC:
        print("entry.png: bad PNG magic", file=sys.stderr)
        return 1
    if len(data) > MAX_BYTES:
        print("entry.png: over 1 MiB", file=sys.stderr)
        return 1
    shutil.copyfile(src, dst)
    print(f"wrote {dst} ({len(data)} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
