# Format library

Nine infographic formats, each matched to the shape of idea it teaches best. Pick by the idea's structure, not by what looks coolest. Every format uses the same brand shell and mascot engine; only the content fragment and its CSS change. Use CSS variables (`--accent`, `--accent-hi`, `--card`, `--line`, `--text`, `--label`, `--muted`, `--bg`) and never hard-code colors, so every format works for any brand, light or dark.

## Contents
1. Quick picker
2. The nine formats (what it is, best for, limits, mascot path, layout recipe)
3. Legibility limits that apply to all formats

---

## 1. Quick picker

| If the idea is... | Use | Runner-up |
|---|---|---|
| Two dimensions crossed (type × topic, role × situation) | `matrix` | `funnel-columns` |
| A few categories to rotate, each with templates or examples | `funnel-columns` | `matrix` |
| Reusable parts recombined into several outputs | `module-recipes` | `flow-engine` |
| The right way vs the wrong way, at several levels | `split-layers` | `branch-builder` |
| Layers that build inward to one payoff | `orbit-core` | `split-layers` |
| One source feeding parallel lanes that converge on an outcome | `flow-engine` | `module-recipes` |
| Who owns what in a team, stack, or system | `org-structure` | `flow-engine` |
| Mix-and-match choices, phrase banks, "pick 1 to 3" | `branch-builder` | `funnel-columns` |
| Steps in order | `step-sequence` | `orbit-core` |

Signal words in the user's idea: "steps / process / first, then" → step-sequence. "Mistakes / myths / what works vs doesn't" → split-layers. "Engine / flywheel / system" → flow-engine. "Templates / prompts / buckets / mix" → funnel-columns. "Framework with layers / foundation / builds to" → orbit-core. "Same parts, different versions" → module-recipes. "Options / choose / variations" → branch-builder. "Team / roles / org / stack" → org-structure. "For each X, do Y" → matrix.

---

## 2. The nine formats

### `matrix`: Two-axis grid
Reference: "How to get post ideas" grid. Tested: `assets/examples/matrix.content.html` + `matrix.css`.
- **Best for:** two independent dimensions where every combination is meaningful. Each cell holds one concrete prompt, example, or rule.
- **Examples:** post formats × content pillars; seniority × interview question type; meeting type × what to prepare.
- **Needs:** 2 to 5 columns, 2 to 5 rows, one short line per cell (max ~60 characters).
- **Mascot path:** snake through cells (row 1 left to right, row 2 right to left, and so on).
- **Layout:** CSS grid, `grid-template-columns: 150px repeat(N,1fr)`, header row of `.label`, row heads `.rowlabel` + `.sublabel`, cells `.card.stop`.

### `funnel-columns`: Buckets with prompt cards
Reference: "How to Post 5x a Week" (Magali De Reu).
- **Best for:** 2 to 4 categories the reader rotates between, each with a short definition, a frequency or ratio, the reaction it should create, and a stack of fill-in-the-blank templates underneath.
- **Examples:** content mix for a LinkedIn audience; types of networking messages; kinds of 1:1 topics.
- **Needs:** per column: name, 2 to 3 bullet description, ratio, 3 to 5 templates.
- **Mascot path:** down column 1's cards, then column 2, then column 3. Headers are not stops.
- **Layout:** flex row of columns. Header block uses a tapered shape (`clip-path: polygon(0 0,100% 0,92% 100%,8% 100%)`) in `--card-on` with a `--accent` border. Cards below joined by a 3px `--line` vertical connector.

### `module-recipes`: Modules to recipes tree
Reference: "How to Build 5 Landing Pages With 7 Evergreen Modules" (Tas Bober).
- **Best for:** a fixed set of reusable building blocks that recombine into several different outputs. Teaches "you don't start from scratch."
- **Examples:** 6 story blocks → 4 interview answers; 5 post parts → 4 post types; resume sections → 3 role targets.
- **Needs:** 4 to 7 modules, 3 to 5 recipes, each recipe listing its modules in order. Mark special or recipe-only modules in `--accent-hi` outline.
- **Mascot path:** each module left to right, then each recipe column header.
- **Layout:** top row of numbered module tiles; SVG bracket connectors (`.connector`); bottom row of recipe columns, each a stack of small chips repeating module names.

### `split-layers`: This works vs this won't, layered
Reference: "The 5 Layers Behind Effective OKR Execution."
- **Best for:** myth-busting and anti-patterns. A layered model where each layer has a good version (left) and a failure version (right).
- **Examples:** layers of a strong LinkedIn profile; what separates good vs bad async updates; career conversations with your manager.
- **Needs:** 3 to 5 layers, each with a name, a 2 to 4 word subtitle, 2 to 3 "works" chips and 2 to 3 "doesn't" chips.
- **Mascot path:** layer badges from the outermost to the core (or top to bottom).
- **Layout:** half-arcs drawn as SVG concentric semicircles. Left half tinted `--accent` at low opacity, right half `--muted` gray. Layer name badges on the center line are the `.stop`s. Chips sit on each side. Labels "This works." / "This won't." at top left and right.

### `orbit-core`: Concentric rings to a payoff
Reference: "How to Write a 'Mic Drop' Strategic Narrative" (Josh Lowman).
- **Best for:** an argument or strategy built outside-in, where each layer narrows toward one outcome at the center.
- **Examples:** building a personal brand from POV to proof; how a promo case builds; storytelling for a product demo.
- **Needs:** 4 to 6 rings, each with a name and 3 to 6 tiny keywords. One core label.
- **Mascot path:** ring names from outer to inner, landing on the core last. Set `data-perch="c"` on ring names.
- **Layout:** SVG dashed circles sharing a bottom tangent point, glowing `--accent` radial core. Ring names in Inter 600, keywords in `.mono` uppercase at 16 to 18px.
- **Caution:** keyword text is small. Cap at about 24 keywords total.

### `flow-engine`: Source, lanes, outcome
Reference: "How to Create a People-Generated Content Engine."
- **Best for:** systems where one input feeds several parallel lanes (personas, channels, stages), each compared on the same attributes, converging into one result.
- **Examples:** how referrals, content, and community each feed your job search; three kinds of mentors and what each is for.
- **Needs:** a top bar with 3 to 5 input chips, 2 to 4 lanes each with the same 2 to 3 attribute headings, a bottom bar with 3 to 5 outcome chips.
- **Mascot path:** top bar, each lane, bottom bar.
- **Layout:** stacked flex: top `.card` with chips, SVG down-arrows, lane columns as `.card.stop`, arrows, bottom `.card.stop`.

### `org-structure`: Nested containers
Reference: "The AI-First Marketing Org Chart" (Lisa Cole).
- **Best for:** who owns what. Team designs, tool stacks, how work gets routed.
- **Examples:** your personal AI stack; how a product trio splits decisions; a one-person content team with AI helpers.
- **Needs:** 2 to 3 levels, max about 16 boxes total. The reference is too dense for a feed post, so simplify hard.
- **Mascot path:** top level first, then each group container.
- **Layout:** outlined containers (`border:2px solid var(--line)`, 20px radius) holding `.card` tiles; the group containers are the `.stop`s.

### `branch-builder`: Phrase tree
Reference: "How to Build Your Signature Writing Style" (Karen Kluss).
- **Best for:** mix-and-match choices. A root with branches of options the reader picks from.
- **Examples:** ways to open a cold DM; how to frame a career gap; closing lines for a post.
- **Needs:** 2 to 3 trees, each with a root chip and 3 to 7 branch chips (a branch can split once).
- **Mascot path:** each root chip, then down its branches.
- **Layout:** panels as `.card`; inside, a vertical 3px `--line` trunk with horizontal arrows into `.chip`s. Root chip filled `--accent`.

### `step-sequence`: Numbered steps along a path
Reference: "How to Create Content IP." Tested: `assets/examples/steps.content.html` + `steps.css`.
- **Best for:** a process in order. How-tos, playbooks, routines.
- **Examples:** your first 30 days of posting; turning a work win into a post; prepping for a hiring manager screen.
- **Needs:** 3 to 7 steps, each with a short title and one line of detail.
- **Mascot path:** step 1 to the last step.
- **Layout (pick one):** a vertical timeline (tested): each row is a `.marker` number circle with an `id` plus a `.card.stop` carrying `data-anchor="#that-id"`, joined by a 3px `--line` spine. The mascot lands on each number and the number fills with the accent color as it's revealed. For 3 to 5 steps a horizontal row of numbered tiles also works; for 4 to 7 steps a winding SVG path with alternating cards is the showier option.

---

## 3. Legibility limits (all formats)

Canvas is 1080×1350 and gets viewed on phones at roughly 40% size, so:
- Body text 20px minimum, card text 22px preferred. Keywords in orbit/split formats 16px minimum and used sparingly.
- One idea per card, about 60 characters max.
- 24 stops max (keeps the GIF under 400 frames). 8 to 16 is the sweet spot.
- Headline max 2 lines. Line 1 white, line 2 in `.accent`.
- If QA flags overflow, cut words before shrinking type.
