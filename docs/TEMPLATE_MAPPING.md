# Figma Template Mapping (GH#17)

Each Kovan poster **event key** is mapped to one or more **approved Figma templates**
(frame IDs). This mapping is the bridge between "the user asked for a birthday poster"
and "which Figma frame to duplicate, edit, and export".

Source of truth: `config/figma_template_map.json`

---

## Why events map to templates

Figma is the sole design platform (Canva was rejected). Reusable, brand-compliant
Figma templates replace ad-hoc design generation, so every poster:

- starts from an approved, on-brand layout;
- has fixed, clearly named placeholder layers
  (`EVENT_TITLE`, `EMPLOYEE_NAME`, `EVENT_DATE`, `GREETING_MESSAGE`,
  `EMPLOYEE_IMAGE`, `KOVAN_LOGO`, `BACKGROUND`);
- keeps the original Kovan logo untouched;
- only swaps variable content, then is validated and exported as PNG.

## File fields

| Field | Meaning |
|---|---|
| `schema_version` | Version of the mapping file format. |
| `last_updated` | ISO date the mapping was last edited. |
| `figma_project.file_id` | The Figma file key (from the file URL). |
| `figma_project.file_name` | Human-readable Figma file name. |
| `figma_project.page_id` | The Figma page (canvas) containing the frames. |
| `figma_project.page_name` | Human-readable page name. |
| `events.<key>.template_name` | Base template name, e.g. `KOVAN_TEMPLATE_BIRTHDAY`. |
| `events.<key>.frames[]` | The approved template variants for this event. |
| `events.<key>.frames[].name` | Variant name, e.g. `KOVAN_TEMPLATE_BIRTHDAY_01`. |
| `events.<key>.frames[].frame_id` | Real Figma node ID for that frame. |
| `events.<key>.current_index` | Rotation index of the last-used / next-to-use frame. |
| `events.<key>.total_templates` | `frames.length` for that event. |
| `events.<key>.next_index` | `(current_index + 1) % total_templates`. |

### Event keys covered

`birthday`, `work_anniversary`, `new_joiner`, `farewell`, `promotion`,
`achievement`, `pongal`, `diwali`, `eid_mubarak`, `christmas`, `new_year`,
`independence_day`, `republic_day`, `womens_day`, `company_event`,
`job_opening`, `general_event`.

Unknown/unsupported events fall back to `general_event`.

---

## Populating real Figma IDs (required before use)

The current file ships with **placeholder IDs** because the reusable Figma frames do
not exist yet (BRD blocker: "Event types have not yet been mapped to Figma file, page,
frame, or component IDs"). Until placeholders are replaced, the mapping must not be
used to select real templates.

To populate:

1. Create the reusable templates in Figma (one frame per variant), naming each
   frame `KOVAN_TEMPLATE_<EVENT>_<NN>` in the `Kovan Poster Templates` file.
2. Open the Figma file. The **file ID** is the `*...*` key in the URL:
   `https://www.figma.com/file/<FILE_ID>/<NAME>`.
3. The **page ID** is the node ID of the page (canvas) that holds the frames.
4. For each frame, copy its **frame ID** (the node ID from the Figma API or the
   `?node-id=` in the frame's share link) into `frames[].frame_id`.
5. `total_templates` = number of frames listed. If you add a second birthday
   variant, add a second entry and set `total_templates: 2`.
6. Remove the `_PLACEHOLDER` suffix so selectors no longer treat IDs as inert.

Never store sensitive tokens in this file; IDs are non-secret node identifiers.

---

## Rotation logic

When an event has multiple approved frames, the pipeline rotates through them so the
same poster is not produced every time. This mirrors the Canva rotation concept but
uses Figma frame IDs.

```text
selected_index = current_index % total_templates
selected_frame = frames[selected_index].frame_id
next_index     = (selected_index + 1) % total_templates
```

- With one template, `current_index` and `next_index` are both `0`.
- `current_index`/`next_index` are committed **only after** the whole pipeline
  succeeds (duplicate → edit → validate → export PNG → save locally), matching the
  current rotation-state rule. Do not advance rotation on a failed run.

## Placement in the pipeline

```
User request
  → detect event key
  → look up events[event_key] in figma_template_map.json
  → select frame via rotation
  → duplicate the frame
  → replace variable content / KOVAN logo
  → validate
  → export PNG → save locally
```

## Related files

- `config/canva_template_map.json` — legacy Canva-only mapping (superseded; keep for
  history until the Canva skill is removed).
- `config/template_rotation.json` — older plain-integer rotation state per event.
  This file's per-event `frames[]` + `current_index` supersede it; migrate when the
  caller is updated.
- `config/message_rotation.json` — message-bank rotation (separate from template
  rotation; do not combine).
- `skills/canva-poster-template/workflows/02_event_and_template_selection.md` and
  `03_rotation_and_content_selection.md` — the equivalent selection/rotation
  procedures for the (legacy) Canva path.
