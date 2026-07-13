# Content Creation Automation Project

**Project:** Content Creation using Goose and Figma MCP  
**Organization:** Kovan Labs  
**Last updated:** 13 July 2026  
**Current focus:** Figma-based reusable poster-template selection, editing, validation, and PNG export

---

## 1. Project Objective

The objective of this project is to build a reusable content-creation workflow that can generate:

- Blog content
- Birthday posters
- Work-anniversary posters
- Festival wishes
- Event and function posters
- Case studies
- Other company-branded content

The workflow is being developed using Goose/GooseWorks skills, reusable design templates, and Figma MCP.

The long-term goal is to accept a simple user request, identify the event type, select the correct Figma template, update the required content, use the original Kovan logo, validate the final layout, export the poster as PNG, and save it in the local output folder.

---

## 2. Initial Goose and GooseWorks Setup

The following work was completed during the initial phase:

- Installed and explored Goose and GooseWorks.
- Tested Goose through the desktop application, terminal, VS Code, and communication-platform experiments.
- Studied how GooseWorks skills can be used for content creation.
- Created custom content-creation skill instructions.
- Created reusable instructions for blog and poster generation.
- Tested whether Goose correctly detects and follows the custom skill.
- Prepared prompts for generating blogs, birthday posters, festival posters, and other content.

### Result

Goose can understand content-generation requests and follow written instructions. However, skill-based poster generation alone is not sufficient for consistently producing professional designs.

---

## 3. Blog Content Workflow

A reusable blog-writing template was prepared with sections such as:

- Blog brief
- Audience
- Reader problem
- Article promise
- Primary keyword
- Content angle
- Headline options
- Final headline
- Introduction
- Main sections
- Conclusion
- Call to action

This template helps Goose produce structured and scan-friendly blog content instead of generating content in an inconsistent format.

---

## 4. Initial Poster Generation Using Goose Skills

Poster generation was first tested using GooseWorks skills and basic local template instructions.

The poster skill included rules for:

- Poster dimensions
- Headline placement
- Employee or event name
- Date placement
- Greeting text
- Company logo placement
- Background selection
- Text alignment
- Safe margins
- Content visibility
- Export format

### Issues Identified

The following problems occurred during poster generation:

- Text was sometimes misaligned.
- Text extended outside the poster frame.
- Some text was not fully visible.
- The company logo was recreated or modified instead of using the original logo file.
- The generated logo did not always match the official Kovan logo.
- Festival posters, such as Pongal posters, did not always receive suitable images.
- The generated layout was inconsistent between requests.
- The design quality was not suitable for every event type.
- Notes such as “greeting” could appear as visible poster text.
- The same generic design style was sometimes used for different events.

### Conclusion

GooseWorks skill instructions are useful for controlling content, but they are not enough to guarantee consistent visual design and alignment. Reusable design templates are required.

---

## 5. Kovan Brand Identity Rules

A separate brand identity instruction file was prepared to protect the company branding.

The brand setup includes three official logo variations:

1. Square logo
2. Horizontal logo
3. White logo

The skill was updated with rules to ensure that Goose or the design platform:

- Uses the original logo asset.
- Does not redraw, recreate, crop, distort, recolor, or regenerate the logo.
- Selects the correct logo based on the background.
- Uses the white horizontal logo on dark or strongly colored backgrounds.
- Maintains the original aspect ratio.
- Keeps sufficient clear space around the logo.
- Places the logo only in approved positions.
- Stops the workflow when the original logo asset is unavailable.

Additional poster rules were added to prevent:

- Text overflow
- Cropped text
- Content outside the safe area
- Overlapping text and images
- Unreadable text
- Accidental display of internal labels or notes

---

## 6. Canva Evaluation

Canva was initially evaluated as a template-based solution because direct poster generation caused layout and branding issues.

Canva was explored for:

- Creating reusable event templates
- Maintaining professional alignment
- Replacing only variable content
- Preserving the original company logo
- Exporting posters as PNG
- Supporting birthdays, work anniversaries, festivals, and company events

The Canva MCP extension was added temporarily to Goose and its available tools were inspected.

The intended Canva workflow was:

1. Receive a poster request.
2. Detect the event type.
3. Map the event type to a template prefix.
4. Search for matching templates.
5. Select a matching template.
6. Rotate between available templates.
7. Copy or open the selected template.
8. Replace variable content.
9. Apply the original Kovan logo.
10. Validate alignment and safe margins.
11. Export the final design as PNG.
12. Save it in the output folder.

---

## 7. Canva Limitations Identified

During testing, several Canva MCP issues were identified.

### Parameter Errors

```text
Only one of query or continuation should be supplied
```

```text
'continuation' must not be blank
```

```text
Invalid continuation: __OMIT__
```

These errors occurred because the MCP request sometimes included both `query` and `continuation`, or sent a blank or placeholder continuation value instead of omitting it.

### Effects of the Errors

Because the search or folder-listing calls failed:

- Matching template titles could not be retrieved reliably.
- Template counts were unavailable.
- A template could not be selected automatically.
- Canva design IDs could not be obtained consistently.
- Template rotation could not be completed.
- Automated editing and export could not proceed reliably.

### Additional Limitations

- Initial template setup required manual work.
- Templates had to be created, organized, and named carefully.
- Template discovery was sensitive to MCP request parameters.
- Automatic selection of reusable templates was unreliable.
- Design-ID mapping was difficult to complete.
- The workflow could not safely choose templates without a stable search result.
- Canva templates could not be used reliably for complete automation.

---

## 8. Final Decision: Discontinue Canva

Canva will not be used for the remaining project implementation.

It was evaluated as a possible template platform, but its limitations in template search, automatic selection, design-ID retrieval, pagination handling, and MCP request validation made the workflow difficult to automate consistently.

The project will now proceed with **Figma only**.

---

## 9. Figma Selected as the Final Design Platform

Figma has been selected as the sole design platform for all future poster-template work.

Figma will be used for:

- Creating reusable branded templates
- Maintaining fixed text and image placeholders
- Mapping event types to files, pages, frames, or component IDs
- Selecting the correct poster template
- Rotating between multiple approved templates
- Updating employee name, date, event title, message, and image
- Applying the original Kovan logo without alteration
- Validating alignment, safe margins, readability, and text overflow
- Exporting the final poster as PNG
- Saving the exported poster in the local output folder

---

## 10. Figma MCP Work Completed

The following work has been completed or started:

- Added or attempted to add the Figma MCP extension to Goose.
- Started the Figma developer MCP server manually using `npx`.
- Confirmed that the MCP server command launches successfully.
- Observed the image-directory warning.
- Identified the need to set an explicit image output directory.
- Tested whether Goose could see the Figma MCP tools.
- Began planning reusable Figma templates for different event categories.

Example server command:

```bash
npx -y figma-developer-mcp@latest \
  --figma-api-key=YOUR_FIGMA_API_KEY \
  --image-dir="/home/thansika/Documents/Content creation/output" \
  --stdio
```

### Current Figma Status

The Figma MCP server can be started manually, but its tools are not yet visible in the active Goose session.

The immediate requirement is to register the Figma MCP server correctly in Goose Desktop and verify that the extension is enabled and exposed to the current session.

---

## 11. Planned Figma Template Structure

Reusable Figma templates will be created for categories such as:

- Birthday
- Work anniversary
- Pongal
- Christmas
- New Year
- General festival wishes
- Company events
- Functions and celebrations

Each template should contain clearly named layers or components for:

- Event title
- Employee name
- Date
- Short greeting message
- Employee or event image
- Company logo
- Decorative background elements

Suggested naming format:

```text
KOVAN_TEMPLATE_BIRTHDAY_01
KOVAN_TEMPLATE_BIRTHDAY_02
KOVAN_TEMPLATE_WORK_ANNIVERSARY_01
KOVAN_TEMPLATE_PONGAL_01
KOVAN_TEMPLATE_CHRISTMAS_01
```

Suggested layer names:

```text
EVENT_TITLE
EMPLOYEE_NAME
EVENT_DATE
GREETING_MESSAGE
EMPLOYEE_IMAGE
KOVAN_LOGO
BACKGROUND
```

Consistent naming will allow Goose and Figma MCP to identify the correct elements and update them safely.

---

## 12. Planned Template Mapping

Each event type will be mapped to an approved Figma template or frame ID.

Example:

```text
birthday -> KOVAN_TEMPLATE_BIRTHDAY
work_anniversary -> KOVAN_TEMPLATE_WORK_ANNIVERSARY
pongal -> KOVAN_TEMPLATE_PONGAL
christmas -> KOVAN_TEMPLATE_CHRISTMAS
new_year -> KOVAN_TEMPLATE_NEW_YEAR
```

The stored mapping may include:

- Event key
- Figma file ID
- Page ID
- Frame ID
- Template name
- Current rotation index
- Total number of templates
- Next rotation index

---

## 13. Planned Template Rotation Logic

When multiple templates exist for the same event, the workflow should rotate between them.

Example:

```text
current_index = 0
selected_template = matching_templates[current_index]
next_index = (current_index + 1) % total_matching_templates
```

The rotation data should be stored locally so the same template is not selected every time.

The Canva rotation concept will be retained, but it will now use Figma file, page, frame, or component IDs.

---

## 14. Current Project Scope

The current project is focused only on the Figma workflow:

- Creating reusable Figma templates
- Naming files, pages, frames, components, and layers consistently
- Mapping event types to Figma template IDs
- Selecting the correct template
- Replacing variable poster content
- Protecting and placing the original company logo
- Validating poster layout and text visibility
- Exporting the final design as PNG
- Saving the output locally

Google Calendar integration, cron jobs, and automatic delivery are deferred until the Figma poster workflow becomes stable.

---

## 15. Work Completed So Far

### Content and Skill Work

- Explored GooseWorks content-creation capabilities.
- Created custom content-creation instructions.
- Prepared a reusable blog template.
- Prepared poster-generation rules.
- Added text-alignment and safe-margin rules.
- Added instructions to prevent internal notes from appearing on posters.
- Added strict original-logo usage rules.
- Prepared event-specific poster workflow instructions.

### Canva Evaluation Work

- Added Canva MCP temporarily for evaluation.
- Inspected Canva MCP tools.
- Created or started creating reusable Canva templates.
- Defined template naming conventions.
- Designed event-key mapping and rotation logic.
- Tested folder and design-search operations.
- Identified continuation-parameter validation issues.
- Documented why reliable automation could not be completed.
- Decided to discontinue Canva.

### Figma Work

- Selected Figma as the final and only design platform.
- Added or configured the Figma MCP server.
- Tested manual server startup.
- Confirmed that the Figma MCP command launches successfully.
- Identified the need for an explicit image export directory.
- Identified that Goose is not yet exposing the Figma tools.
- Planned reusable Figma templates.
- Planned event-to-template mapping.
- Planned template rotation using Figma IDs.

### Testing and Documentation

- Prepared test prompts for Goose.
- Tested non-mutating MCP calls.
- Documented exact Canva MCP errors.
- Compared skill-based generation with template-based generation.
- Identified current blockers and next implementation steps.

---

## 16. Current Status

| Area | Status |
|---|---|
| Goose installation and exploration | Completed |
| GooseWorks content skill | Completed |
| Blog template | Completed |
| Poster-generation skill rules | Completed |
| Brand and logo rules | Completed |
| Canva MCP evaluation | Completed |
| Canva as final platform | Rejected due to limitations |
| Figma selected as final platform | Completed |
| Figma MCP server startup | Tested |
| Figma MCP registration in Goose | In progress |
| Figma tools inside Goose | Not yet available |
| Reusable Figma templates | Planned / in progress |
| Event-to-Figma-template mapping | Pending |
| Template rotation in Figma | Pending |
| Poster editing through Figma MCP | Pending |
| Poster validation | Pending |
| Poster PNG export automation | Pending |
| Calendar and cron automation | Deferred |

---

## 17. Current Blockers

The current blockers are:

1. Figma MCP tools are not yet visible inside the active Goose session.
2. The Figma MCP server must be registered correctly in Goose Desktop.
3. The reusable Figma template structure has not yet been finalized.
4. Event types have not yet been mapped to Figma file, page, frame, or component IDs.
5. Template rotation has not yet been implemented using Figma IDs.
6. Automated content replacement has not yet been tested.
7. The final validation and PNG export workflow has not yet been completed.

The earlier Canva issues are no longer active implementation blockers because Canva has been removed from the final workflow.

---

## 18. Next Steps

1. Register the Figma MCP server correctly in Goose Desktop.
2. Confirm that all required Figma MCP tools are visible in the Goose session.
3. Set an explicit image export directory.
4. Create reusable Figma templates for every required event category.
5. Define a consistent naming convention for files, pages, frames, components, and layers.
6. Add fixed placeholders for name, date, event title, greeting, employee image, and company logo.
7. Map each event key to the correct Figma template or frame ID.
8. Implement template-selection and rotation logic using Figma IDs.
9. Test updating one birthday template through Goose.
10. Add the original Kovan logo without modifying it.
11. Validate text overflow, alignment, readability, safe margins, and image placement.
12. Export the completed poster as PNG.
13. Save the exported poster in the local poster output folder.
14. Add calendar reading and scheduled automation only after the Figma workflow is stable.

---

## 19. Expected Final Workflow

```text
User request
    ↓
Detect poster or event type
    ↓
Map event key to Figma template/frame ID
    ↓
Select an approved Kovan Figma template
    ↓
Apply template rotation when multiple designs are available
    ↓
Open or duplicate the selected Figma frame
    ↓
Replace variable content
    ↓
Insert the original Kovan logo
    ↓
Validate text, margins, images, and branding
    ↓
Export as PNG
    ↓
Save in the local output folder
```

---

## 20. Project Outcome So Far

The project has progressed from basic AI-generated posters to a controlled template-based automation design.

The key finding is that GooseWorks skills are effective for defining content and rules, but professional poster generation requires reusable templates and strict asset handling.

Canva was evaluated but rejected because its MCP workflow introduced limitations in template search, automatic selection, design-ID retrieval, pagination handling, and request validation.

Figma has now been selected as the sole design platform for the remaining project implementation.

The immediate goal is to complete Figma MCP registration, reusable template creation, event-to-template mapping, automated content replacement, validation, and PNG export before adding scheduling or calendar-based automation.
