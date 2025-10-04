#!/usr/bin/env python3
import json, collections
from pathlib import Path
p=Path("data/ads.jsonl")
c=collections.Counter()
if p.exists():
    with p.open() as f:
        for line in f:
            line=line.strip()
            if not line: continue
            ad=json.loads(line)
            h=(ad.get("hook_text") or "").strip().lower()
            if h:
                c[h]+=1
print("TOP HOOKS (pt-BR):")
for hook,n in c.most_common(20):
    print(f"{n}\t{hook}")
