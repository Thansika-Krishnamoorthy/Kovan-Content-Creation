# Kovan Labs — Brand Design System (`design.md`)

> **Purpose.** This is the authoritative brand and design specification for **automated agents** (LLMs, coding agents, design/codegen tools). When generating *any* Kovan Labs artifact — website, app UI, slide deck, document, email, social post, illustration, or copy — treat the tokens and rules below as **binding constraints**.
>
> **Conflict rule.** If a user instruction conflicts with this file, follow the brand rules — unless the user *explicitly* overrides a specific rule. Never silently drift.
>
> **Source of truth precedence:** machine-readable tokens (§11–§12) > tables in this doc > prose. If anything here is ambiguous, prefer the most conservative on-brand choice.

---

## 0. Agent quick-start

1. Load §11 (`tokens.json`) and/or §12 (CSS / Tailwind) into your working context before producing output.
2. **Type:** headings/display = **Poppins**; body/UI = **Inter**. Never substitute without a fallback chain (§4).
3. **Color:** exactly one primary accent — **Spark `#F14924`**. Backgrounds default to **paper/mist**; text defaults to **Ink/body**. Secondary accents (Amber, Jade, Cobalt) are used sparingly and never all at once. See proportion rule §3.
4. **Logo:** use only approved files (§13); never recolor, rotate, or distort (§5).
5. **Tone:** clear, confident, human, forward-looking (§10).
6. Validate every output against the **MUST / SHOULD / NEVER** ruleset in §14 before returning it.

---

## 1. Brand essentials

| Field | Value |
|---|---|
| Name | **Kovan Labs** |
| Tagline | **Unlocking Potential Through Technology.** |
| Essence | Technology that turns potential into outcomes. |
| Personality | Precise, optimistic, human, modern. Engineering rigor without coldness. |
| Wordmark | "Kovan Labs" set in Poppins. "Kovan" is the lead; "Labs" is the qualifier. |

---

## 2. Color — tokens

### Core palette
| Token | Hex | Name | Primary role |
|---|---|---|---|
| `spark` | `#F14924` | Spark (orange-red) | **Primary accent.** CTAs, key highlights, brand moments. |
| `amber` | `#FFBE00` | Amber (yellow) | Secondary accent. Energy, highlights, data. **Pair with Ink text only.** |
| `jade` | `#00A86B` | Jade (green) | Secondary accent. Growth, success, data. |
| `cobalt` | `#0066A4` | Cobalt (blue) | Secondary accent. Trust, links, data. |
| `ink` | `#090C08` | Ink (near-black) | Primary dark surface + high-emphasis text. Use **instead of pure `#000`.** |

### Neutrals
| Token | Hex | Name | Role |
|---|---|---|---|
| `paper` | `#FFFFFF` | Paper | Default background. |
| `mist` | `#F4F5F4` | Mist | Subtle surface / section fill. |
| `field` | `#EDEEEC` | Field | Inputs, secondary surfaces. |
| `line` | `#D9DCD7` | Line | Borders, dividers, hairlines. |
| `grey` | `#5A5F58` | Grey | Secondary / muted text (passes contrast on light). |
| `greyl` | `#9AA09A` | Grey Light | Disabled text, decorative only — **not for body text.** |
| `body` | `#1A1C19` | Body | Default body-text color on light backgrounds. |

### Semantic mapping (use these names in code)
| Semantic | Maps to |
|---|---|
| `--color-primary` | `spark` |
| `--color-bg` | `paper` |
| `--color-surface` | `mist` |
| `--color-surface-2` | `field` |
| `--color-border` | `line` |
| `--color-text` | `body` |
| `--color-text-strong` | `ink` |
| `--color-text-muted` | `grey` |
| `--color-text-disabled` | `greyl` |
| `--color-dark-bg` | `ink` |
| `--color-on-dark` | `paper` |

---

## 3. Color — usage & pairing rules

**Proportion (60 / 30 / 10).** ~60% neutral (paper/mist), ~30% structural dark or supporting color (Ink), ~10% Spark accent. Spark is a seasoning, not a base. Never flood a layout with Spark.

**One primary, limited secondaries.** Spark is the only primary accent. Use **at most two** of {Amber, Jade, Cobalt} in a single composition, and only for data, illustration, or categorization — never as competing CTAs.

**Accessibility & pairing (text contrast on `#FFFFFF`):**
| Foreground | On white | Verdict for text |
|---|---|---|
| `ink` / `body` | ~16–20:1 | ✅ Body text (preferred). |
| `grey` | ~6.5:1 | ✅ Secondary text. |
| `cobalt` | ~5.8:1 | ✅ Text & links OK. |
| `spark` | ~3.7:1 | ⚠️ **Large/bold only** (≥24px, or ≥19px bold) and UI accents. Not for body text. |
| `jade` | ~2.8:1 | ⚠️ Large/bold display only. Prefer as a fill. |
| `amber` | ~1.7:1 | ⛔ **Never** as text on light. |
| `greyl` | ~2.6:1 | ⛔ Decorative/disabled only. |

**Text on colored fills:**
- On **Spark / Cobalt / Ink** → use **white (`paper`)** text. (White on Spark = large/bold/button labels; fine for UI.)
- On **Amber** → use **Ink** text, always.
- On **Jade** → use **Ink** text for small sizes; white only for large display.

**Dark mode / dark sections:** background = `ink` (`#090C08`), text = `paper`, accent = `spark` or `amber`. Keep Ink, not pure black.

**Do**
- Use Spark to draw the eye to the single most important action.
- Use neutrals to carry 90% of most layouts.

**Don't**
- Don't put Spark next to Red or use it for error states — define errors with a distinct utility red, not a brand color.
- Don't gradient-blend brand colors into muddy mid-tones.

---

## 4. Typography

| Role | Family | Weight | Notes |
|---|---|---|---|
| Display / Headings / Wordmark | **Poppins** | 600 (SemiBold), 700 for display | Geometric, confident. |
| Body / UI / Captions | **Inter** | 400 / 500 / 600 | Highly legible at small sizes. |

**Type scale — 1.25 (major third) modular scale, base 16px:**
| Step | Size (px) | Suggested use |
|---|---|---|
| `display` | 61 | Hero display |
| `h1` | 49 | Page title |
| `h2` | 39 | Section heading |
| `h3` | 31 | Sub-section |
| `h4` | 25 | Card / block title |
| `lead` | 20 | Lead paragraph / large body |
| `body` | 16 | Default body |
| (caption) | 13 | Captions/labels (derived: 16 ÷ 1.25) |

**Rules**
- Line-height: headings ~1.1–1.2; body ~1.5–1.6.
- Letter-spacing: tighten display/headings slightly (−0.01em to −0.02em); body 0. Eyebrows/labels: UPPERCASE, +0.06em to +0.1em tracking.
- Casing: Sentence case for headings and most UI. UPPERCASE only for short eyebrows/labels. Avoid ALL-CAPS paragraphs.
- Never use Poppins for long body copy; never use Inter for the wordmark.

**Fallback stacks**
```css
--font-display: "Poppins", "Segoe UI", system-ui, -apple-system, Arial, sans-serif;
--font-body:    "Inter", "Segoe UI", system-ui, -apple-system, Arial, sans-serif;
```
**Web sources:** Poppins & Inter via Google Fonts (`fonts.google.com`) or self-host. Load weights: Poppins 600/700; Inter 400/500/600.

---

## 5. Logo & mark

**The mark** is a four-tile geometric **"K"** built from brand colors:
- **Top-left:** Spark `#F14924` triangle
- **Center:** Jade `#00A86B` triangle
- **Bottom-left:** Cobalt `#0066A4` triangle
- **Right:** Amber `#FFBE00` rectangle

The tiles read as a "K" and encode the four brand colors. The wordmark "Kovan Labs" is set in Poppins.

**Variants (use approved files only — §13):**
- Horizontal lockup (mark + wordmark) — default.
- Vertical lockup (mark over wordmark) — square/centered contexts.
- Tagline lockups (horizontal/vertical + "Unlocking Potential Through Technology.").
- Mark only — avatars, favicons, app icons, tight spaces.
- **Monochrome:** single-color Ink (on light) and single-color White (on dark). Use only when full color is not possible.

**Clear space:** keep a minimum margin equal to the height of one mark tile on all sides. Nothing intrudes.

**Minimum size:** horizontal lockup ≥ 120px wide on screen (≥ 24mm print); mark ≥ 24px. Below that, switch to mark-only.

**Placement:** prefer top-left or centered. On busy imagery, place on a solid Ink/paper panel or use the monochrome variant.

**NEVER:** recolor the tiles · rotate/skew/stretch · add shadows/glows/outlines · change tile proportions · place full-color logo on low-contrast/clashing backgrounds · reconstruct the logo from scratch when an approved asset exists · use the old/teal template colors.

---

## 6. Spacing, grid & radius

**Spacing scale (4px base):** `4, 8, 12, 16, 24, 32, 48, 64, 96` px. Compose layouts from these steps only.

**Radius:** `sm 4px` (inputs, chips) · `md 8px` (buttons, small cards) · `lg 16px` (cards, panels) · `pill 999px` (tags, avatars). Keep corner treatment consistent within a surface.

**Grid:** 12-column, 24px gutters, max content width ~1200–1280px. Generous whitespace — the brand reads clean and engineered, not dense.

**Elevation:** subtle only. Shadow example: `0 2px 8px rgba(9,12,8,0.08)`. Avoid heavy/colored drop shadows.

---

## 7. Graphic language (motifs & patterns)

A small kit of geometric motifs derived from the mark. Use as supporting texture — never louder than content.

| Motif | What it is | Use |
|---|---|---|
| **Emblem** | Geometric growth/illustration anchored in Ink | Editorial/explainer accents, "approach" sections. |
| **Dot-wave** | Clean 4-color halftone dot pattern (sine wave) | Background texture, dividers, hero fills (low opacity). |
| **Rings / Ripple** | Concentric Amber rings + Spark sparkle field | Expansive/optimistic moments, closing slides, covers. |
| **Spark(le)** | Single Spark 4-point starburst | Small highlight / emphasis accent. |

**Rules:** keep motifs to the brand palette; use at low density and/or reduced opacity behind content; align to the grid; don't combine more than one busy motif per view; don't recolor outside the palette.

---

## 8. Iconography

Geometric, consistent stroke weight (~2px at 24px), rounded joints, minimal detail — echoing the mark's clean angularity. Single-color (Ink, or accent for emphasis). Avoid skeuomorphism, gradients within icons, or mixed icon families.

---

## 9. Imagery & illustration

- **Illustration is preferred** for brand moments: flat, geometric, palette-driven (the motif system).
- **Photography:** authentic, human, technology-forward; natural light; uncluttered. Subjects doing real work, not staged clip-art.
- **Avoid generic/holiday stock** (e.g., random drones, decorative "office" stock) — it reads off-brand. If no on-brand asset exists, prefer a clean motif or solid Ink/paper panel over filler stock.
- Apply a subtle Ink overlay if text must sit on a photo; maintain contrast.

---

## 10. Voice & tone

**Principles**
1. **Clear** — plain language, short sentences, no jargon for its own sake.
2. **Confident** — make a point; avoid hedging and filler.
3. **Human** — warm and direct; write to a person, not a market.
4. **Forward-looking** — frame around possibility and outcomes ("unlocking potential").

**Do:** lead with the benefit · use active voice · be specific · use "you/we."
**Don't:** overclaim/hype · stack buzzwords · use ALL-CAPS for emphasis · bury the point.

**Tagline usage:** "Unlocking Potential Through Technology." — title case, with the period. Use as a sign-off or hero support line; don't crowd it with other taglines.

**Micro-examples**
- CTA: "Get started" / "See how it works" — not "Click here."
- Headline: "Turn data into decisions." — not "Synergistic AI-driven solutions."

---

## 11. Tokens (`tokens.json`)

```json
{
  "color": {
    "spark":  "#F14924",
    "amber":  "#FFBE00",
    "jade":   "#00A86B",
    "cobalt": "#0066A4",
    "ink":    "#090C08",
    "paper":  "#FFFFFF",
    "mist":   "#F4F5F4",
    "field":  "#EDEEEC",
    "line":   "#D9DCD7",
    "grey":   "#5A5F58",
    "greyLight": "#9AA09A",
    "body":   "#1A1C19"
  },
  "semantic": {
    "primary": "#F14924",
    "bg": "#FFFFFF",
    "surface": "#F4F5F4",
    "surface2": "#EDEEEC",
    "border": "#D9DCD7",
    "text": "#1A1C19",
    "textStrong": "#090C08",
    "textMuted": "#5A5F58",
    "textDisabled": "#9AA09A",
    "darkBg": "#090C08",
    "onDark": "#FFFFFF"
  },
  "font": {
    "display": "Poppins",
    "body": "Inter",
    "weights": { "body": 400, "medium": 500, "semibold": 600, "bold": 700 }
  },
  "fontSize": {
    "caption": 13, "body": 16, "lead": 20, "h4": 25,
    "h3": 31, "h2": 39, "h1": 49, "display": 61
  },
  "lineHeight": { "heading": 1.15, "body": 1.55 },
  "space": [4, 8, 12, 16, 24, 32, 48, 64, 96],
  "radius": { "sm": 4, "md": 8, "lg": 16, "pill": 999 },
  "shadow": { "card": "0 2px 8px rgba(9,12,8,0.08)" }
}
```

---

## 12. Implementation snippets

### CSS custom properties
```css
:root {
  /* color */
  --color-spark:#F14924; --color-amber:#FFBE00; --color-jade:#00A86B;
  --color-cobalt:#0066A4; --color-ink:#090C08;
  --color-paper:#FFFFFF; --color-mist:#F4F5F4; --color-field:#EDEEEC;
  --color-line:#D9DCD7; --color-grey:#5A5F58; --color-grey-light:#9AA09A;
  --color-body:#1A1C19;
  /* semantic */
  --color-primary:var(--color-spark);
  --color-bg:var(--color-paper);
  --color-surface:var(--color-mist);
  --color-border:var(--color-line);
  --color-text:var(--color-body);
  --color-text-strong:var(--color-ink);
  --color-text-muted:var(--color-grey);
  /* type */
  --font-display:"Poppins","Segoe UI",system-ui,-apple-system,Arial,sans-serif;
  --font-body:"Inter","Segoe UI",system-ui,-apple-system,Arial,sans-serif;
  /* radius + shadow */
  --radius-sm:4px; --radius-md:8px; --radius-lg:16px; --radius-pill:999px;
  --shadow-card:0 2px 8px rgba(9,12,8,0.08);
}
body{ background:var(--color-bg); color:var(--color-text);
  font-family:var(--font-body); line-height:1.55; }
h1,h2,h3,h4{ font-family:var(--font-display); font-weight:600;
  color:var(--color-text-strong); line-height:1.15; }
.btn-primary{ background:var(--color-primary); color:var(--color-paper);
  border-radius:var(--radius-md); font-family:var(--font-body); font-weight:600; }
```

### Tailwind (`tailwind.config.js` → `theme.extend`)
```js
extend: {
  colors: {
    spark:"#F14924", amber:"#FFBE00", jade:"#00A86B", cobalt:"#0066A4",
    ink:"#090C08", paper:"#FFFFFF", mist:"#F4F5F4", field:"#EDEEEC",
    line:"#D9DCD7", grey:"#5A5F58", greyl:"#9AA09A", body:"#1A1C19",
  },
  fontFamily: {
    display:['Poppins','ui-sans-serif','system-ui','sans-serif'],
    body:['Inter','ui-sans-serif','system-ui','sans-serif'],
  },
  fontSize: {
    caption:'13px', base:'16px', lead:'20px',
    h4:'25px', h3:'31px', h2:'39px', h1:'49px', display:'61px',
  },
  borderRadius:{ sm:'4px', md:'8px', lg:'16px', pill:'999px' },
  boxShadow:{ card:'0 2px 8px rgba(9,12,8,0.08)' },
}
```

---

## 13. Asset manifest

Approved assets live in the **Brand Kit** (e.g., the SharePoint *Brand Kit* folder). Reference these rather than recreating.

| Category | Files | Use |
|---|---|---|
| Logos | `logo_horizontal`, `logo_vertical`, `*_tagline`, `mark` (+ `*_white`, `*_mono_ink`, `*_mono_white`) | Lockups for all contexts; mono/white for constrained or dark backgrounds. |
| Guidelines | `Kovan_Labs_Brand_Guidelines.docx` | Full human-readable spec (this file is its agent-facing distillation). |
| Templates | `Kovan_Labs_Deck_Template.pptx`, `Kovan_Labs_Document_Template.docx`, `Kovan_Labs_Email_Template.html`, `Kovan_Labs_Email_Signature.html` | Branded starting points for decks, letters, email. |
| Cards (print) | `Kovan_Labs_ID_Card.pdf`, `…_Business_Card.pdf`, `…_Device_Card.pdf`, `…_Parking_Permit.pdf` | Print-ready, on-brand. |
| Graphics | `Kovan_Labs_Graphic_{Emblem,DotWave,Ripple,Rings,Spark}.{png,svg}` (+ `…_Graphic_Assets_SVG.zip`) | Motif system (§7). SVG for scaling/recolor within palette. |

---

## 14. Agent ruleset — MUST / SHOULD / NEVER

**MUST**
- Use **Poppins** for headings/display and **Inter** for body/UI, with the fallback chains in §4.
- Use **Spark `#F14924`** as the single primary accent; keep it to ~10% of any composition.
- Use **Ink `#090C08`** (not `#000`) for dark surfaces and high-emphasis text; **`#1A1C19`** for body copy.
- Pull all colors, type, spacing, and radii from §11/§12 tokens — no off-token values.
- Pair **Amber** with **Ink** text only.
- Maintain logo clear space (= one tile height) and minimum sizes (§5).
- Meet contrast guidance in §3 for all text.

**SHOULD**
- Default to **paper/mist** backgrounds with **Ink/body** text.
- Limit accent colors to Spark + at most two secondaries per view.
- Prefer the motif system or solid panels over generic stock imagery.
- Write in the brand voice (§10); lead with the benefit.
- Use approved asset files (§13) rather than regenerating the logo/motifs.

**NEVER**
- Never recolor, rotate, distort, or add effects to the logo, or rebuild it when an approved file exists.
- Never use Amber (or Grey Light) for text on light backgrounds.
- Never use pure black `#000` or off-palette colors.
- Never set body copy in Poppins, or the wordmark in Inter.
- Never use ALL-CAPS for paragraphs, or stack buzzwords/hype.
- Never use the legacy template's teal or unrelated stock-photo aesthetic.

---

*Single source of truth for agents. If you change brand tokens, update §11–§12 first, then propagate.*
