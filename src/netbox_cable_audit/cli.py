import argparse
import os
import sys
from collections import Counter
from netbox_cable_audit.collectors.json import LldpInputError
from netbox_cable_audit.netbox import NetBoxClient, NetBoxError
from netbox_cable_audit.runner import run_audit

def _format_remote(device: str | None, interface: str | None) -> str:
    if not device:
        return "-"
    return f"{device} {interface}" if interface else device

def print_results(results) -> None:
    print(
        f"{'DEVICE':<16}"
        f"{'INTERFACE':<14}"
        f"{'NETBOX':<28}"
        f"{'LLDP':<28}"
        f"STATUS"
    )
    for result in results:
        print(
            f"{result.local_device:<16}"
            f"{result.local_interface:<14}"
            f"{_format_remote(result.netbox_remote_device, result.netbox_remote_interface):<28}"
            f"{_format_remote(result.lldp_remote_device, result.lldp_remote_interface):<28}"
            f"{result.status}"
        )
    counts = Counter(result.status for result in results)
    print()
    print(
        f"Checked: {len(results)} | "
        f"Match: {counts['MATCH']} | "
        f"Mismatch: {counts['MISMATCH']} | "
        f"Undocumented: {counts['UNDOCUMENTED']} | "
        f"Not detected: {counts['NOT_DETECTED']}"
    )

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="netbox-cable-audit",
        description="Compare LLDP neighbor data with NetBox cabling.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    audit_parser = subparsers.add_parser(
        "audit",
        help="Compare LLDP data with NetBox cabling",
    )
    audit_parser.add_argument("lldp_file", help="Path to an LLDP JSON file")
    audit_parser.add_argument(
        "--netbox-url",
        required=True,
        help="NetBox base URL, for example http://localhost:8000",
    )
    return parser

def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    token = os.getenv("NETBOX_TOKEN", "").strip()
    if not token:
        print("ERROR: NETBOX_TOKEN is not set.", file=sys.stderr)
        return 2
    client = NetBoxClient(args.netbox_url, token)
    try:
        results = run_audit(args.lldp_file, client)
    except (LldpInputError, NetBoxError, OSError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    print_results(results)
    return 1 if any(result.status != "MATCH" for result in results) else 0

if __name__ == "__main__":
    raise SystemExit(main())
