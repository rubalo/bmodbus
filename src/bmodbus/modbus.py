import csv
import functools
import logging
import pathlib
import time
from abc import abstractmethod
from dataclasses import dataclass
from typing import List

import serial
from pymodbus.client import ModbusBaseClient, ModbusSerialClient, ModbusTcpClient
from pymodbus.transaction import ModbusAsciiFramer, ModbusRtuFramer, ModbusSocketFramer

FORMAT = "%(asctime)-15s %(levelname)-8s %(module)-15s:%(lineno)-8s %(message)s"
logging.basicConfig(format=FORMAT)
_logger = logging.getLogger()

# set defaults
comm_defaults = {
    "tcp": ["socket", 5020],
    "udp": ["socket", 5020],
    "serial": ["rtu", "/dev/ptyp0"],
    "tls": ["tls", 5020],
}
framers = {
    "ascii": ModbusAsciiFramer,
    "rtu": ModbusRtuFramer,
    "socket": ModbusSocketFramer,
}


modbusExceptionCodes = {
    0x01: "IllegalFunction",
    0x02: "IllegalAddress",
    0x03: "IllegalValue",
    0x04: "SlaveFailure",
    0x05: "Acknowledge",
    0x06: "SlaveBusy",
    0x07: "NegativeAcknoledge",
    0x08: "MemoryParityError",
    0x0A: "GatewayPathUnavailable",
    0x0B: "GatewayNoResponse",
}


class ModbusError(Exception):
    pass


@dataclass
class TcpConfig:
    address: str = "127.0.0.1"
    port: int = 5020


@dataclass
class SerialConfig:
    serial_port: str = "COM1"
    baudrate: int = 19200
    bytesize: int = 8
    stopbits: int = 1
    parity: str = serial.PARITY_NONE
    close_after_each_call: bool = True  # Mostly for windows
    timeout: float = 1.0


@dataclass
class ModbusClient:
    client: ModbusBaseClient
    slave: int

    def _handle_error(fn):
        @functools.wraps(fn)
        def comm_fn(*args, **kwargs):
            try:
                res = fn(*args, *kwargs)
                return res
            except ModbusError as e:
                error = e.args[0].exception_code
                _logger.error(
                    f"Error comminucating with modbus server: {modbusExceptionCodes[error]}"
                )
                raise e

        return comm_fn

    @_handle_error
    def read_holding_register(self, address: int) -> int:
        """Read holding registers"""
        rr = self.client.read_holding_registers(address, 1, slave=self.slave)
        if rr.isError():
            raise ModbusError(rr)
        txt = f"### address {address} is: {str(rr.registers[0])}"
        _logger.debug(txt)
        return rr.registers[0]

    @_handle_error
    def write_holding_register(self, address: int, value: int) -> int:
        """Write holding register"""
        rq = self.client.write_registers(address, value, slave=self.slave)
        if rq.isError():
            raise ModbusError(rq)  # test that calls was OK
        txt = f"### address {address} set to: {str(value)}"
        _logger.debug(txt)
        return value

    @_handle_error
    def read_input_register(self, address: int) -> int:
        """Read input registers"""
        rr = self.read_input_registers(address, 1)
        return rr[0]

    @_handle_error
    def read_input_registers(self, address: int, count: int) -> List[int]:
        """Read input registers"""
        rr = self.client.read_input_registers(address, count, slave=self.slave)
        if rr.isError():
            raise ModbusError(rr)
        txt = f"### address {address}, count {count} is: {str(rr.registers)}"
        _logger.debug(txt)
        return rr.registers

    @_handle_error
    def execute_commands(self, filename: pathlib.Path) -> None:
        """Execute a list of commands"""
        res = list()
        with open(filename, "r") as f:
            command_reader = csv.reader(f, delimiter=",")
            for row in command_reader:
                if row[0].startswith("#"):
                    continue

                fn = int(row[0])
                address = int(row[1])
                value = 0

                if fn == 3:
                    r = self.read_holding_register(address)
                    _logger.info(f"Reading holding register {address}: {r}")
                elif fn == 4:
                    r = self.read_input_register(address)
                    _logger.info(f"Reading input register {address}: {r}")
                elif fn == 6:
                    value = int(row[2])
                    r = self.write_holding_register(address, value)
                    _logger.info(f"Wrinting holding register {address}: {r}")
                elif fn == 999:
                    _logger.info(f"Sleeps for {address} seconds")
                    time.sleep(address)
                else:
                    _logger.error(f"function {row[0]} not implemented")


class ModbusClientBuilder:
    @abstractmethod
    def client(**kwargs) -> ModbusBaseClient:
        client = ""
        if kwargs.get("type") == "TCP":
            client = ModbusTcpClient(
                host=kwargs.get("address", "127.0.0.1"),
                port=kwargs.get("port", 5020),
                framer=framers[kwargs.get("framer")],
                timeout=kwargs.get("timeout", 1),
                # retries=3,
                # retry_on_empty=False,
                # close_comm_on_error=False,
                # strict=True,
                # TCP setup parameters
                # source_address=("localhost", 0),
            )
        elif kwargs.get("type") == "SERIAL":
            client = ModbusSerialClient(
                port=kwargs.get("port", "/dev/ptyp0"),
                framer=framers[kwargs.get("framer")],
                bytesize=kwargs.get("bytesize"),
                parity=kwargs.get("parity"),
                stopbits=kwargs.get("stopbytes"),
                timeout=kwargs.get("timeout", 1),
            )
        else:
            raise NotImplementedError

        return ModbusClient(client, kwargs.get("slave"))
