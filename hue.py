import json
import requests
import hue_color

HUE_DEFAULT_TRANSITION_TIME = 4
HUE_LIGHT_TYPES = {"Color light":{"supports_color":True, "supports_ct":False, "dimmable":True}, \
                    "Extended color light":{"supports_color":True, "supports_ct":True, "dimmable":True}, \
                    "Color temperature light":{"supports_color":False, "supports_ct":True, "dimmable":True}, \
                    "Dimmable light":{"supports_color":False, "supports_ct":False, "dimmable":True}}
HUE_DEFAULT_USERNAME = "newdeveloper"

class HueBridge:
    def __init__(self, ip, username):
        self.ip = ip
        self.username = username
        self.base_url = 'http://' + ip + '/api/' + username

    def _request(self, method, res_location, data={}):
        """
        Requests resources from the Hue Bridge via HTTP

        Params:
        -------
        arg1 : str 
            The Name of the HTTP request method used
        arg2 : str
            The path to the relative location of the resource
        arg3 : dict
            Additional request data

        Returns:
        --------
        dict
            Dictionary containing the received resource
        """
        if method == 'GET': return requests.get(self.base_url + res_location).json()
        elif method == 'PUT': return requests.put(self.base_url + res_location, json.dumps(data)).json()

    def _request_groups(self):
        """ Helper method to get all current groups saved in the Hue Bridge """
        group_states = self._request('GET', '/groups')
        groups = dict()
        for id, attr in group_states.items(): groups[id] = HueGroup(self, attr)
        return groups

    def _request_scenes(self):
        """ Helper method to get all current scenes saved in the Hue Bridge """
        scene_states = self._request('GET', '/scenes')
        scenes = dict()
        for id, attr in scene_states.items(): scenes[id] = HueScene(attr)
        return scenes

    def get_group(self, name):
        if not hasattr(self, 'groups'): self.groups = self._request_groups()
        for id, group in self.groups.items():
            if group.name == name: return { id : group}
        return None

    def get_scene(self, group, name):
        if not hasattr(self, 'scenes'): self.scenes = self._request_scenes()

        for id in self.scenes:
            scene = self.scenes[id] 
            if scene.name == name and scene.lights == group.lights: 
                return { id : scene }
        return None

class HueApiObject:
    def __init__(self, attr):
        for attr_name, val in attr.items():
            object.__setattr__(self, attr_name, val)

    def __str__(self):
        return str(self.__dict__)

class HueGroup(HueApiObject):
    ROUTE = '/groups'

    def __init__(self, bridge, attr):
        super().__init__(attr)

    def set_scene(self, bridge, group_id, scene_name):
        scene_id, _ = bridge.get_scene(self, scene_name).popitem()
        self.set_action(bridge, group_id, 'scene', scene_id)

    def set_action(self, bridge, group_id, key, value):
        path = self.ROUTE + '/' + group_id + '/action/'
        responses = bridge._request('PUT', path, {key:value, 'ct':'wow'})
        for response in responses:
            response_type, response_value = response.popitem() 
            if response_type == 'success':
                key, value = response_value.popitem()
                attr = key[len(path):]
                self.action[attr] = value

    def dim(self, bridge, group_id, amount):
        self.set_action(bridge, group_id, 'bri', self.action['bri'] + amount)

class HueScene(HueApiObject):
    ROUTE = '/scenes'

    def __init__(self, attr):
        super().__init__(attr)