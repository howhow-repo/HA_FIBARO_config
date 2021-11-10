# -*- coding: utf-8 -*-
from decouple import config

from lib.hc3 import FibaroHC3
from lib.home_assistant import HomeAssistant

if __name__ == '__main__':
    HA = HomeAssistant(ip=config('HA_IP'), port=config('HA_PORT'), token=config('HA_AUTH_TOKEN'))

    HC = FibaroHC3(ip=config('HC_IP'), port=config('HC_PORT'),
                   username=config('HC_USERNAME'), password=config("HC_PASSWORD"))
    ha_entities = (HA.get_all_entity())
    [print(e) for e in ha_entities]
    print("====\n")
    [print(
        {
            'name': e['attributes']['friendly_name'],
            'type': (str.split(e['entity_id'], "."))[0],
        }
    ) for e in ha_entities if 'friendly_name' in e['attributes'].keys()]

    for light in ha_lights:
        fqa = HC.create_ha_light_fqa(ha_ip=config('HA_IP'), ha_port=config('HA_PORT'),
                                      entity_id=light['entity_id'],
                                      ha_auth_token= config('HA_AUTH_TOKEN'),
                                      name=f"HA_{light['attributes']['friendly_name']}")
        HC.upload_fqa(fqa)
    #     print(resp)
