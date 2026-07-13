# Workflow 3: Rotation and content selection

## Purpose

Select the correct template variation and approved message without changing state before the poster succeeds.

## Template rotation

Read:

```text
/home/thansika/Documents/Content creation/config/template_rotation.json
```

Use:

```text
selected_index = stored_index % number_of_matching_templates
selected_template = matching_templates[selected_index]
next_index = (selected_index + 1) % number_of_matching_templates
```

Rules:

- Store only the next numeric position for each event.
- Do not store Canva design IDs.
- When one template matches, use index `0`.
- Do not update the file yet.
- Keep template rotation separate from message rotation.

## Message selection

Priority:

1. User-provided custom message, after fit validation.
2. Next approved message from:
   `/home/thansika/Documents/Content creation/config/POSTER_MESSAGE_BANK.md`
3. General-event message bank for unsupported named events.

Read message state from:

```text
/home/thansika/Documents/Content creation/config/message_rotation.json
```

Rules:

- Replace variables such as `{name}`, `{years}`, `{role}`, and `{event}`.
- Prefer 15–30 words.
- Keep the message within 2–4 lines.
- If it does not fit, try the next approved message in the same category.
- Do not freely generate a replacement message when an approved bank exists.
- Do not update message rotation yet.
- Record the selected message number for later commit.

## Required state rule

Rotation state is committed only after:

```text
Canva edit succeeds
AND editable link is retrieved
AND PNG export succeeds
AND PNG is saved locally
AND saved file is non-empty
```
