#!/usr/bin/env python3
"""Render a brand infographic HTML file into a looping GIF, an MP4 and a still PNG.

Usage:
  python3 render.py path/to/infographic.html --out /mnt/user-data/outputs --name my-infographic
  python3 render.py path/to/infographic.html --qa-only      # layout check + preview PNG, no video

The HTML must be built from assets/base.html (it exposes window.__render / __still / __qa).
"""
import argparse, asyncio, glob, os, shutil, subprocess, sys, tempfile

SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FPS_RENDER = 30
GIF_MAX_BYTES = 4_800_000   # LinkedIn caps GIFs at 5 MB
GIF_MAX_FRAMES = 390        # LinkedIn freezes GIFs past roughly 400 frames


def install_fonts():
    dst = os.path.expanduser("~/.fonts")
    os.makedirs(dst, exist_ok=True)
    for f in glob.glob(os.path.join(SKILL_DIR, "assets", "fonts", "*")):
        target = os.path.join(dst, os.path.basename(f))
        if not os.path.exists(target):
            shutil.copy(f, target)
    subprocess.run(["fc-cache", "-f"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def find_chrome():
    for pattern in ["/opt/pw-browsers/chromium-*/chrome-linux/chrome",
                    os.path.expanduser("~/.cache/ms-playwright/chromium-*/chrome-linux/chrome")]:
        hits = sorted(glob.glob(pattern))
        if hits:
            return hits[-1]
    return None  # let Playwright use its default


async def capture(html, frames_dir, still_path, qa_only):
    from playwright.async_api import async_playwright
    async with async_playwright() as p:
        exe = find_chrome()
        browser = await p.chromium.launch(**({"executable_path": exe} if exe else {}))
        page = await browser.new_page(viewport={"width": 1080, "height": 1350})
        await page.goto("file://" + os.path.abspath(html) + "?export")
        await page.evaluate("window.__ready")
        problems = await page.evaluate("window.__qa()")
        total = await page.evaluate("window.__total")
        # Mascot check: confirm the hopper really travels to every stop (catches a silent, static animation).
        hops = await page.evaluate("window.__mascotCheck()")
        spots = {(h["x"] // 20, h["y"] // 20) for h in hops}
        if not hops:
            problems.append("MASCOT: no stops, so the mascot never leaves home")
        elif len(spots) < len(hops):
            problems.append("MASCOT: two stops share a landing spot, so a hop is invisible. Check data-perch / data-anchor")
        elif not all(h["visible"] for h in hops):
            problems.append("MASCOT HIDDEN at stops " + ", ".join(str(h["stop"]) for h in hops if not h["visible"]) + ": something is painted on top of it (check z-index)")
        elif any(h["x"] < 0 or h["x"] > 1080 or h["y"] < 0 or h["y"] > 1350 for h in hops):
            problems.append("MASCOT: a landing spot is off the canvas")
        print(f"Mascot check: {len(hops)} landings at", ", ".join(f"({h['x']},{h['y']})" for h in hops))
        await page.evaluate("window.__still()")
        await page.screenshot(path=still_path)
        n = 0
        if not qa_only:
            n = int(total / 1000 * FPS_RENDER)
            for f in range(n):
                await page.evaluate(f"window.__render({f * 1000 / FPS_RENDER})")
                await page.screenshot(path=os.path.join(frames_dir, f"f{f:04d}.png"))
        await browser.close()
        return problems, total, n


def filmstrip(frames_dir, n, out):
    """8 evenly spaced frames side by side, for Claude to eyeball the motion before delivering."""
    if n < 8:
        return None
    idx = [int(i * (n - 1) / 7) for i in range(8)]
    inputs = []
    for i in idx:
        inputs += ["-i", os.path.join(frames_dir, f"f{i:04d}.png")]
    ffmpeg(*inputs, "-filter_complex",
           "".join(f"[{k}:v]scale=270:-1[s{k}];" for k in range(8)) + "".join(f"[s{k}]" for k in range(8)) + "hstack=inputs=8",
           out)
    return out


def ffmpeg(*args):
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", *args], check=True)


def make_gif(frames_dir, out, duration_s):
    fps = 15
    while duration_s * fps > GIF_MAX_FRAMES and fps > 8:
        fps -= 1
    for colors in (128, 96, 64):
        vf = (f"fps={fps},split[a][b];[a]palettegen=max_colors={colors}:stats_mode=diff[p];"
              f"[b][p]paletteuse=dither=bayer:bayer_scale=4:diff_mode=rectangle")
        ffmpeg("-framerate", str(FPS_RENDER), "-i", os.path.join(frames_dir, "f%04d.png"), "-vf", vf, "-loop", "0", out)
        if os.path.getsize(out) <= GIF_MAX_BYTES:
            return fps, colors
    return fps, colors


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("html")
    ap.add_argument("--out", default="/mnt/user-data/outputs")
    ap.add_argument("--name", default=None)
    ap.add_argument("--qa-only", action="store_true")
    a = ap.parse_args()
    name = a.name or os.path.splitext(os.path.basename(a.html))[0]
    os.makedirs(a.out, exist_ok=True)
    frames = tempfile.mkdtemp(prefix="g95frames_")
    still = os.path.join(a.out, f"{name}-still.png")
    problems, total, n = asyncio.run(capture(a.html, frames, still, a.qa_only))

    print(f"Loop length: {total/1000:.1f}s")
    if problems:
        print("LAYOUT PROBLEMS (fix before posting):")
        for pr in problems[:30]:
            print("  -", pr)
    else:
        print("Layout QA: clean")
    print("Still:", still)
    if a.qa_only:
        return

    mp4 = os.path.join(a.out, f"{name}.mp4")
    gif = os.path.join(a.out, f"{name}.gif")
    ffmpeg("-framerate", str(FPS_RENDER), "-i", os.path.join(frames, "f%04d.png"), "-c:v", "libx264",
           "-pix_fmt", "yuv420p", "-crf", "18", "-preset", "slow", "-movflags", "+faststart", mp4)
    strip = filmstrip(frames, n, os.path.join("/home/claude", f"{name}-filmstrip.png"))
    if strip:
        print("Filmstrip (view this to confirm the mascot hops before delivering):", strip)
    fps, colors = make_gif(frames, gif, total / 1000)
    size = os.path.getsize(gif)
    print(f"GIF: {gif}  ({size/1e6:.2f} MB, {int(total/1000*fps)} frames @ {fps}fps, {colors} colors)")
    if size > GIF_MAX_BYTES:
        print("WARNING: GIF is over LinkedIn's 5 MB limit. Cut stops or shorten the loop.")
    print("MP4:", mp4)
    shutil.rmtree(frames, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
