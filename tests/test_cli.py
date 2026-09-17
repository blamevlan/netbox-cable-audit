from unittest.mock import patch

from netbox_cable_audit.cli import main
from netbox_cable_audit.models import AuditResult

@patch("netbox_cable_audit.cli.run_audit")
def test_cli_returns_zero_when_everything_matches(mock_run, monkeypatch):
    monkeypatch.setenv("NETBOX_TOKEN", "test-token")
    mock_run.return_value = [AuditResult(
        status="MATCH",
        local_device="sw-core-01",
        local_interface="Gi1/0/1",
        netbox_remote_device="sw-access-01",
        netbox_remote_interface="Gi1/0/48",
        lldp_remote_device="sw-access-01",
        lldp_remote_interface="Gi1/0/48",
    )]

    assert main([
        "audit",
        "examples/lldp.json",
        "--netbox-url",
        "https://netbox.example.com",
    ]) == 0

@patch("netbox_cable_audit.cli.run_audit")
def test_cli_returns_one_for_discrepancy(mock_run, monkeypatch):
    monkeypatch.setenv("NETBOX_TOKEN", "test-token")
    mock_run.return_value = [AuditResult(
        status="MISMATCH",
        local_device="sw-core-01",
        local_interface="Gi1/0/1",
        netbox_remote_device="sw-access-02",
        netbox_remote_interface="Gi1/0/48",
        lldp_remote_device="sw-access-01",
        lldp_remote_interface="Gi1/0/48",
    )]

    assert main([
        "audit",
        "examples/lldp.json",
        "--netbox-url",
        "https://netbox.example.com",
    ]) == 1

def test_cli_returns_two_without_token(monkeypatch):
    monkeypatch.delenv("NETBOX_TOKEN", raising=False)

    assert main([
        "audit",
        "examples/lldp.json",
        "--netbox-url",
        "https://netbox.example.com",
    ]) == 2
