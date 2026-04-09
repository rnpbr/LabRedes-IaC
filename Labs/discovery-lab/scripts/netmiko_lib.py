from netmiko import ConnectHandler, SSHDetect
from entities import Host
from commands import Commands
from display import Display
import os
from dotenv import load_dotenv

load_dotenv()


class Netmiko:
    def __init__(self, host: Host):
        self.host = host
        self.netmiko_host = {
            "host": host.ip,
            "username": os.environ["DEVICE_USERNAME"],
            "password": os.environ["DEVICE_PASSWORD"],
            "port": os.environ.get("DEVICE_PORT") or 22,  # optional, defaults to 22
            "secret": os.environ.get("DEVICE_SECRET") or "",  # optional, defaults to ''
        }

    def test_connection(self):
        if self.host.model:
            self.netmiko_host["device_type"] = self.host.model
        else:
            self.guess_device_model()

        # Set commands to model
        self.model_commands = Commands().get_command(self.host.model)

        try:
            self.net_connect = ConnectHandler(**self.netmiko_host)
            return True

        except Exception as err:
            print(f"Host unachievable: {err}")
            return False

    def send_command_to_device(
        self, command, use_textfsm=True
    ) -> dict | str | list | None:
        self.host.command = command
        Display().host_data(self.host)

        try:
            output = self.net_connect.send_command(command, use_textfsm=use_textfsm)
            return output

        except Exception as err:
            print(err)
            return err

    def guess_device_model(self):
        self.netmiko_host["device_type"] = "autodetect"

        guesser = SSHDetect(**self.netmiko_host)
        best_match = guesser.autodetect()
        self.netmiko_host["device_type"] = best_match

        print(best_match)
        print(guesser.potential_matches)

    def normalize_string(self, text):
        text = text.strip()

        if text.startswith("[") and text.endswith("]"):
            text = text[1:-1]

        return text

    def is_not_integer(string):
        try:
            int(string)
            return False
        except ValueError:
            return True

    def get_interfaces(self):
        command = self.model_commands["interface"]

        interfaces = self.send_command_to_device(command)

        for interface in interfaces:
            name = interface["interface"]
            name_splited = name.split("/")
            interface_number = name_splited[len(name_splited) - 1]

            is_string = self.is_not_integer(interface_number)
            print(interface_number, is_string)

            if len(interface_number) < 2 or is_string:

                mac_address = self.send_command_to_device(
                    f'show interfaces {name} | match "Hardware address"',
                    False,
                )

                # mac_address = mac_address.split(" ")[2]
                if mac_address:
                    mac_address = mac_address.split(" ")[7].replace("/n", "")
                    interface.update({"mac_address": mac_address})

        return interfaces

    def get_hardware(self):
        command = self.model_commands["hardware"]

        data = self.send_command_to_device(command)[0]

        serial = data["chassis_serial_number"]
        model = data["chassis_description"]

        hardware = {
            "serial": self.normalize_string(serial),
            "model": self.normalize_string(model),
        }
        return hardware

    def close_connection(self):
        self.net_connect.disconnect()
