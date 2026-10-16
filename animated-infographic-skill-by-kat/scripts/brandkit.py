#!/usr/bin/env python3
"""Brand kit tools for the brand-infographics skill.

Subcommands
  suggest  --logo FILE                     print the logo's dominant colors (to propose a palette)
  setup    --brand-dir DIR --name ... [...] create/update a brand: fonts, logo, brand.json
  build    --brand-dir DIR --content FRAG.html [--css FMT.css] --title T --alt A --out PAGE.html
  package  --skill-dir DIR --brand-dir DIR --out ZIP   zip the skill with this brand baked in

A brand directory holds: brand.json, mark.(svg|png), optional wordmark.(svg|png), fonts/*.woff2|ttf, learnings.md
"""
import argparse, base64, colorsys, glob, json, os, re, shutil, subprocess, sys, tarfile, tempfile, zipfile

SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ---------------------------------------------------------------- color math
def hex2rgb(h):
    h = h.strip().lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))

def rgb2hex(c):
    return "#%02x%02x%02x" % tuple(max(0, min(255, round(v))) for v in c)

def mix(a, b, t):
    a, b = hex2rgb(a), hex2rgb(b)
    return rgb2hex([a[i] + (b[i] - a[i]) * t for i in range(3)])

def lum(h):
    def ch(v):
        v /= 255
        return v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4
    r, g, b = hex2rgb(h)
    return 0.2126 * ch(r) + 0.7152 * ch(g) + 0.0722 * ch(b)

def contrast(a, b):
    la, lb = sorted([lum(a), lum(b)], reverse=True)
    return (la + 0.05) / (lb + 0.05)

def readable(color, bg, toward, target=4.5):
    """Nudge `color` toward `toward` until it reads on `bg`."""
    t, c = 0.0, color
    while contrast(c, bg) < target and t < 1:
        t += 0.05
        c = mix(color, toward, t)
    return c

def alpha(h, a):
    r, g, b = hex2rgb(h)
    return f"rgba({r},{g},{b},{a})"

def tokens(b):
    c = b["colors"]
    bg, text, accent = c["background"], c["text"], c["accent"]
    dark = lum(bg) < 0.25
    accent_hi = c.get("accent_light") or readable(accent, bg, "#ffffff" if dark else "#000000")
    tint = mix(text, accent, .55)  # surfaces lean slightly toward the accent so they feel on-brand
    on_accent = "#ffffff" if contrast("#ffffff", accent) >= contrast("#111111", accent) else "#111111"
    t = {
        "bg": bg, "text": text, "accent": accent, "accent-hi": accent_hi,
        "ring": c.get("ring") or (mix(accent, "#ffffff", .25) if dark else accent),
        "card": c.get("surface") or mix(bg, tint, .06 if dark else .04),
        "card-on": mix(bg, accent, .14 if dark else .08),
        "line": c.get("border") or mix(bg, tint, .2 if dark else .18),
        "label": readable(mix(bg, text, .8), bg, text, 7),
        "muted": readable(mix(bg, text, .58), bg, text, 4.5),
        "on-accent": on_accent,
        "plate": c.get("plate") or bg,
        "pill-bg": c.get("pill") or (mix(bg, "#000000", .5) if dark else mix(bg, text, .05)),
        "pill-text": text,
    }
    css = [f"  --{k}:{v};" for k, v in t.items()]
    css += [f"  --accent-a55:{alpha(accent, .55)};", f"  --accent-a40:{alpha(accent, .40)};"]
    f = b["fonts"]
    css += [f"  --f-head:'{f['heading']['family']}',system-ui,sans-serif;",
            f"  --f-body:'{f['body']['family']}',system-ui,sans-serif;",
            f"  --f-label:'{f['label']['family']}',ui-monospace,monospace;",
            f"  --head-weight:{f['heading'].get('weight', 600)};",
            f"  --label-case:{b['style'].get('label_case', 'uppercase')};",
            f"  --label-track:{b['style'].get('label_tracking', '3px')};",
            f"  --radius:{b['style'].get('radius', 16)}px;",
            f"  --home-size:{b['mascot'].get('home_size', 130)};",
            f"  --home-plate:{1 if b['mascot'].get('home_plate') else 0};"]
    warn = []
    if contrast(text, bg) < 7:
        warn.append(f"text on background contrast is {contrast(text, bg):.1f}:1 (aim for 7+)")
    if accent_hi != accent and not c.get("accent_light"):
        warn.append(f"accent {accent} was lightened/darkened to {accent_hi} for text legibility")
    return "\n".join(css), warn, t

# ---------------------------------------------------------------- fonts
def slug(family):
    return re.sub(r"[^a-z0-9]+", "-", family.lower()).strip("-")

def fetch_fontsource(family, dest, weights=(400, 500, 600, 700)):
    """Download a Google/open font from the npm registry (@fontsource). Returns list of (weight, path)."""
    tmp = tempfile.mkdtemp()
    try:
        r = subprocess.run(["npm", "pack", f"@fontsource/{slug(family)}", "--silent"], cwd=tmp,
                           capture_output=True, text=True, timeout=90)
        tgz = glob.glob(os.path.join(tmp, "*.tgz"))
        if r.returncode or not tgz:
            return []
        out = []
        with tarfile.open(tgz[0]) as tf:
            for w in weights:
                name = f"package/files/{slug(family)}-latin-{w}-normal.woff2"
                try:
                    m = tf.getmember(name)
                except KeyError:
                    continue
                p = os.path.join(dest, f"{slug(family)}-{w}.woff2")
                with tf.extractfile(m) as src, open(p, "wb") as dst:
                    dst.write(src.read())
                out.append((w, p))
        return out
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

def install_font(spec, fonts_dir):
    """spec: {'family': 'Space Grotesk', 'file': optional uploaded path}. Fills spec['files']."""
    os.makedirs(fonts_dir, exist_ok=True)
    if spec.get("file"):
        src = spec.pop("file")
        p = os.path.join(fonts_dir, os.path.basename(src))
        shutil.copy(src, p)
        spec["files"] = [{"weight": "100 900", "path": os.path.basename(p)}]
        return f"{spec['family']}: using uploaded file"
    got = fetch_fontsource(spec["family"], fonts_dir)
    if got:
        spec["files"] = [{"weight": w, "path": os.path.basename(p)} for w, p in got]
        return f"{spec['family']}: downloaded weights {', '.join(str(w) for w, _ in got)}"
    shutil.copy(os.path.join(SKILL_DIR, "assets", "fonts", "Inter.ttf"), os.path.join(fonts_dir, "Inter.ttf"))
    note = f"{spec['family']}: NOT FOUND as an open font. Using Inter. Ask for the font file (.ttf/.otf/.woff2)."
    spec["family"], spec["files"] = "Inter", [{"weight": "100 900", "path": "Inter.ttf"}]
    return note

def font_faces(b, brand_dir):
    css, seen = [], set()
    for role in ("heading", "body", "label"):
        f = b["fonts"][role]
        for fl in f.get("files", []):
            key = (f["family"], fl["path"])
            if key in seen:
                continue
            seen.add(key)
            path = os.path.join(brand_dir, "fonts", fl["path"])
            ext = os.path.splitext(path)[1].lower()
            fmt = {".woff2": "woff2", ".woff": "woff", ".otf": "opentype"}.get(ext, "truetype")
            data = base64.b64encode(open(path, "rb").read()).decode()
            css.append(f"@font-face{{font-family:'{f['family']}';src:url(data:font/{fmt};base64,{data}) format('{fmt}');"
                       f"font-weight:{fl['weight']};font-style:normal;font-display:block}}")
    return "\n".join(css)

# ---------------------------------------------------------------- logo / mark
def prep_image(src, dest_stem):
    """Copy an SVG as-is; trim transparent/flat padding on raster images and save as PNG."""
    ext = os.path.splitext(src)[1].lower()
    if ext == ".svg":
        dst = dest_stem + ".svg"
        shutil.copy(src, dst)
        return dst, None
    from PIL import Image, ImageChops
    im = Image.open(src).convert("RGBA")
    note = None
    if im.getextrema()[3][0] == 255:  # no transparency at all
        note = "logo has a solid background (no transparency). Ask for a transparent PNG or SVG, or turn on mascot.home_plate."
        bgc = Image.new("RGBA", im.size, im.getpixel((0, 0)))
        box = ImageChops.difference(im, bgc).getbbox()
    else:
        box = im.getchannel("A").getbbox()
    if box:
        im = im.crop(box)
    w, h = im.size
    side = max(w, h)
    sq = Image.new("RGBA", (side, side), (0, 0, 0, 0))
    sq.paste(im, ((side - w) // 2, (side - h) // 2))
    if side > 800:
        sq = sq.resize((800, 800), Image.LANCZOS)
    dst = dest_stem + ".png"
    sq.save(dst)
    return dst, note

def monogram(name, color, font_family, dest):
    letter = (name.strip() or "?")[0].upper()
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><text x="50" y="52" text-anchor="middle" '
           f'dominant-baseline="central" font-family="{font_family},sans-serif" font-weight="700" font-size="78" '
           f'fill="{color}">{letter}</text></svg>')
    open(dest, "w").write(svg)
    return dest

def data_uri(path):
    ext = os.path.splitext(path)[1].lower()
    mime = {".svg": "image/svg+xml", ".jpg": "image/jpeg", ".jpeg": "image/jpeg"}.get(ext, "image/png")
    return f"data:{mime};base64," + base64.b64encode(open(path, "rb").read()).decode()

def suggest(logo):
    from PIL import Image
    im = Image.open(logo).convert("RGBA")
    im.thumbnail((200, 200))
    data = im.get_flattened_data() if hasattr(im, 'get_flattened_data') else im.getdata()
    px = [p[:3] for p in data if p[3] > 200]
    if not px:
        print("no opaque pixels")
        return
    q = Image.new("RGB", (len(px), 1))
    q.putdata(px)
    pal = q.quantize(colors=6).convert("RGB").getcolors(len(px))
    for count, c in sorted(pal, reverse=True):
        print(f"{rgb2hex(c)}  {100 * count / len(px):.0f}%")

# ---------------------------------------------------------------- build
BACKDROPS = {
    "rays": '<div class="backdrop rays"><i style="left:0;width:70px;height:520px;opacity:.7"></i><i style="left:95px;width:40px;height:380px;opacity:.5"></i><i style="left:170px;width:60px;height:300px;opacity:.35"></i><i style="left:780px;width:30px;height:220px;opacity:.25"></i><i style="left:850px;width:60px;height:300px;opacity:.35"></i><i style="left:945px;width:40px;height:380px;opacity:.5"></i><i style="left:1010px;width:70px;height:520px;opacity:.7"></i></div>',
    "glow": '<div class="backdrop glow"></div>',
    "grid": '<div class="backdrop grid"></div>',
    "texture": '<div class="backdrop texture" style="background-image:url({{TEXTURE}})"></div>',
    "none": "",
}

def load(brand_dir):
    p = os.path.join(brand_dir, "brand.json")
    if not os.path.exists(p):
        sys.exit(f"No brand.json in {brand_dir}. Run brand setup first (SKILL.md Phase 0).")
    return json.load(open(p))

def build(brand_dir, content, css, title, alt, out):
    b = load(brand_dir)
    css_vars, warn, _ = tokens(b)
    footer = b.get("footer", {})
    if footer.get("wordmark"):
        foot = f'<div class="footer"><img alt="" src="{data_uri(os.path.join(brand_dir, footer["wordmark"]))}"></div>'
    elif footer.get("text"):
        handle = f'<span style="opacity:.6">{footer["handle"]}</span>' if footer.get("handle") else ""
        foot = f'<div class="footer"><div class="pill lbl">{footer["text"]}{handle}</div></div>'
    else:
        foot = ""
    html = open(os.path.join(SKILL_DIR, "assets", "base.html")).read()
    rep = {
        "{{TITLE}}": title, "{{ALT_TEXT}}": alt.replace('"', "&quot;"),
        "{{FONT_FACES}}": font_faces(b, brand_dir), "{{CSS_VARS}}": css_vars,
        "{{FORMAT_CSS}}": open(css).read() if css else "",
        "{{CONTENT}}": open(content).read(),
        "{{BACKDROP}}": BACKDROPS.get(b["style"].get("backdrop", "glow"), ""),
        "{{FOOTER}}": foot,
        "{{MARK_SRC}}": data_uri(os.path.join(brand_dir, b["mascot"]["mark"])),
    }
    st = b["style"]
    if st.get("backdrop") == "texture" and st.get("texture"):
        rep["{{BACKDROP}}"] = rep["{{BACKDROP}}"].replace("{{TEXTURE}}", data_uri(os.path.join(brand_dir, st["texture"])))
        rep["{{CSS_VARS}}"] += f"\n  --texture-opacity:{st.get('texture_opacity', .22)};"
        if st.get("texture_fade", "top") == "full":
            rep["{{BACKDROP}}"] = rep["{{BACKDROP}}"].replace('class="backdrop texture"', 'class="backdrop texture full"')
    for k, v in rep.items():
        html = html.replace(k, v)
    # brand images referenced in content/css as brand:filename.jpg get inlined
    def _img(m):
        path = os.path.join(brand_dir, "images", m.group(1))
        if not os.path.exists(path):
            print("BRAND NOTE: missing image", m.group(1))
            return m.group(0)
        return data_uri(path)
    html = re.sub(r"brand:([\w.\-]+\.(?:jpg|jpeg|png|svg))", _img, html)
    html = html.replace("{{EYEBROW}}", b.get("eyebrow", ""))
    open(out, "w").write(html)
    for w in warn:
        print("BRAND NOTE:", w)
    print("Built", out)

# ---------------------------------------------------------------- setup
def setup(a):
    d = a.brand_dir
    os.makedirs(os.path.join(d, "fonts"), exist_ok=True)
    p = os.path.join(d, "brand.json")
    b = json.load(open(p)) if os.path.exists(p) else {
        "name": "", "audience": "", "eyebrow": "",
        "colors": {}, "fonts": {"heading": {}, "body": {}, "label": {}},
        "style": {"backdrop": "glow", "label_case": "uppercase", "label_tracking": "3px", "radius": 16},
        "mascot": {"home_size": 130, "home_plate": False},
        "footer": {}, "voice": [],
    }
    notes = []
    if a.name: b["name"] = a.name
    if a.audience: b["audience"] = a.audience
    if a.eyebrow is not None: b["eyebrow"] = a.eyebrow
    for k in ("background", "text", "accent", "accent_light", "surface", "border", "plate"):
        v = getattr(a, k)
        if v: b["colors"][k] = v
    for role in ("heading", "body", "label"):
        fam, fil = getattr(a, f"{role}_font"), getattr(a, f"{role}_font_file")
        if fam or fil:
            spec = {"family": fam or os.path.splitext(os.path.basename(fil))[0], "weight": b["fonts"][role].get("weight", 600 if role == "heading" else 400)}
            if fil: spec["file"] = fil
            notes.append(install_font(spec, os.path.join(d, "fonts")))
            b["fonts"][role] = spec
    if a.heading_weight: b["fonts"]["heading"]["weight"] = a.heading_weight
    for role in ("body", "label"):  # default unset roles
        if not b["fonts"][role].get("family") and b["fonts"]["heading"].get("family"):
            b["fonts"][role] = dict(b["fonts"]["heading"], weight=400)
    if a.backdrop: b["style"]["backdrop"] = a.backdrop
    if a.label_case: b["style"]["label_case"] = a.label_case
    if a.radius is not None: b["style"]["radius"] = a.radius
    if a.home_size: b["mascot"]["home_size"] = a.home_size
    if a.home_plate is not None: b["mascot"]["home_plate"] = a.home_plate == "on"
    if a.mark:
        for old in glob.glob(os.path.join(d, "mark.*")):
            os.remove(old)
        dst, note = prep_image(a.mark, os.path.join(d, "mark"))
        b["mascot"]["mark"] = os.path.basename(dst)
        if note:
            notes.append(note)
    if not b["mascot"].get("mark"):
        fam = b["fonts"]["heading"].get("family", "Inter")
        b["mascot"]["mark"] = os.path.basename(monogram(b["name"], b["colors"].get("accent", "#333"), fam, os.path.join(d, "mark.svg")))
        notes.append("No logo mark given, so a monogram of the first letter is standing in.")
    if a.wordmark:
        dst, note = prep_image(a.wordmark, os.path.join(d, "wordmark"))
        b["footer"] = {"wordmark": os.path.basename(dst)}
    if a.footer_text is not None:
        b["footer"] = {"text": a.footer_text}
        if a.handle: b["footer"]["handle"] = "  " + a.handle
    for img in a.image or []:
        os.makedirs(os.path.join(d, "images"), exist_ok=True)
        from PIL import Image
        im = Image.open(img).convert("RGB")
        im.thumbnail((1400, 1400))
        name = slug(os.path.splitext(os.path.basename(img))[0]) + ".jpg"
        im.save(os.path.join(d, "images", name), quality=82)
        b.setdefault("images", [])
        if name not in b["images"]:
            b["images"].append(name)
        notes.append(f"image saved as brand:{name}")
    if a.texture:
        b["style"]["backdrop"] = "texture"
        b["style"]["texture"] = "images/" + slug(os.path.splitext(os.path.basename(a.texture))[0]) + ".jpg"
        if not os.path.exists(os.path.join(d, b["style"]["texture"])):
            notes.append("texture must also be passed with --image")
    if a.texture_opacity is not None: b["style"]["texture_opacity"] = a.texture_opacity
    if a.texture_fade: b["style"]["texture_fade"] = a.texture_fade
    for v in a.voice or []:
        b.setdefault("voice", []).append(v)
    if not os.path.exists(os.path.join(d, "learnings.md")):
        open(os.path.join(d, "learnings.md"), "w").write(f"# Learnings: {b['name'] or 'this brand'}\n\nOne-line rules from past edits. Newest at the bottom; a newer rule replaces an older one it contradicts.\n\n## Design\n\n## Copy\n\n## Animation\n")
    missing = [k for k in ("background", "text", "accent") if k not in b["colors"]]
    if missing:
        notes.append("Missing colors: " + ", ".join(missing))
    json.dump(b, open(p, "w"), indent=2)
    if not missing and b["fonts"]["heading"].get("family"):
        _, warn, t = tokens(b)
        notes += warn
        print("Derived palette:", json.dumps(t))
    for n in notes:
        print("NOTE:", n)
    print("Saved", p)

def package(skill_dir, brand_dir, out, slug_name):
    tmp = tempfile.mkdtemp()
    root = os.path.join(tmp, slug_name)
    shutil.copytree(skill_dir, root, ignore=shutil.ignore_patterns("__pycache__", "brand"))
    shutil.copytree(brand_dir, os.path.join(root, "brand"))
    skill_md = os.path.join(root, "SKILL.md")
    s = open(skill_md).read()
    s = re.sub(r"^name: .*$", f"name: {slug_name}", s, count=1, flags=re.M)
    bname = json.load(open(os.path.join(brand_dir, "brand.json"))).get("name", "")
    s = re.sub(r"^description: ", f"description: {bname}'s copy, brand already set up. ", s, count=1, flags=re.M)
    open(skill_md, "w").write(s)
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        for base, _, files in os.walk(root):
            for f in files:
                full = os.path.join(base, f)
                z.write(full, os.path.relpath(full, tmp))
    shutil.rmtree(tmp)
    print("Packaged", out)

def main():
    ap = argparse.ArgumentParser()
    sp = ap.add_subparsers(dest="cmd", required=True)
    s = sp.add_parser("suggest"); s.add_argument("--logo", required=True)
    s = sp.add_parser("setup")
    s.add_argument("--brand-dir", required=True)
    for k in ("name", "audience", "eyebrow", "background", "text", "accent", "accent_light", "surface", "border", "plate",
              "heading_font", "body_font", "label_font", "heading_font_file", "body_font_file", "label_font_file",
              "mark", "wordmark", "footer_text", "handle"):
        s.add_argument("--" + k.replace("_", "-"), dest=k, default=None)
    s.add_argument("--heading-weight", type=int)
    s.add_argument("--backdrop", choices=list(BACKDROPS))
    s.add_argument("--label-case", choices=["uppercase", "none"])
    s.add_argument("--radius", type=int)
    s.add_argument("--home-plate", choices=["on", "off"])
    s.add_argument("--home-size", type=int, help="px size of the mark at the top (default 130; wide marks can go to 170)")
    s.add_argument("--image", action="append", help="a brand photo/texture to keep; referenced in content as brand:<name>.jpg")
    s.add_argument("--texture", help="one of the --image files to use as the page backdrop")
    s.add_argument("--texture-opacity", type=float)
    s.add_argument("--texture-fade", choices=["top", "full"])
    s.add_argument("--voice", action="append", help="a copy rule from their guidelines; repeatable")
    s = sp.add_parser("build")
    for k in ("brand-dir", "content", "title", "alt", "out"):
        s.add_argument("--" + k, required=True)
    s.add_argument("--css")
    s = sp.add_parser("package")
    for k in ("skill-dir", "brand-dir", "out", "slug"):
        s.add_argument("--" + k, required=True)
    a = ap.parse_args()
    if a.cmd == "suggest": suggest(a.logo)
    elif a.cmd == "setup": setup(a)
    elif a.cmd == "build": build(a.brand_dir, a.content, a.css, a.title, a.alt, a.out)
    elif a.cmd == "package": package(a.skill_dir, a.brand_dir, a.out, a.slug)

if __name__ == "__main__":
    main()
