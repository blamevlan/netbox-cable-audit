# Design

`netbox-cable-audit` is a read-only CLI tool that compares LLDP neighbor data with the cabling documented in NetBox.

The main purpose is to find connections where the actual network topology and the NetBox documentation do not match.

## Scope

The first version uses:

- LLDP data from a JSON file
- cabling data from the NetBox REST API
- NetBox cable traces to resolve the actual endpoint of a connection

The JSON input is mainly used to keep LLDP collection separate from the audit logic. Real collectors such as NAPALM or SNMP can be added later.

The tool does not modify NetBox.

## Connection model

Both data sources are converted to the same internal representation:

```text
local_device
local_interface
remote_device
remote_interface
source