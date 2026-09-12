"""Resolve source addresses only through explicitly trusted proxy networks."""

from ipaddress import ip_address, ip_network

from fastapi import HTTPException, Request

from app.core.config import get_settings


def client_ip(request: Request) -> str:
    # Uvicorn proxy rewriting must be disabled so this is the actual socket peer.
    networks = [
        ip_network(value.strip())
        for value in get_settings().trusted_proxy_cidrs.split(",")
        if value.strip()
    ]
    try:
        address = ip_address(request.client.host) if request.client else None
        if address is None:
            raise ValueError("Missing socket peer")
        forwarded = ",".join(request.headers.getlist("x-forwarded-for")).split(",")
        while any(address in network for network in networks):
            if not forwarded or not forwarded[-1].strip():
                raise ValueError("Trusted proxy did not provide a client address")
            address = ip_address(forwarded.pop().strip())
        if address.version == 6 and address.ipv4_mapped:
            address = address.ipv4_mapped
        return str(address)
    except ValueError as exc:
        raise HTTPException(503, "Client address unavailable") from exc
