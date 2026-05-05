"""OpenHands parser: output.jsonl -> {instance_id: [{thought, action, result}]}."""

import json
from typing import Any, Dict, List


def _read_jsonl(path: str) -> List[dict]:
    rows = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError as e:
                print(f"[openhands parser] skipping malformed line: {e}")
    return rows


def _build_iterations(history_entry: dict) -> List[Dict[str, Any]]:
    agent_turns = [
        h for h in history_entry["history"]
        if h.get("source") == "agent" and "content" in h and "tool_call_metadata" in h
    ]
    iterations = []
    for h in agent_turns:
        msg = h["tool_call_metadata"]["model_response"]["choices"][0]["message"]
        # Render None as "None" to match the published files.
        thought = str(msg.get("content"))
        tool_calls = msg.get("tool_calls") or []
        action = tool_calls[0]["function"] if tool_calls else {}
        iterations.append({"thought": thought, "action": action, "result": h["content"]})
    return iterations


def parse_file(jsonl_path: str) -> Dict[str, List[Dict[str, Any]]]:
    return {entry["instance_id"]: _build_iterations(entry) for entry in _read_jsonl(jsonl_path)}
