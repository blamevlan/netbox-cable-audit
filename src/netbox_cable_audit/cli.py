import argparse
import os
import sys

from netbox_cable_audit.netbox import NetBoxClient
from netbox_cable_audit.runner import run_audit


def print_results(results):
    print(
        f"{'DEVICE':<16}"
        f"{'INTERFACE':<14}"
        f"{'NETBOX':<28}"
        f"{'LLDP':<28}"
        f"STATUS"
    )

    for result in results:
        netbox_remote = "-"

        if result.netbox_remote_device:
            netbox_remote = (
                f"{result.netbox_remote_device} "
                f"{result.netbox_remote_interface}"
            )

        lldp_remote = "-"

        if result.lldp_remote_device:
            lldp_remote = (
                f"{result.lldp_remote_device} "
                f"{result.lldp_remote_interface}"
            )

        print(
            f"{result.local_device:<16}"
            f"{result.local_interface:<14}"
            f"{netbox_remote:<28}"
            f"{lldp_remote:<28}"
            f"{result.status}"
        )


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="netbox-cable-audit"
    )

    subparsers = parser.add_subparsers(
        dest="command",
        required=True,
    )

    audit_parser = subparsers.add_parser(
        "audit",
        help="Compare LLDP data with NetBox cabling",
    )

    audit_parser.add_argument(
        "lldp_file",
        help="Path to LLDP JSON file",
    )

    audit_parser.add_argument(
        "--netbox-url",
        required=True,
        help="NetBox base URL",
    )

    args = parser.parse_args(argv)

    token = os.getenv("NETBOX_TOKEN")

    if not token:
        print(
            "ERROR: NETBOX_TOKEN is not set.",
            file=sys.stderr,
        )
        return 2

    client = NetBoxClient(
        args.netbox_url,
        token,
    )

    try:
        results = run_audit(
            args.lldp_file,
            client,
        )
    except Exception as exc:
        print(
            f"ERROR: {exc}",
            file=sys.stderr,
        )
        return 2

    print_results(results)

    if any(
        result.status != "MATCH"
        for result in results
    ):
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
