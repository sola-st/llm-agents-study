"""Serialize iteration dicts into the 5 relationship-pair text views per agent."""

import os
from typing import Any, Dict, Iterable, List


_AGENT_CONFIG = {
    "acr": {
        "ext": "",
        "iter_word_ta": "Iteration",
        "iter_word_other": "Iteration",
        "action_folder": "action_actions",
        "list_sep": "\n\n",
        "pair_sep": "\n\n",
        "results_pair_sep": "\n\n",
        "trailing": "\n\n",
        "use_inline_next": False,
        "drop_dangling_last_result": True,
    },
    "oh": {
        "ext": ".txt",
        "iter_word_ta": "Iteration",
        "iter_word_other": "iteration",
        "action_folder": "actions_actions",
        "list_sep": "\n",
        "pair_sep": "\n---\n",
        "results_pair_sep": "\n---\n",
        "trailing": "",
        "use_inline_next": True,
        "drop_dangling_last_result": False,
    },
    "ra": {
        "ext": "",
        "iter_word_ta": "Iteration",
        "iter_word_other": "iteration",
        "action_folder": "actions_actions",
        "list_sep": "\n",
        "pair_sep": "\n---\n",
        "results_pair_sep": "\n---\n",
        "trailing": "",
        "use_inline_next": True,
        "drop_dangling_last_result": False,
    },
    "ra_old": {
        "ext": "",
        "iter_word_ta": "iteration",
        "iter_word_other": "iteration",
        "action_folder": "actions_actions",
        "list_sep": "\n",
        "pair_sep": "\n---\n",
        "results_pair_sep": "\n---\n",
        "trailing": "\n",
        "use_inline_next": True,
        "drop_dangling_last_result": False,
        "old_style": True,
    },
}


def _action_repr(action: Any) -> str:
    return action if isinstance(action, str) else str(action)


def _format_thoughts_actions(iters: List[Dict[str, Any]], cfg: dict) -> str:
    word = cfg["iter_word_ta"]
    if cfg["use_inline_next"]:
        prefix = "Thought and Action at" if cfg.get("old_style") else ""
        rows = []
        for i, it in enumerate(iters):
            head = f"{prefix} {word} {i}:" if prefix else f"{word.capitalize()} {i}:"
            rows.append(
                f"{head} Thought={it.get('thought', '')}; "
                f"Action={_action_repr(it.get('action', ''))}"
            )
        joined = cfg["pair_sep"].join(rows)
        suffix = cfg["pair_sep"] if cfg.get("old_style") else cfg["trailing"]
        return joined + suffix
    blocks = [
        f"Thought at {word} {i}: {it.get('thought', '')}\n"
        f"Action at {word} {i}: {_action_repr(it.get('action', ''))}"
        for i, it in enumerate(iters)
    ]
    return cfg["pair_sep"].join(blocks) + cfg["trailing"]


def _format_singleton_list(iters: List[Dict[str, Any]], cfg: dict, field: str, label: str) -> str:
    word = cfg["iter_word_other"]
    label_disp = "Though" if cfg.get("old_style") and field == "thought" else label
    rows = []
    for i, it in enumerate(iters):
        value = it.get(field, "")
        if field == "action":
            value = _action_repr(value)
        rows.append(f"{label_disp} at {word} {i}: {value}")
    return cfg["list_sep"].join(rows) + cfg["trailing"]


def _format_result_paired_with_next(
    iters: List[Dict[str, Any]], cfg: dict, next_field: str, next_label: str,
) -> str:
    word = cfg["iter_word_other"]
    n = len(iters)

    if cfg["use_inline_next"]:
        old = cfg.get("old_style", False)
        end_sentinel = "END OF TRAJECTORY" if old else "END"
        rows = []
        for i, it in enumerate(iters):
            if i + 1 < n:
                nxt = iters[i + 1].get(next_field, "")
                if next_field == "action":
                    nxt = _action_repr(nxt)
            else:
                nxt = end_sentinel
            if old:
                suffix = f"; {next_label.capitalize()} at {word}{i + 1} : {nxt}"
            else:
                suffix = f"; Next {next_label}: {nxt}"
            rows.append(f"Result at {word} {i}: {it.get('result', '')}{suffix}")
        joined = cfg["results_pair_sep"].join(rows)
        end = cfg["results_pair_sep"] if old else cfg["trailing"]
        return joined + end

    # ACR: interleave Result_i + next-element on separate lines; drop dangling final result.
    blocks = []
    upper = n - 1 if cfg["drop_dangling_last_result"] else n
    for i in range(upper):
        if i + 1 >= n:
            break
        nxt = iters[i + 1].get(next_field, "")
        if next_field == "action":
            nxt = _action_repr(nxt)
        blocks.append(
            f"Result at {word} {i}: {iters[i].get('result', '')}\n"
            f"{next_label.capitalize()} at {word} {i + 1}: {nxt}"
        )
    return cfg["results_pair_sep"].join(blocks) + cfg["trailing"]


def _write(path: str, text: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


def serialize_instance(
    instance_id: str, iterations: List[Dict[str, Any]], agent: str, parsed_root: str,
) -> Dict[str, str]:
    if agent not in _AGENT_CONFIG:
        raise ValueError(f"unknown agent {agent!r}; expected one of {list(_AGENT_CONFIG)}")
    cfg = _AGENT_CONFIG[agent]
    ext = cfg["ext"]

    views = {
        "thoughts_actions": _format_thoughts_actions(iterations, cfg),
        "thoughts_thoughts": _format_singleton_list(iterations, cfg, "thought", "Thought"),
        cfg["action_folder"]: _format_singleton_list(iterations, cfg, "action", "Action"),
        "results_actions": _format_result_paired_with_next(iterations, cfg, "action", "action"),
        "results_thoughts": _format_result_paired_with_next(iterations, cfg, "thought", "thought"),
    }

    written = {}
    for view, content in views.items():
        path = os.path.join(parsed_root, view, f"{instance_id}{ext}")
        _write(path, content)
        written[view] = path
    return written


def serialize_many(instances: Iterable[tuple], agent: str, parsed_root: str) -> None:
    for instance_id, iters in instances:
        serialize_instance(instance_id, iters, agent, parsed_root)
