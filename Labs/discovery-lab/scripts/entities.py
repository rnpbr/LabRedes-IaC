from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Host:
    host_id: str
    name: str
    ip: str
    model: Optional[str] = field(default=None)
    command: Optional[str] = field(default=None)


@dataclass
class IpAddress:
    address: str
    status: str


#     "status": {
#     "value": "active",
#     "label": "Active"
#   },


@dataclass
class Interface:
    device_id: str
    name: str
    description: str
    type: str
    mtu: str


# MUT -> mtu
