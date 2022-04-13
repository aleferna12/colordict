import json
import os
import colordict.general as cg
_package_path = os.path.dirname(__file__)


class ColorDict(dict):
    def __init__(self, norm=255, mode='rgb', is_grayscale=False, palettes='all', palettes_path=''):
        dict.__init__(self)
        self.palettes = {}
        self.norm = norm
        self.mode = mode
        self.is_grayscale = is_grayscale
        self.palettes_path = palettes_path if palettes_path else os.path.join(_package_path, 'palettes')
        self._changed = set()
        for palette in os.scandir(self.palettes_path):
            pal_name = palette.name[:palette.name.index('.')]
            if palettes == 'all' or pal_name in palettes:
                with open(palette.path, 'r') as file: pal_dict = json.load(file)
                if pal_dict:
                    self.palettes[pal_name] = list(pal_dict)
                    for name, value in pal_dict.items():
                        self[name] = cg.renorm(value, 255, self.norm)

    def __getitem__(self, item):
        if isinstance(item, str):
            key, mode = item, self.mode
        else:
            key, mode = item
        value = dict.__getitem__(self, key)
        if self.is_grayscale:
            value = cg.grayscale(value)
        if mode == 'rgb':
            value = value[:3]
        elif mode == 'hex':
            value = cg.rgb_to_hex(cg.renorm(value, self.norm, 255))
        elif mode in ['yiq', 'hls', 'hsv']:
            converted = getattr(cg, 'rgb_to_' + mode)(cg.renorm(value[:3], self.norm, 1))
            value = cg.renorm(converted, 1, self.norm)
        return value

    def __setitem__(self, key, value):
        value = tuple(value)
        if not 3 <= len(value) <= 4:
            raise ValueError("Values assigned to ColorDict keys must be in (r, g, b) or (r, g, b, a) format")
        elif len(value) == 3:
            value += (self.norm,)
        dict.__setitem__(self, key, value)

    def named(self, rgb_a):
        color_list = []
        for name, value in self.items():
            if value[:len(rgb_a)] == rgb_a: color_list.append(name)
        return color_list

    def add(self, name, rgb_a, palette='independent', check=True):
        if check and name in self:
            print(f'Key "{name}" was not added because it already exists with value {self[name]}')
        else:
            self[name] = rgb_a
            if palette not in self.palettes: self.palettes[palette] = []
            self.palettes[palette].append(name)
            self._changed.add(palette)

    def remove(self, name, palette):
        self.palettes[palette].remove(name)
        self._changed.add(palette)

    def remove_all(self, name):
        del self[name]
        for palette, pal_list in self.palettes.items():
            self._changed.add(palette)
            try: pal_list.remove(name)
            except ValueError: pass

    def save(self):
        for palette in self._changed:
            pal_dict = {name: [int(spec*255/self.norm) for spec in self[name, 'rgba']] for name in self.palettes[palette]}
            with open(os.path.join(self.palettes_path, palette + '.json'), 'w') as file:
                json.dump(pal_dict, file, indent=4)
        self._changed.clear()

    def backup(self):
        color_dict = {}
        for palette, color_list in self.palettes.items():
            color_dict[palette] = {name: [int(spec*255/self.norm) for spec in self[name, 'rgba']] for name in color_list}
        with open(os.path.join(_package_path, 'backup.json'), 'w') as file:
            json.dump(color_dict, file, indent=4)

    def restore(self):
        self.clear()
        self.palettes.clear()
        self._changed.clear()
        with open(os.path.join(_package_path, 'backup.json'), 'r') as file:
            color_dict = json.load(file)
        for palette, color_list in color_dict.items():
            if color_list:
                self.palettes[palette] = list(color_list)
                self._changed.add(palette)
                for name, value in color_list.items():
                    self[name] = cg.renorm(value, 255, self.norm)
