#!/usr/bin/env python3
"""Compile a single portable self-contained HTML file for sharing via WhatsApp/AirDrop."""
from __future__ import annotations

import base64
import json
import re
from pathlib import Path

BASE_DIR = Path("/Users/video/.gemini/antigravity/scratch/vacaciones-familia-colombia")
INDEX_HTML = BASE_DIR / "index.html"
STYLES_CSS = BASE_DIR / "styles.css"
HOTELS_JS = BASE_DIR / "data" / "hotels_data.js"
APP_JS = BASE_DIR / "app.js"
OUT_HTML = BASE_DIR / "compartir-vacaciones-esposa.html"


def main():
    html = INDEX_HTML.read_text(encoding="utf-8")
    css = STYLES_CSS.read_text(encoding="utf-8")
    hotels_raw = HOTELS_JS.read_text(encoding="utf-8")
    app_js = APP_JS.read_text(encoding="utf-8")

    # Parse window.VACATION_DATA JSON and inline proof screenshots as base64 data URIs
    m = re.match(r"^\s*window\.VACATION_DATA\s*=\s*(.*);\s*$", hotels_raw, re.S)
    if not m:
        raise RuntimeError("Could not parse window.VACATION_DATA from data/hotels_data.js")
    payload = json.loads(m.group(1))

    for h in payload.get("hotels", []):
        for p in h.get("photos", []):
            lp = p.get("localPath", "")
            if lp.startswith("assets/proofs/"):
                fpath = BASE_DIR / lp
                if fpath.exists():
                    b64 = base64.b64encode(fpath.read_bytes()).decode("ascii")
                    data_uri = f"data:image/png;base64,{b64}"
                    p["remoteUrl"] = data_uri
                    p["localPath"] = data_uri

    inlined_data_js = "window.__SHAREABLE_MODE__ = true;\nwindow.VACATION_DATA = " + json.dumps(payload, ensure_ascii=False) + ";"

    # Replace external local links/scripts with inline tags
    html = html.replace('<link rel="stylesheet" href="styles.css" />', f"<style>\n{css}\n</style>")
    html = html.replace('<script src="data/hotels_data.js"></script>', f"<script>\n{inlined_data_js}\n</script>")
    html = html.replace('<script src="app.js"></script>', f"<script>\n{app_js}\n</script>")

    OUT_HTML.write_text(html, encoding="utf-8")
    size_kb = OUT_HTML.stat().st_size / 1024
    print(f"Generated {OUT_HTML} ({size_kb:.1f} KB)")


if __name__ == "__main__":
    main()
