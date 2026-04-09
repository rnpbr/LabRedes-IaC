import requests
import json


class NetboxApi:
    site_id = ""
    manufacturer_id = ""
    device_type_id = ""
    device_role_id = ""
    plataform_id = ""
    device_id = ""

    def __init__(self, url, token):
        self.__baseurl = url
        self.__token = token
        self.__head = {
            "Authorization": f"Token {self.__token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    def post_to_netbox(self, path, body):
        url = f"{self.__baseurl}{path}"

        response = requests.post(url, headers=self.__head, json=body)

        if response.status_code == 201:
            return response.json()

        print("Erro ao no Post ao netbox")

    def get_from_netbox(self, path):
        url = f"{self.__baseurl}{path}"

        response = requests.post(url, headers=self.__head)
        data = response.json()
        results = data.get("results", None)
        if results is not None:
            return results
        else:
            return data

    def map_manufacturers(self, model):
        switcher = {
            "juniper_junos": "Juniper",
            "extreme_exos": "Extreme",
            "huawei": "Huawei",
        }
        return switcher.get(model, "")

    def map_plataforms(self, model):
        switcher = {
            "juniper_junos": "junos",
            "extreme_exos": "exos",
            "huawei": "huawei",
        }
        return switcher.get(model, "")

    def map_roles(self, acronym):
        switcher = {
            "br": {
                "name": "Border",
                "slug": "border",
                "description": "Equipamentos de Borda",
                "color": "4b5df3",
            },
            "nc": {
                "name": "Core",
                "slug": "core",
                "description": "Equipamentos de Núcleo",
                "color": "5a0c1e",
            },
            "dt": {
                "name": "Distribution",
                "slug": "distribution",
                "description": "Equipamentos de Distribuição",
                "color": "39ffa0",
            },
            "ac": {
                "name": "Access",
                "slug": "access",
                "description": "Equipamentos de Acesso",
                "color": "f26e3c",
            },
            "cl": {
                "name": "Client",
                "slug": "client",
                "description": "Equipamentos de Cliente",
                "color": "9a7ee6",
            },
            "tx": {
                "name": "Transmission",
                "slug": "transmission",
                "description": "Equipamentos de Transmissão",
                "color": "f26e3c",
            },
            "sv": {
                "name": "Server",
                "slug": "server",
                "description": "Equipamentos de Servidor",
                "color": "161e4e",
            },
            "oob": {
                "name": "Out-of-Band",
                "slug": "out-of-band",
                "description": "Equipamentos de Out of Band",
                "color": "1ff836",
            },
        }
        default = {
            "name": "Default",
            "slug": "default",
            "description": "Equipamentos de sem função",
            "color": "eaeaea",
        }
        return switcher.get(acronym, default)

    def create_site(self, name):
        get_url = "/dcim/sites"
        post_url = "/dcim/sites/"

        body = {"name": name, "slug": name.lower(), "status": "active"}

        sites = self.get_from_netbox(get_url)

        if len(sites) > 0:
            for site in sites:
                if site["name"] == name:
                    print("Site já existe!")
                    self.site_id = site["id"]
                    return site

        response = self.post_to_netbox(post_url, body)
        self.site_id = response["id"]

        return response

    def create_manufacturer(self, model):
        get_url = "/dcim/manufacturers"
        post_url = "/dcim/manufacturers/"

        name = self.map_manufacturers(model)
        body = {"name": name, "slug": name.lower()}

        manufacturers = self.get_from_netbox(get_url)

        if len(manufacturers) > 0:
            for manufacturer in manufacturers:
                if manufacturer["name"] == name:
                    print("Fabricante já existe!")
                    self.manufacturer_id = manufacturer["id"]
                    return manufacturer

        response = self.post_to_netbox(post_url, body)
        self.manufacturer_id = response["id"]

        return response

    def create_device_type(self, data):
        get_url = "/dcim/device-types"
        post_url = "/dcim/device-types/"
        body = {"model": data["model"], "slug": data["slug"]}

        device_types = self.get_from_netbox(get_url)

        if len(device_types) > 0:
            for device_type in device_types:
                if device_type["model"] == data["model"]:
                    print("Modelo já existe!")
                    self.device_type_id = device_type["id"]
                    return device_type

        body.update(
            {
                "manufacturer": {"id": self.manufacturer_id},
            }
        )
        response = self.post_to_netbox(post_url, body)
        self.device_type_id = response["id"]

        return response

    def create_platafom(self, model):
        get_url = "/dcim/platforms"
        post_url = "/dcim/platforms/"

        name = self.map_plataforms(model)
        body = {"name": name, "slug": name.lower()}

        plataforms = self.get_from_netbox(get_url)

        if len(plataforms) > 0:
            for plataform in plataforms:
                if plataform["name"] == name:
                    print("Plataforma já existe!")
                    self.plataform_id = plataform["id"]
                    return plataform

        body.update(
            {
                "manufacturer": {"id": self.manufacturer_id},
            }
        )
        response = self.post_to_netbox(post_url, body)
        self.plataform_id = response["id"]

        return response

    def create_device_role(self, name):
        get_url = "/dcim/device-roles"
        post_url = "/dcim/device-roles/"

        parts = name.split("-")

        if len(parts) >= 3:
            acronym = str(parts[2])
        else:
            acronym = "default"

        role = self.map_roles(acronym)
        device_roles = self.get_from_netbox(get_url)

        if len(device_roles) > 0:
            for device_role in device_roles:
                if device_role["name"] == role["name"]:
                    print("Função já existe!")
                    self.device_role_id = device_role["id"]
                    return device_role

        response = self.post_to_netbox(post_url, role)

        self.device_role_id = response["id"]
        return response

    def create_device(self, data):
        get_url = "/dcim/devices"
        post_url = "/dcim/devices/"

        body = {
            "site": {"id": self.site_id},
            "device_type": {"id": self.device_type_id},
            "role": {"id": self.device_role_id},
            "plataform": {"id": self.plataform_id},
            "name": data["name"],
            "serial": data["serial"],
            "status": data["status"],
        }

        devices = self.get_from_netbox(get_url)

        if len(devices) > 0:
            for device in devices:
                if device["name"] == data["name"]:
                    print("Dispositivo já existe!")
                    self.device_id = device["id"]
                    return device

        response = self.post_to_netbox(post_url, body)
        self.device_id = response["id"]

        return response

    def create_interface(self):
        body = {"name": data["interface"], "description": data["description"]}

    def create_ip(self):
        print("oi")
