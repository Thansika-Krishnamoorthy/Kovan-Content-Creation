# Workflow 2: Event and template selection

## Purpose

Identify the event, read the configured Canva folder ID, list regular Canva designs, and select only approved event templates.

## Folder configuration

Read:

```text
/home/thansika/Documents/Content creation/config/canva_folder.json
```

Expected structure:

```json
{
  "folder_name": "Kovan Poster Templates",
  "folder_id": "CANVA_FOLDER_ID"
}
```

## Mandatory Canva restrictions

- Use the configured folder ID directly.
- Do not call `search-folders`.
- Do not call `search-brand-templates`.
- Do not use Brand Templates.
- Do not use Autofill.
- Do not search the entire Canva library.
- Call `list-folder-items` for the configured folder.
- On the first call, omit `continuation` entirely.
- Use a continuation token only when Canva returned it from the immediately previous page.

## Event-prefix mapping

```text
birthday          → KOVAN_TEMPLATE_BIRTHDAY
work_anniversary  → KOVAN_TEMPLATE_WORK_ANNIVERSARY
new_joiner        → KOVAN_TEMPLATE_NEW_JOINER
farewell          → KOVAN_TEMPLATE_FAREWELL
promotion         → KOVAN_TEMPLATE_PROMOTION
achievement       → KOVAN_TEMPLATE_ACHIEVEMENT
pongal            → KOVAN_TEMPLATE_PONGAL
diwali            → KOVAN_TEMPLATE_DIWALI
eid_mubarak       → KOVAN_TEMPLATE_EID_MUBARAK
christmas         → KOVAN_TEMPLATE_CHRISTMAS
new_year          → KOVAN_TEMPLATE_NEW_YEAR
independence_day  → KOVAN_TEMPLATE_INDEPENDENCE_DAY
republic_day      → KOVAN_TEMPLATE_REPUBLIC_DAY
womens_day        → KOVAN_TEMPLATE_WOMENS_DAY
company_event     → KOVAN_TEMPLATE_COMPANY_EVENT
job_opening       → KOVAN_TEMPLATE_JOB_OPENING
general_event     → KOVAN_TEMPLATE_GENERAL_EVENT
```

## Selection procedure

1. Detect the event key from the request.
2. Determine the matching template prefix.
3. Read `canva_folder.json`.
4. Confirm:
   - folder name is exactly `Kovan Poster Templates`;
   - folder ID is present and non-empty.
5. List regular designs inside that folder.
6. Keep only titles beginning with the required event prefix.
7. Reject:
   - designs outside the folder;
   - completed posters;
   - unrelated designs;
   - designs without `KOVAN_TEMPLATE_`;
   - incorrect-logo designs;
   - premium-blocked designs.
8. Sort matching templates by numeric suffix: `_01`, `_02`, `_03`, and so on.
9. If no event-specific template exists, try `KOVAN_TEMPLATE_GENERAL_EVENT`.
10. If no approved template exists, stop.

## Unknown event rule

Normalize the event name to uppercase with underscores:

```text
KOVAN_TEMPLATE_<NORMALIZED_EVENT_NAME>
```

Then try the general-event prefix.

## Required failure message

```text
No approved Canva template was found for this event type.
Please create or approve a Canva template before continuing.
```
