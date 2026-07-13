# Workflow 6: Failure handling

## Stop the workflow when

- brand reference cannot be read;
- `canva_folder.json` cannot be read;
- configured folder ID is missing or empty;
- folder-item listing fails;
- no approved matching template exists;
- approved logo is missing;
- required photo is missing;
- content cannot fit safely;
- Canva editing fails;
- editable link cannot be retrieved;
- PNG export fails;
- local saving fails;
- saved file is empty.

## Pagination errors

When Canva returns:

```text
Only one of query or continuation should be supplied
```

or:

```text
Invalid continuation
```

then:

1. Stop immediately.
2. Do not retry repeatedly.
3. Do not switch to Brand Templates.
4. Do not search the entire Canva library.
5. Do not select a random design.
6. Do not create a new design.
7. Keep rotation files unchanged.
8. Report the exact error.

## Never do these as fallback

- generate a replacement image;
- create a new poster from scratch;
- use another company's design;
- edit the master template;
- hide the error;
- claim export or saving succeeded when it did not.

## Failure response

Return:

```text
Failed step:
Tool used:
Exact error:
Master template unchanged:
Copied design created:
Editable Canva link available:
PNG export completed:
Local file saved:
Rotation files changed:
Manual action required:
```
