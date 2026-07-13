# Workflow 5: Validation, export, saving, and response

## Final validation

Before export, verify:

- brand reference was read;
- correct event and template were selected;
- original master was not modified;
- copied design has a separate ID;
- logo remains unchanged;
- all required placeholders are replaced;
- no `MESSAGE`, `NOTE`, or `PLACEHOLDER` labels remain;
- text is fully visible;
- no overlaps or clipping exist;
- photo is not distorted;
- safe margins are preserved;
- no generated image was used;
- no premium element blocks export;
- editable link points to the copied design.

## Export

1. Export only the completed copied design as PNG.
2. Do not export the master.
3. Do not substitute another format automatically.
4. Do not repeatedly call export after failure.
5. Download the export.
6. Save directly inside:

```text
/home/thansika/Documents/Content creation/output/posters
```

## Filename format

```text
<event_type>_<person_or_event_name>_<YYYY-MM-DD>.png
```

Rules:

- lowercase;
- spaces replaced by underscores;
- unsafe characters removed;
- no overwrite;
- add `_02`, `_03`, and so on when needed.

## Local verification

Confirm:

- file exists;
- file size is greater than zero.

## Rotation commit

Only after complete success:

1. Save the next message index.
2. Save the next template index.
3. If any previous step failed, update neither file.

## Final response format

```text
Canva MCP status:
Brand reference status:
Configured Canva folder name:
Configured Canva folder ID:
Event type:
Template used:
Template index:
Next template index:
Copied design name:
Copied design ID:
Message number:
Changes completed:
Photo replacement status:
Logo status:
Editable Canva link:
PNG export status:
PNG filename:
PNG local file path:
Manual changes required:
```

Do not report success unless both are present:

```text
Editable Canva link: <Canva editor URL>
PNG local file path: /home/thansika/Documents/Content creation/output/posters/<filename>.png
```
