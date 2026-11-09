#!/usr/bin/env python3
"""Copy dashboard data files into the website and rebuild data/manifest.json.

Usage: python3 scripts/export_data.py DOCS_DIR FILES_DIR [SITE_DIR]

DOCS_DIR   folder of dataset records (one <id>.json per dataset, as saved by an
           ArtifactData "list" of the dashboard's "datasets" collection)
FILES_DIR  folder holding new data files named <id>.json ({"rows": [...]});
           only the datasets present here are replaced on the website
SITE_DIR   the website folder (default: the folder above this script)
"""
import datetime as dt
import glob
import json
import os
import sys


def fail(msg):
    print("FAIL:", msg)
    sys.exit(1)


def main(docs_dir, files_dir, site_dir):
    data_dir = os.path.join(site_dir, "data")
    os.makedirs(data_dir, exist_ok=True)
    docs = {}
    for p in glob.glob(os.path.join(docs_dir, "*.json")):
        d = json.load(open(p))
        d = d.get("data", d)  # accept a raw record or {id, data, version}
        docs[os.path.basename(p)[:-5]] = d
    if len(docs) < 30:
        fail(f"only {len(docs)} dataset records found in {docs_dir}")
    copied = []
    for p in glob.glob(os.path.join(files_dir, "*.json")):
        ds = os.path.basename(p)[:-5]
        if ds not in docs:
            continue
        body = json.load(open(p))
        rows = body.get("rows") if isinstance(body, dict) else body
        if not isinstance(rows, list) or not rows:
            fail(f"{ds}: no rows")
        json.dump({"rows": rows}, open(os.path.join(data_dir, ds + ".json"), "w"), separators=(",", ":"), ensure_ascii=False)
        copied.append(ds)
    missing = [ds for ds in docs if not os.path.exists(os.path.join(data_dir, ds + ".json"))]
    if missing:
        fail("no data file on the website for " + ", ".join(sorted(missing)))
    manifest = {
        "generated": dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "datasets": {
            ds: {
                "title": d.get("title", ds),
                "description": d.get("description", ""),
                "updated": (d.get("updated") or {}).get("at"),
                "schedule": d.get("schedule", ""),
                "blob": ((d.get("source") or {}).get("url", "").split("/_blob/") + [None])[1],
            }
            for ds, d in sorted(docs.items())
        },
    }
    json.dump(manifest, open(os.path.join(data_dir, "manifest.json"), "w"), indent=1, ensure_ascii=False)
    print(f"copied {len(copied)} data files ({', '.join(sorted(copied)) or 'none'}); manifest lists {len(docs)} datasets")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        fail(__doc__)
    main(sys.argv[1], sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
