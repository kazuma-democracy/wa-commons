from __future__ import annotations

import argparse

from .identity.jpx_snapshot import build_pilot, write_pilot


def main() -> None:
    parser = argparse.ArgumentParser(prog="wa-commons")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("build-jpx-pilot", help="Build a reproducible JPX identity pilot")
    p.add_argument("snapshot_file")
    p.add_argument("output")
    p.add_argument("--snapshot", required=True)
    p.add_argument("--source-url", required=True)
    p.add_argument("--retrieved-at", required=True)
    p.add_argument("--limit", type=int, default=100)

    args = parser.parse_args()
    if args.command == "build-jpx-pilot":
        payload = build_pilot(
            args.snapshot_file,
            snapshot=args.snapshot,
            source_url=args.source_url,
            retrieved_at=args.retrieved_at,
            limit=args.limit,
        )
        write_pilot(payload, args.output)
        print(f"wrote {payload['manifest']['entity_count']} entities to {args.output}")


if __name__ == "__main__":
    main()
