"""AutoCodeRover parser: role/content messages -> [{thought, action, result}]."""

import json
import os
import re
from typing import Any, Dict, List


_SEARCH_NAMES = (
    "search_code_in_file",
    "search_code",
    "search_method_in_class",
    "search_method_in_file",
    "search_method",
    "search_class_in_file",
    "search_class",
    "get_class_full_snippet",
)


def _find_search_calls(text: str) -> List[str]:
    """Balanced search_*(...) extractor that tolerates nested parens in string args."""
    out: List[str] = []
    n = len(text)
    i = 0
    while i < n:
        best = -1
        best_name = None
        for name in _SEARCH_NAMES:
            idx = text.find(name, i)
            if idx >= 0 and (best < 0 or idx < best):
                best = idx
                best_name = name
        if best < 0:
            break
        end_name = best + len(best_name)
        if end_name >= n or text[end_name] != "(":
            i = end_name
            continue
        depth = 1
        j = end_name + 1
        in_str = None
        while j < n and depth > 0:
            ch = text[j]
            if in_str:
                if ch == "\\":
                    j += 2
                    continue
                if ch == in_str:
                    in_str = None
            elif ch in ('"', "'"):
                in_str = ch
            elif ch == "(":
                depth += 1
            elif ch == ")":
                depth -= 1
            j += 1
        if depth == 0:
            out.append(text[best:j])
            i = j
        else:
            i = j
    return out


def _has_bare_search_lines(text: str) -> bool:
    return any(ln.strip().startswith("search_") for ln in text.splitlines())


def _parse_rounds(logs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    rounds = []
    for i, msg in enumerate(logs):
        if msg["role"] != "assistant":
            continue
        prev_user = None
        for j in range(i - 1, -1, -1):
            if logs[j]["role"] == "user":
                prev_user = logs[j]
                break
        next_user = logs[i + 1] if i + 1 < len(logs) and logs[i + 1]["role"] == "user" else None
        rounds.append({"assistant": msg, "user_prompt": prev_user, "user_feedback": next_user})
    return rounds


def _extract_search_actions(text: str) -> str:
    # Bare-line lists join with ';' (matches original parse_acr); prose-embedded calls use ', '.
    if _has_bare_search_lines(text):
        bare = [ln.strip().rstrip(";") for ln in text.splitlines() if ln.strip().startswith("search_")]
        return ";".join(bare)
    seen = set()
    out = []
    for m in _find_search_calls(text):
        if m not in seen:
            seen.add(m)
            out.append(m)
    return ", ".join(out)


_ERROR_PHRASES = (
    "I'm here to assist within the constraints of our interaction",
    "I'm here to assist based on the information provided",
    "I'm here to provide analysis and insights",
)


def _classify_round(round_data: Dict[str, Any]) -> Dict[str, str]:
    assistant_text = round_data["assistant"]["content"]
    prompt_text = round_data["user_prompt"]["content"] if round_data["user_prompt"] else ""
    feedback_text = round_data["user_feedback"]["content"] if round_data["user_feedback"] else ""

    thought = assistant_text.strip()

    if any(p in assistant_text for p in _ERROR_PHRASES) or assistant_text.startswith(("I'm ", "I ")):
        return {"thought": thought, "action": "ErrorResponse",
                "result": "The assistant indicated a limitation in responding."}

    if "# modification" in assistant_text.lower():
        return {"thought": thought, "action": "write_patch",
                "result": "The result is contained in the reasoning"}

    # Search beats Locate/Analyze when the assistant emits actual search calls.
    if _find_search_calls(assistant_text) or _has_bare_search_lines(assistant_text):
        return {"thought": thought, "action": _extract_search_actions(assistant_text),
                "result": feedback_text.rstrip()}

    if (
        "where are bug locations" in prompt_text
        or "The buggy locations is not precise" in prompt_text
        or "Buggy Files and Methods" in assistant_text
        or re.search(r"(?i)bug locations:", assistant_text)
    ):
        return {"thought": thought, "action": "Locate",
                "result": "The result is contained in the reasoning"}

    if (
        "Let's analyze" in prompt_text
        or assistant_text.strip().startswith("Analyzing")
        or "Based on the search results" in assistant_text
    ):
        return {"thought": thought, "action": "Analyze",
                "result": "The result is contained in the reasoning"}

    if "below search API" in prompt_text:
        return {"thought": thought, "action": _extract_search_actions(assistant_text),
                "result": feedback_text.rstrip()}

    if "The buggy locations is not precise" in feedback_text:
        return {"thought": thought, "action": "Locate",
                "result": "The buggy locations is not precise. You may need to check whether "
                          "the arguments are correct and search more information."}

    return {"thought": thought, "action": "Analyze",
            "result": "The result is contained in the reasoning"}


def parse_messages(messages: List[Dict[str, Any]]) -> List[Dict[str, str]]:
    return [_classify_round(r) for r in _parse_rounds(messages)]


def parse_file(trajectory_file: str) -> List[Dict[str, str]]:
    with open(trajectory_file) as f:
        return parse_messages(json.load(f))


def find_latest_patch_file(instance_dir: str) -> str:
    candidates = [f for f in os.listdir(instance_dir) if f.startswith("debug_agent_write_patch_")]
    if not candidates:
        raise FileNotFoundError(f"No debug_agent_write_patch_* file in {instance_dir}")
    return os.path.join(instance_dir, sorted(candidates)[-1])


def find_instance_dir(raw_root: str, instance_id: str) -> str:
    candidates = [d for d in os.listdir(raw_root) if d.startswith(instance_id)]
    if not candidates:
        raise FileNotFoundError(f"No folder starting with {instance_id} in {raw_root}")
    return os.path.join(raw_root, sorted(candidates)[-1])


def parse_instance(raw_root: str, instance_id: str) -> List[Dict[str, str]]:
    return parse_file(find_latest_patch_file(find_instance_dir(raw_root, instance_id)))
