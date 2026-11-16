#!/usr/bin/env python3
"""Fetch and validate official hotel & room photos for all compared Colombian beach hotels."""
from __future__ import annotations

import json
import os
import re
import shutil
import ssl
import struct
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

BASE_DIR = Path("/Users/video/.gemini/antigravity/scratch/vacaciones-familia-colombia")
PHOTOS_DIR = BASE_DIR / "assets" / "photos"
PROOFS_DIR = BASE_DIR / "assets" / "proofs"
MANIFEST_PATH = BASE_DIR / "data" / "photos_manifest.json"

CTX = ssl.create_default_context()
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"

BLOCK_SUBSTRINGS = [
    "logo", "icon", "favicon", "flag", "pixel", "avatar", "white.png",
    "loading", "assistcard", "sprite", "marca-de-agua", "1982-con-fondo-blanco",
    "destacados-", "friends-hor", "palmtree", "pobladopromocionenhotelesensanadres",
    "destino-medellin", "destino-valledupar", "destino-san-andres",
    "slide-ibiza", "slideseaview", "slide-sirenis-hotel-club-siesta",
    "puntacana", "playadelcarmen", "bg-mapa", "iconos-", "whatsapp-image",
    "nuevo-formato-post", "captura+de+pantalla",
]

PROOFS_SRC = {
    "sol-caribe-checkout.png": "/Users/video/.gemini/antigravity/brain/0c8bed5e-58b3-458b-8576-32349316610c/browser_evidence/9c4592a3-344e-4a53-9e7e-ba884889d6d6/final_step_67.png",
    "arena-blanca-checkout.png": "/Users/video/.gemini/antigravity/brain/0c8bed5e-58b3-458b-8576-32349316610c/browser_evidence/fcf4ceb9-7631-4843-b89b-213bfc9a8c5a/final_step_86.png",
    "almejal-checkout.png": "/Users/video/.gemini/antigravity/brain/0c8bed5e-58b3-458b-8576-32349316610c/browser_evidence/b5f06375-ef38-42ba-b516-d3f92f64d712/final_step_59.png",
    "wayira-checkout.png": "/Users/video/.gemini/antigravity/brain/0c8bed5e-58b3-458b-8576-32349316610c/browser_evidence/802afdd7-00f4-403f-964d-746da866efa4/final_step_104.png",
    "las-americas-agotado.png": "/Users/video/.gemini/antigravity/brain/0c8bed5e-58b3-458b-8576-32349316610c/browser_evidence/4e58c9e3-87fe-42f0-bc24-d269e9e03d41/final_step_114.png",
}


def fetch_html(url: str, timeout: int = 12) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "es-CO,es;q=0.9"})
    with urllib.request.urlopen(req, timeout=timeout, context=CTX) as r:
        return r.read().decode("utf-8", "ignore")


def get_image_dimensions(data: bytes) -> tuple[int, int]:
    try:
        if data.startswith(b"\x89PNG\r\n\x1a\n") and len(data) >= 24:
            return struct.unpack(">II", data[16:24])
        if data.startswith(b"RIFF") and data[8:12] == b"WEBP":
            chunk = data[12:16]
            if chunk == b"VP8 " and len(data) >= 30:
                w = struct.unpack("<H", data[26:28])[0] & 0x3FFF
                h = struct.unpack("<H", data[28:30])[0] & 0x3FFF
                return w, h
            if chunk == b"VP8L" and len(data) >= 25:
                bits = struct.unpack("<I", data[21:25])[0]
                return (bits & 0x3FFF) + 1, ((bits >> 14) & 0x3FFF) + 1
            if chunk == b"VP8X" and len(data) >= 30:
                w = int.from_bytes(data[24:27], "little") + 1
                h = int.from_bytes(data[27:30], "little") + 1
                return w, h
        if data.startswith(b"\xff\xd8"):
            i = 2
            while i < len(data) - 9:
                if data[i] != 0xFF:
                    i += 1
                    continue
                marker = data[i + 1]
                if marker in (0xC0, 0xC1, 0xC2):
                    h, w = struct.unpack(">HH", data[i + 5:i + 9])
                    return w, h
                if marker in (0xD8, 0xD9, 0x01) or (0xD0 <= marker <= 0xD7):
                    i += 2
                else:
                    seg_len = struct.unpack(">H", data[i + 2:i + 4])[0]
                    i += 2 + seg_len
    except Exception:
        pass
    return 0, 0


def is_valid_image_bytes(data: bytes) -> bool:
    if len(data) < 10240:
        return False
    if data.startswith((b"\xff\xd8\xff", b"\x89PNG\r\n\x1a\n", b"RIFF", b"GIF8")):
        w, h = get_image_dimensions(data)
        if w and h and (w < 320 or h < 200):
            return False
        return True
    return False


def infer_category(url: str, caption: str, default_cat: str = "instalaciones") -> str:
    fname = urllib.parse.unquote(url.split("?")[0].rstrip("/").split("/")[-1]).lower()
    fname = fname.replace("cabanas-el-tesoro-", "").replace("hotel-en-tolu-", "")
    txt = f"{fname} {caption.lower()}"
    if any(k in txt for k in [
        "restaurante", "comida", "food", "gastron", "bucanero", "barbacoa",
        "bar-", "snack", "cocktail", "jasai", "isashii", "asawaa", "palaa",
        "fish", "patacon", "chef", "welcome-drink", "arches"
    ]):
        return "gastronomia"
    if any(k in txt for k in [
        "habitacion", "room", "suite", "standar", "king", "twin", "queen",
        "cuadruple", "doble", "triple", "alcoba", "balcony", "hb+sup",
        "caban-as+estandar", "exterior+caban-a", "cabanas.webp", "bungalow-kids",
        "bungalow-wayuu", "corridor"
    ]):
        return "habitaciones"
    return default_cat


def clean_caption(url: str, fallback: str) -> str:
    name = urllib.parse.unquote(url.split("?")[0].rstrip("/").split("/")[-1])
    name = re.sub(r"\.[a-zA-Z0-9]+$", "", name)
    name = re.sub(r"[-_+]+", " ", name)
    name = re.sub(r"\b(on vacation|colombia|destino|nacional|guajira|san andres|hotel|1920w|2880w|11zon|opt|mv2|5c9ddd|sirenis|hotels)\b", "", name, flags=re.I)
    name = re.sub(r"\s+", " ", name).strip()
    if len(name) < 4 or re.fullmatch(r"[0-9a-f\s]+", name.lower()):
        return fallback
    return name[:72].strip().capitalize()


def is_blocked(url: str) -> bool:
    low = url.lower()
    return any(b in low for b in BLOCK_SUBSTRINGS)


def add_item(bucket: list, seen_urls: set, url: str, category: str = "", caption: str = "", default_cat: str = "instalaciones"):
    u = url.strip().rstrip(")")
    if not u or u in seen_urls or is_blocked(u):
        return
    seen_urls.add(u)
    cat = category or infer_category(u, caption, default_cat)
    cap = caption or clean_caption(u, "Instalaciones oficiales del hotel")
    bucket.append({"url": u, "category": cat, "caption": cap})


def balance_gallery(items: list[dict], max_total: int = 18, max_rooms: int = 7, max_food: int = 4) -> list[dict]:
    rooms = [i for i in items if i["category"] == "habitaciones"][:max_rooms]
    food = [i for i in items if i["category"] == "gastronomia"][:max_food]
    inst = [i for i in items if i["category"] == "instalaciones"]
    remaining = max_total - len(rooms) - len(food)
    combined = rooms + inst[:max(remaining, 4)] + food
    return combined[:max_total]


def collect_candidates() -> dict[str, list[dict]]:
    candidates: dict[str, list[dict]] = {}

    # 1. Sol Caribe San Andres
    slug = "sol-caribe-san-andres"
    items, seen = [], set()
    try:
        h = fetch_html("https://www.solarhoteles.com/es/hoteles/sol-caribe-san-andres-en-isla-san-andres/")
        paths = list(dict.fromkeys(re.findall(r"/media/uploads/(?:galeriahoteles|galeriahabitaciones|cms_apps/imagenes|cms)/[^\"\x27\s>?]+", h)))
        for p in paths:
            full = f"https://www.solarhoteles.com{p}?q=pr:sharp/rs:fill/w:1200/h:800/f:jpg"
            cap = "Habitación Estándar — Sol Caribe San Andrés" if "habitacion" in p else ""
            add_item(items, seen, full, caption=cap)
    except Exception as e:
        print(f"[WARN] {slug}: {e}")
    candidates[slug] = balance_gallery(items, max_total=18, max_rooms=6, max_food=5)

    # 2. Decameron Maryland
    slug = "decameron-maryland"
    items, seen = [], set()
    for page_url, forced_cat, cap_prefix in [
        ("https://www.decameron.com/es/hoteles/san-andres-islas/decameron-maryland/habitaciones/", "habitaciones", "Habitación Decameron Maryland"),
        ("https://www.decameron.com/es/hoteles/san-andres-islas/decameron-maryland/", "", "Decameron Maryland"),
        ("https://www.decameron.com/es/hoteles/san-andres-islas/decameron-maryland/galeria/", "instalaciones", "Galería Decameron Maryland"),
    ]:
        try:
            h = fetch_html(page_url)
            paths = list(dict.fromkeys(re.findall(r"/media/uploads/(?:galeriahabitaciones|galeriahoteles|cms_apps/imagenes)/[^\"\x27\s>?]+", h)))
            for p in paths:
                if "delfines" in p.lower():
                    continue
                full = f"https://www.decameron.com{p}?q=pr:sharp/rs:fill/w:1200/h:800/g:ce/f:webp"
                cat = forced_cat
                if any(k in p.lower() for k in ["comida", "restaurante", "bar"]):
                    cat = "gastronomia"
                elif any(k in p.lower() for k in ["habitacion", "queen"]):
                    cat = "habitaciones"
                elif not cat:
                    cat = "instalaciones"
                cap = f"{cap_prefix}: {clean_caption(p, 'Instalaciones')}" if forced_cat else ""
                add_item(items, seen, full, category=cat, caption=cap)
        except Exception as e:
            print(f"[WARN] {slug} ({page_url}): {e}")
    candidates[slug] = balance_gallery(items, max_total=18, max_rooms=7, max_food=4)

    # 3. Hotel Arena Blanca (strictly JPGs + HD fit URL so no 15MB raw files or PNG icons)
    slug = "hotel-arena-blanca"
    items, seen = [], set()
    add_item(items, seen, "https://aresai.backhotelite.com/media/uploads/cms_apps/imagenes/DOBLE_ESTANDAR_1.jpg", "habitaciones", "Habitación Estándar — Hotel Arena Blanca")
    for page_url, forced_cat in [
        ("https://www.hotelarenablanca.com.co/habitaciones", "habitaciones"),
        ("https://www.hotelarenablanca.com.co/galeria", "instalaciones"),
        ("https://www.hotelarenablanca.com.co/", "instalaciones"),
    ]:
        try:
            h = fetch_html(page_url)
            ids = list(dict.fromkeys(re.findall(r"5c9ddd_[a-zA-Z0-9]+~mv2\.(?:jpg|jpeg)", h)))
            for mid in ids:
                full = f"https://static.wixstatic.com/media/{mid}/v1/fit/w_1200,h_800,q_85/{mid}"
                cap = "Habitación — Hotel Arena Blanca" if forced_cat == "habitaciones" else "Hotel Arena Blanca San Andrés (piscina y áreas)"
                add_item(items, seen, full, category=forced_cat, caption=cap)
        except Exception as e:
            print(f"[WARN] {slug} ({page_url}): {e}")
    candidates[slug] = balance_gallery(items, max_total=16, max_rooms=5, max_food=3)

    # 4. Grand Sirenis San Andres
    slug = "grand-sirenis-san-andres"
    items, seen = [], set()
    try:
        h = fetch_html("https://www.sirenishotels.com/hoteles-san-andres/grand-sirenis-san-andres/")
        room_paths = list(dict.fromkeys(re.findall(r"/content/imgsxml/galerias/panel_habitaciones/[^\"\x27\s>?]+\.(?:jpg|jpeg)", h, re.I)))
        for p in room_paths:
            add_item(items, seen, f"https://www.sirenishotels.com{p}", "habitaciones", f"Suite Grand Sirenis: {clean_caption(p, 'Habitación moderna')}")
        hero_paths = list(dict.fromkeys(re.findall(r"/content/imgsxml/panel_herohotel/[^\"\x27\s>?]+\.(?:jpg|jpeg)", h, re.I)))
        for p in hero_paths:
            if "san-andr" in p.lower() or "sirenis" in p.lower():
                add_item(items, seen, f"https://www.sirenishotels.com{p}")
        gal_paths = list(dict.fromkeys(re.findall(r"/content/imgsxml/galerias/panel_galeria/x/[^\"\x27\s>?]+\.(?:jpg|jpeg)", h, re.I)))
        for p in gal_paths:
            add_item(items, seen, f"https://www.sirenishotels.com{p}")
    except Exception as e:
        print(f"[WARN] {slug}: {e}")
    candidates[slug] = balance_gallery(items, max_total=18, max_rooms=7, max_food=5)

    # 5. Hotel Las Mananitas (Capurgana)
    slug = "hotel-las-mananitas"
    items, seen = [], set()
    try:
        h = fetch_html("https://hotellasmananitas.com/")
        paths = list(dict.fromkeys(re.findall(r"media/[^\"\x27\s>?)]+\.(?:jpg|jpeg|webp)", h, re.I)))
        for p in paths:
            full = f"https://hotellasmananitas.com/{p}"
            cap, cat = "", ""
            if any(k in p.lower() for k in ["balcony", "corridor", "hero-night"]):
                cat = "habitaciones"
                cap = "Balcón y habitaciones vista al mar — Hotel Las Mañanitas"
            elif any(k in p.lower() for k in ["sapzurro", "lamiel", "reef", "bay-boats"]):
                cat = "instalaciones"
                cap = f"Excursión incluida: {clean_caption(p, 'Capurganá y Sapzurro')}"
            add_item(items, seen, full, category=cat, caption=cap)
    except Exception as e:
        print(f"[WARN] {slug}: {e}")
    candidates[slug] = balance_gallery(items, max_total=22, max_rooms=6, max_food=6)

    # 6. Ecolodge El Almejal (Bahia Solano)
    slug = "ecolodge-el-almejal"
    items, seen = [], set()
    for page_url, forced_cat in [
        ("https://www.almejal.com.co/caba%C3%B1as-almejal-Bahiasolano", "habitaciones"),
        ("https://www.almejal.com.co/", "instalaciones"),
    ]:
        try:
            h = fetch_html(page_url)
            urls = list(dict.fromkeys(re.findall(r"https://irp\.cdn-website\.com/c251327a/dms3rep/multi/[^\"\x27\s>?)]+\.(?:jpg|jpeg|png|webp)", h, re.I)))
            for u in urls:
                cap = "Cabaña Familiar entre selva y playa — Ecolodge El Almejal" if forced_cat == "habitaciones" else ""
                add_item(items, seen, u, category=forced_cat, caption=cap)
        except Exception as e:
            print(f"[WARN] {slug} ({page_url}): {e}")
    candidates[slug] = balance_gallery(items, max_total=18, max_rooms=6, max_food=3)

    # 7. Wayira Beach (Mayapo, La Guajira)
    slug = "wayira-beach"
    items, seen = [], set()
    try:
        h = fetch_html("https://www.onvacation.com/co/destinos/nacionales/guajira/hotel-wayira-beach/")
        urls = [u for u in dict.fromkeys(re.findall(r"(?:https://www\.onvacation\.com)?/wp-content/uploads/[^\"\x27\s>?)]+\.(?:webp|jpg|jpeg)", h, re.I)) if "wayira" in u.lower()]
        for u in urls:
            full = u if u.startswith("http") else f"https://www.onvacation.com{u}"
            add_item(items, seen, full)
    except Exception as e:
        print(f"[WARN] {slug}: {e}")
    candidates[slug] = balance_gallery(items, max_total=18, max_rooms=7, max_food=4)

    # 8. Isla Mucura (Punta Faro + Hotel Isla Mucura)
    slug = "punta-faro-mucura"
    items, seen = [], set()
    try:
        h_pf = fetch_html("https://www.puntafaro.com/")
        imgix_ids = list(dict.fromkeys(re.findall(r"webbox\.imgix\.net/images/iqirqtkvzpgilsbk/([^\"\x27\s>?&]+)", h_pf)))
        for idx_id in imgix_ids:
            if idx_id.endswith(".png"):
                continue
            full = f"https://webbox.imgix.net/images/iqirqtkvzpgilsbk/{idx_id}?auto=format,compress&w=1200&q=80"
            add_item(items, seen, full, caption="Hotel Punta Faro — Isla Múcura")
    except Exception as e:
        print(f"[WARN] {slug} puntafaro: {e}")
    try:
        h_im = fetch_html("https://hotelislamucura.com/")
        im_urls = list(dict.fromkeys(re.findall(r"https://hotelislamucura\.com/wp-content/uploads/[^\"\x27\s>?)]+\.(?:webp|jpg|jpeg)", h_im, re.I)))
        for u in im_urls[:8]:
            add_item(items, seen, u, caption="Hotel Isla Múcura — Archipiélago San Bernardo")
    except Exception as e:
        print(f"[WARN] {slug} islamucura: {e}")
    candidates[slug] = balance_gallery(items, max_total=12, max_rooms=4, max_food=3)

    # 9. Covenas & Tolu
    slug = "poblado-covenas-tesoro"
    items, seen = [], set()
    try:
        h_tes = fetch_html("https://cabanaseltesoro.com/")
        tes_urls = list(dict.fromkeys(re.findall(r"https://cabanaseltesoro\.com/wp-content/uploads/[^\"\x27\s>?)]+\.(?:webp|jpg|jpeg)", h_tes, re.I)))
        for u in tes_urls:
            add_item(items, seen, u)
    except Exception as e:
        print(f"[WARN] {slug} tesoro: {e}")
    try:
        h_pob = fetch_html("https://hotelpoblado.com/")
        pob_urls = list(dict.fromkeys(re.findall(r"https://irp\.cdn-website\.com/78cf0bd5/dms3rep/multi/[^\"\x27\s>?)]+\.(?:jpg|jpeg|webp)", h_pob, re.I)))
        for u in pob_urls:
            add_item(items, seen, u, caption="Hotel Poblado Coveñas")
    except Exception as e:
        print(f"[WARN] {slug} poblado: {e}")
    candidates[slug] = balance_gallery(items, max_total=12, max_rooms=4, max_food=3)

    # 10. On Vacation San Andres Reference
    slug = "on-vacation-san-andres"
    items, seen = [], set()
    for page_url, key in [
        ("https://www.onvacation.com/co/destinos/nacionales/san-andres/hotel-tone/", "tone"),
        ("https://www.onvacation.com/co/destinos/nacionales/san-andres/hotel-blue-cove/", "cove"),
    ]:
        try:
            h = fetch_html(page_url)
            urls = [u for u in dict.fromkeys(re.findall(r"(?:https://www\.onvacation\.com)?/wp-content/uploads/[^\"\x27\s>?)]+\.(?:webp|jpg|jpeg)", h, re.I)) if key in u.lower()]
            for u in urls:
                full = u if u.startswith("http") else f"https://www.onvacation.com{u}"
                add_item(items, seen, full)
        except Exception as e:
            print(f"[WARN] {slug} ({key}): {e}")
    candidates[slug] = balance_gallery(items, max_total=12, max_rooms=4, max_food=3)

    return candidates


def download_one(slug: str, idx: int, item: dict) -> dict | None:
    url = item["url"]
    ext = ".jpg"
    path_no_q = url.split("?")[0].lower()
    for cand_ext in (".webp", ".png", ".jpeg", ".jpg"):
        if path_no_q.endswith(cand_ext):
            ext = ".jpg" if cand_ext == ".jpeg" else cand_ext
            break
    out_dir = PHOTOS_DIR / slug
    out_dir.mkdir(parents=True, exist_ok=True)
    fname = f"{idx:02d}_{item['category']}{ext}"
    out_path = out_dir / fname

    try:
        req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "image/webp,image/jpeg,image/png,*/*;q=0.8"})
        with urllib.request.urlopen(req, timeout=12, context=CTX) as r:
            ctype = (r.headers.get("Content-Type") or "").lower()
            if ctype and "image" not in ctype:
                return None
            data = r.read()
        if not is_valid_image_bytes(data):
            return None
        w, h = get_image_dimensions(data)
        out_path.write_bytes(data)
        return {
            "localPath": f"assets/photos/{slug}/{fname}",
            "remoteUrl": url,
            "category": item["category"],
            "caption": item["caption"],
            "bytes": len(data),
            "width": w,
            "height": h,
        }
    except Exception:
        return None


def main():
    if PHOTOS_DIR.exists():
        shutil.rmtree(PHOTOS_DIR)
    PHOTOS_DIR.mkdir(parents=True, exist_ok=True)
    PROOFS_DIR.mkdir(parents=True, exist_ok=True)

    copied_proofs = {}
    for dest_name, src_path in PROOFS_SRC.items():
        if os.path.exists(src_path):
            shutil.copy2(src_path, PROOFS_DIR / dest_name)
            copied_proofs[dest_name] = f"assets/proofs/{dest_name}"

    print("Discovering official hotel & room images...")
    candidates = collect_candidates()
    manifest = {"hotels": {}, "proofs": copied_proofs}

    tasks = []
    with ThreadPoolExecutor(max_workers=10) as pool:
        for slug, items in candidates.items():
            for idx, item in enumerate(items, start=1):
                fut = pool.submit(download_one, slug, idx, item)
                tasks.append((slug, idx, fut))

        per_hotel: dict[str, list] = {slug: [] for slug in candidates}
        for slug, idx, fut in tasks:
            res = fut.result()
            if res:
                per_hotel[slug].append((idx, res))

    total_photos = 0
    for slug, entries in per_hotel.items():
        entries.sort(key=lambda x: x[0])
        photos = [e[1] for e in entries]
        manifest["hotels"][slug] = photos
        rooms_cnt = sum(1 for p in photos if p["category"] == "habitaciones")
        food_cnt = sum(1 for p in photos if p["category"] == "gastronomia")
        inst_cnt = sum(1 for p in photos if p["category"] == "instalaciones")
        total_photos += len(photos)
        print(f"  {slug:28s}: {len(photos):2d} ({rooms_cnt} hab, {inst_cnt} inst, {food_cnt} gast)")

    MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Done! Total valid photos: {total_photos}. Proofs copied: {len(copied_proofs)}")


if __name__ == "__main__":
    main()
