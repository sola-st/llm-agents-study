"""CLI: python -m parsers {acr|oh|ra} --... --out trajectories/<agent>/parsed."""

import argparse
import os
import sys

from . import autocoderover, openhands, repairagent
from .serialize import serialize_instance


def _cmd_acr(args: argparse.Namespace) -> int:
    if not os.path.isdir(args.raw_root):
        print(f"raw root not found: {args.raw_root}", file=sys.stderr)
        return 2
    instances = args.instances
    if not instances:
        # Strip timestamps from <instance>_<timestamp>/ folder names.
        seen = set()
        bare = []
        for d in sorted(os.listdir(args.raw_root)):
            if not os.path.isdir(os.path.join(args.raw_root, d)):
                continue
            stem = d.rsplit("_2", 1)[0] if "_2" in d else d
            if stem not in seen:
                seen.add(stem)
                bare.append(stem)
        instances = bare

    n_ok = n_err = 0
    for inst in instances:
        try:
            iters = autocoderover.parse_instance(args.raw_root, inst)
        except Exception as e:
            print(f"[acr] {inst}: FAILED ({e})", file=sys.stderr)
            n_err += 1
            continue
        serialize_instance(inst, iters, "acr", args.out)
        print(f"[acr] {inst}: {len(iters)} iterations")
        n_ok += 1
    print(f"[acr] done: ok={n_ok} err={n_err}")
    return 0 if n_err == 0 else 1


def _cmd_oh(args: argparse.Namespace) -> int:
    if not os.path.isfile(args.jsonl):
        print(f"jsonl not found: {args.jsonl}", file=sys.stderr)
        return 2
    parsed = openhands.parse_file(args.jsonl)
    n_ok = 0
    for instance_id, iters in parsed.items():
        if args.instances and instance_id not in set(args.instances):
            continue
        serialize_instance(instance_id, iters, "oh", args.out)
        print(f"[oh] {instance_id}: {len(iters)} iterations")
        n_ok += 1
    print(f"[oh] done: ok={n_ok}")
    return 0


def _cmd_ra(args: argparse.Namespace) -> int:
    if not os.path.isdir(args.logs_dir):
        print(f"logs dir not found: {args.logs_dir}", file=sys.stderr)
        return 2
    parsed = repairagent.parse_directory(args.logs_dir)
    n_ok = 0
    for instance_id, iters in parsed.items():
        if args.instances and instance_id not in set(args.instances):
            continue
        # 'experiment_*' files were produced by an older formatter; auto-route them.
        if args.format == "auto":
            agent = "ra_old" if instance_id.startswith("experiment_") else "ra"
        else:
            agent = args.format
        serialize_instance(instance_id, iters, agent, args.out)
        print(f"[{agent}] {instance_id}: {len(iters)} iterations")
        n_ok += 1
    print(f"[ra] done: ok={n_ok}")
    return 0


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="parsers", description="Parse agent trajectories.")
    sub = p.add_subparsers(dest="agent", required=True)

    p_acr = sub.add_parser("acr", help="AutoCodeRover")
    p_acr.add_argument("--raw-root", required=True, help="dir containing <instance>_<timestamp>/ folders")
    p_acr.add_argument("--instances", nargs="*", default=[], help="optional instance ids; default = all")
    p_acr.add_argument("--out", required=True, help="output parsed/ root")
    p_acr.set_defaults(func=_cmd_acr)

    p_oh = sub.add_parser("oh", help="OpenHands / CodeActAgent")
    p_oh.add_argument("--jsonl", required=True, help="path to OpenHands output.jsonl")
    p_oh.add_argument("--instances", nargs="*", default=[], help="optional instance id filter")
    p_oh.add_argument("--out", required=True, help="output parsed/ root")
    p_oh.set_defaults(func=_cmd_oh)

    p_ra = sub.add_parser("ra", help="RepairAgent")
    p_ra.add_argument("--logs-dir", required=True, help="dir of RepairAgent text logs")
    p_ra.add_argument("--instances", nargs="*", default=[], help="optional instance id filter")
    p_ra.add_argument("--out", required=True, help="output parsed/ root")
    p_ra.add_argument("--format", choices=["auto", "ra", "ra_old"], default="auto",
                      help="auto routes experiment_* to ra_old, else ra")
    p_ra.set_defaults(func=_cmd_ra)

    args = p.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
