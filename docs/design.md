# Design

`netbox-cable-audit` is a read-only CLI that compares LLDP neighbor data with cabling documented in NetBox.

Both sources are converted into a shared `Connection` model before comparison.

## Results

- `MATCH`
- `MISMATCH`
- `UNDOCUMENTED`
- `NOT_DETECTED`

## Cable traces

NetBox may document passive components between active devices. The NetBox client resolves the interface `/trace/` endpoint and uses the final termination of the documented path.

## Structure

```text
src/netbox_cable_audit/
├── __init__.py
├── models.py
├── auditor.py
├── netbox.py
├── runner.py
├── cli.py
└── collectors/
    ├── __init__.py
    └── json.py
```

The audit logic is independent of the LLDP collector so live collectors can be added later.
