#!/usr/bin/python3

from configparser import ConfigParser
from argparse import ArgumentParser
import time
import math
from subprocess import check_call
from os import getenv
from sys import stdout

MAKE_INSTALL_PREFIX = '/usr'

#--------------------------------------------------DEFAULTS

VERSION = '1.6'

DISPLAY = getenv('DISPLAY')

ONCE = False

SIMULATE = False

INTERVAL = 120

CONFIG_DIR = getenv('XDG_CONFIG_HOME')
if not CONFIG_DIR:
    CONFIG_DIR = getenv('HOME') + '/.config'
CONFIG_DIR += '/blugon'

BACKEND = 'scg'

#--------------------------------------------------DEFINITIONS

MAX_MINUTE = 24 * 60

COLOR_TABLE = {
        0:  '282a2e',
        1:  'a54242',
        2:  '8c9440',
        3:  'de935f',
        4:  '5f819d',
        5:  '85678f',
        6:  '5e8d87',
        7:  '707880',
        8:  '373b41',
        9:  'cc6666',
        10: 'b5bd68',
        11: 'f0c674',
        12: '81a2be',
        13: 'b294bb',
        14: '8abeb7',
        15: 'c5c8c6'}

BACKEND_LIST = [ 'xgamma', 'scg', 'tty' ]

#--------------------------------------------------PARSER

argparser = ArgumentParser(prog='blugon', description="A simple Blue Light Filter for X")

argparser.add_argument('-v', '--version', action='store_true', dest='version', help='print version and exit')
argparser.add_argument('-p', '--printconfig', action='store_true', dest='printconfig', help='print default configuration and exit')
argparser.add_argument('-o', '--once', action='store_true', dest='once', help='apply configuration for current time and exit')
argparser.add_argument('-s', '--simulation', action='store_true', dest='simulate', help='simulate blugon over one day and exit')
argparser.add_argument('-i', '--interval', nargs='?', dest='interval', type=float, help='set %(dest)s in seconds (default: '+str(INTERVAL)+')')
argparser.add_argument('-c', '--config', nargs='?', dest='config_dir', type=str, help='set configuration directory (default: '+CONFIG_DIR+')')
argparser.add_argument('-b', '--backend', nargs='?', dest='backend', type=str, help='set backend (default: '+BACKEND+')')

args = argparser.parse_args()

if args.version:
    print('blugon ' + VERSION)
    exit()

#--------------------------------------------------CONFIG

                                               #---ARGUMENTS
if args.config_dir:
    CONFIG_DIR = args.config_dir
if not CONFIG_DIR.endswith('/'):
    CONFIG_DIR += '/'
CONFIG_FILE_GAMMA = CONFIG_DIR + 'gamma'
CONFIG_FILE_GAMMA_FALLBACK = MAKE_INSTALL_PREFIX + '/share/blugon/configs/default/gamma'
CONFIG_FILE_TEMP = CONFIG_DIR + 'temp'
CONFIG_FILE_CONFIG = CONFIG_DIR + 'config'
                                               #---ARGUMENTS END

confparser = ConfigParser()
confparser['main'] = {
        'interval': str(INTERVAL),
        'backend':  BACKEND      }

confparser['tty'] = {
        'color0':  str(COLOR_TABLE[0]) ,
        'color1':  str(COLOR_TABLE[1]) ,
        'color2':  str(COLOR_TABLE[2]) ,
        'color3':  str(COLOR_TABLE[3]) ,
        'color4':  str(COLOR_TABLE[4]) ,
        'color5':  str(COLOR_TABLE[5]) ,
        'color6':  str(COLOR_TABLE[6]) ,
        'color7':  str(COLOR_TABLE[7]) ,
        'color8':  str(COLOR_TABLE[8]) ,
        'color9':  str(COLOR_TABLE[9]) ,
        'color10': str(COLOR_TABLE[10]),
        'color11': str(COLOR_TABLE[11]),
        'color12': str(COLOR_TABLE[12]),
        'color13': str(COLOR_TABLE[13]),
        'color14': str(COLOR_TABLE[14]),
        'color15': str(COLOR_TABLE[15])}

if args.printconfig:
    confparser.write(stdout)
    exit()

confparser.read(CONFIG_FILE_CONFIG)

confs = confparser['main']

#--------------------------------------------------ARGUMENTS

ONCE = args.once

SIMULATE = args.simulate

INTERVAL = confs.getint('interval')
if args.interval:
    INTERVAL = math.ceil(args.interval)

BACKEND = confs.get('backend')
if args.backend:
    BACKEND = args.backend
if not BACKEND in BACKEND_LIST:
    raise ValueError('backend not found, choose from:\n    ' + '\n    '.join(BACKEND_LIST))

if (not DISPLAY) and (BACKEND != 'tty'):
    exit(11)                             # provide exit status 11 for systemd-service

#--------------------------------------------------FUNCTIONS

def verbose_print(string):
    if VERBOSE:
        print(string)
    return

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
        return color / 255

    temp = temp / 100

    if temp <= 66:                               # red
        r = 255
    else:
        r = temp - 60
        r = 329.698727446 * (r ** -0.1332047592)

    if temp <= 66:                               # green
        g = temp
        g = 99.4708025861 * math.log(g) - 161.1195681661
    else:
        g = temp - 60
        g = 288.1221695283 * (g ** -0.0755148492)

    if temp <= 10:                               # blue
        b = 0
    elif temp >= 66:
        b = 255
    else:
        b = temp - 10
        b = 138.5177312231 * math.log(b) - 305.0447927307

    return map(rgb_to_gamma, (r, g, b))

def read_gamma():
    """
    Reads configuration of Gamma values from 'CONFIG_FILE_GAMMA'
    Returns 2 lists: gamma, minutes
    """
    def line_to_list(line):
        str_ls = line.split()
        if not str_ls:                    # remove empty line
            return False
        if str_ls[0].startswith('#'):     # remove comment
            return False
        flt_ls = list(map(float, str_ls)) # to gamma values
        return flt_ls
    def check_length(ls):
        length = len(ls)
        if (not (length==5 or length==3)):
            raise ValueError('gamma configuration requires syntax:\n'
                    '    [hour] [minute]   [red-gamma] [green-gamma] [blue-gamma]\n'
                    'or  [hour] [minute]   [temperature]')
        if length==3:                      # handle temperature configuration
            r, g, b = temp_to_gamma(ls[2])
            del ls[2]
            ls = ls + [r, g, b]
        return ls
    def time_to_minutes(ls):
        ls[0] = int(60 * ls[0] + ls[1])
        del ls[1]
        return ls
    def take_first(ls):
        return ls[0]
    def pop_first(ls):
        x = ls[0]
        del ls[0]
        return x

    try:
        file_gamma = open(CONFIG_FILE_GAMMA, 'r')
    except:
        verbose_print('Using fallback gamma configuration file: \'' + CONFIG_FILE_GAMMA_FALLBACK + '\'')
        file_gamma = open(CONFIG_FILE_GAMMA_FALLBACK, 'r')
    gamma = list(map(line_to_list, file_gamma.read().splitlines()))
    file_gamma.close()

    gamma = list(filter(lambda x : x, gamma)) # removes empty lines and comments
    gamma = list(map(check_length, gamma))    # sanity check, temperature to gamma
    gamma = list(map(time_to_minutes, gamma))
    gamma.sort(key=take_first)                # sort by time
    minutes = (list(map(pop_first, gamma)))
    return gamma, minutes

def calc_gamma(minute, list_minutes, list_gamma):
    """Calculates the RGB Gamma values inbetween configured times"""
    next_index = list_minutes.index(next((x for x in list_minutes if x >= minute), list_minutes[0]))
    next_minute = list_minutes[next_index]
    prev_minute = list_minutes[next_index - 1]
    if next_minute < prev_minute:
        next_minute += MAX_MINUTE

    def inbetween_gamma(next_gamma, prev_gamma):
        """Calculates Gamma value with a linear function"""
        diff_gamma = next_gamma - prev_gamma
        diff_minute = next_minute - prev_minute
        add_minute = minute - prev_minute
        try:
            factor = add_minute / diff_minute
        except:
            factor = 0
        gamma = prev_gamma + factor * diff_gamma
        return gamma

    next_red = list_gamma[next_index][0]
    prev_red = list_gamma[next_index - 1][0]
    next_green = list_gamma[next_index][1]
    prev_green = list_gamma[next_index - 1][1]
    next_blue = list_gamma[next_index][2]
    prev_blue = list_gamma[next_index - 1][2]

    red_gamma = inbetween_gamma(next_red, prev_red)
    green_gamma = inbetween_gamma(next_green, prev_green)
    blue_gamma = inbetween_gamma(next_blue, prev_blue)

    return red_gamma, green_gamma, blue_gamma

def call_xgamma(red_gamma, green_gamma, blue_gamma):
    """Start a subprocess of backend xorg-xgamma"""
    str_red_gamma = str(red_gamma)
    str_green_gamma = str(green_gamma)
    str_blue_gamma = str(blue_gamma)
    check_call(['xgamma', '-quiet', '-rgamma', str_red_gamma, '-ggamma', str_green_gamma, '-bgamma', str_blue_gamma])
    return

def call_scg(red_gamma, green_gamma, blue_gamma):
    """Start a subprocess of backend scg"""
    str_red_gamma = str(red_gamma)
    str_green_gamma = str(green_gamma)
    str_blue_gamma = str(blue_gamma)
    check_call([MAKE_INSTALL_PREFIX + '/lib/blugon/scg', str_red_gamma, str_green_gamma, str_blue_gamma])
    return

def call_tty(red_gamma, green_gamma, blue_gamma):
    """Start a subprocess of backend tty"""
    def hex_tempered(i):
        color = COLOR_TABLE[i]
        def flt_to_hex(flt):
            if flt > 255:
                flt = 255
            return format(int(flt), 'x')
        hex_r = flt_to_hex(red_gamma * int(color[0:2], 16))
        hex_g = flt_to_hex(green_gamma * int(color[2:4], 16))
        hex_b = flt_to_hex(blue_gamma * int(color[4:6], 16))
        string = format(i, 'X') + hex_r + hex_g + hex_b
        return string
    hex_list = [ hex_tempered(i) for i in range(16) ]
    check_call([MAKE_INSTALL_PREFIX + '/lib/blugon/tty.sh'] + hex_list)
    return

def call_backend(backend, red_gamma, green_gamma, blue_gamma):
    """Wrapper to call various backends"""
    if backend == 'xgamma':
        call_xgamma(red_gamma, green_gamma, blue_gamma)
    elif backend == 'scg':
        call_scg(red_gamma, green_gamma, blue_gamma)
    elif backend == 'tty':
        call_tty(red_gamma, green_gamma, blue_gamma)
    return

def get_minute():
    """Returns the current minute"""
    time_struct = time.localtime()
    minute = 60 * time_struct.tm_hour + time_struct.tm_min + time_struct.tm_sec / 60
    return minute

def reprint_time(minute):
    """Prints time in a human readable format"""
    str_hour = ('00' + str(int(minute // 60)))[-2:]
    str_minute = ('00' + str(int(minute % 60)))[-2:]
    print('\r' + str_hour + ':' + str_minute, end='')
    return

#--------------------------------------------------MAIN

def main():
    LIST_GAMMA, LIST_MINUTES = read_gamma()

    def while_body(minute, sleep_time=0):
        """Puts everything together to have only one function to call"""
        red_gamma, green_gamma, blue_gamma = calc_gamma(minute, LIST_MINUTES, LIST_GAMMA)
        call_backend(BACKEND, red_gamma, green_gamma, blue_gamma)
        try:
            time.sleep(sleep_time)
        except:
            exit()
        return

    if ONCE:
        while_body(get_minute(), 0)
        exit()

    if SIMULATE:
        current_minute = get_minute()
        steps = 100
        sleep_time = 1 / 50
        for step in range(0, steps):
            minute = (current_minute + step * MAX_MINUTE / steps) % MAX_MINUTE
            reprint_time(minute)
            while_body(minute, sleep_time)
        print() # print newline
        while_body(current_minute)
        exit()

    while True :
        while_body(get_minute(), INTERVAL)

    return

if __name__ == "__main__":
    main()
