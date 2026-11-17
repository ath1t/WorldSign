#!/usr/bin/env python3
import json, pathlib, sys
ROOT=pathlib.Path(__file__).resolve().parents[1]
errors=[]
def load(p):
    try:return json.loads(p.read_text(encoding="utf-8"))
    except Exception as e:errors.append(f"{p.relative_to(ROOT)}: {e}");return {}
langs=load(ROOT/"data/languages.json").get("languages",[])
cats=load(ROOT/"data/categories.json").get("categories",[])
data=load(ROOT/"data/signs/index.json").get("signs",[])
lang_ids={x["id"] for x in langs};cat_ids={x["id"] for x in cats};seen=set()
for s in data:
    sid=s.get("id")
    if not sid or sid in seen:errors.append(f"Missing/duplicate sign id: {sid}")
    seen.add(sid)
    if s.get("language") not in lang_ids:errors.append(f"{sid}: unknown language")
    if s.get("category") not in cat_ids:errors.append(f"{sid}: unknown category")
    if s.get("reviewStatus")=="approved" and not s.get("consent",{}).get("documented"):errors.append(f"{sid}: approved without documented consent")
print(f"Languages: {len(langs)} | Categories: {len(cats)} | Sign entries: {len(data)}")
if errors:
    print("\\n".join(errors));sys.exit(1)
print("Validation passed.")
