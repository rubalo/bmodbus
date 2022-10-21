from dataclasses import dataclass

from dataclasses_json import DataClassJsonMixin


class TCPConfigSchema:
    ADDRESS = "address"
    PORT = "port"
    FRAMER = "framer"


class RTUConfigSchema:
    PORT = "port"
    BAUDRATE = "baudrate"
    PARITY = "parity"
    BYTESIZE = "bytesize"
    STOPBITS = "stopbits"
    FRAMER = "framer"


@dataclass
class TCPConfig(DataClassJsonMixin):
    address: str
    port: int
    framer: str = "socket"
    type: str = "TCP"


@dataclass
class RTUConfig(DataClassJsonMixin):
    port: str
    baudrate: int
    parity: str
    bytesize: int
    stopbits: int
    framer: str
    type: str = "SERIAL"
