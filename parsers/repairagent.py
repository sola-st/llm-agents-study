"""RepairAgent parser: ASSISTANT/USER text log -> [{thought, action, result}]."""

import json
import os
import re
from typing import Any, Dict, List, Tuple


_ASSIST = "--------------- ASSISTANT ----------------"
_USER = "------------------ USER ------------------"
_END = "=========================================="

_PROMPT_HISTORY_RE = re.compile(r"^prompt_history_")


def _instance_id_from_filename(fname: str) -> str:
    # Strip 'prompt_history_' but keep 'experiment_<n>_' (matches published filenames).
    return _PROMPT_HISTORY_RE.sub("", os.path.splitext(fname)[0])


def _split_sections(log_text: str) -> List[Tuple[str, str]]:
    # keepends=True preserves trailing newlines that the published files rely on.
    pairs: List[Tuple[str, str]] = []
    assistant_buf, user_buf = [], []
    in_assistant = in_user = False

    for line in log_text.splitlines(keepends=True):
        bare = line.rstrip("\n")
        if _ASSIST in bare:
            in_assistant, in_user = True, False
            assistant_buf = []
        elif _USER in bare:
            in_assistant, in_user = False, True
            user_buf = []
        elif _END in bare:
            if assistant_buf and user_buf:
                pairs.append(("".join(assistant_buf), "".join(user_buf)))
            in_assistant = in_user = False
            assistant_buf, user_buf = [], []
        elif in_assistant:
            assistant_buf.append(line)
        elif in_user:
            user_buf.append(line)
    return pairs


def _try_load_json(text: str) -> Dict[str, Any] | None:
    s = text.strip()
    if not (s.startswith("{") and s.endswith("}")):
        return None
    try:
        return json.loads(s)
    except json.JSONDecodeError:
        return None


def parse_text(log_text: str) -> List[Dict[str, Any]]:
    iterations: List[Dict[str, Any]] = []
    for assistant_block, user_block in _split_sections(log_text):
        emitted = _try_load_json(assistant_block)
        if not emitted:
            continue
        thought = emitted.pop("thoughts", "") or emitted.pop("thought", "")
        # Unwrap the "command" wrapper so the action matches the published shape.
        action = emitted.get("command", emitted)
        iterations.append({"thought": thought, "action": action, "result": user_block})
    return iterations


def parse_file(log_path: str) -> List[Dict[str, Any]]:
    with open(log_path, "r", encoding="utf-8") as f:
        return parse_text(f.read())


def parse_directory(logs_dir: str) -> Dict[str, List[Dict[str, Any]]]:
    out = {}
    for fname in sorted(os.listdir(logs_dir)):
        path = os.path.join(logs_dir, fname)
        if not os.path.isfile(path):
            continue
        out[_instance_id_from_filename(fname)] = parse_file(path)
    return out
