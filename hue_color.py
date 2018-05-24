def rgb2xy(rgb_color):
    # Gamma Correction
    r = gamma_correct(rgb_color[0])
    g = gamma_correct(rgb_color[1])
    b = gamma_correct(rgb_color[2])

    # RGB to XYZ
    X = r * 0.664511 + g * 0.154324 + b * 0.162028
    Y = r * 0.283881 + g * 0.668433 + b * 0.047685
    Z = r * 0.000088 + g * 0.072310 + b * 0.986039

    # Calculate XY from XYZ
    return xyz2xy((X,Y,Z))

def xy2rgb(xy_color, brightness=1.0):
    X,Y,Z = xy2xyz(xy_color, brightness)

    # XYZ to RGB
    r = X * 1.656492 - Y * 0.354851 - Z * 0.255038
    g = -X * 0.707196 + Y * 1.655397 + Z * 0.036152
    b = X * 0.051713 - Y * 0.121364 + Z * 1.011530

    # Gamma Correction
    r = gamma_correct(r, True)
    g = gamma_correct(g, True)
    b = gamma_correct(b, True)

    # Bring all negative components to zero
    r,g,b = map(lambda x: max(0,x), [r,g,b])

    # If one component is greater than 1, weight components by that value.
    max_component = max(r,g,b)
    if max_component > 1: r,g,b = map(lambda x: x / max_component, [r,g,b])

    return r,g,b

def xyz2xy(xyz_color):
    xyz_sum = xyz_color[0] + xyz_color[1] + xyz_color[2]
    x = xyz_color[0] / xyz_sum
    y = xyz_color[1] / xyz_sum
    return x,y

def xy2xyz(xy_point, brightness=1.0):
    Y = brightness
    X = (Y / xy_point[1]) * xy_point[0]
    Z = (Y / xy_point[1]) * (1 - xy_point[0] - xy_point[1])

    return X,Y,Z

def gamma_correct(val, reverse=False):
    if reverse:
        if val <= 0.0031308: return val * 12.92
        else: return (1.0 + 0.055) * pow(val, (1.0 / 2.4)) - 0.055
    else:
        if val > 0.04045: return pow((val + 0.055) / (1.0 + 0.055), 2.4)
        else: return val / 12.92

def hex2rgb(hex, prefix='0x'):
    hex = hex.lstrip(prefix)
    return tuple(int(hex[i:i+2],16) for i in range(0,5,2))

def rgb2hex(rgb, prefix='0x'):
    return prefix + '%X%X%X' % (rgb[0], rgb[1], rgb[2])