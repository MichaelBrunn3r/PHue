import urllib.request
import json
import http.client
import time
import re

class HueLightCapabilites:
    def __init__(self, capabilities):
        mindimlvl = capabilities['control'].get('mindimlevel')
        self.isDimmable = mindimlvl != None
        if self.isDimmable: self.mindimlevel = mindimlvl

        colorgamut = capabilities['control'].get('colorgamut')
        self.supports_color = colorgamut != None
        if self.supports_color: self.colorgamut = colorgamut

        ct = capabilities['control'].get('ct')
        self.supports_ct = ct != None
        if self.supports_ct: self.ct = ct

    def __str__(self):
        attributes = list()
        if self.isDimmable: attributes.append("'mindimlevel':" + str(self.mindimlevel))
        if self.supports_color: attributes.append("'colorgamut':" + str(self.colorgamut))
        if self.supports_ct: attributes.append("'ct':" + str(self.ct))

        serial = ""
        for i in range(len(attributes)):
            if i != 0: serial += ', '
            serial += attributes[i]
        return '{' + serial + '}'


class HueLight:
    def __init__(self, id, uniqueid, modelid, name, state, capabilities):
        self.id = int(id)
        self.uniqueid = uniqueid
        self.modelid = modelid
        self.name = name

        # Capabilites of the light
        self.capabilities = HueLightCapabilites(capabilities)

        # State of the light
        self.isOn = state['on']
        if self.capabilities.supports_color or self.capabilities.supports_ct: self.bri = state['bri']
        if self.capabilities.supports_ct: self.ct = state['ct']
        if self.capabilities.supports_color:
            self.hue = state['hue']
            self.sat = state['sat']

    def on(self, transition_time=10):
        connection.request("PUT", "/api/" + username + "/lights/" + str(self.id) + "/state", '{"on":true, "transitiontime":' + str(transition_time) + '}')
        http_response = connection.getresponse()
        json_response = json.loads(http_response.read().decode('utf-8'))
        print(json_response)
        self.isOn = True

    def off(self, transition_time=10):
        connection.request("PUT", "/api/" + username + "/lights/" + str(self.id) + "/state", '{"on":false, "transitiontime":' + str(transition_time) + '}')
        http_response = connection.getresponse()
        json_response = json.loads(http_response.read().decode('utf-8'))
        print(json_response)
        self.isOn = False

    def blink(self):
        if self.isOn:
            self.off(0)
            self.on(0)
        else:
            self.on(0)
            self.off(0)
        

    def __str__(self):
        attributes = list()
        attributes.append('"id":' + str(self.id) + ', "uniqueid:"' + str(self.uniqueid) + ', "modelid":' + str(self.modelid) \
                + ', "name":' + str(self.name) + ', "capabilites":' + str(self.capabilities))

        if self.capabilities.supports_color or self.capabilities.supports_ct: attributes.append("'bri':" + str(self.bri))
        if self.capabilities.supports_color: attributes.append("'hue':" + str(self.hue) + ", 'sat':" + str(self.sat))
        if self.capabilities.supports_ct: attributes.append("'ct':" + str(self.ct))

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
        lights.append(HueLight(key, value['uniqueid'], value['modelid'], value['name'], value['state'], value['capabilities']))

    return lights

hue_bridge_ip = "192.168.0.100"
username = "x5lCjhRO0qBi3rf4MGVh-5pSEPq5vcnKpCGV0O9q"
connection = http.client.HTTPConnection(hue_bridge_ip)
lights = hue_get_lights(connection, username)
current_light = None
for light in lights: 
    if light.id == 10: current_light = light
	

#current_time_millis = lambda: int(round(time.time() * 1000))
#last_t = current_time_millis()
#while True:
#    if current_time_millis() - last_t > 10000:
#        print("triggered")
#    last_t = current_time_millis()
#    print("cycle")
#
#    if current_light.isOn: current_light.off(5)
#    else: current_light.on(5)

current_light.blink()
