import urllib.request
import json
import http.client
import time
import re

HUE_DEFAULT_TRANSITION_TIME = 4
HUE_LIGHT_TYPES = {"Color light":{"supports_color":True, "supports_ct":False, "isDimmable":True}, \
                    "Extended color light":{"supports_color":True, "supports_ct":True, "isDimmable":True}, \
                    "Color temperature light":{"supports_color":False, "supports_ct":True, "isDimmable":True}, \
                    "Dimmable light":{"supports_color":False, "supports_ct":False, "isDimmable":False}}

class HueLightCapabilites:
    def __init__(self, light_type, capabilities):
        light_type = light_type.lower()

        for type_name, type_capabilities in HUE_LIGHT_TYPES.items():
            if light_type == type_name.lower():
                self.supports_color = type_capabilities['supports_color']
                self.supports_ct = type_capabilities['supports_ct']
                self.isDimmable = type_capabilities['isDimmable']
                break

        if self.supports_color: self.colorgamut = capabilities['control']['colorgamut']
        if self.supports_ct: self.ct = capabilities['control']['ct']
        if self.isDimmable: self.mindimlevel = capabilities['control']['mindimlevel']

    def __str__(self):
        attributes = list()
        if hasattr(self, 'colorgamut'): attributes.append("'colorgamut':" + str(self.colorgamut))
        if hasattr(self, 'ct'): attributes.append("'ct':" + str(self.ct))
        if hasattr(self, 'mindimlevel'): attributes.append("'mindimlevel':" + str(self.mindimlevel))

        serial = ""
        for i in range(len(attributes)):
            if i != 0: serial += ', '
            serial += attributes[i]
        return '{' + serial + '}'


class HueLightState:
    def __init__(self, on, state):
        self.on = on

        bri = state.get('bri')
        if bri != None: self.bri = bri

        ct = state.get('ct')
        if ct != None: self.ct = ct

        hue = state.get('hue')
        if hue != None: self.hue = hue

        sat = state.get('sat')
        if sat != None: self.sat = sat

    def __str__(self):
        attributes = list()
        if hasattr(self, 'bri'): attributes.append("'bri':" + str(self.bri))
        if hasattr(self, 'ct'): attributes.append("'ct':" + str(self.ct))
        if hasattr(self, 'hue'): attributes.append("'hue':" + str(self.hue))
        if hasattr(self, 'sat'): attributes.append("'sat':" + str(self.sat))

        serial = ""
        for i in range(len(attributes)):
            if i != 0: serial += ', '
            serial += attributes[i]
        return '{' + serial + '}'


class HueLight:
    def __init__(self, id, uniqueid, modelid, name, light_type, capabilities, state):
        self.id = int(id)
        self.uniqueid = uniqueid
        self.modelid = modelid
        self.name = name
        self.type = light_type

        # Capabilites of the light
        self.capabilities = capabilities

        # State of the light
        self.state = state

    def on(self, transition_time=HUE_DEFAULT_TRANSITION_TIME):
        connection.request("PUT", "/api/" + username + "/lights/" + str(self.id) + "/state", \
                            '{"on":true, "transitiontime":' + str(transition_time) + ', "bri":' + str(self.state.bri) + '}')
        http_response = connection.getresponse()
        json_response = json.loads(http_response.read().decode('utf-8'))
        print(json_response)
        self.state.on = True

    def off(self, transition_time=HUE_DEFAULT_TRANSITION_TIME):
        connection.request("PUT", "/api/" + username + "/lights/" + str(self.id) + "/state", '{"on":false, "transitiontime":' + str(transition_time) + '}')
        http_response = connection.getresponse()
        json_response = json.loads(http_response.read().decode('utf-8'))
        print(json_response)
        self.state.on = False

    def blink(self):
        if self.state.on:
            self.off(0)
            self.on(0)
        else:
            self.on(0)
            self.off(0)

    def __str__(self):
        attributes = list()
        attributes.append('"id":' + str(self.id))
        attributes.append('"uniqueid:"' + str(self.uniqueid))
        attributes.append('"modelid":' + str(self.modelid))
        attributes.append('"name":' + str(self.name))
        attributes.append('"capabilites":' + str(self.capabilities))

        serial = ""
        for i in range(len(attributes)):
            if i != 0: serial += ', '
            serial += attributes[i]
        return '{' + serial + '}'


def hue_get_lights(connection, username):
    connection.request("GET", "/api/" + username + "/lights")
    http_response = connection.getresponse()
    json_response = json.loads(http_response.read().decode('utf-8'))

    lights = list()

    for key,value in json_response.items():
        light_capabilities = HueLightCapabilites(value['type'], value['capabilities'])
        light_state = HueLightState(value['state']['on'], value['state'])
        lights.append(HueLight(key, value['uniqueid'], value['modelid'], value['name'], value['type'], light_capabilities, light_state))

    return lights

hue_bridge_ip = "192.168.0.100"
username = "x5lCjhRO0qBi3rf4MGVh-5pSEPq5vcnKpCGV0O9q"
connection = http.client.HTTPConnection(hue_bridge_ip)
lights = hue_get_lights(connection, username)
current_light = None
for light in lights: 
    if light.id == 10: current_light = light

current_light.blink()