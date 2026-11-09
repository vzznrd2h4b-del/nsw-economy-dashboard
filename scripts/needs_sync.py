#!/usr/bin/env python3
"""Print the dataset ids whose data file on the website is out of date.

Usage: python3 scripts/needs_sync.py DOCS_DIR [SITE_DIR]

DOCS_DIR holds the dashboard's dataset records (<id>.json each, as saved by an
ArtifactData "list" of its "datasets" collection). A dataset needs syncing when
its record points at a different data file (source.url) from the one recorded in
data/manifest.json, or when the website has no data file for it. Prints one line
per dataset: "<id> <asset id>".
"""
import glob
import json
import os
import sys

docs_dir = sys.argv[1]
site_dir = sys.argv[2] if len(sys.argv) > 2 else os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
try:
    manifest = json.load(open(os.path.join(site_dir, "data", "manifest.json")))["datasets"]
except FileNotFoundError:
    manifest = {}
for p in sorted(glob.glob(os.path.join(docs_dir, "*.json"))):
    ds = os.path.basename(p)[:-5]
    d = json.load(open(p))
    d = d.get("data", d)
    url = (d.get("source") or {}).get("url", "")
    if "/_blob/" not in url:
        continue
    blob = url.split("/_blob/")[1]
    have = (manifest.get(ds) or {}).get("blob")
    if have != blob or not os.path.exists(os.path.join(site_dir, "data", ds + ".json")):
        print(ds, blob)
