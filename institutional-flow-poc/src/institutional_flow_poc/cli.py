import argparse
import json
from pathlib import Path

from .metrics import DEFAULT_GROUPS
from .pipeline import analyze_data, fetch_data, process_data, report_data
from .web_payload import export_web_data


def build_parser():
    parser = argparse.ArgumentParser(description="TWSE institutional flow PoC")
    subparsers = parser.add_subparsers(dest="command", required=True)
    for name in ("fetch", "run"):
        command = subparsers.add_parser(name)
        command.add_argument("--days", type=int, default=120)
        command.add_argument("--end-date")
    subparsers.add_parser("process")
    analyze = subparsers.add_parser("analyze")
    analyze.add_argument("--groups", default=",".join(DEFAULT_GROUPS), help="法人組合，以逗號分隔；可用 foreign,trust,dealer,combined,all 或以 + 自由組合")
    analyze.add_argument("--basis", choices=("shares", "amount"), default="shares")
    analyze.add_argument("--compare-basis", choices=("shares", "amount"))
    subparsers.add_parser("report")
    subparsers.add_parser("export-web")
    return parser


def main(argv=None):
    args = build_parser().parse_args(argv)
    if args.command in {"fetch", "run"}:
        print(json.dumps(fetch_data(args.days, args.end_date), ensure_ascii=False))
    if args.command in {"process", "run"}:
        print(json.dumps(process_data(), ensure_ascii=False))
    if args.command in {"analyze", "run"}:
        groups = tuple(item.strip() for item in getattr(args, "groups", ",".join(DEFAULT_GROUPS)).split(",") if item.strip())
        print(json.dumps(analyze_data(groups=groups, basis=args.basis, compare_basis=args.compare_basis), ensure_ascii=False))
    if args.command in {"report", "run"}:
        print(json.dumps(report_data(), ensure_ascii=False))
    if args.command == "export-web":
        path = export_web_data(Path("outputs"), Path("web/data"))
        print(json.dumps({"path": str(path), "success": True, "failure": []}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
