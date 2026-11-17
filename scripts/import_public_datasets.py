#!/usr/bin/env python3
"""Import text-only sign lexicons whose source terms permit redistribution.

No videos, images, ELAN files, or other media are downloaded or copied.
Run: python scripts/import_public_datasets.py
"""
from __future__ import annotations
import csv, io, json, re, shutil, sys, tempfile, urllib.request, zipfile, urllib.parse
from pathlib import Path
from datetime import date

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
SIGNS = DATA / "signs"
MIRRORS = DATA / "mirrors"
TODAY = date.today().isoformat()

SOURCES = {
    "msl4emergency": {
        "title": "MSL4Emergency — Myanmar Sign Language Corpus",
        "url": "https://github.com/ye-kyaw-thu/MSL4Emergency",
        "license": "CC BY-NC-SA 4.0",
        "attribution": "Contributors to MSL4Emergency; see original repository README.",
    },
    "easier-wordnet": {
        "title": "EASIER Multilingual Sign Language Wordnet v0.6",
        "url": "https://www.fdr.uni-hamburg.de/record/14190",
        "license": "CC BY 4.0",
        "attribution": "Bigeard et al. (2024), EASIER Multilingual Sign Language Wordnet, DOI: 10.25592/uhhfdm.14190.",
    },
    "asl-lex-2": {
        "title": "ASL-LEX 2.0",
        "url": "https://asl-lex.org/download.html",
        "license": "CC BY 4.0 (database only; reference videos excluded)",
        "attribution": "Sehyr et al. (2021), The ASL-LEX 2.0 Project, doi:10.1093/deafed/enaa038; Caselli et al. (2017), doi:10.3758/s13428-016-0742-0.",
    },
}

# Officially published source examples from the MSL4Emergency README. These are
# corpus phrases/transcriptions, not isolated lexical signs or signer media.
MSL_README_EXAMPLES = [
 ("FIRE HOOK", "မီးချိတ်", "မီးချိတ်", "emergency"),
 ("SANDBAG", "သဲ အိတ်", "အိတ် ထဲ သဲ", "emergency"),
 ("FIRE EXTINGUISHER", "မီးသတ်ဆေးဘူး", "အနီ ဘူး ဖြန်း", "emergency"),
 ("FLAMMABLE MATERIALS", "မီးလောင် လွယ် သော ပစ္စည်း များ", "မီးလောင် တစ်ခါတည်း ဓာတ်ဆီ စက္ကူ စွန့်ပစ် အမျိုးမျိုး", "safety"),
 ("FUEL", "လောင်စာဆီ", "ဓာတ်ဆီ 9 2 9 5 အောက်တိန်း အမျိုးမျိုး", "safety"),
 ("LIGHT SWITCH", "မီးခလုပ်", "ခလုပ် နှိပ်", "daily-life"),
 ("SMOKE", "မီးခိုး", "မီး အခိုးအငွေ့ အမဲ", "emergency"),
 ("OXYGEN", "အောက်စီဂျင်", "အောက်ဆီဂျင် o 2", "health"),
 ("EXIT", "ထွက်ပေါက်", "ဆိုင်းဘုတ် အဲဒီက ပြေး တံခါးပေါက်", "safety"),
 ("FIRE ENGINE", "မီးသတ်ကား", "ကား အရေးပေါ် မီးသတ်", "emergency"),
 ("RESCUE AND EMERGENCY RECOVERY", "ကယ်ဆယ်ရေး နှင့် အရေးပေါ် ပြန်လည် ထူထောင်ရေး", "လူ ကယ်ဆယ် ယခု မြန်မြန် ပြင်ဆင် ထူထောင်", "emergency"),
 ("SPECIAL ATTENTION", "အထူး သတိပြု", "ဒုက္ခ ဂရုစိုက်", "safety"),
 ("DO NOT JUMP", "ခုန် မ ချ နဲ့", "ခုန်ချ မလုပ်နဲ့", "safety"),
 ("EARTHQUAKE SAFETY", "ငလျင် လှုပ် နေ ရင် အဆာက်အအုံ ထဲ သို့ ပြေး မ ဝင် ပါ နဲ့", "ငလျှင်လှုပ် အိမ် ပြေးဝင် မလုပ်ရ မလုပ်နဲ့", "disaster"),
 ("BLEEDING", "သွေး တွေ တော်တော် ထွက် နေ တယ်", "သွေး ထွက် အများကြီး", "health"),
]

LANGUAGES = {
 "dse": ("Dutch Sign Language (NGT)", "Netherlands"),
 "fsl": ("French Sign Language (LSF)", "France"),
 "gss": ("Greek Sign Language (GSL)", "Greece"),
 "sgg": ("Swiss-German Sign Language (DSGS)", "Switzerland"),
 "pso": ("Polish Sign Language (PJM)", "Poland"),
 "swl": ("Swedish Sign Language (STS)", "Sweden"),
}

def get(url: str, timeout=90) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": "WorldSign-data-import/1.0 (attribution-preserving text-only importer)"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()

def read_json(path: Path, default):
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return default

def write_json(path: Path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

def slug(s: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", str(s).lower()).strip("-")
    return s[:90] or "entry"

def msl_records():
    records=[]
    for i,(gloss,burmese,trans,category) in enumerate(MSL_README_EXAMPLES,1):
        records.append({"id":f"msl-msl4e-{i:03d}-{slug(gloss)}","language":"msl","entryType":"phrase","gloss":gloss,"meaning":burmese,"transcription":trans,"alternates":[burmese],"category":category,"region":"Myanmar (corpus region; local variation requires review)","notes":"Phrase-level example reproduced from the source README. Not an isolated lexical sign; no individual media mapping is supplied in this record.","media":{"type":"none","url":"","alt":""},"source":{"title":SOURCES["msl4emergency"]["title"],"url":SOURCES["msl4emergency"]["url"]},"license":"CC BY-NC-SA 4.0","attribution":SOURCES["msl4emergency"]["attribution"],"consent":{"documented":False,"recordId":""},"reviewStatus":"source-documented-needs-community-review","reviewer":"","created":TODAY})
    return records

def normkeys(row):
    return {re.sub(r"[^a-z0-9]+","",k.lower()): (v or "").strip() for k,v in row.items() if k}

def pick(row, *names):
    for n in names:
        v=row.get(re.sub(r"[^a-z0-9]+","",n.lower()),"")
        if v: return v
    return ""

def parse_msl_text():
    """Fetch only text annotation files from GitHub; never fetch video/ELAN media."""
    api="https://api.github.com/repos/ye-kyaw-thu/MSL4Emergency/git/trees/master?recursive=1"
    try:
        tree=json.loads(get(api).decode("utf-8"))
    except Exception as e:
        print(f"WARNING: MSL4Emergency tree download failed: {e}",file=sys.stderr)
        return []
    allowed_names={"my","sl","my-sl","my-mypos","my-pos","note.txt"}
    raw_dir=MIRRORS/"msl4emergency"/"raw"
    raw_dir.mkdir(parents=True,exist_ok=True)
    downloaded=[]
    for item in tree.get("tree",[]):
        path=item.get("path","")
        name=Path(path).name.lower()
        if not path.startswith("msl4emergency-ver-1.0/") or item.get("type")!="blob":
            continue
        # Strict allow-list: text annotation filenames/extensions only.
        if name not in allowed_names and Path(name).suffix.lower() not in {".txt", ".tsv", ".csv"}:
            continue
        if any(x in path.lower() for x in ("video", "elan", "pfsx", ".mp4", ".mov")):
            continue
        if item.get("size",0)>20_000_000:
            continue
        raw_url="https://raw.githubusercontent.com/ye-kyaw-thu/MSL4Emergency/master/"+urllib.parse.quote(path)
        try:
            blob=get(raw_url)
            dest=raw_dir/Path(path).name
            dest.write_bytes(blob)
            downloaded.append((dest,blob))
        except Exception as e:
            print(f"WARNING: MSL text file skipped {path}: {e}",file=sys.stderr)
    # my-sl is retained verbatim. Parse only rows with an explicit delimiter;
    # do not guess alignments from whitespace or line order.
    out=[]
    for path,blob in downloaded:
        if path.name.lower()!="my-sl":
            continue
        text=blob.decode("utf-8-sig",errors="replace")
        for line_no,line in enumerate(text.splitlines(),1):
            line=line.strip()
            if not line or line.startswith("#"): continue
            parts=re.split(r"\t+|\s+\|\|\s+|\s*\|\s*",line)
            if len(parts)<2: continue
            burmese,trans=parts[0].strip(),parts[1].strip()
            if not burmese or not trans or burmese.lower() in {"myanmar","burmese","source"}: continue
            out.append({"id":f"msl-msl4e-text-{len(out)+1:04d}","language":"msl","entryType":"phrase","gloss":burmese,"meaning":burmese,"transcription":trans,"alternates":[],"category":"emergency","region":"Myanmar; regional variety requires community validation","notes":f"Imported from the MSL4Emergency my-sl text annotation file, line {line_no}. Source alignment preserved; not an isolated lexical sign.","media":{"type":"none","url":"","alt":""},"source":{"title":SOURCES["msl4emergency"]["title"],"url":SOURCES["msl4emergency"]["url"],"file":path.name,"line":line_no},"license":"CC BY-NC-SA 4.0","attribution":SOURCES["msl4emergency"]["attribution"],"consent":{"documented":False,"recordId":""},"reviewStatus":"source-imported-needs-community-review","reviewer":"","created":TODAY})
    return out

def parse_easier():
    """Join official Wordnet sign metadata to accepted synset links, text only."""
    base="https://www.fdr.uni-hamburg.de/record/14190/files/"
    files={}
    for name in ("sign_data.csv","synset_links_accepted.csv","custom_synsets.csv"):
        try:
            files[name]=get(base+name+"?download=1")
        except Exception as e:
            print(f"WARNING: EASIER {name} download failed: {e}", file=sys.stderr)
    easier_langs={"bfi":"British Sign Language","dse":"Dutch Sign Language","fsl":"French Sign Language","gsg":"German Sign Language","gss":"Greek Sign Language","sgg":"Swiss-German Sign Language","pso":"Polish Sign Language","swl":"Swedish Sign Language"}
    for code in easier_langs:
        name=f"sign_wordnet_gloss_{code}.tab"
        try:
            files[name]=get(base+name+"?download=1")
        except Exception as e:
            print(f"WARNING: EASIER {name} download failed: {e}", file=sys.stderr)
    if "sign_data.csv" not in files:
        return []
    def csvrows(blob):
        text=blob.decode("utf-8-sig",errors="replace")
        return [normkeys(r) for r in csv.DictReader(io.StringIO(text))]
    sign_rows=csvrows(files["sign_data.csv"])
    links=csvrows(files["synset_links_accepted.csv"]) if "synset_links_accepted.csv" in files else []
    synsets=csvrows(files["custom_synsets.csv"]) if "custom_synsets.csv" in files else []
    by_sign={}
    for link in links:
        sid=pick(link,"sign_id","sign id","type_id","type id","sign")
        if sid: by_sign.setdefault(sid,[]).append(link)
    syn_by_id={}
    for syn in synsets:
        sid=pick(syn,"synset_id","synset id","id")
        if sid: syn_by_id[sid]=syn
    out=[]
    lang_alias={"bfi":"bfi","dse":"dse","fsl":"fsl","gsg":"gsg","gss":"gss","pso":"pso","sgg":"sgg","swl":"swl"}
    for i,row in enumerate(sign_rows,1):
        lang=pick(row,"language","lang","iso","language_code","dataset","sign_language").lower()
        lang=lang_alias.get(lang, {"bsl":"bfi","british":"bfi","ngt":"dse","dutch":"dse","lsf":"fsl","french":"fsl","dgs":"gsg","german":"gsg","gsl":"gss","greek":"gss","dsgs":"sgg","swiss-german":"sgg","pjm":"pso","polish":"pso","sts":"swl","swedish":"swl"}.get(lang,lang))
        if lang not in lang_alias:
            continue
        raw_id=pick(row,"id","sign_id","type_id","type id") or str(i)
        gloss=pick(row,"gloss","keyword","lemma","sign_gloss","name","label","type_gloss") or raw_id
        syn_links=by_sign.get(raw_id,[])
        syn_refs=[]
        meanings=[]
        for link in syn_links:
            synid=pick(link,"synset_id","synset id","synset")
            conf=pick(link,"confidence","status")
            syn_refs.append({"id":synid,"confidence":conf})
            syn=syn_by_id.get(synid,{})
            definition=pick(syn,"definition","gloss","description")
            if definition: meanings.append(definition)
        url=pick(row,"url","web_url","page_url","sign_url")
        out.append({"id":f"easier-{lang}-{slug(raw_id)}","language":lang,"entryType":"lexical-sign","gloss":gloss,"meaning":meanings[0] if meanings else "","transcription":"","alternates":[],"category":"daily-life","region":"","notes":"Imported from EASIER Multilingual Sign Language Wordnet. A gloss is a written label, not a spoken-language translation. Synset links and confidence are preserved when available.","media":{"type":"none","url":"","alt":""},"source":{"title":SOURCES["easier-wordnet"]["title"],"url":SOURCES["easier-wordnet"]["url"],"originalEntryUrl":url},"license":"CC BY 4.0","attribution":SOURCES["easier-wordnet"]["attribution"],"sourceData":row,"synsets":syn_refs,"consent":{"documented":False,"recordId":""},"reviewStatus":"source-imported-needs-community-review","reviewer":"","created":TODAY})
    # Import language-specific gloss tables. They provide actual source glosses
    # (not translated meanings or sign descriptions); preserve each synset key.
    for filename,blob in files.items():
        match=re.fullmatch(r"sign_wordnet_gloss_([a-z]{3})\.tab",filename)
        if not match: continue
        lang=match.group(1)
        text=blob.decode("utf-8-sig",errors="replace")
        for line_no,line in enumerate(text.splitlines(),1):
            if not line.strip() or line.lstrip().startswith("#"): continue
            cols=line.split("\t")
            if len(cols)<2: continue
            synset_id=cols[0].strip()
            for gloss in cols[1:]:
                gloss=gloss.strip()
                if not gloss: continue
                out.append({"id":f"easier-{lang}-{slug(synset_id)}-{slug(gloss)}","language":lang,"entryType":"lexical-sign","gloss":gloss,"meaning":"","transcription":"","alternates":[],"category":"daily-life","region":"","notes":"Gloss imported from the EASIER Wordnet language table. Glosses are labels, not translations or instructions for performing a sign.","media":{"type":"none","url":"","alt":""},"source":{"title":SOURCES["easier-wordnet"]["title"],"url":SOURCES["easier-wordnet"]["url"],"file":filename,"line":line_no,"synset":synset_id},"license":"CC BY 4.0","attribution":SOURCES["easier-wordnet"]["attribution"],"sourceData":{"synset":synset_id},"consent":{"documented":False,"recordId":""},"reviewStatus":"source-imported-needs-community-review","reviewer":"","created":TODAY})
    # preserve exact downloaded text-only source tables for reproducibility
    dest=MIRRORS/"easier-wordnet"/"raw"
    dest.mkdir(parents=True,exist_ok=True)
    for name,blob in files.items(): (dest/name).write_bytes(blob)
    return out

def parse_asllex():
    """Import ASL-LEX lexical metadata only; never download or mirror videos."""
    urls=["https://osf.io/9nygd/download","https://osf.io/ygq4v/download"]
    blobs=[]
    for url in urls:
        try: blobs.append((url,get(url)))
        except Exception as e: print(f"WARNING: ASL-LEX download failed for {url}: {e}",file=sys.stderr)
    if not blobs: return []
    out=[]
    for url,blob in blobs:
        try:
            text=blob.decode("latin-1")
            rows=csv.DictReader(io.StringIO(text))
            for i,raw in enumerate(rows,1):
                row=normkeys(raw)
                gloss=pick(row,"gloss","sign","lemma","english_gloss","word","entry_identifier","entry_id")
                if not gloss: continue
                raw_id=pick(row,"id","sign_id","item","item_id") or str(i)
                # Strip media URLs and any video-related columns from the mirrored record.
                safe={k:v for k,v in row.items() if not any(x in k for x in ("video","movie","media","clip","image"))}
                out.append({"id":f"asllex-{slug(raw_id)}","language":"ase","entryType":"lexical-sign","gloss":gloss,"meaning":pick(row,"english_translation","english translation","translation","english"),"transcription":"","alternates":[],"category":"daily-life","region":"United States","notes":"ASL-LEX lexical/phonological metadata. Reference videos and other media are excluded. Source metadata is not a movement or handshape tutorial.","media":{"type":"none","url":"","alt":""},"source":{"title":SOURCES["asl-lex-2"]["title"],"url":SOURCES["asl-lex-2"]["url"]},"license":"CC BY 4.0 (database only; videos excluded)","attribution":SOURCES["asl-lex-2"]["attribution"],"sourceData":safe,"consent":{"documented":False,"recordId":""},"reviewStatus":"source-imported-needs-community-review","reviewer":"","created":TODAY})
        except Exception as e: print(f"WARNING: Could not parse ASL-LEX file: {e}",file=sys.stderr)
    return out

def main():
    SIGNS.mkdir(parents=True,exist_ok=True)
    records=msl_records()
    msl_text=parse_msl_text()
    easier=parse_easier()
    asl=parse_asllex()
    records.extend(msl_text); records.extend(easier); records.extend(asl)
    # Preserve existing community/manual entries. Fresh source rows replace
    # matching IDs; unrelated user records are never discarded by a refresh.
    existing=read_json(SIGNS/"index.json",{"signs":[]}).get("signs",[])
    records.extend(existing)
    # Stable de-duplication; newer downloaded source records win on ID collision.
    unique={}
    for item in records: unique[item["id"]]=item
    records=list(unique.values())
    write_json(SIGNS/"index.json",{"schemaVersion":"1.1.0","signs":records})
    by_lang={}
    for item in records: by_lang.setdefault(item["language"],[]).append(item)
    for lang,items in by_lang.items(): write_json(SIGNS/f"{lang}.json",{"language":lang,"signs":items})
    # Keep empty per-language files for configured languages, and add languages from Wordnet.
    langfile=read_json(DATA/"languages.json",{"languages":[]})
    known={x["id"] for x in langfile["languages"]}
    for code,(name,region) in LANGUAGES.items():
        if code not in known: langfile["languages"].append({"id":code,"name":name,"region":region,"family":"Sign language","status":"EASIER Wordnet source data; community review required"})
    write_json(DATA/"languages.json",langfile)
    sourcesfile=read_json(DATA/"sources.json",{"sources":[]})
    for sid,name,langs,region,kind,size,license_,reuse,url,evidence in [
      ("easier-wordnet","EASIER Multilingual Sign Language Wordnet",["BSL","NGT","LSF","DGS","GSL","DSGS","PJM","STS"],"Europe","Lexical sign metadata and accepted synset links","Multiple language tables; exact imported count reported by importer","CC BY 4.0","Attribution required. This import excludes video/media files and preserves synset confidence.","https://www.fdr.uni-hamburg.de/record/14190","Open-access record lists CSV and tabular sign data under CC BY 4.0."),
      ("asl-lex","ASL-LEX 2.0",["American Sign Language"],"United States","Lexical and phonological database","2,723 signs","CC BY 4.0 (database only; videos excluded)","Attribution required. Import only database metadata; do not copy reference videos.","https://asl-lex.org/download.html","Official download page specifies CC BY 4.0 for database and excludes videos."),
    ]:
        entry={"id":sid,"name":name,"languages":langs,"region":region,"kind":kind,"size":size,"license":license_,"reuse":reuse,"status":"Text-only importer configured; run scripts/import_public_datasets.py to refresh","url":url,"evidence":evidence}
        old=next((x for x in sourcesfile["sources"] if x.get("id")==sid),None)
        if old: old.update(entry)
        else: sourcesfile["sources"].append(entry)
    # Correct prior ASL-LEX source statement to the official project licence.
    for src in sourcesfile["sources"]:
        if src.get("id")=="asl-lex":
            src["license"]="CC BY 4.0 (database only; reference videos excluded)"
            src["reuse"]="Attribution required. Official ASL-LEX page licenses database/visualization CC BY 4.0; reference videos remain copyrighted and are not copied."
            src["status"]="Text-only importer configured; verify imported release"
            src["url"]="https://asl-lex.org/download.html"
    write_json(DATA/"sources.json",sourcesfile)
    print(f"Imported {len(records)} records: MSL README examples={len(msl_records())}, MSL text pairs={len(msl_text)}, EASIER={len(easier)}, ASL-LEX={len(asl)}")
    print("Only text and metadata were retained. No video, image, or ELAN media was downloaded.")
    print("Review status is not approved; community review remains required.")

if __name__=="__main__": main()
