import requests
import json
from entities import Host


class ZabbixApi:
    body = {
        "jsonrpc": "2.0",
        "method": "item.get",
        "params": {
            "selectHosts": ["name"],
            "selectInterfaces": ["ip"],
            "output": ["lastvalue"],
            "search": {"key_": "system.descr[sysDescr.0]"},
            "monitored": True,
        },
        "id": 1,
    }

    def __init__(self, url, token):
        self.__url = url
        self.__token = token
        self.__head = {
            "Authorization": f"Bearer {self.__token}",
            "Content-type": "application/json-rpc",
        }

    def map_models(self, model):
        switcher = {
            "Juniper": "juniper_junos",
            "ExtremeXOS": "extreme_exos",
            "Huawei": "huawei",
        }
        return switcher.get(model, "")

    def get_hosts(self):
        response = requests.get(
            self.__url, headers=self.__head, data=json.dumps(self.body)
        )
        data = json.loads(response.text)["result"]
        return data

    def get_organized_hosts(self):
        data = self.get_hosts()

        resolved_hosts = []
        problem_hosts = []

        for host_data in data:
            host_id = host_data["hosts"][0]["hostid"]
            name = host_data["hosts"][0]["name"]
            ip = host_data["interfaces"][0]["ip"]
            model = host_data["lastvalue"].split()

            if len(model) > 0:
                resolved_hosts.append(
                    Host(
                        host_id,
                        name,
                        ip,
                        model=self.map_models(model[0]),
                    )
                )
            else:
                problem_hosts.append(
                    Host(
                        host_id,
                        name,
                        ip,
                    )
                )

        return resolved_hosts, problem_hosts
