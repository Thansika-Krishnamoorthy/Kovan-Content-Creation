---
name: canva-poster-template
description: Orchestrates approved Canva poster creation for Kovan Labs using a configured Canva folder ID, reusable regular Canva designs, message and template rotation, strict brand validation, editable-copy creation, PNG export, and local saving without generating any image.
---

# Canva Poster Template Skill

Use this skill whenever a user asks to create, prepare, edit, or export a Kovan Labs poster using Canva.

This file is the workflow controller. Follow the workflow files in the exact order below.

## Workflow order

1. `workflows/01_request_and_brand_validation.md`
2. `workflows/02_event_and_template_selection.md`
3. `workflows/03_rotation_and_content_selection.md`
4. `workflows/04_canva_copy_and_edit.md`
5. `workflows/05_validation_export_and_response.md`
6. `workflows/06_failure_handling.md`

Do not skip a workflow stage.

## Absolute rules

- Never generate any image, background, person, logo, icon, illustration, or substitute visual.
- Use only approved regular Canva designs stored in `Kovan Poster Templates`.
- Never edit a master template directly.
- Never use Canva Brand Templates or Autofill.
- Never call `search-folders`.
- Use the configured folder ID from `config/canva_folder.json`.
- Never send `continuation: ""`.
- Do not retry the same failed Canva call automatically.
- Update rotation files only after editing, export, download, and local saving all succeed.
- Every successful result must include the editable Canva link and saved PNG path.

## Required project paths

```text
Project root:
/home/thansika/Documents/Content creation

Brand reference:
/home/thansika/Documents/Content creation/reference/brand/Kovan_Brand_Identity.txt

Canva folder configuration:
/home/thansika/Documents/Content creation/config/canva_folder.json

Template rotation:
/home/thansika/Documents/Content creation/config/template_rotation.json

Message rotation:
/home/thansika/Documents/Content creation/config/message_rotation.json

Message bank:
/home/thansika/Documents/Content creation/config/POSTER_MESSAGE_BANK.md

Output folder:
/home/thansika/Documents/Content creation/output/posters
```

## Supported event keys

```text
birthday
work_anniversary
new_joiner
farewell
promotion
achievement
pongal
diwali
eid_mubarak
christmas
new_year
independence_day
republic_day
womens_day
company_event
job_opening
general_event
```

## Mandatory execution rule

Run the workflow sequentially:

```text
Request validation
→ Brand validation
→ Event detection
→ Folder-item listing
→ Template filtering
→ Template rotation
→ Message selection
→ Copy master
→ Edit copy
→ Validate
→ Export PNG
→ Save locally
→ Update rotation
→ Return editable link and path
```
