---
name: canva-poster-template
description: Identifies the requested event, automatically discovers approved Canva templates from the Canva folder named Kovan Poster Templates, creates an editable copy, fills event details, rotates approved event messages and matching templates, preserves Kovan Labs branding, returns the editable Canva link, exports the completed poster as PNG, and saves it to the configured output folder without generating any image.
---

# Canva Poster Template Skill

Use this skill whenever a user asks to create, prepare, edit, or export a poster using Canva.

Supported requests include:

- Birthday
- Work anniversary
- Employee welcome or new joiner
- Farewell
- Promotion
- Achievement or congratulations
- Pongal
- Diwali or Deepavali
- Eid Mubarak
- Christmas
- New Year
- Independence Day
- Republic Day
- Women's Day
- Company event
- Job opening
- General event
- Other named events when an approved Canva template exists

---

# 1. Absolute image-generation restriction

Never generate any image yourself.

Do not use an image-generation model to create:

- Posters
- Backgrounds
- Employee photos
- Festival artwork
- Decorative illustrations
- Company logos
- Icons
- Objects
- People
- Replacement images
- Template alternatives

Use only:

- Approved Canva templates already available in the user's Canva library
- Existing elements inside the approved Canva template
- User-provided photos
- Approved images already stored in Canva
- Approved assets from the local project
- Original Kovan Labs logo files

If a required image is unavailable:

1. Stop the workflow.
2. Ask the user to provide the original image.
3. Do not create an AI-generated substitute.
4. Do not create a new poster from scratch.

The Canva master template is the only design source.

---

# 2. Required integrations

The following must already be connected and enabled:

- Canva MCP
- Local filesystem access for reading configuration files and saving exports

Do not repeatedly call the same Canva tool.

Do not repeat a failed search automatically.

Do not use pagination unless Canva returns a valid continuation token.

Never send:

```text
continuation: ""
```

Never invent, reuse, or send an invalid continuation token.

Stop after one failed Canva search and clearly report the error.

---

# 3. Project paths

Project root:

```text
/home/thansika/Documents/Content creation
```

Brand reference:

```text
/home/thansika/Documents/Content creation/reference/brand/Kovan_Brand_Identity.txt
```


Canva template folder:

```text
Kovan Poster Templates
```


Message rotation state:

```text
/home/thansika/Documents/Content creation/config/message_rotation.json
```

Template rotation state:

```text
/home/thansika/Documents/Content creation/config/template_rotation.json
```

Poster message bank:

```text
/home/thansika/Documents/Content creation/config/POSTER_MESSAGE_BANK.md
```

Output root:

```text
/home/thansika/Documents/Content creation/output/posters
```

---

# 4. Kovan Labs brand reference

Before selecting, copying, modifying, exporting, or saving a Canva poster, read:

```text
/home/thansika/Documents/Content creation/reference/brand/Kovan_Brand_Identity.txt
```

Treat this file as the primary source of truth for:

- Brand personality
- Voice and tone
- Approved colours
- Logo usage
- Typography
- Layout and spacing
- Image style
- Contrast
- Final brand validation

If the file cannot be read, stop and report:

```text
Kovan Labs Brand Identity reference file could not be accessed.
```

Do not continue without reading the brand reference.

---

# 5. Understand the request

Extract:

- Event type
- Person or employee name
- Event title
- Event date
- Event time
- Venue
- Designation
- Years completed
- Achievement details
- Job title
- Experience
- Skills
- Job location
- Application details
- Optional custom message
- Photo asset name, Canva asset, or public image URL
- Required output format
- Required output folder
- Specific Canva template name, when provided

Ask only for information that is required by the selected template.

Do not ask for a custom message unless the user specifically wants to provide one.

When no custom message is supplied, use the external event-specific message bank in `config/POSTER_MESSAGE_BANK.md` together with the rotation logic in this skill.

---

# 6. Event identification and template prefixes

Classify the request using the following rules.

## Birthday

Keywords:

```text
birthday
happy birthday
birthday wish
birthday celebration
```

Template prefix:

```text
KOVAN_TEMPLATE_BIRTHDAY
```

Output folder:

```text
output/posters/birthday
```

Message placeholder:

```text
BIRTHDAY_MESSAGE
```

## Work anniversary

Keywords:

```text
work anniversary
service anniversary
years of service
joining anniversary
employment anniversary
```

Template prefix:

```text
KOVAN_TEMPLATE_WORK_ANNIVERSARY
```

Output folder:

```text
output/posters/work_anniversary
```

Message placeholder:

```text
ANNIVERSARY_MESSAGE
```

## Employee welcome or new joiner

Keywords:

```text
new joiner
employee welcome
welcome aboard
new employee
new team member
```

Template prefix:

```text
KOVAN_TEMPLATE_NEW_JOINER
```

Output folder:

```text
output/posters/new_joiner
```

Message placeholder:

```text
WELCOME_MESSAGE
```

## Farewell

Keywords:

```text
farewell
goodbye
last working day
send-off
retirement
```

Template prefix:

```text
KOVAN_TEMPLATE_FAREWELL
```

Output folder:

```text
output/posters/farewell
```

Message placeholder:

```text
FAREWELL_MESSAGE
```

## Promotion

Keywords:

```text
promotion
promoted
new role
new designation
career advancement
```

Template prefix:

```text
KOVAN_TEMPLATE_PROMOTION
```

Output folder:

```text
output/posters/promotion
```

Message placeholder:

```text
PROMOTION_MESSAGE
```

## Achievement or congratulations

Keywords:

```text
achievement
award
winner
congratulations
certification
milestone
recognition
success
```

Template prefix:

```text
KOVAN_TEMPLATE_ACHIEVEMENT
```

Output folder:

```text
output/posters/achievement
```

Message placeholder:

```text
ACHIEVEMENT_MESSAGE
```

## Pongal

Keywords:

```text
pongal
thai pongal
harvest festival
pongal wishes
```

Template prefix:

```text
KOVAN_TEMPLATE_PONGAL
```

Output folder:

```text
output/posters/pongal
```

Message placeholder:

```text
FESTIVAL_MESSAGE
```

## Diwali or Deepavali

Keywords:

```text
diwali
deepavali
festival of lights
```

Template prefix:

```text
KOVAN_TEMPLATE_DIWALI
```

Output folder:

```text
output/posters/diwali
```

Message placeholder:

```text
FESTIVAL_MESSAGE
```


## Eid Mubarak

Keywords:

```text
eid
eid mubarak
eid ul-fitr
eid al-fitr
ramadan eid
bakrid
eid ul-adha
eid al-adha
```

Event key:

```text
eid_mubarak
```

Template prefix:

```text
KOVAN_TEMPLATE_EID_MUBARAK
```

Output folder:

```text
output/posters/eid_mubarak
```

Message placeholder:

```text
FESTIVAL_MESSAGE
```

## Christmas

Keywords:

```text
christmas
merry christmas
xmas
```

Template prefix:

```text
KOVAN_TEMPLATE_CHRISTMAS
```

Output folder:

```text
output/posters/christmas
```

Message placeholder:

```text
FESTIVAL_MESSAGE
```

## New Year

Keywords:

```text
new year
happy new year
new year celebration
```

Template prefix:

```text
KOVAN_TEMPLATE_NEW_YEAR
```

Output folder:

```text
output/posters/new_year
```

Message placeholder:

```text
FESTIVAL_MESSAGE
```

## Independence Day

Keywords:

```text
independence day
august 15
15 august
```

Template prefix:

```text
KOVAN_TEMPLATE_INDEPENDENCE_DAY
```

Output folder:

```text
output/posters/independence_day
```

Message placeholder:

```text
EVENT_MESSAGE
```

## Republic Day

Keywords:

```text
republic day
january 26
26 january
```

Template prefix:

```text
KOVAN_TEMPLATE_REPUBLIC_DAY
```

Output folder:

```text
output/posters/republic_day
```

Message placeholder:

```text
EVENT_MESSAGE
```

## Women's Day

Keywords:

```text
women's day
womens day
international women's day
march 8
```

Template prefix:

```text
KOVAN_TEMPLATE_WOMENS_DAY
```

Output folder:

```text
output/posters/womens_day
```

Message placeholder:

```text
EVENT_MESSAGE
```

## Company event

Keywords:

```text
company event
office event
corporate event
team event
function
seminar
workshop
conference
celebration
```

Template prefix:

```text
KOVAN_TEMPLATE_COMPANY_EVENT
```

Output folder:

```text
output/posters/company_event
```

Message placeholder:

```text
EVENT_MESSAGE
```

## Job opening

Keywords:

```text
job opening
hiring
we are hiring
vacancy
career opportunity
recruitment
job post
```

Template prefix:

```text
KOVAN_TEMPLATE_JOB_OPENING
```

Output folder:

```text
output/posters/job_opening
```

Message placeholder:

```text
EVENT_MESSAGE
```

## Unknown or other event

1. Extract the event name.
2. Convert it to uppercase with underscores.
3. Search:

```text
KOVAN_TEMPLATE_<NORMALIZED_EVENT_NAME>
```

4. If no approved event-specific template is found, search:

```text
KOVAN_TEMPLATE_GENERAL_EVENT
```

5. If neither exists, stop and report:

```text
No approved Canva template was found for this event type.
Please create or approve a Canva template before continuing.
```

Never create a design from scratch.

---

# 7. Approved template naming

Every approved Canva master template should follow:

```text
KOVAN_TEMPLATE_<EVENT_TYPE>_<NUMBER>
```

Examples:

```text
KOVAN_TEMPLATE_BIRTHDAY_01
KOVAN_TEMPLATE_WORK_ANNIVERSARY_01
KOVAN_TEMPLATE_NEW_JOINER_01
KOVAN_TEMPLATE_FAREWELL_01
KOVAN_TEMPLATE_PROMOTION_01
KOVAN_TEMPLATE_ACHIEVEMENT_01
KOVAN_TEMPLATE_PONGAL_01
KOVAN_TEMPLATE_DIWALI_01
KOVAN_TEMPLATE_EID_MUBARAK_01
KOVAN_TEMPLATE_CHRISTMAS_01
KOVAN_TEMPLATE_NEW_YEAR_01
KOVAN_TEMPLATE_INDEPENDENCE_DAY_01
KOVAN_TEMPLATE_REPUBLIC_DAY_01
KOVAN_TEMPLATE_WOMENS_DAY_01
KOVAN_TEMPLATE_COMPANY_EVENT_01
KOVAN_TEMPLATE_JOB_OPENING_01
KOVAN_TEMPLATE_GENERAL_EVENT_01
```

Only select designs whose title starts with:

```text
KOVAN_TEMPLATE_
```

Never select:

- Random Canva marketplace templates
- Designs belonging to another company
- Designs without the approved prefix
- Old completed posters
- Incomplete designs
- Templates containing an incorrect company logo
- Premium templates that cannot be exported

---

# 8. Canva folder-based template discovery

All approved reusable poster templates are stored in the Canva folder named exactly:

```text
Kovan Poster Templates
```

Do not use a local template design-ID map.

Do not require manual design-ID configuration.


Do not search the entire Canva library when the approved Canva folder can be accessed.

## Folder discovery procedure

For every poster request:

1. Identify the event type from the user request.
2. Convert the event type to the approved event key and template prefix.
3. Find the Canva folder named exactly:

```text
Kovan Poster Templates
```

4. List the designs inside that folder.
5. Accept only designs whose titles begin with the required event prefix.
6. Reject designs outside this folder.
7. Reject completed posters, unrelated designs, and designs without the approved prefix.
8. Sort matching template titles by numeric suffix:

```text
_01
_02
_03
_04
```

9. Select the current template using `template_rotation.json`.
10. Copy the selected template.
11. Never edit the original template.
12. Edit only the copied design.
13. Return the copied design's editable Canva link.
14. Export the completed copied design as PNG.
15. Save the PNG inside:

```text
/home/thansika/Documents/Content creation/output/posters
```

## Approved event keys and prefixes

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

## Folder restrictions

Only use designs that satisfy all of the following:

- Located inside `Kovan Poster Templates`
- Title begins with `KOVAN_TEMPLATE_`
- Title matches the identified event prefix
- Contains the approved Kovan Labs logo
- Is an approved reusable master template
- Can be copied and exported
- Does not contain a premium restriction that blocks export

Never select:

- Designs outside `Kovan Poster Templates`
- Random Canva marketplace templates
- Designs from another company
- Completed posters
- Old exports
- Designs for another event
- Designs without the approved prefix
- Designs with an incorrect logo

## Canva pagination handling

For the first folder lookup or folder-item listing request:

- Do not include `continuation`.
- Do not send an empty continuation value.
- Do not invent a continuation token.
- Use a continuation token only when Canva returns one from the immediately previous page.

If Canva returns:

```text
Invalid continuation
```

1. Do not retry repeatedly.
2. Do not select a random template.
3. Do not create a new design.
4. Stop and report that the Canva MCP client sent an invalid pagination value.
5. Keep all local rotation files unchanged.

---

# 9. Template rotation

Template rotation state is stored in:

```text
/home/thansika/Documents/Content creation/config/template_rotation.json
```

Template rotation stores only the next position for each event.

It does not store design IDs.

Example:

```json
{
  "birthday": 0,
  "christmas": 0,
  "pongal": 0,
  "diwali": 0,
  "eid_mubarak": 0
}
```

## Rotation procedure

1. Identify the event key.
2. Discover all matching templates inside `Kovan Poster Templates`.
3. Sort matching templates by numbered suffix.
4. Read the stored event index from `template_rotation.json`.
5. Calculate:

```text
selected_index = stored_index % number_of_matching_templates
selected_template = matching_templates[selected_index]
```

6. Copy and edit the selected template.
7. After Canva editing, editable-link retrieval, PNG export, and local saving all succeed, calculate:

```text
next_index = (selected_index + 1) % number_of_matching_templates
```

8. Save `next_index` to `template_rotation.json`.
9. Do not update the index when any step fails.
10. When only one template matches, always use index `0`.
11. Never select the same template repeatedly when multiple templates are available.
12. Keep template rotation independent from message rotation.

Example for three Christmas templates:

```text
Request 1 → KOVAN_TEMPLATE_CHRISTMAS_01
Request 2 → KOVAN_TEMPLATE_CHRISTMAS_02
Request 3 → KOVAN_TEMPLATE_CHRISTMAS_03
Request 4 → KOVAN_TEMPLATE_CHRISTMAS_01
```

---
# 10. Copy rule

Never edit a master template directly.

For every poster:

1. Retrieve the approved template.
2. Create a copy using Canva `copy-design`.
3. Confirm that the copy has a separate design ID or edit link.
4. Rename the copied design.
5. Edit only the copied design.

Copied design naming format:

```text
<Person or event name> - <Event type> - <Event date>
```

Examples:

```text
Deepika - Birthday - 13 July 2026
Arun - Work Anniversary - 13 July 2026
Pongal Wishes - Pongal - 15 January 2027
Data Engineer - Job Opening - 13 July 2026
```

---

# 11. Approved placeholders

Templates should use clear uppercase placeholders.

Common placeholders:

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

Replace only placeholders that exist in the selected template.

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

Replace all required placeholders with final content before export.

---

# 12. Logo handling

The official Kovan Labs logo must already be present inside every approved Canva master template.

Preserve it exactly as it appears.

Never:

- Remove it
- Replace it
- Regenerate it
- Redraw it
- Recolour it
- Crop it
- Stretch it
- Rotate it
- Apply shadows
- Apply glow
- Apply filters
- Alter its proportions
- Cover it
- Place text over it

If the template does not contain the official Kovan Labs logo, stop and report:

```text
The selected Canva template does not contain the approved Kovan Labs logo.
```

Do not automatically create or recreate the logo.

---

# 13. Message selection priority

Use this order:

1. If the user provides an approved custom message, use it after validating length and fit.
2. Otherwise, select the next message from the matching event message bank.
3. Do not freely generate a new message when an approved bank exists.
4. For an unsupported named event, use the general-event message bank unless an event-specific bank has been added.

---

# 14. Message rotation

Read:

```text
/home/thansika/Documents/Content creation/config/message_rotation.json
```

Rotation sequence:

```text
1 → 2 → 3 → 4 → 5 → 6 → 7 → 8 → 9 → 10 → 1
```

Procedure:

1. Identify the event key.
2. Read the current stored value.
3. Select the next message.
4. Replace variables such as `{name}`, `{years}`, `{role}`, or `{event}`.
5. Use the selected message in the copied template.
6. Update the rotation value only after Canva editing and export succeed.
7. Do not update the file if the workflow fails.
8. Never use the same message twice consecutively for the same event type.
9. After message 10, return to message 1.

Initial file:

```json
{
  "birthday": 0,
  "work_anniversary": 0,
  "new_joiner": 0,
  "farewell": 0,
  "promotion": 0,
  "achievement": 0,
  "pongal": 0,
  "diwali": 0,
  "eid_mubarak": 0,
  "christmas": 0,
  "new_year": 0,
  "independence_day": 0,
  "republic_day": 0,
  "womens_day": 0,
  "company_event": 0,
  "job_opening": 0,
  "general_event": 0
}
```

---

# 15. External message bank

The approved poster messages are stored separately in:

```text
/home/thansika/Documents/Content creation/config/POSTER_MESSAGE_BANK.md
```

Do not keep event messages inside this skill file.

When the user does not provide a custom message:

1. Read `POSTER_MESSAGE_BANK.md`.
2. Identify the matching event category.
3. Read the current event index from `message_rotation.json`.
4. Select the next approved message from that category.
5. Replace variables such as `{name}`, `{years}`, `{role}`, or `{event}`.
6. Validate that the selected message fits safely in the template.
7. If it does not fit, select the next approved message in the same category.
8. Update the rotation index only after Canva editing, png export, and local
   saving succeed.
9. Do not generate a new message when a matching approved message bank exists.
10. If the message-bank file cannot be accessed, stop and report:

```text
Poster message bank could not be accessed.
```

The message-bank file is the single source of truth for approved rotating
messages.


---

# 16. Message fit rules

Before inserting the message:

1. Check the template message area.
2. Prefer messages between 15 and 30 words.
3. Keep the message within 2 to 4 lines.
4. Preserve the approved font family.
5. Do not reduce the font below a readable size.
6. Do not allow text to overflow.
7. Do not allow text to overlap the name, image, logo, border, or decorations.
8. Do not cut words.
9. Do not hide overflow using ellipses.
10. If the selected message does not fit, use the next message in the same bank.
11. Update the rotation state only for the message that was successfully used.

---

# 17. Typography

Use these fonts when supported by the selected Canva template:

- Heading: Poppins SemiBold or Bold
- Employee name: Poppins Bold
- Date, designation, or subtitle: Poppins Medium
- Body message: Inter Regular or Medium

Preserve the template's approved hierarchy.

Avoid:

- Decorative fonts
- Handwritten fonts
- Script fonts
- Excessive all-uppercase text
- More than two font families
- Unreadably small text

For light backgrounds:

- Main text: `#000000`
- Secondary text: `#808080`

For dark backgrounds:

- Main text: `#FFFFFF`

Use approved Kovan Labs colours for highlights only when readability remains strong:

- Red: `#EF3829`
- Green: `#00A95C`
- Yellow: `#FDB917`
- Blue: `#0076BE`
- Black: `#000000`
- Gray: `#808080`
- White: `#FFFFFF`

---

# 18. Layout and spacing

Preserve the selected template's layout.

Maintain:

- Minimum 52px outer safe margin
- Minimum 20px gutter spacing
- Clear visual hierarchy
- Consistent alignment
- Separation between text, images, logo, and decorations

Do not allow:

- Text outside the canvas
- Text crossing the safe margin
- Images crossing the safe margin
- Logo crossing the safe margin
- Overlapping content
- Cropped words
- Crowded text
- Inconsistent gaps

If content does not fit:

1. Use a shorter approved message.
2. Improve line breaks.
3. Slightly reduce font size while keeping it readable.
4. Use another approved template variation.
5. Stop if safe fitting is impossible.

---

# 19. Photo handling

Use a photo only when:

- The user provides it
- It exists as an approved Canva asset
- It exists in the approved local asset folder
- It is accessible through a public image URL supported by Canva MCP

Never generate a missing employee photo.

When replacing a photo:

1. Use the existing Canva photo frame.
2. Preserve aspect ratio.
3. Do not stretch or distort the image.
4. Keep the face visible and centred.
5. Do not crop the forehead or chin unnecessarily.
6. Do not cover the image with text.
7. Do not cover the image with the logo.
8. Do not apply unapproved filters.

If the photo cannot be replaced correctly:

1. Keep the placeholder unchanged.
2. Return the Canva edit link.
3. Clearly state that manual replacement is required.
4. Do not generate a substitute.

---

# 20. Canva editing workflow

For every poster request:

1. Read the Kovan Labs brand reference.
2. Parse the user request.
3. Identify the event type and event key.
4. Extract available event details.
5. Ask only for missing information required by the selected template.
6. Convert the event key to the approved template prefix.
7. Find the Canva folder named exactly `Kovan Poster Templates`.
8. List the designs inside that folder.
9. Do not include an empty `continuation` value.
10. Filter the listed designs using the approved event prefix.
11. Reject unrelated designs and designs outside the approved folder.
12. Sort matching templates by numbered suffix.
13. Stop if no approved matching template is found.
14. Read `template_rotation.json`.
15. Select the current matching template using the stored event index.
16. Record the selected template title and template index.
17. Copy the selected master template.
18. Confirm that the copied design has a separate Canva design ID.
19. Confirm that the copied design provides an editable Canva URL.
20. Rename the copied design.
21. Read the external message bank from `config/POSTER_MESSAGE_BANK.md`.
22. Read the message rotation state from `message_rotation.json`.
23. Select the next approved event message unless the user supplied a custom message.
24. Replace all required text placeholders.
25. Replace the employee photo only when a Canva-accessible approved asset is available.
26. Preserve the existing Kovan Labs logo and all locked brand elements.
27. Never generate any image.
28. Validate text, spacing, contrast, logo, image crop, and unresolved placeholders.
29. Commit the Canva editing transaction.
30. Retrieve and preserve the editable Canva link for the copied design.
31. Export the completed copied design as PNG.
32. Download the exported PNG file.
33. Save the PNG directly inside:

```text
/home/thansika/Documents/Content creation/output/posters
```

34. Verify that the saved PNG exists and is not empty.
35. Update `message_rotation.json`.
36. Calculate the next template index.
37. Update `template_rotation.json`.
38. Update neither rotation file if editing, export, or local saving fails.
39. Return:
    - event type;
    - selected template title;
    - selected template index;
    - next template index;
    - copied design ID;
    - editable Canva link;
    - PNG filename;
    - absolute local PNG path.

The editable Canva link and local PNG file are mandatory outputs for every successful poster request.

---
# 21. Output folder and filenames

All completed poster exports must be saved directly inside:

```text
/home/thansika/Documents/Content creation/output/posters
```

Do not create or use event-specific subfolders unless the user explicitly requests them.

The required filename format is:

```text
<event_type>_<person_or_event_name>_<YYYY-MM-DD>.png
```

Rules:

- Use lowercase.
- Replace spaces with underscores.
- Remove unsafe filename characters.
- Use the `.png` extension.
- Do not overwrite an existing file.
- Add `_02`, `_03`, and so on when a file already exists.
- Save the file directly in the poster output folder.
- Return the absolute saved path.

Examples:

```text
/home/thansika/Documents/Content creation/output/posters/birthday_deepika_2026-07-13.png
/home/thansika/Documents/Content creation/output/posters/work_anniversary_arun_2026-07-13.png
/home/thansika/Documents/Content creation/output/posters/pongal_wishes_2027-01-15.png
/home/thansika/Documents/Content creation/output/posters/job_opening_data_engineer_2026-07-13.png
```

Before saving, create the base output folder when it does not exist.

---

# 22. Editable-link and png export rules

For every successfully created poster, always provide the editable Canva link for the copied design.

The editable link must:

- Refer to the copied design, not the master template.
- Open the design in Canva's editor.
- Be returned even after export succeeds.
- Never be replaced by a preview-only or download-only link.

Export the completed copied design as:

```text
png
```

Save the exported png directly to:

```text
/home/thansika/Documents/Content creation/output/posters
```

Export PNG by default whenever the user asks to create a completed poster.

Do not export only when the user explicitly requests Canva editing without export.

Do not silently substitute PNG, JPG, PDF, or another format when png export fails.

Do not export:

- The original master template
- An incomplete poster
- A poster with unresolved placeholders
- A poster with incorrect branding
- A poster with clipped or overlapping text
- A poster with a modified logo
- A poster containing any generated image

Use the Canva export result or returned download URL only for the completed copied design.

After export:

1. Download the png file.
2. Save it with the approved filename.
3. Verify that the file exists.
4. Verify that its file size is greater than zero.
5. Return the exact absolute path.
6. Keep and return the editable Canva link separately.

Do not repeatedly call the export tool.

If Canva or the available Canva MCP tool does not support png export for the selected design:

1. Do not claim that an png was created.
2. Do not substitute another format automatically.
3. Return the editable Canva link when the copy was created successfully.
4. Report the exact png export limitation or error.
5. State that png export requires manual action in Canva or a supported export tool.

If export fails because of premium or restricted Canva elements:

1. Do not retry repeatedly.
2. Report the exact export error.
3. Return the editable Canva link.
4. State that the restricted element must be replaced manually.

---

# 23. Final validation

Before export, verify:

- Brand reference was read successfully.
- Correct event type was identified.
- Correct approved template was used.
- Original template was not modified.
- Copied design has a separate ID.
- Official Kovan Labs logo remains unchanged.
- All required placeholders were replaced.
- No visible labels such as `MESSAGE`, `NOTE`, or `PLACEHOLDER` remain.
- Person or event name is fully visible.
- Message fits safely.
- Text is readable.
- No text is clipped.
- No text overlaps another element.
- No text extends outside the canvas.
- No image is stretched or distorted.
- No logo overlaps the photo.
- No text overlaps the photo.
- Safe margins are maintained.
- No generated image was used.
- No premium element blocks export.
- Editable Canva link points to the copied design.
- png export completed successfully.
- Exported png exists directly inside `/home/thansika/Documents/Content creation/output/posters`.
- Exported png file size is greater than zero.

Do not export until all critical checks pass.

---

# 24. Failure handling

Stop the workflow when:

- Brand reference cannot be read
- No approved matching Canva template exists inside `Kovan Poster Templates`
- Canva folder discovery fails
- The template does not contain the approved logo
- A required employee photo is missing
- Text cannot fit safely
- Canva editing fails
- Canva export fails
- The output file cannot be saved locally

Never:

- Generate a replacement image
- Create a replacement poster
- Use another company's design
- Select a random public Canva template
- Repeat failed calls continuously
- Edit the master template
- Hide an error

Report:

- Failed step
- Tool used
- Exact error
- Whether the master template remained unchanged
- Whether manual action is required

---

# 25. Final response format

Return:

```text
Canva MCP status:
Brand reference status:
Canva template folder status:
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

A successful result must contain:

```text
Editable Canva link: <Canva editor URL>
Template index: <current selected index>
Next template index: <next stored index>
PNG local file path: /home/thansika/Documents/Content creation/output/posters/<filename>.png
```

Do not report success when either the editable Canva link or saved PNG file is
missing.

Always return the editable Canva link after creating or modifying the copied
design.

---

# Final mandatory rule

The skill may identify, discover, retrieve, copy, edit, validate, export, and save an approved Canva template. Every successful poster workflow must return the copied design's editable Canva link and save the exported png directly inside `/home/thansika/Documents/Content creation/output/posters`.

The skill must never generate a poster image, background, person, logo, festival illustration, decorative graphic, or substitute image by itself.
