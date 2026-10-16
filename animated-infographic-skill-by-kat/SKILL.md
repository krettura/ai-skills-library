---
name: animated-infographic-skill-by-kat
description: Makes animated, on-brand LinkedIn infographics (looping GIF plus MP4 and still PNG) for any person or company. Sets up their brand once from a logo, colors, fonts, and brand guidelines, then turns their expertise into a teaching infographic where their logo hops through the content. Picks the best format for the idea (grid, bucket columns, steps, do-vs-don't layers, orbit, flow engine, phrase tree, modules-to-recipes, org structure), renders it, iterates on edits, and remembers them. Use whenever someone wants an infographic, a framework visual, an animated or looping graphic for LinkedIn, "something like that post," a branded visual explainer, or says "I want to create an infographic to teach..." even if they don't say infographic.
---

# Animated infographics (by Kat Rettura)

Turn someone's expertise into an animated LinkedIn infographic in their brand. Their logo mark starts big at the top, shrinks into a badge, hops through the content (each piece lights up as it lands), then flies home, so the GIF loops seamlessly.

**Questions:** use the multiple-choice question tool for every choice below when one is available (`ask_user_input_v0` or `AskUserQuestion`). Tappable answers are much faster than typing. Otherwise ask in one short message.

**Paths:** `<skill>` means this skill's folder. Work in `/home/claude/`. Deliver to `/mnt/user-data/outputs/` (or the session's outputs folder).

## Phase 0: Brand (once per brand)

Check for `<skill>/brand/brand.json`.
- **It exists:** copy `<skill>/brand/` to `/home/claude/brand/`, read `brand.json` and `learnings.md`, greet them by brand name, and go to Step 1.
- **It doesn't:** run setup below first.

### Setup
1. Ask for everything in one message (they can send it in pieces):
   > To make these in your brand, send me:
   > 1. Your logo. Ideally the icon/symbol on its own, as an SVG or transparent PNG. A full logo works too.
   > 2. Your brand colors, or your brand guidelines (PDF, link, or screenshot).
   > 3. Your fonts, if you know them.
   > 4. Who your posts are for, in a few words.
   > 5. Optional: photos or textures you use (paper, fabric, patterns).
   >
   > Only the logo and audience are required. I can pull colors from your logo.
2. Read `references/brand-setup.md`, then pull the brand out of what they sent. If they gave a website, fetch it and read colors and fonts from it. If they gave only a logo, run `brandkit.py suggest` and propose a palette.
3. Run `brandkit.py setup --brand-dir /home/claude/brand ...` and handle every NOTE it prints.
4. Show them the brand on a real example so they judge it in context:
   ```
   python3 <skill>/scripts/brandkit.py build --brand-dir /home/claude/brand \
     --content <skill>/assets/examples/matrix.content.html --css <skill>/assets/examples/matrix.css \
     --title "Brand preview" --alt "Brand preview" --out /home/claude/preview.html
   python3 <skill>/scripts/render.py /home/claude/preview.html --out /mnt/user-data/outputs --name brand-preview
   ```
   Deliver the GIF and ask: **How does the brand look?** Looks right / Adjust colors / Adjust fonts / Adjust the logo or mascot. Apply changes by rerunning `setup` with just the changed flags, re-render, ask again.
5. When they approve, save their own copy of the skill with the brand built in:
   ```
   python3 <skill>/scripts/brandkit.py package --skill-dir <skill> --brand-dir /home/claude/brand \
     --slug <brandname>-infographics --out /mnt/user-data/outputs/<brandname>-infographics.zip
   ```
   Deliver it and say in two lines: upload this zip in Settings > Capabilities > Skills (and remove the blank version) so future chats skip setup. Then continue to Step 1 in this chat if they have an idea ready.

## Step 1: Get the prompt

The entry point is:
> I want to create an infographic to teach **[who]** how to **[do what / solve what pain point]**.

If the message already covers it, move on. If not, show the template. Nothing else yet.

## Step 2: Clarify the shape

Ask up to three questions in one call. They map to a format, so don't skip them:
1. **What shape is this idea?** Steps in order / Types or categories to pick from / Right way vs wrong way / A system with parts that work together
2. **How many main pieces?** 3 to 5 / 6 to 9 / 10 or more
3. **What should the reader do after?** Save it as a reference / Follow it step by step / Rethink something they're doing wrong / Pick what fits them

Skip any the prompt already answers.

## Step 3: Get their expertise

Ask for the substance in one short message: their framework, notes, a past post, a doc, a voice memo transcript. Check uploaded and project files first and offer to use anything relevant.

The graphic is only as good as the thinking in it, and their audience follows them for their take. Use their structure and wording. If you fill gaps (example prompts in a grid, say), tell them which parts are yours.

## Step 4: Choose the format

Read `references/formats.md`, pick the format that fits the idea's shape, and tell them your choice plus the runner-up in one or two sentences. Build right away; the edit loop is where they react.

## Step 5: Build and render

1. Write two files:
   - `/home/claude/<slug>.content.html`: the content fragment. Start with `<div class="eyebrow lbl">{{EYEBROW}}</div>` (or a custom eyebrow) and a `<h1 class="headline">` with a second line in `<span class="accent">`. End with an optional one-line `.footnote`.
   - `/home/claude/<slug>.css`: layout rules for this format only.
   Look at `assets/examples/` first (matrix and steps are tested, working examples).
2. Rules for the fragment:
   - Give every element the mascot should visit `class="stop"` and `data-stop="1..n"` in visiting order. Cards that are stops also get `.card` so they light up.
   - To land the mascot on a specific spot (a step number, a node), give that element an `id` and the stop `data-anchor="#id"`. Otherwise `data-perch` picks a corner: `tr` (default), `tl`, `top`, `c`, `l`, `r`.
   - Use the brand variables (`--accent`, `--accent-hi`, `--text`, `--label`, `--muted`, `--card`, `--line`, `--bg`). Never hard-code a color or font, so it stays on brand.
   - Don't give content a `z-index` of 50 or more; the mascot must stay on top.
   - Follow the voice rules in `brand.json` and every rule in `learnings.md`.
3. Build: `python3 <skill>/scripts/brandkit.py build --brand-dir /home/claude/brand --content <slug>.content.html --css <slug>.css --title "..." --alt "..." --out /home/claude/<slug>.html`
4. Check layout: `python3 <skill>/scripts/render.py /home/claude/<slug>.html --qa-only --out /home/claude/qa`, then view the still. Fix every problem it reports and anything cramped. Cut words before shrinking text.
5. Render: `python3 <skill>/scripts/render.py /home/claude/<slug>.html --out /mnt/user-data/outputs --name <slug>`. It keeps the GIF under LinkedIn's 5 MB and 400-frame limits.
6. Before delivering, confirm the animation works. The mascot is the signature, and a hidden or static mascot is the most common silent failure:
   - The mascot check must show one landing per stop and no MASCOT problems.
   - View the filmstrip it saves and confirm the mascot starts big at the top, hops through the stops, and returns home.
7. Deliver the GIF, MP4, and still, GIF first. Add at most three short lines: the format, anything you wrote that they should check, and the posting tip (upload the GIF with LinkedIn's photo button so it loops; the video button freezes it).

## Step 6: Edit loop

Right after delivering, ask: **Want to change anything?** Copy edits / Design edits / Both / Looks good, ship it

For edits, take what they said (or ask once), apply everything in one pass, rebuild, re-render, deliver, and ask again. Keep edits surgical. Brand-level changes (a color, a font, the mascot) go through `brandkit.py setup`, not the fragment.

## Step 7: Remember what changed

When they ship, turn each edit from this session into a one-line rule in `/home/claude/brand/learnings.md`, phrased to apply to future infographics ("Keep card copy under 8 words," not "changed card 3"). Skip one-off content fixes. If a new rule contradicts an old one, replace the old one.

If anything changed in `brand/` (learnings or brand settings), skill files can't update themselves, so repackage with the Phase 0 `package` command and deliver the zip with one line: re-upload this in Settings > Capabilities > Skills so the next infographic starts with these changes.
