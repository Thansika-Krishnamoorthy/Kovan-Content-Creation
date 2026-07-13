# Modular Canva Poster Skill

Keep `SKILL.md` as the only main skill entry point.

The files inside `workflows/` are workflow modules referenced by the main skill. This is safer than registering six separate skills because Goose has one clear trigger and one controlled execution order.

Copy this folder into your Goose skills location, preserving the folder structure.

Do not move the workflow files away from `SKILL.md` unless you also update the references.
