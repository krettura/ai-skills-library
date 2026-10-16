# Brand setup guide

How to turn whatever the user hands you into `brand/brand.json`. Run this once per brand. Every later infographic reuses it.

## What to collect

| Item | Required | Accepts | If missing |
|---|---|---|---|
| Brand name | yes | text | ask |
| Logo mark (the icon that hops) | strongly preferred | SVG best, transparent PNG ok | monogram of the first letter in the accent color |
| Wordmark for the footer | optional | SVG/PNG | footer pill with the brand name as text |
| Colors: background, text, accent | yes | hex codes, a brand guide PDF, a website, or just the logo | run `brandkit.py suggest --logo` and propose a palette |
| Fonts: heading, body, label | optional | font names or font files | Inter for all three |
| Audience (who the posts are for) | yes | one line | ask; it becomes the eyebrow default |
| Voice rules | optional | brand guidelines, do/don't lists | none |

## Reading brand guidelines
A brand guide (PDF, Notion page, website) usually has everything. Pull:
- **Colors:** pick ONE background, ONE text color, ONE accent. Infographics with more than one accent look busy. Put a second brand color in `accent_light` only if it reads well as text on the background.
- **Fonts:** the display/headline font is `heading`, the paragraph font is `body`. For `label` (small caps labels, numbers, eyebrow) use the brand's mono or secondary font if it has one, otherwise reuse the body font.
- **Voice:** copy 3 to 6 concrete rules into `--voice` ("sentence case headlines," "never say 'synergy'"). Skip vague ones ("be authentic").
- **Radius / shape:** sharp-cornered brands → `--radius 4`; soft brands → 16 to 24.

## Choosing the backdrop
- `rays`: dramatic vertical light beams from the top. Dark, techy, cinematic brands.
- `glow`: soft accent glow behind the headline. Safe default for most brands.
- `grid`: faint graph paper fading down. Builders, design, editorial, light brands.
- `none`: flat. Minimal or very busy logos.
- `texture`: one of their own images (paper, fabric, stripes, sky) behind the top of the canvas at low opacity. Pass it with `--image FILE --texture FILE`, tune with `--texture-opacity .12 to .25`. Keep it subtle; busy textures fight the text.

## Brand images
Photos and textures they send go in with `--image` (repeatable). They're saved to `brand/images/` and used in content as `<img class="photo" src="brand:name.jpg">`, which the build inlines. Good use: one image per card or section that matches its meaning. Don't put text on top of photos.

## Mascot rules
The brand mark is the signature of every infographic: big at the top, shrinks into a badge, hops through the content, flies home.
- The badge is a circle in the background color with an accent ring. The mark sits inside at 60%.
- If the mark disappears against the background (dark mark on a dark background, or a logo with a solid box behind it), use `--plate "#ffffff"` (or another contrasting color) and `--home-plate on` so it always sits on a plate.
- The mark sits at 130px at the top by default. A wide, short mark can go to `--home-size 170`. Check the preview: it must not touch the eyebrow line.
- Wide logos (wordmarks) look tiny as a mascot. Ask for the icon/symbol version. If there isn't one, cut a distinctive letter out of the wordmark (keep the transparent cutout) and use that as the mark, with the full wordmark in the footer via `--wordmark`. Fall back to the monogram only if that doesn't read.

## Commands
```
python3 <skill>/scripts/brandkit.py suggest --logo LOGO.png
python3 <skill>/scripts/brandkit.py setup --brand-dir /home/claude/brand \
  --name "Acme" --audience "first-time managers" --eyebrow "For new managers" \
  --background "#0b0b10" --text "#ffffff" --accent "#ff5a36" \
  --heading-font "Space Grotesk" --body-font "Inter" --label-font "JetBrains Mono" \
  --mark logo-icon.svg --footer-text "ACME" --handle "@acme" --backdrop glow \
  --voice "Sentence case headlines" --voice "No exclamation points"
```
`setup` can be rerun with only the flags that change. Fonts download automatically for any open font (Google Fonts catalog). For a paid or custom font, ask for the file and pass `--heading-font-file path.otf`.

Read the NOTE lines it prints. They tell you about missing colors, fonts it couldn't find, low contrast, and logos with solid backgrounds. Fix or tell the user about each one.
