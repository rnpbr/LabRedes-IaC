import docker
from pyzabbix import ZabbixAPI
import os
from dotenv import load_dotenv

load_dotenv()

# Configurações do Zabbix
ZABBIX_URL = os.environ["ZABBIX_URL"]
ZABBIX_USER = os.environ["ZABBIX_USER"]
ZABBIX_PASSWORD = os.environ["ZABBIX_PASSWORD"]
ZABBIX_GROUP = os.environ["ZABBIX_GROUP"]
ZABBIX_TEMPLATE = os.environ["ZABBIX_TEMPLATE"]

# Nome e IPs dos roteadores
EXPECTED_CONTAINERS = {
    "POP-GO": "172.10.10.12",
    "POP-MS": "172.10.10.17",
    "POP-MT": "172.10.10.18",
}

# Conectar ao Zabbix API
zabbix = ZabbixAPI(ZABBIX_URL)
zabbix.login(ZABBIX_USER, ZABBIX_PASSWORD)

# Conectar ao Docker
client = docker.from_env()

# Obter lista de containers em execução
containers = client.containers.list()

# Buscar o ID do grupo no Zabbix
group_data = zabbix.hostgroup.get(filter={"name": ZABBIX_GROUP})
if not group_data:
    print(f"Grupo {ZABBIX_GROUP} não encontrado, criando...")
    group_id = zabbix.hostgroup.create(name=ZABBIX_GROUP)["groupids"][0]
else:
    group_id = group_data[0]["groupid"]

# Buscar o ID do template
template_data = zabbix.template.get(filter={"host": ZABBIX_TEMPLATE})
if not template_data:
    print(f"Template {ZABBIX_TEMPLATE} não encontrado!")
    exit(1)
template_id = template_data[0]["templateid"]

# Criar hosts no Zabbix apenas para os routers esperados
for container_name, container_ip in EXPECTED_CONTAINERS.items():
    print(f"Registrando container {container_name} ({container_ip}) no Zabbix...")

    # Verificar se o host já existe
    existing_host = zabbix.host.get(filter={"host": container_name})
    if existing_host:
        print(f"Host {container_name} já cadastrado no Zabbix, pulando...")
        continue

    # Criar o host no Zabbix
    zabbix.host.create(
        host=container_name,
        interfaces=[
            {
                "type": 2,  # SNMP
                "main": 1,
                "useip": 1,
                "ip": container_ip,
                "dns": "",
                "port": "161",
                "details": {
                    "version": 2,
                    "community": "{$SNMP_COMMUNITY}",
                    "max_repetitions": 10,
                },
            }
        ],
        groups=[{"groupid": group_id}],
        templates=[{"templateid": template_id}],
    )

    print(f"Host {container_name} registrado com sucesso!")

print("Finalizado!")
