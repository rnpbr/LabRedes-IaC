from zabbix_api import ZabbixApi
from netbox_api import NetboxApi
from netmiko_lib import Netmiko
from entities import Host
import os
from dotenv import load_dotenv
import pprint

load_dotenv()

zabbix = ZabbixApi(url=os.environ["ZABBIX_URL"], token=os.environ["ZABBIX_TOKEN"])
netbox = NetboxApi(url=os.environ["NETBOX_URL"], token=os.environ["NETBOX_TOKEN"])

# Testar conexão com as duas API's

default_site_name = "default-netbox-site"

site_name = input(
    "Digite o nome do seu site do NetBox (padrão: default-netbox-site): "
).strip()

if not site_name:
    site_name = default_site_name

print(f"\nO nome do site definido é: {site_name}")


print("\n 1 --- Criando site no Netbox...")
netbox.create_site(site_name)


print("\n 2 --- Importando informações do Zabbix... ")
[resolved_hosts, unresolved_hosts] = zabbix.get_organized_hosts()

for host in resolved_hosts:
    if host.model == "juniper_junos":
        print("\n 3 --- Consultando dispositivo...")
        netmiko = Netmiko(host)

        print("\n 3.1 Verificando conexão com o dispositivo...")
        reachable = netmiko.test_connection()

        if reachable:
            print("\n 3.2 Coletando informações...")
            hardware = netmiko.get_hardware()
            print(f"\n\n Hardware coletado: {hardware}\n\n")

            # interfaces = netmiko.get_interfaces()

            # for interface in interfaces:
            #    pprint.pprint(interfaces)

            print("\n\n 4 --- Criando Dispositivo no Netbox...")
            manufacturer = netbox.create_manufacturer(host.model)
            print(manufacturer["name"])

            device_type = netbox.create_device_type(
                {"model": hardware["model"], "slug": hardware["model"].lower()}
            )
            print(f"Fabricante: {device_type['model']}")

            plataform = netbox.create_platafom(host.model)
            print(f"Plataforma: {plataform['name']}")

            print(host.name)
            device_role = netbox.create_device_role(host.name)
            print(f"Função: {device_role['name']}")

            device = netbox.create_device(
                {"name": host.name, "serial": hardware["serial"], "status": "active"}
            )
            print(f"Dispositivo: {device['name']}")


print("\n\n ******* Importação finalizada! ********")

# Interface
# Nome -> interface: ge0/0/0
# MUT -> mtu

# Endereço IP
#
