from __future__ import annotations
import os
import sys
import time
from typing import Optional
from src.engine import load_default_engine, StoryError
from src.validator import validate

# Default story path (relative to project root)
STORY_PATH = os.path.join(
    os.path.dirname(__file__), '..', 'stories', 'sample_story.json'
)

INTRO = (
    "Text Adventure (Prototype)\n"
    "Type the choice id or number. Type 'inv' for inventory,\n"
    "'state' for flags/stats, 'quit' to exit.\n"
)


def main():
    # Allow overriding story path and start id via command-line args:
    #   python -m src.cli <story_path> <start_id>
    story_path = os.path.abspath(STORY_PATH)
    start_id = 'intro'
    if len(sys.argv) >= 2:
        story_path = os.path.abspath(sys.argv[1])
    if len(sys.argv) >= 3:
        start_id = sys.argv[2]

    engine = load_default_engine(story_path, start_id)
    print(INTRO)
    last_auto: Optional[str] = None
    while True:
        scene = engine.current_scene()
        print(f"\n== {scene.id.upper()} ==")
        print(scene.text)
        if engine.state.ended:
            print(f"\n*** THE END ({engine.state.ending_code}) ***")
            break
        auto = engine.process_timeouts()
        if auto and auto != last_auto:
            print(f"[Timed auto] {auto}")
            last_auto = auto
            continue
        choices = engine.list_choices()
        actionable = []
        for idx, c in enumerate(choices, start=1):
            enabled = True
            if c.type == 'gated':
                # gated: show but maybe disabled
                cond_pass = all(
                    engine.expr_ctx.resolve(expr) for expr in c.conditions
                )
                if not cond_pass:
                    enabled = False
            label = c.label if enabled else f"{c.label} [LOCKED]"
            print(f" {idx}. {label} (id={c.id})")
            actionable.append((idx, c, enabled))
        cmd = input("> ").strip()
        if cmd.lower() in ("quit", "exit"):
            print("Goodbye")
            break
        if cmd.lower().startswith('wait'):
            parts = cmd.split()
            ms = 500
            if len(parts) > 1 and parts[1].isdigit():
                ms = int(parts[1])
            time.sleep(ms / 1000.0)
            continue
        if cmd.lower() == 'inv':
            inv = engine.state.inventory
            if not inv:
                print("(inventory empty)")
            else:
                for k, v in inv.items():
                    print(f" - {k} x{v}")
            continue
        if cmd.lower() == 'state':
            print("Flags:", engine.state.flags)
            print("Stats:", engine.state.stats)
            print("Reputation:", engine.state.reputation)
            continue
        if cmd.lower().startswith('validate'):
            parts = cmd.split()
            maxc = 12
            if len(parts) > 1 and parts[1].isdigit():
                maxc = int(parts[1])
            issues = validate(engine.scenes, engine.state.scene_id, max_choices=maxc)
            if not issues:
                print("Validation: OK")
            else:
                print("Validation issues:")
                for issue in issues:
                    print(" -", issue)
            continue
        # Allow number or id
        chosen = None
        if cmd.isdigit():
            num = int(cmd)
            for (n, c, enabled) in actionable:
                if n == num:
                    if not enabled:
                        print("That choice is locked.")
                        break
                    chosen = c.id
                    break
        else:
            chosen = cmd
        if not chosen:
            print("Invalid input")
            continue
        try:
            engine.choose(chosen)
        except StoryError as e:
            print(f"Error: {e}")
            continue

if __name__ == '__main__':
    main()

