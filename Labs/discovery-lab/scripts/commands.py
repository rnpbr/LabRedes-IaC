class Commands:
    juniper_commands = {
        "interface": "show interfaces",
        "hardware": "show chassis hardware | match Chassis",
    }

    extreme_exos = {"interface": "show ports information detail"}

    huawei = {"interface": "display interface brief"}

    switcher = {
        "juniper_junos": juniper_commands,
        "extreme_exos": extreme_exos,
        "huawei": huawei,
    }

    def get_command(self, model):
        command = self.switcher.get(model, "")
        return command
