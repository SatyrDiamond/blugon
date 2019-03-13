import matplotlib.pyplot as plt
import math

KELVIN_MIN = 1000
KELVIN_MAX = 12000
KELVIN_STEP = 100
KELVIN_RGB_TABLE = [
    [255,  56,   0],
    [255,  71,   0],
    [255,  83,   0],
    [255,  93,   0],
    [255, 101,   0],
    [255, 109,   0],
    [255, 115,   0],
    [255, 121,   0],
    [255, 126,   0],
    [255, 131,   0],
    [255, 138,  18],
    [255, 142,  33],
    [255, 147,  44],
    [255, 152,  54],
    [255, 157,  63],
    [255, 161,  72],
    [255, 165,  79],
    [255, 169,  87],
    [255, 173,  94],
    [255, 177, 101],
    [255, 180, 107],
    [255, 184, 114],
    [255, 187, 120],
    [255, 190, 126],
    [255, 193, 132],
    [255, 196, 137],
    [255, 199, 143],
    [255, 201, 148],
    [255, 204, 153],
    [255, 206, 159],
    [255, 209, 163],
    [255, 211, 168],
    [255, 213, 173],
    [255, 215, 177],
    [255, 217, 182],
    [255, 219, 186],
    [255, 221, 190],
    [255, 223, 194],
    [255, 225, 198],
    [255, 227, 202],
    [255, 228, 206],
    [255, 230, 210],
    [255, 232, 213],
    [255, 233, 217],
    [255, 235, 220],
    [255, 236, 224],
    [255, 238, 227],
    [255, 239, 230],
    [255, 240, 233],
    [255, 242, 236],
    [255, 243, 239],
    [255, 244, 242],
    [255, 245, 245],
    [255, 246, 247],
    [255, 248, 251],
    [255, 249, 253],
    [254, 249, 255],
    [252, 247, 255],
    [249, 246, 255],
    [247, 245, 255],
    [245, 243, 255],
    [243, 242, 255],
    [240, 241, 255],
    [239, 240, 255],
    [237, 239, 255],
    [235, 238, 255],
    [233, 237, 255],
    [231, 236, 255],
    [230, 235, 255],
    [228, 234, 255],
    [227, 233, 255],
    [225, 232, 255],
    [224, 231, 255],
    [222, 230, 255],
    [221, 230, 255],
    [220, 229, 255],
    [218, 229, 255],
    [217, 227, 255],
    [216, 227, 255],
    [215, 226, 255],
    [214, 225, 255],
    [212, 225, 255],
    [211, 224, 255],
    [210, 223, 255],
    [209, 223, 255],
    [208, 222, 255],
    [207, 221, 255],
    [207, 221, 255],
    [206, 220, 255],
    [205, 220, 255],
    [207, 218, 255],
    [207, 218, 255],
    [206, 217, 255],
    [205, 217, 255],
    [204, 216, 255],
    [204, 216, 255],
    [203, 215, 255],
    [202, 215, 255],
    [202, 214, 255],
    [201, 214, 255],
    [200, 213, 255],
    [200, 213, 255],
    [199, 212, 255],
    [198, 212, 255],
    [198, 212, 255],
    [197, 211, 255],
    [197, 211, 255],
    [197, 210, 255],
    [196, 210, 255],
    [195, 210, 255],
    [195, 209, 255]]

x = [x for x in range(KELVIN_MIN, KELVIN_MAX + KELVIN_STEP, KELVIN_STEP) ]
r, g, b = map(list, zip(*KELVIN_RGB_TABLE))

print(x)
plt.plot(x, r, 'r')
plt.plot(x, g, 'g')
plt.plot(x, b, 'b')

plx = [ 1900, 2600, 1850, 3200, 5200, 5400, 6000, 7000, 20000 ]
plr = [  255,  255,  255,  255,  255,  255,  255,  201,    64 ]
plg = [  147,  197,  214,  241,  250,  255,  255,  226,   156 ]
plb = [   41,  143,  170,  224,  244,  251,  255,  255,   255 ]
plt.plot(plx, plr, 'ro')
plt.plot(plx, plg, 'go')
plt.plot(plx, plb, 'bo')

def temp_to_gamma(temp):
    """
    Transforms temperature in Kelvin to Gamma values between 0 and 1.
    Source: http://www.tannerhelland.com/4435/convert-temperature-rgb-algorithm-code/
    """
    def rgb_to_gamma(color):
        if color < 0:
            color = 0
        if color > 255:
            color = 255
        return color #/ 255

    temp = temp / 100

    if temp <= 66: # red
        r = 255
    else:
        r = temp - 60
        r = 329.698727446 * (r ** -0.1332047592)

    if temp <= 66: # green
        g = temp
        g = 99.4708025861 * math.log(g) - 161.1195681661
    else:
        g = temp - 60
        g = 288.1221695283 * (g ** -0.0755148492)

    if temp <= 10: # blue
        b = 0
    elif temp >= 66:
        b = 255
    else:
        b = temp - 10
        b = 138.5177312231 * math.log(b) - 305.0447927307

    return map(rgb_to_gamma, (r, g, b))

tr, tg, tb = map(list, zip(*[ temp_to_gamma(y) for y in x ]))
plt.plot(x, tr, 'r')
plt.plot(x, tg, 'g')
plt.plot(x, tb, 'b')

plt.show()