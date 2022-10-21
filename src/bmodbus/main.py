import json
import logging
import pathlib

import click
import serial

from . import config, modbus

FORMAT = "%(asctime)-15s %(levelname)-8s %(module)-15s:%(lineno)-8s %(message)s"
logging.basicConfig(format=FORMAT)
_logger = logging.getLogger()
_logger.setLevel(logging.INFO)


class ContextSchema:
    CLIENT = "client"


@click.group
def cli():
    pass


@cli.command()
@click.option(
    "--address", prompt="Enter the slave address", default=modbus.TcpConfig.address
)
@click.option("--port", prompt="Enter the slave port", default=modbus.TcpConfig.port)
@click.option(
    "--dest",
    prompt="Enter the destination file",
    default="config_tcp.json",
    type=click.Path(),
)
def create_tcp_config(address, port, dest):
    tcp_config = config.TCPConfig(address, port)
    p = pathlib.Path(dest)
    with open(p, "w") as f:
        f.write(tcp_config.to_json())
    _logger.info(f"Configuration saved to : {p.absolute()}")


@cli.command()
@click.option(
    "--port", prompt="Enter the slave port", default=modbus.SerialConfig.serial_port
)
@click.option(
    "--baudrate",
    prompt="Enter the baud rate",
    default=modbus.SerialConfig.baudrate,
    type=click.Choice(serial.SerialBase.BAUDRATES),
)
@click.option(
    "--bytesize",
    prompt="Enter the byte size",
    default=modbus.SerialConfig.bytesize,
    type=click.Choice(serial.SerialBase.BYTESIZES),
)
@click.option(
    "--parity",
    prompt="Enter the parity",
    type=click.Choice(serial.SerialBase.PARITIES),
    default=modbus.SerialConfig.parity,
)
@click.option(
    "--stopbits",
    prompt="Enter the stop bits",
    default=modbus.SerialConfig.stopbits,
    type=click.Choice(serial.SerialBase.STOPBITS),
)
@click.option(
    "--dest",
    prompt="Enter the destination file",
    default="config_serial.json",
    type=click.Path(),
)
@click.option("--frame", type=click.Choice(["rtu", "acsii"]), default="rtu")
def create_serial_config(port, baudrate, bytesize, parity, stopbits, dest, frame):
    serial_config = config.RTUConfig(port, baudrate, bytesize, parity, stopbits, frame)
    p = pathlib.Path(dest)
    with open(p, "w") as f:
        f.write(serial_config.to_json())
    _logger.info(f"Configuration saved to : {p.absolute()}")


@cli.group
@click.option(
    "-c", "--config-file", "configfile", type=click.Path(exists=True), required=True
)
@click.option("-s", "--slave", type=int, default=1, prompt="Enter a slave number")
@click.pass_context
def do(ctx, configfile, slave):
    with open(configfile, "r") as f:
        data = json.load(f)
        ctx.obj = modbus.ModbusClientBuilder.client(slave=slave, **data)


@do.command
@click.argument("address", type=int, required=True)
@click.pass_context
def read_input_register(ctx, address):
    client: modbus.ModbusClient = ctx.obj
    _logger.info(f"Read input register: Slave {client.slave}, Address {address}")
    client.read_input_register(address)


@do.command
@click.argument("address", type=int, required=True)
@click.pass_context
def read_holding_register(ctx, address):
    client: modbus.ModbusClient = ctx.obj
    _logger.info(f"Read holding register: Slave {client.slave}, Address {address}")
    r = client.read_holding_register(address)
    _logger.info(f"Address: {address}, value: {r}")


@do.command
@click.argument("address", type=int, required=True)
@click.argument("value", type=int, required=True)
@click.pass_context
def write_holding_register(ctx, address, value):
    client: modbus.ModbusClient = ctx.obj
    _logger.info(
        f"Write holding register: Slave {client.slave}, Address {address}, Value {value}"
    )
    client.write_holding_register(address, value)
    r = client.read_holding_register(address)
    _logger.info(f"Address: {address}, value: {r}")


@do.command
@click.argument("file", required=True, type=click.Path(exists=True))
@click.pass_context
def batch(ctx, file):
    client: modbus.ModbusClient = ctx.obj
    _logger.info(f"Batch mode: file {file}, Slave {client.slave}")
    client.execute_commands(file)


if __name__ == "__main__":
    cli()
