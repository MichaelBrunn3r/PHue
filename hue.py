import json
import time
import requests
from collections import deque
import hue_color

HUE_DEFAULT_TRANSITION_TIME = 4
HUE_LIGHT_TYPES = {"Color light":{"supports_color":True, "supports_ct":False, "dimmable":True}, \
                    "Extended color light":{"supports_color":True, "supports_ct":True, "dimmable":True}, \
                    "Color temperature light":{"supports_color":False, "supports_ct":True, "dimmable":True}, \
                    "Dimmable light":{"supports_color":False, "supports_ct":False, "dimmable":True}}
HUE_DEFAULT_USERNAME = "newdeveloper"

class HueBridge(object):
    def __init__(self, ip, username=HUE_DEFAULT_USERNAME):
        self.ip = ip
        self.username = username
        self.base_url = 'http://' + self.ip + '/api/' + username
        self.lights = self.get_lights()
        self.sensors = self.get_sensors()

    def _request(self, method, relative_url, data={}):
        if method == 'GET': return requests.get(self.base_url + relative_url)
        elif method == 'PUT': return requests.put(self.base_url + relative_url, json.dumps(data))

    def get_lights(self):
        response = self._request('GET', HueLight.ROUTE).json()

        lights = dict()
        for id, attr in response.items():
            lights[id] = HueLight(self, id, attr)

        return lights

    def get_sensors(self):
        response = self._request('GET', HueSensor.ROUTE).json()
        
        sensors = dict()
        for id, attr in response.items():
            sensors[id] = HueSensor(self, id, attr)

        return sensors

class HueApiObject:
    def __init__(self, bridge, id, attr):
        object.__setattr__(self, 'bridge', bridge)
        object.__setattr__(self, 'id', id)

        for attr_name, val in attr.items():
            object.__setattr__(self, attr_name, val)

    def __str__(self):
        return str(self.__dict__)

class HueLight(HueApiObject):
    ROUTE = '/lights'

    def __init__(self, bridge, id, attr):
        super().__init__(bridge, id, attr)

        light_type = HUE_LIGHT_TYPES.get(self.type)
        if light_type != None:
            self.dimmable = light_type['dimmable']
            self.supports_color = light_type['supports_color']
            self.supports_ct = light_type['supports_ct']
            

    def update_state(self, new_state, transitiontime=HUE_DEFAULT_TRANSITION_TIME):
        relative_url = self.ROUTE + '/' + '10' + '/state'

        result = dict()
        for response in self.bridge._request('PUT', relative_url, new_state).json():
            response_type, response_val = response.popitem()

            if response_type == 'success': 
                attr_name, attr_val = response_val.popitem()
                attr_name = attr_name[len(relative_url+'/'):]
                result[attr_name] = {'success':True, 'val':attr_val}
                self.state.update({attr_name:attr_val})
            elif response_type == 'error':
                attr_name = response_val['address'][len(relative_url+'/'):]
                result[attr_name] = {'success':False}
        return result
        
class HueSensor(HueApiObject):
    ROUTE = '/sensors'
