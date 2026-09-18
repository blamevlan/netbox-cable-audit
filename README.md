# netbox-cable-audit

A small read-only CLI I wrote to compare cabling documented in NetBox with the neighbors switches report through LLDP.

Current version: **0.1.0**

The tool does not write to NetBox.

## Results

- `MATCH`: NetBox and LLDP point to the same remote device and interface
- `MISMATCH`: both sides have data, but the remote endpoint differs
- `UNDOCUMENTED`: LLDP sees a neighbor, but NetBox has no documented connection
- `NOT_DETECTED`: NetBox has a documented connection, but LLDP did not report a neighbor

## Cable traces

Passive components such as patch panels can sit between two active devices. NetBox models that path, while LLDP only sees the active endpoints.

```text
sw-core-01
    |
patch panel
    |
patch panel
    |
sw-access-01
```

The NetBox client follows the interface `/trace/` endpoint and compares LLDP with the final active endpoint of the documented path.

## Install

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e ".[dev]"
```

Activating the virtual environment is optional.

## LLDP input

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

A device can also be present with an empty object. That keeps it in audit scope even if LLDP found no neighbors.

## Run

Set a read-only NetBox API token:

```powershell
$env:NETBOX_TOKEN = "your-token"
```

Then run the audit:

```powershell
.\.venv\Scripts\netbox-cable-audit.exe audit examples\lldp.json --netbox-url http://localhost:8000
```

## Exit codes

- `0`: audit completed and every result is `MATCH`
- `1`: audit completed with at least one discrepancy
- `2`: input, configuration or API error

## Tests

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

## Local NetBox lab

`scripts/seed_netbox_lab.ps1` creates a disposable lab with two access switches, a server and a two-patch-panel path.

The script prompts for a writable NetBox authorization header if `NETBOX_SEED_AUTH` is not already set.

## Current scope

Version 0.1 intentionally does not include live SNMP/NAPALM collection, interface-name normalization, NetBox writes, a web UI or a NetBox plugin.

## License

MIT. See [LICENSE](LICENSE).
