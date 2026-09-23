"""Every test is offline. Source-scout tests use explicit fake transports."""
import socket
import pytest


@pytest.fixture(autouse=True)
def prohibit_test_network(monkeypatch):
    def denied(*args, **kwargs):
        raise AssertionError("Network access is forbidden in the offline test suite")
    monkeypatch.setattr(socket, "create_connection", denied)
    monkeypatch.setattr(socket.socket, "connect", denied)
    monkeypatch.setattr(socket.socket, "connect_ex", denied)
