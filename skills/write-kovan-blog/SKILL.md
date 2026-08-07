---
name: write-kovan-blog
description: Create, revise, SEO-optimize, and publish structured Kovan Labs blog articles on any supported agent or authoring platform, automatically selecting the conventional, volume-edition, or technology-radar HTML template from the title and brief. Coordinate with the seo-audit skill for search intent, on-page SEO, crawlability, metadata, internal linking, and content-quality checks. Use original, research-informed web writing with topic-specific headings, branded metadata, relevant images, optional comparisons, verified quotations, contextual links, FAQs, social links, and Kovan Labs copyright. Use when a user asks to write, optimize, revise, or publish a blog; build a blog page; populate a Kovan blog template; or convert an article draft into branded HTML. When the source is a Markdown file in this repository, first use the generate-blog-from-markdown skill for branch/path validation and Markdown intake.
---

# Write a Kovan Labs blog

## Workflow

When the user wants a blog from a Markdown file in this repository, use `skills/generate-blog-from-markdown/SKILL.md` first to validate the source branch and `.md` path, preserve the original Markdown, and resolve referenced images. Then continue with this skill's branded HTML workflow.

1. Read `/home/thansika/Documents/Content creation/05 Brand Assets/design.md` and `05 Brand Assets/README.md` before creating branded HTML. Treat `design.md` as the visual source of truth. Read `references/brand-system.md` for the blog-specific translation of the supplied Newsletter, One-Pager, and Report templates.
2. Gather or infer the title, one-line summary, author, publication date, category, purpose, background, main sections, FAQ items, and social links. Leave clear placeholders only when the missing value cannot be inferred safely.
3. Use `/home/thansika/Documents/Content creation/reference/blog_template.md` as the drafting structure when Markdown is useful or requested. Treat Markdown as an intermediate source, never as the only delivered format.
4. Choose exactly one of the three templates using the title-first rules below before drafting. Copy the chosen template to the requested output location, transfer the completed article into it, and replace every `{{PLACEHOLDER}}`; never edit a reusable template for one article.
5. Research current facts when the request needs them. Prefer authoritative primary sources. Link only claims, quotations, tools, or destinations for which verification or reader follow-up is genuinely useful; do not hyperlink every name or familiar term. Embed links naturally in the smallest meaningful phrase. Do not announce provenance with phrases such as “according to,” “taken from,” “source,” or “original post” unless that provenance is itself relevant to the story. Do not add unexplained bare URLs.
6. Before drafting, review successful current articles for the same topic and audience when browsing is available. Compare the headline promise, opening hook, section rhythm, paragraph length, evidence, examples, and ending. Apply shared editorial techniques in original Kovan Labs prose. Never claim an article is the “most read” without verifiable audience data, and never imitate a living writer's distinctive style.
7. Link references to earlier Kovan Labs articles directly to their local or published article URL. Check existing blog outputs before treating a phrase as plain text.
8. Treat files in `05 Brand Assets` as decorative brand motifs only. Never present them as editorial evidence, article illustrations, diagrams, screenshots, or captioned content images. Give decorative motifs empty alt text and `aria-hidden="true"`; position them outside the article’s semantic content flow. For genuine topic images supplied by the user or obtained from an appropriate licensed source, prefer the template’s two-column `media-quote` feature: image on the left and a verified quotation or key insight on a Mist panel to the right, stacked image-first on mobile. Use useful alt text, source attribution, and a caption when required. Remove the complete feature when no genuine image is needed.
9. Tables are optional. Include a comparison or data table only when rows and columns make the information materially easier to understand than prose or a short list. Otherwise remove the complete table section from the generated HTML. Keep included cells concise and make the table horizontally scrollable on mobile.
10. Render quotations with `blockquote`; render important non-quotation guidance with the highlighted note component. Copy every attributed quotation verbatim from its source, preserving the speaker's exact wording. Do not rewrite, polish, correct grammar, shorten, combine, or otherwise alter quoted text. If exact wording cannot be verified, write a clearly labelled paraphrase without quotation marks and link the source. Never style paraphrased text as a direct quotation.
11. Add three to five concise FAQs when the topic supports genuine follow-up questions. Keep them additive: do not reduce a volume to one FAQ merely to avoid repetition, and do not reuse generic answers across different topics. Omit a question only when its answer would repeat the body without adding practical clarification.
12. Include only LinkedIn and Instagram in every blog footer. Use `https://in.linkedin.com/company/kovan-labs` for LinkedIn and `https://www.instagram.com/lifeatkovan/` for Instagram. Do not add Facebook, X/Twitter, or other social channels unless the user explicitly changes this rule.
13. Use `© {{YEAR}} Kovan Labs. All rights reserved.` in the footer.
14. Deliver a complete `.html` file for every finished blog, even when the article was drafted from the Markdown template or supplied as Markdown by the user.
15. Before placing any radar blip, define an internal benchmark that applies equally to every compared item. Use identical workloads, inputs, environment and measurement units; use at least three runs or equivalent repeated evidence; record the aggregation method and explicit ring thresholds during generation. Do not display the benchmark rubric, calculations or evidence table in the finished blog unless the user explicitly requests them. If comparable evidence is missing, treat the item as **Unrated** and do not plot it in Adopt, Trial, Assess or Caution. Never invent extra blips from surrounding context: plot only items actually evaluated by the supplied resource or requested scope.

## SEO skill coordination

1. Load and use the `seo-audit` skill from `coreyhaines31/marketingskills` for every new blog, substantial blog rewrite, collection page, radar page or volume page.
2. Apply it before drafting to identify reader intent, the primary topic, useful supporting questions and internal-link opportunities. Apply it again after HTML generation to audit crawlability, title and meta description, heading hierarchy, canonical handling, image text alternatives, structured-data opportunities, content quality and link clarity.
3. Treat `seo-audit` as an auditing companion, not a license to add keywords, links, schema or sections that do not help the reader. Kovan editorial, quotation, citation and brand rules remain authoritative.
4. If `seo-audit` is unavailable, state that the companion skill is not installed and continue with this skill's built-in SEO checklist. Never silently skip SEO validation.

## Template selection

Infer the article shape from its title first, then use the supplied brief or source material to break a tie. Do not ask the user to choose when one option is reasonably clear.

1. **Conventional article — `templates/blog-template.html`**
   - Default for a single argument, explanation, company profile, event recap, tutorial, case study, opinion, or question-led article.
   - Typical title signals: “why,” “how,” “what,” “guide,” “lessons,” “introducing,” “inside,” a company or event name, or one clearly bounded topic.
   - Examples: “Why microservices are useful,” “The primitive paradox,” “About Kovan Labs,” or an event recap.
2. **Volume or edition — `templates/blog-volume-template.html`**
   - Use for a recurring publication that collects multiple related perspectives under one edition theme and benefits from grouped sections and edition navigation.
   - Typical title signals: “volume,” “edition,” “digest,” “monthly,” “quarterly,” “issue,” or an explicit series and volume number.
   - Examples: “Kovan Engineering Digest · Volume 1,” “AI Engineering · July edition,” or “Cloud Perspectives · Issue 3.”
3. **Technology radar — `templates/blog-radar-template.html`**
   - Use only when the title calls for mapping multiple technologies or practices across the four radar quadrants and the Adopt, Trial, Assess, and Caution rings.
   - Typical title signals: “radar,” “technology landscape,” “ecosystem map,” “maturity map,” “adoption map,” or a broad comparison of many tools, platforms, techniques, languages, and frameworks.
   - Do not use the radar merely because an article mentions three tools. Use it only when classification and maturity placement are central to the article.
   - Choose a topic-appropriate benchmark before assigning rings. For performance comparisons, a valid default is: fastest verified aggregate = Adopt; up to 10% slower = Trial; more than 10% and up to 25% slower = Assess; more than 25% slower, repeated failures, or a critical reliability/security problem = Caution. State when another rubric is used.

Selection precedence: explicit “radar” or maturity-mapping intent → radar template; explicit volume, issue, edition or multi-story digest intent → volume template; otherwise → conventional article template. Record the selected template internally before writing and keep its design language intact.

## Platform-independent requirement

- Apply this same three-template selection workflow whenever this skill creates a blog, regardless of whether it is invoked from Codex, another agent host, an IDE, a CLI, or a connected content platform.
- Treat the files in `/home/thansika/Documents/Content creation/templates` as the canonical templates. Do not substitute a platform-native theme, generated approximation, or unrelated layout when these files are accessible.
- If a platform cannot render local HTML directly, still generate the completed HTML from the selected template first, then export, upload, embed, or adapt that output as the platform requires without changing the core Kovan design system.
- If the canonical templates are unavailable in another environment, stop and request access to them rather than silently recreating their design from memory.

## Mandatory brand assets

1. Use only original files from `/home/thansika/Documents/Content creation/05 Brand Assets`. Never recreate or modify a logo or motif.
2. Confirm required assets are readable before generating the blog. Stop and report a missing file instead of drawing, typing, downloading, or substituting it.
3. In the conventional article and radar templates, use `logo_horizontal.png` at the top-left on a Paper logo bar. In the radar template, follow it with a separate Ink edition strip. In the volume template, use `logo_mono_white.png` inside one continuous Ink masthead that merges the logo, volume marker and title banner. Preserve each logo's 1800:364 aspect ratio, intrinsic attributes, clear space, and a 120px minimum displayed width.
4. For output in `output/website`, use the matching logo path and `../../05%20Brand%20Assets/graphic_dotwave.png`. Recalculate relative paths when saving elsewhere.
5. Use the supplied full-colour dot-wave as the decorative accent on the right side of the title banner. Make it follow the full banner height and extend through the right edge of the masthead. Merge it into the Ink background with a long transparent horizontal fade so no independent image boundary is visible. Keep it secondary to the title with reduced opacity, never place it behind readable text, and do not repeat it elsewhere.
6. Use `graphic_rings.png` and `graphic_spark.png` as softly blended page-edge decorations. In the volume template, size them responsively at approximately 180–240px, use about 20% opacity, and soften their outside edges with a transparency mask. Distribute them vertically as percentages of the article height, alternate the left and right gutters, and keep them away from readable text and controls. Prevent horizontal scrolling, make them non-interactive with empty alt text, and hide them below 1280px where the side gutters cannot contain them safely.
7. Keep title bands compact and content-responsive. In the volume template, use a hero minimum-height range of approximately 240–340px with about 40px desktop and 32px mobile vertical padding; allow unusually long headlines to increase the height naturally instead of clipping or overflowing. Use Ink `#090C08`, a Spark category eyebrow, a Paper title, and Grey Light summary text.
8. Do not crop, stretch, recolour, rotate, filter, add effects, reconstruct, or place content inside official-logo clear space. Decorative motifs use empty alt text.
9. Make all images and decorations responsive. Use `max-width:100%` and intrinsic aspect ratios for content images, cap large editorial images with viewport-aware maximum heights, and prevent two-column image panels from stretching to match unusually long text. Size hero motifs and page-edge decorations with `clamp()`, anchor edge decor with percentage transforms instead of fixed negative pixel offsets, clip page-level overflow, and hide nonessential edge decor on narrower displays.

## Editorial rules

- Use a professional, approachable, direct voice.
- Use sentence case for headings.
- Make the opening summary one sentence and keep it short enough for the hero banner.
- Open with the central insight, tension, question, or reader problem. Then supply only the background needed to understand the argument.
- Never expose template labels such as `Objective`, `Context`, `Introduction`, `Main section`, or `Conclusion` as visible headings.
- Replace structural labels with specific, benefit-led or question-led headings that communicate each section's idea when scanned alone.
- Prefer short paragraphs, descriptive headings, concrete examples, varied sentence rhythm, and an inverted-pyramid opening suited to web reading.
- Keep paragraphs under 240 characters when doing so does not damage clarity; otherwise split them at a natural idea boundary.
- Use descriptive anchor text: write `[WCAG contrast guidance](URL)`, not `click here`.
- Hyperlink the smallest meaningful phrase supporting a claim.
- Keep citations editorially quiet: let the linked phrase carry the reference without interrupting the prose to explain where it came from.
- Distinguish external citations from internal related-blog links through wording, not visual clutter.
- Avoid duplicate sections, placeholder claims, keyword stuffing, and unsupported superlatives.
- Use ISO dates internally and display dates in a natural reader-facing format.

## Radar and volume content modes

- Treat the radar page as an orientation and decision-navigation page. Explain the topic boundary, source or evidence, benchmark, quadrant meanings, ring meanings, major patterns, uncertainty, and how to use the map. Keep individual blip explanations brief and move their full teaching content to linked volumes.
- A radar page must answer: what is being mapped, why the map matters, how items were classified, how to interpret quadrants and rings, what patterns deserve attention, and what the reader should open next.
- Do not crowd the radar with full tutorials for every blip. Its visible prose should be concise but complete enough that the map is understandable without opening another page.
- Treat each linked volume as the detailed teaching page. Start every perspective with a brief takeaway, then provide separate detail, example, boundary or trade-off, and next action.
- Each substantive volume perspective must contain multiple useful paragraphs or equivalent structured content. One sentence below a heading is never sufficient.
- Use the volume template's `ENTRY_n_SUMMARY`, `ENTRY_n_DETAIL`, `ENTRY_n_EXAMPLE`, and `ENTRY_n_BOUNDARY_ACTION` fields. Replace every field with topic-specific writing; never duplicate the same generic text across blips.
- Do not add a “Read perspective” or “Supporting reference” link to every volume entry. Keep the explanation on the volume page itself. Add an inline contextual link only when that entry needs a distinct authoritative destination; if multiple entries would point to the same general source or parent page, link it once in the overview, reference note or navigation instead.
- Radar content may summarize; volume content must teach.
- In radar theme sections, keep the section-level title visually subordinate to the individual insight headings. Use the canonical template's smaller responsive section-title scale; do not style the wrapper title at the same size as or larger than the insight titles beneath it.

## Explanation depth and readability

Apply progressive disclosure to every explanatory section: give the reader a brief answer first, then enough detail to understand and use it.

- Open each section with a one- or two-sentence takeaway that answers the heading directly.
- Follow with a plain-language explanation of **what it is**, **why it matters**, and **how it works** in the article's context.
- Add at least one concrete example, scenario, workflow, or decision when the concept is not self-evident.
- Close with the relevant limitation, trade-off, safeguard, or next action when one exists.
- Define unfamiliar terminology on first use. Prefer familiar words, active voice, and short sentences; use technical terms only when they improve precision.
- Keep the summary brief without making the explanation shallow. The opening lines must communicate the central point; the following detail must build practical understanding.
- Keep the progression invisible to the reader. Never prefix prose with structural labels such as “Briefly,” “In detail,” “Detail,” “Example,” or “Boundary and next step.” Integrate examples, limitations and actions naturally into the narrative or give them specific topic-led subheadings when separation is useful.
- Every paragraph must advance the explanation with a new fact, mechanism, consequence, example, qualification or decision. Do not restate the summary in longer words, repeat a definition across sections, or reuse generic implementation advice to simulate depth.
- Do not create a substantive heading whose content is only one short sentence. Merge it into another section or expand it with useful explanation.
- For standard articles, develop each major idea across multiple connected paragraphs instead of filling placeholders with isolated statements.
- For volume entries, explain the overview, operating context, implementation implications, and boundary or trade-off. A one-sentence card is not a complete article.
- For each radar blip's dedicated volume, include at least four distinct, topic-specific perspectives. Across the volume, cover capability, practical use, implementation or operating model, evidence or measurement, risks or limitations, and adoption guidance.
- Make FAQs additive: answer genuine follow-up questions with enough context to stand alone rather than repeating the body.
- Never increase length through repetition, generic filler, duplicated definitions, or unsupported claims. Depth must come from explanation, evidence, examples, and decisions.

Use this sequence internally when drafting; do not print these labels in the article:

1. **Brief:** state the direct answer or central idea.
2. **Detail:** explain what it means and how it works.
3. **Example:** show it in a concrete situation.
4. **Boundary:** explain when it may fail, cost more, or need safeguards.
5. **Action:** tell the reader what to evaluate or do next.

## Search engine optimization

- Write for reader intent first. Identify the primary question the article answers and keep every major section relevant to it.
- Put the primary topic naturally in the HTML title, H1, meta description, opening paragraph, and at least one descriptive H2 when appropriate. Do not force exact-match repetition.
- Keep every page title and meta description unique, concise, descriptive, and accurate.
- Maintain one H1 and a logical H2/H3 hierarchy. Headings must describe their actual content and remain understandable when scanned alone.
- Use descriptive internal links between radar, volume, related Kovan articles, and detail pages. Avoid generic anchor text such as “click here.”
- Link authoritative primary sources only where verification or follow-up is useful.
- Give genuine editorial images useful alt text; keep decorative motifs empty and hidden from assistive technology.
- Use human-readable lowercase hyphenated filenames. Add a canonical URL only when the published destination is known; never invent one.
- Avoid keyword stuffing, duplicated copy, doorway pages, misleading headings, hidden SEO text, and near-identical generated articles.
- Give every page distinct value. Each blip volume needs topic-specific explanations, examples, risks, and FAQs rather than a shared generic shell.
- Preserve performance and mobile readability: responsive images, no page-level horizontal scrolling, and no unnecessary third-party scripts.

## HTML validation

Before delivery:

1. Confirm no required `{{PLACEHOLDER}}` remains.
2. Confirm title, summary, author, publication date, and category are present.
3. Confirm every image has non-empty `alt` text unless it is decorative.
4. Confirm links use valid destinations and external links use `rel="noopener noreferrer"` when opened in a new tab.
5. Confirm all FAQ controls work with keyboard input and expose their expanded state.
6. Confirm the page remains readable at 320 px width and tables can scroll horizontally.
7. Confirm the footer contains exactly the linked LinkedIn and Instagram icons plus the Kovan Labs copyright.
8. Confirm the title-header composition contains exactly one readable approved logo at its top-left, its displayed dimensions preserve the source aspect ratio, and no reconstructed logo or duplicate lockup text exists. Require `logo_horizontal.png` on Paper for the conventional and radar templates, and `logo_mono_white.png` on Ink for the volume template.
9. Compare every attributed quotation against its linked source and confirm the wording is verbatim. Confirm that paraphrases do not use quotation marks or `blockquote`.
9. Confirm all visual values and asset choices comply with `05 Brand Assets/design.md` and `references/brand-system.md`; reject legacy teal, blue-gradient banners, pure black, and off-token colors.
10. For the volume template, confirm the sticky section links resolve; do not insert an in-page search bar for a single-topic volume; entries are grouped only where those groups clarify the content; unused groups and previous/next links are removed; and every retained link resolves. For the radar template, confirm the four separate quadrant graphs combine into one radar; use the canonical Techniques, Platforms, Tools, and Languages & Frameworks categories; use Adopt/Trial/Assess/Caution rings; print the ring names directly on the radar's horizontal centre axes in centre-out order; keep every blip inside its assigned quadrant and ring; scatter blips naturally rather than aligning them in straight lines; omit the catalogue completely; and ensure quadrant filters remain keyboard operable.
11. For every plotted radar blip, verify internally that comparable evidence produces its assigned ring, that hover/focus exposes its name and ring without exposing benchmark calculations, and that activation opens a dedicated detail page. Reject any placement based only on subjective preference or undocumented inference.
12. Confirm no file from `05 Brand Assets` appears inside `figure`, has a descriptive content-image alt attribute, or carries a caption. Confirm every optional table has a clear comparison purpose; remove it when that purpose is absent.
13. Confirm images preserve their aspect ratios, media/quote images do not grow with long adjacent text, hero motifs remain contained by their banners, and no decorative asset creates horizontal scrolling at desktop, tablet, or 320px mobile widths.
14. Confirm every substantive heading follows the brief-then-detail pattern, uses understandable language, and contains topic-specific explanation rather than a single short sentence or generic filler.
15. For every radar blip volume, confirm at least four substantive perspectives collectively explain capability, practical use, implementation, evidence, limitations, and adoption guidance.
16. Confirm the title, meta description, H1, heading hierarchy, filename, internal links, and image alt text follow the SEO rules without keyword stuffing or duplicated page copy.
17. Scan visible prose and metadata for accidental punctuation introduced by editing, including doubled full stops, duplicated commas and stray sentence fragments. Preserve intentional ellipses and valid relative paths such as `../`.

## Outputs

- Save an optional Markdown source in `/home/thansika/Documents/Content creation/output/blogs` unless the user chooses another location.
- Always save the final HTML article in `/home/thansika/Documents/Content creation/output/website` unless the user chooses another location.
- Save every article generated from `templates/blog-volume-template.html` inside `/home/thansika/Documents/Content creation/output/website/volume`. Create the directory when missing. Keep conventional articles and radar collection pages directly in `output/website` unless the user requests another structure.
- From a radar or collection page in `output/website`, link a volume as `volume/{{VOLUME_FILENAME}}.html`. Between files inside `output/website/volume`, use sibling filenames. From a volume back to its radar or collection, use `../{{COLLECTION_FILENAME}}.html`. Recalculate brand assets from the volume directory with `../../../05%20Brand%20Assets/`.
- Do not report the blog as complete until its HTML output exists and passes the HTML validation checklist.
- Use a lowercase hyphenated filename based on the article title.
- Do not overwrite an existing article unless the user requests it; add a version suffix instead.
