# netbox-cable-audit

`netbox-cable-audit` is a small read-only CLI that compares LLDP neighbor data with cabling documented in NetBox.

It is intended for cases where NetBox is the source of truth, but the actual network topology should be checked against what switches report through LLDP.

## Results

- `MATCH` — NetBox and LLDP point to the same remote device and interface
- `MISMATCH` — both sides have data, but the remote endpoint differs
- `UNDOCUMENTED` — LLDP sees a neighbor, but NetBox has no documented connection
- `NOT_DETECTED` — NetBox has a documented connection, but LLDP did not report a neighbor

The tool does not modify NetBox.

## Cable traces

NetBox can model passive components such as patch panels between two active devices.

```text
sw-core-01
    |
patch panel
    |
patch panel
    |
sw-access-01
```

LLDP only sees the active endpoints. The NetBox client therefore uses the interface `/trace/` endpoint and compares LLDP against the final endpoint of the documented path.

## Install

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e ".[dev]"
```

Activation of the virtual environment is optional.

## LLDP JSON format

```json
{
  "sw-core-01": {
    "Gi1/0/1": {
      "remote_device": "sw-access-01",
      "remote_interface": "Gi1/0/48"
    }
  }
}
```

A device may also be present with no discovered neighbors:

```json
{
  "sw-core-01": {}
}
```

This keeps the device in audit scope so documented NetBox links can still be reported as `NOT_DETECTED`.

## Run

Set a read-only NetBox API token:

```powershell
$env:NETBOX_TOKEN = "your-token"
```

Run the audit:

```powershell
.\.venv\Scripts\netbox-cable-audit.exe audit examples\lldp.json --netbox-url http://localhost:8000
```

## Exit codes

- `0` — audit completed and every result is `MATCH`
- `1` — audit completed with at least one discrepancy
- `2` — input, configuration, or API error

## Tests

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

Pytest uses a temporary directory inside the project to avoid Windows temp-directory permission problems.

## Local NetBox lab

`scripts/seed_netbox_lab.ps1` creates a disposable lab with two access switches, a server and a two-patch-panel path.

The script prompts for a writable NetBox authorization header if `NETBOX_SEED_AUTH` is not already set.

## Current scope

Version 0.1 intentionally does not include live SNMP/NAPALM collection, interface-name normalization, NetBox writes, a web UI, or a NetBox plugin.
