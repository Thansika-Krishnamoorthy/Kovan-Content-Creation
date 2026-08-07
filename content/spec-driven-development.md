# Spec-Driven Development

## What is Spec-Driven Development?

**Spec-driven development** means writing a clear **specification (spec)** of what a system should do **before writing the implementation code**.

The specification becomes the main reference for developers, AI coding agents, testers, and stakeholders.

## Simple Flow

```text
Idea → Specification → Development → Testing → Final Product
```

## What a Specification Usually Defines

A specification usually explains:

- What problem the system solves
- Required features
- Inputs and expected outputs
- Business rules
- User workflows
- Technical constraints
- Error-handling behaviour
- Acceptance criteria

## Example

Suppose you want to build an automated blog generator.

A simple specification might look like this:

```md
# Feature: Generate a Blog from a Markdown File

## Input

- A Markdown file containing the blog content
- A selected HTML template

## Requirements

1. Read the title, headings, paragraphs, and images.
2. Insert the content into the selected template.
3. Preserve the template's colours and layout.
4. Generate a responsive HTML page.
5. Save the output inside the `output/blogs` folder.

## Error Handling

- Show an error if the Markdown file does not exist.
- Show an error if the selected template is unavailable.

## Acceptance Criteria

- The generated page must open correctly in a browser.
- All Markdown sections must appear in the output.
- The layout must work on desktop and mobile.
```

Only after agreeing on this specification would development begin.

## Traditional Development vs Spec-Driven Development

| Traditional Approach | Spec-Driven Approach |
|---|---|
| Start coding from a general idea | Define requirements before coding |
| Requirements may remain informal | Requirements are documented clearly |
| Testing decisions come later | Acceptance criteria are defined early |
| Developers may interpret things differently | Everyone follows the same specification |
| Changes can become confusing | Changes are made by updating the specification |

## Why It Is Useful with AI Coding Agents

When using tools such as Codex, GitHub Copilot, Claude Code, Goose, or Antigravity, a detailed specification helps the agent:

- Understand the complete requirement
- Generate more accurate code
- Avoid making unwanted assumptions
- Follow folder structures and naming rules
- Apply branding and validation rules consistently
- Check whether the generated result meets the requirements

Instead of giving a simple prompt such as:

> Create a blog generator.

You can provide a detailed specification:

> Build a Python application that reads Markdown files from `content/`, applies one of three templates from `templates/`, generates responsive HTML in `output/blogs/`, preserves code blocks and images, and reports missing files clearly.

This produces a more predictable result.

## Prompt vs Specification

A **prompt** tells the AI what to do at that moment.

A **specification** describes the complete behaviour, constraints, and expected result of the system.

A specification can be used repeatedly throughout the development process:

```text
Plan → Generate Code → Review Code → Test → Verify Completion
```

## Conclusion

In simple terms, **spec-driven development means deciding and documenting exactly what must be built before deciding how to build it.**
