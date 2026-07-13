# Workflow 1: Request and brand validation

## Purpose

Validate the user request, required local files, branding source, and image restrictions before any Canva operation.

## Steps

1. Read:
   `/home/thansika/Documents/Content creation/reference/brand/Kovan_Brand_Identity.txt`
2. Stop if the file cannot be accessed.
3. Extract available request details:
   - event type;
   - employee or event name;
   - date;
   - time;
   - venue;
   - designation;
   - years completed;
   - achievement;
   - job details;
   - custom message;
   - photo source;
   - requested output.
4. Ask only for details required by the selected template.
5. Do not ask for a custom message unless the user wants to provide one.
6. Confirm that no image generation is required.
7. Accept photos only when they are:
   - supplied by the user;
   - approved Canva assets;
   - approved local assets;
   - accessible through a supported public URL.
8. Never generate a missing photo, logo, background, festival visual, icon, or illustration.

## Stop conditions

Stop when:

- the brand reference cannot be read;
- a required image is unavailable;
- the user requests generation of a substitute image;
- required template information cannot be obtained.

## Required failure message

```text
Kovan Labs Brand Identity reference file could not be accessed.
```
