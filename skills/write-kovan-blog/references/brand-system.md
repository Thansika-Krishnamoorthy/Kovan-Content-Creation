# Kovan Labs blog brand system

Use this reference with `05 Brand Assets/design.md`, which remains authoritative. These notes capture how the supplied Newsletter, One-Pager, and Report templates translate the system into a long-form web article.

## Source files

- `05 Brand Assets/design.md`: binding tokens and rules.
- `05 Brand Assets/README.md`: approved asset purposes and restrictions.
- `Kovan Labs Newsletter.html`: compact web rhythm, Ink hero, Spark eyebrow, Mist notices, and dark footer.
- `Kovan Labs One-Pager.html`: compact Ink title band, structured cards, short labels, and restrained secondary accents.
- `Kovan Labs Report Template.html`: editorial hierarchy, generous whitespace, metadata treatment, tables, and dot-wave placement.

## Blog translation

- Use Poppins 600/700 only for headings and display text. Use Inter 400/500/600 for body, UI, metadata, and captions.
- Use Paper and Mist for most surfaces, Ink for the title band and footer, Body for prose, Grey for metadata, Cobalt for links, and Spark for the category and one key emphasis.
- Use the exact token values from `design.md`; do not revive legacy teal, blue-gradient banners, pure black, or off-token neutrals.
- Keep the top composition compact: a Paper logo bar followed by an Ink title band. Put category, title, and one-line summary in the title band.
- Use a maximum reading width near 760px and a wider 1200px alignment container for the brand bar/title band.
- Use the 4px spacing scale only: 4, 8, 12, 16, 24, 32, 48, 64, and 96px.
- Use 8px radii for controls and notices, 16px for editorial images, and only the subtle approved card shadow.
- Prefer thin Line borders and whitespace over boxed sections.
- Style tables with an Ink header, Line dividers, and alternating Mist rows. Keep them horizontally scrollable on small screens.
- Style important notes as Mist panels with a soft Spark and Amber glow. Style verified quotations separately with a soft Cobalt and Jade glow. Do not use a leading dark or colored rule on highlight panels.
- Style FAQs as Mist disclosure rows; use a border and subtle shadow only while expanded.

## Template selection

- Use `assets/blog-template.html` for a focused article with one central argument and a linear reading path.
- Use `templates/blog-volume-template.html` for a recurring volume, issue, digest or edition that gathers several related stories beneath one editorial theme.
- The volume layout uses a continuous Ink masthead with `logo_mono_white.png`, a volume marker, editorial introduction, sticky navigation, searchable category filters, perspectives grouped by maturity, cross-volume themes, FAQ, and optional previous/next volume navigation.
- Do not call the Kovan template “Technology Radar,” copy another company’s category names, reproduce a radar diagram, or reuse another company’s text, imagery, typography, colors, or branding.

## Approved asset selection

Use only files in `05 Brand Assets`; never recreate, recolor, crop, stretch, rotate, filter, or add effects.

- `logo_horizontal.png`: default top-left logo on Paper; minimum 120px wide.
- `logo_horizontal_tagline.png`: formal/sign-off contexts when the tagline adds value and does not duplicate nearby copy.
- `logo_mono_white.png`: dark backgrounds only when a second lockup is genuinely needed.
- `logo_mono_ink.png`: constrained single-color light-background uses.
- `logo_vertical.png` and `logo_vertical_tagline.png`: centered or narrow compositions, not the default blog header.
- `mark.png`: favicon or genuinely tight space at 24px or larger.
- `graphic_dotwave.png`: bright Paper/Mist section divider in full brand colour; do not use it as the standard dark-hero motif.
- `graphic_emblem.png`: an approach, people, collaboration, or growth section.
- `graphic_rings.png`: an optimistic closing or outcomes section.
- `graphic_spark.png`: the standard compact accent for the Ink hero, kept secondary to the title.

Use at most one busy motif in a viewport/composition. Every graphic from `05 Brand Assets` is decoration, not article content or evidence. Place it outside the semantic reading flow with empty alt text and `aria-hidden="true"`; never wrap it in `figure`, give it a caption, or use descriptive alt text. Genuine editorial images must come from user-provided or appropriately licensed non-brand sources.

Tables are optional components. Retain one only when a genuine comparison, decision matrix, dataset, or repeated-field mapping becomes clearer in rows and columns. Remove the entire table wrapper when prose or a short list communicates the idea just as well.

When a genuine editorial image is used, prefer a balanced two-column feature block: image on the left; verified quotation or concise key insight on a Mist panel to the right. Crop with `object-fit: cover` only for non-logo editorial photography or illustrations. Keep the source caption with the image and stack the image above the text panel on mobile. This treatment is optional and must be removed when the article has no suitable content image.

## Responsive and accessibility checks

- Preserve every logo and motif aspect ratio and its intrinsic width/height attributes.
- Keep official-logo clear space equal to one tile height; never place it on a busy motif.
- Maintain readable contrast according to `design.md`; Amber is never text on a light background.
- Keep the article readable at 320px, allow tables to scroll, expose keyboard focus, and honor reduced-motion preferences.
- If a remote font fails, retain the approved Segoe UI/system fallback chain.
