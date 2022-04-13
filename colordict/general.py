import colorsys


# Returns a color value normalized to "new"
def renorm(color_value, old, new):
    return tuple([spec*new/old for spec in color_value])


# Converts rgb color to grayscale
# This can be used to visualize how a palette would look if printed in black and white
def grayscale(rgb):
    ws = (0.3, 0.59, 0.11)
    return (sum(rgb[i]*ws[i] for i in range(3)),)*3


# Converts rgb value with norm=255 to hex string
def rgb_to_hex(rgb):
    return '#%02x%02x%02x' % tuple([int(spec) for spec in rgb[:3]])


# Converts hex value to rgb with norm=255
def hex_to_rgb(hex_):
    return tuple(int(hex_.strip('#')[i:i + 2], 16) for i in (0, 2, 4))


def _tuplefier(func):
    def inner(color_value):
        return func(*color_value)

    return inner


for conv_func in colorsys.__all__:
    globals()[conv_func] = _tuplefier(getattr(colorsys, conv_func))