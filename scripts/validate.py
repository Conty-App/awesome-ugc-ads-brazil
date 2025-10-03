#!/usr/bin/env python3
import json, sys, re
from pathlib import Path
REQ={"id","platform","language","ugc_type","hook_text","cta_text","script_text","video_url","terms_ok"}
PLAT={"reels","tiktok","shorts","linkedin","other"}
LANG={"pt-BR"}
TYPES={"testimonial","unboxing","before_after","review","tutorial","qna","offer","educational","trend","product_haul"}
URL=re.compile(r"^https?://")
ok=True
seen=set()
p=Path("data/ads.jsonl")
if not p.exists():
    print("arquivo data/ads.jsonl inexistente"); sys.exit(1)
for i,line in enumerate(p.open(),1):
    line=line.strip()
    if not line: 
        continue
    try:
        ad=json.loads(line)
    except Exception as e:
        print(f"[L{i}] json invalido: {e}"); ok=False; continue
    miss=REQ-ad.keys()
    if miss:
        print(f"[L{i}] faltando: {sorted(miss)}"); ok=False
    rid=ad.get("id")
    if not rid:
        print(f"[L{i}] id vazio"); ok=False
    elif rid in seen:
        print(f"[L{i}] id duplicado: {rid}"); ok=False
    seen.add(rid)
    if ad.get("platform") not in PLAT:
        print(f"[L{i}] platform invalida: {ad.get('platform')}"); ok=False
    if ad.get("language") not in LANG:
        print(f"[L{i}] language invalido: {ad.get('language')}"); ok=False
    if ad.get("ugc_type") not in TYPES:
        print(f"[L{i}] ugc_type invalido: {ad.get('ugc_type')}"); ok=False
    if not URL.match(ad.get("video_url","")):
        print(f"[L{i}] video_url invalido"); ok=False
    if not isinstance(ad.get("terms_ok"),bool) or not ad.get("terms_ok"):
        print(f"[L{i}] terms_ok deve ser true"); ok=False
if not ok:
    sys.exit(1)
print("OK")
