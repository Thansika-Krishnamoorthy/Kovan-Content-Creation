#!/usr/bin/env python3
"""Validate config/figma_template_map.json integrity and exercise rotation.

Run:  python3 scripts/validate_figma_template_map.py
Exit code 0 = OK, 1 = integrity error.
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MAP = os.path.join(ROOT, "config", "figma_template_map.json")


def select_frame(entry, current_index):
    total = len(entry["frames"])
    assert total > 0, f"event with no frames: {entry}"
    idx = current_index % total
    frame = entry["frames"][idx]
    next_index = (idx + 1) % total
    return frame["name"], frame["frame_id"], idx, total, next_index


def main():
    with open(MAP, "r", encoding="utf-8") as fh:
        data = json.load(fh)

    events = data["events"]
    print(f"schema_version : {data.get('schema_version')}")
    print(f"event count    : {len(events)}")
    print(f"figma file_id  : {data['figma_project']['file_id']}")
    print()

    errors = []
    for key, entry in sorted(events.items()):
        total = len(entry["frames"])
        exp_next = (entry["current_index"] + 1) % total if total else 0
        if entry["total_templates"] != total:
            errors.append(f"{key}: total_templates={entry['total_templates']} != frames={total}")
        if entry["next_index"] != exp_next:
            errors.append(f"{key}: next_index={entry['next_index']} != expected={exp_next}")
        for fr in entry["frames"]:
            if "PLACEHOLDER" in fr["frame_id"].upper():
                print(f"  [PLACEHOLDER] {key}: frame '{fr['name']}' has no real Figma ID yet")

    if errors:
        print("\nINTEGRITY ERRORS:")
        for e in errors:
            print("  -", e)
        sys.exit(1)

    # Exercise rotation on the only multi-template event (birthday).
    print("\nRotation demo (birthday has 2 templates):")
    entry = events["birthday"]
    for i in range(4):
        name, fid, idx, total, nxt = select_frame(entry, i)
        print(f"  run index {i}: frame={name} (idx {idx} of {total}) -> next={nxt}")

    print("\nOK: figma_template_map.json is valid and rotation-consistent.")


if __name__ == "__main__":
    main()
