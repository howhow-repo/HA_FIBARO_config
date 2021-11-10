# -*- coding: utf-8 -*-
import base64
import json
from io import StringIO
import requests


class FibaroHC3:
    """"""
    def __init__(self, ip, port, username, password):
        self.ip = ip
        self.port = port
        self._header = {
            'Content-Type': 'application/json',
            'Authorization': 'Basic ' + base64.b64encode(f"{username}:{password}".encode('utf-8')).decode('utf-8')
        }
        self.info = self.get_info()

    @classmethod
    def create_ha_light_fqa(cls, ha_ip, ha_port, entity_id, ha_auth_token, name="HA_LIGHT"):
        file_path = './fqa_templates/HA_LIGHT.fqa'
        with open(file_path, 'r', encoding="utf-8") as f:
            data = json.load(f)
            variables = [
                {"name": "ip", "type": "string", "value": ha_ip},
                {"name": "port", "type": "string", "value": ha_port},
                {"name": "entity_id", "type": "string", "value": entity_id},
                {"name": "HA_AUTH_TOKEN", "type": "string", "value": ha_auth_token},
            ]
            data["initialProperties"]["quickAppVariables"] = variables
            data['name'] = name
            new_data = StringIO(json.dumps(data, ensure_ascii=False))
            return new_data

    def get_data(self, uri):
        url = 'http://' + self.ip + ':' + self.port + uri
        r = requests.get(url, headers=self._header)
        return r

    def get_info(self):
        uri = "/api/settings/info"
        r = self.get_data(uri)
        return r.json()

    def get_all_devices(self):
        uri = "/api/devices"
        r = self.get_data(uri)
        return r.json()

    def upload_fqa(self, file):
        header = self._header.copy()
        del header['Content-Type']
        uri = '/api/quickApp/import'
        url = 'http://' + self.ip + ':' + self.port + uri
        payload = {"file": file}
        r = requests.post(url=url, files=payload, headers=header)
        return r


