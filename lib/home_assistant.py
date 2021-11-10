# -*- coding: utf-8 -*-
import requests


class HomeAssistant:
    def __init__(self, ip, port, token):
        self.ip = ip
        self.port = port
        self._header = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + token
        }

    def is_connected(self):
        uri = '/api/'
        url = 'http://' + self.ip + ':' + self.port + uri
        r = requests.get(url, headers=self._header)
        if (r.json())['message'] == "API running." :
            return True
        return False

    def get_all_entity(self):
        uri = "/api/states"
        url = 'http://' + self.ip + ':' + self.port + uri
        r = requests.get(url, headers=self._header)

        return r.json()

    def get_lights(self):
        return [e for e in self.get_all_entity() if (e['entity_id'].split("."))[0] == 'light']

    def get_media_player(self):
        pass
