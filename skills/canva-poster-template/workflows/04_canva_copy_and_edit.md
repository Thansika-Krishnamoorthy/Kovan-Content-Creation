# Workflow 4: Canva copy and edit

## Purpose

Copy the selected master design, edit only the copy, preserve branding, and fill approved placeholders.

## Copy rule

1. Retrieve the selected regular Canva design.
2. Call `copy-design`.
3. Confirm the copy has a different design ID.
4. Rename the copy:

```text
<Person or event name> - <Event type> - <Event date>
```

5. Never edit the original master template.

## Approved placeholders

```text
EVENT_TITLE
EMPLOYEE_NAME
EVENT_DATE
EVENT_TIME
EVENT_VENUE
DESIGNATION
YEARS_COMPLETED
YEARS_OF_SERVICE
ACHIEVEMENT
EMPLOYEE_PHOTO
BIRTHDAY_MESSAGE
ANNIVERSARY_MESSAGE
WELCOME_MESSAGE
FAREWELL_MESSAGE
PROMOTION_MESSAGE
ACHIEVEMENT_MESSAGE
FESTIVAL_MESSAGE
EVENT_MESSAGE
JOB_TITLE
EXPERIENCE
JOB_LOCATION
SKILLS
APPLICATION_DETAILS
```

Replace only placeholders present in the selected template.

Do not leave visible labels such as:

```text
MESSAGE
GREETING
NOTE
EMPLOYEE NAME
PHOTO
LOGO
PLACEHOLDER
```

## Logo rules

The approved Kovan Labs logo must already exist in the master template.

Never:

- remove;
- replace;
- regenerate;
- recolour;
- crop;
- stretch;
- rotate;
- filter;
- cover;
- overlap with text.

Stop if the approved logo is missing.

## Photo rules

- Use only an approved accessible photo.
- Replace it inside the existing Canva frame.
- Preserve aspect ratio.
- Keep the face visible and centred.
- Do not stretch or distort.
- Do not cover the image with text or logo.
- If replacement fails, keep the placeholder and report manual replacement.

## Text and layout rules

- Preserve the approved template hierarchy.
- Keep minimum 52px outer safe margin.
- Keep minimum 20px gutters.
- Do not allow clipping, overlap, cropped words, or off-canvas content.
- Use another approved message or template variation if content cannot fit.
- Do not reduce text to an unreadable size.

## Editing transaction

1. Begin the Canva editing transaction when required.
2. Apply only approved changes.
3. Validate the copy.
4. Commit the transaction.
5. Retrieve the editable Canva editor link.
