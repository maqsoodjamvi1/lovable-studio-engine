#!/usr/bin/env python3
"""Decode .gz.b64 companions into full source files."""
import gzip, base64
from pathlib import Path
root = Path(__file__).resolve().parent.parent
for p in root.rglob("*.gz.b64"):
    out = Path(str(p)[:-7])
    data = gzip.decompress(base64.b64decode(p.read_text().strip()))
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(data)
    print("restored", out.relative_to(root), len(data), "bytes")
