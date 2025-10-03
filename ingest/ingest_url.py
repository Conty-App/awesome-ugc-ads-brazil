#!/usr/bin/env python3
import argparse, json, os, re, shutil, tempfile
from pathlib import Path
from datetime import datetime
import subprocess
import whisper
import yt_dlp

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/"data"/"ads.jsonl"

ALLOWED_TYPES={"testimonial","unboxing","before_after","review","tutorial","qna","offer","educational","trend","product_haul"}

CTA_PATTERNS=[
    r"\b(comente|comenta)\b.*\b(quero|planilha|me manda|eu quero)\b",
    r"\blink\s+na\s+bio\b",
    r"\bbaixe\b|\bbaixa\b|\bdownload\b",
    r"\buse\b.*\bcupom\b",
    r"\barrasta?\b|\bdesliza(r)?\b",
    r"\bse inscreva\b|\bassine\b|\bcadastre\-se\b",
    r"\bprimeira compra\b"
]

def parse_args():
    ap=argparse.ArgumentParser()
    ap.add_argument("--url",required=True)
    ap.add_argument("--ugc-type",required=True)
    ap.add_argument("--brand",default="")
    ap.add_argument("--category",default="")
    ap.add_argument("--language",default="pt-BR")
    ap.add_argument("--terms-ok",default="false")
    ap.add_argument("--model",default="small")
    ap.add_argument("--aspect-ratio",default="9:16")
    return ap.parse_args()

def next_id():
    if not DATA.exists():
        return "br_001"
    m=0
    with DATA.open() as f:
        for line in f:
            line=line.strip()
            if not line: 
                continue
            try:
                ad=json.loads(line)
            except:
                continue
            rid=str(ad.get("id",""))
            x=re.match(r"br_(\d+)$",rid)
            if x:
                n=int(x.group(1))
                m=max(m,n)
    return f"br_{m+1:03d}"

def clean(t):
    t=(t or "").strip()
    t=re.sub(r"\s+"," ",t)
    return t

def sentences(text):
    s=re.split(r"(?<=[\.\!\?])\s+", text.strip())
    return [clean(x) for x in s if clean(x)]

def guess_hook(script):
    s=sentences(script)
    if not s:
        return ""
    for x in s[:3]:
        if len(x.split())<=14:
            return x
    return s[0]

def guess_cta(script):
    low=script.lower()
    for pat in CTA_PATTERNS:
        if re.search(pat,low):
            s=sentences(script)
            for x in s[::-1]:
                if re.search(pat,x.lower()):
                    return x
    s=sentences(script)
    return s[-1] if s else ""

def detect_platform(url):
    u=url.lower()
    if "tiktok.com" in u:
        return "tiktok"
    if "instagram.com" in u:
        return "reels"
    if "youtube.com" in u or "youtu.be" in u:
        return "shorts"
    if "linkedin.com" in u:
        return "linkedin"
    return "other"

def download(url,out_dir):
    ydl_opts={
        "outtmpl": str(out_dir/ "%(id)s.%(ext)s"),
        "format": "mp4/best",
        "noplaylist": True,
        "quiet": True,
        "nocheckcertificate": True,
        "geo_bypass": True
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info=ydl.extract_info(url, download=True)
    if "_filename" in info:
        video=Path(info["_filename"])
    else:
        video=next(out_dir.glob(f"{info.get('id','*')}.*"), None)
    dur=None
    if "duration" in info and isinstance(info["duration"],(int,float)):
        dur=int(info["duration"])
    desc=info.get("description") or ""
    return {"video":video,"duration":dur,"description":desc}

def to_wav(video_path,out_dir):
    a=out_dir/(video_path.stem+".wav")
    subprocess.run(["ffmpeg","-i",str(video_path),"-vn","-acodec","pcm_s16le","-ar","16000","-ac","1",str(a)],check=True,capture_output=True)
    return a

def transcribe(audio_path,model_name):
    model=whisper.load_model(model_name)
    result=model.transcribe(str(audio_path),language="pt")
    return clean(result["text"])

def main():
    args=parse_args()
    if args.ugc_type not in ALLOWED_TYPES:
        raise SystemExit("ugc-type invalido")
    terms=str(args.terms_ok).strip().lower() in {"1","true","yes","y"}
    tmp=Path(tempfile.mkdtemp(prefix="ingest_"))
    try:
        meta=download(args.url,tmp)
        if not meta["video"] or not meta["video"].exists():
            raise SystemExit("falha no download")
        wav=to_wav(meta["video"],tmp)
        script=transcribe(wav,args.model)
        if not script:
            raise SystemExit("transcricao vazia")
        hook=guess_hook(script)
        cta=guess_cta(script)
        caption=clean(meta.get("description") or "")
        rid=next_id()
        platform=detect_platform(args.url)
        rec={
            "id":rid,
            "platform":platform,
            "brand":clean(args.brand),
            "category":clean(args.category),
            "language":args.language,
            "ugc_type":args.ugc_type,
            "video_url":args.url,
            "hook_text":hook,
            "cta_text":cta,
            "caption_text":caption or None,
            "script_text":script,
            "duration_sec":meta.get("duration"),
            "aspect_ratio":args.aspect_ratio,
            "terms_ok":terms,
            "notes":"auto-ingest via ingest_url.py "+datetime.utcnow().isoformat()+"Z"
        }
        DATA.parent.mkdir(parents=True,exist_ok=True)
        with DATA.open("a",encoding="utf-8") as f:
            f.write(json.dumps(rec,ensure_ascii=False)+"\n")
        print(json.dumps({"status":"ok","id":rid,"platform":platform,"hook_text":hook,"cta_text":cta},ensure_ascii=False))
    finally:
        shutil.rmtree(tmp,ignore_errors=True)

if __name__=="__main__":
    main()
