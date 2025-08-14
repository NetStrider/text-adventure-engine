"""Story validation utilities.

Checks:
* Start scene exists
* Unreachable scenes
* Dead choice targets
* Excessive choices per scene
* Duplicate choice ids within a scene
* Dangling scenes (no choices & no endings)
* Scenes mixing endings and choices
"""
from __future__ import annotations

from typing import Dict, List, Set
from src.engine import Scene


def validate(scenes: Dict[str, Scene], start_id: str, max_choices: int = 12) -> List[str]:
    issues: List[str] = []
    if start_id not in scenes:
        issues.append(f"Start scene '{start_id}' missing")
        return issues
    visited: Set[str] = set()
    queue: List[str] = [start_id]
    while queue:
        cur = queue.pop(0)
        if cur in visited:
            continue
        visited.add(cur)
        for c in scenes[cur].choices:
            if c.target and c.target in scenes and c.target not in visited:
                queue.append(c.target)
    for sid in scenes:
        if sid not in visited:
            issues.append(f"Scene '{sid}' unreachable from start '{start_id}'")
    for scene in scenes.values():
        seen_choice_ids: Set[str] = set()
        for c in scene.choices:
            if c.id in seen_choice_ids:
                issues.append(f"Duplicate choice id '{c.id}' in scene '{scene.id}'")
            seen_choice_ids.add(c.id)
            if c.target and c.target not in scenes:
                issues.append(f"Choice '{c.id}' in scene '{scene.id}' targets missing scene '{c.target}'")
        if len(scene.choices) > max_choices:
            issues.append(f"Scene '{scene.id}' has {len(scene.choices)} choices (>{max_choices})")
        if not scene.choices and not scene.endings:
            issues.append(f"Scene '{scene.id}' has no choices and no endings (dangling dead-end)")
        if scene.endings and scene.choices:
            issues.append(f"Scene '{scene.id}' has endings and choices (ambiguous terminal)")
    return issues

__all__ = ["validate"]
