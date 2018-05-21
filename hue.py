import json
import time
import re
import requests

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
        attr = {}
        if hasattr(self, 'colorgamut'): attr['colorgamut'] = self.colorgamut
        if hasattr(self, 'ct'): attr['ct'] = self.ct
        if hasattr(self, 'mindimlevel'): attr['mindimlevel'] = self.mindimlevel
        return json.dumps(attr)


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
        attr = {}
        attr['on'] = self.on
        if hasattr(self, 'bri'): attr['bri'] = self.bri
        if hasattr(self, 'ct'): attr['ct'] = self.ct
        if hasattr(self, 'hue'): attr['hue'] = self.hue
        if hasattr(self, 'sat'): attr['sat'] = self.sat
        return json.dumps(attr)


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

    def on(self, transitiontime=HUE_DEFAULT_TRANSITION_TIME):
        requests.put(base_url + "/lights/" + str(self.id) + "/state", data=json.dumps({'on':True, 'transitiontime':transitiontime, 'bri':self.state.bri}))
        self.state.on = True

    def off(self, transitiontime=HUE_DEFAULT_TRANSITION_TIME):
        requests.put(base_url + "/lights/" + str(self.id) + "/state", data=json.dumps({'on':False, 'transitiontime':transitiontime}))
        self.state.on = False

    def blink(self):
        if self.state.on:
            self.off(0)
            time.sleep(1)
            self.on(0)
        else:
            self.on(0)
            time.sleep(1)
            self.off(0)

    def __str__(self):
        attr = {}
        attr['id'] = self.id
        attr['uniqueid'] = self.uniqueid
        attr['modelid'] = self.modelid
        attr['name'] = self.name
        attr['state'] = json.loads(str(self.state))
        attr['capabilities'] = json.loads(str(self.capabilities))
        return json.dumps(attr)


def hue_get_lights(username):
    json_response = requests.get(base_url + '/lights').json()

    lights = list()
    for key,value in json_response.items():
        light_capabilities = HueLightCapabilites(value['type'], value['capabilities'])
        light_state = HueLightState(value['state']['on'], value['state'])
        lights.append(HueLight(key, value['uniqueid'], value['modelid'], value['name'], value['type'], light_capabilities, light_state))

    return lights

hue_bridge_ip = "192.168.0.100"
username = "x5lCjhRO0qBi3rf4MGVh-5pSEPq5vcnKpCGV0O9q"
base_url = "http://" + hue_bridge_ip + "/api/" + username

lights = hue_get_lights(username)
current_light = None
for light in lights: 
    if light.id == 10: current_light = light

current_light.blink()