import os
from eCLAT_Code.Code.path import Path

def allow():
    path = Path.import_path + "hike_program/allow.c"
    if os.path.exists(path):
        return path
        #return "eCLAT_Code/Code/Lib/hike/allow.c"

def bar():
    path = Path.import_path + "hike_program/bar.c"
    if os.path.exists(path):
        return path
        #return "eCLAT_Code/Code/Lib/hike/bar.c"

def drop():
    path = Path.import_path + "hike_program/drop.c"
    if os.path.exists(path):
        return path
    #return "eCLAT_Code/Code/Lib/hike/drop.c"

def fast():
    path = Path.import_path + "hike_program/fast.c"
    if os.path.exists(path):
        return path
    #return "eCLAT_Code/Code/Lib/hike/fast.c"

def mon():
    path = Path.import_path + "hike_program/mon.c"
    if os.path.exists(path):
        return path
    #return "eCLAT_Code/Code/Lib/hike/mon.c"

def parse_ethernet():
    path = Path.import_path + "hike_program/parse_ethernet.c"
    if os.path.exists(path):
        return path
    #return "eCLAT_Code/Code/Lib/hike/parse_ethernet.c"

def slow():
    path = Path.import_path + "hike_program/slow.c"
    if os.path.exists(path):
        return path
    #return "eCLAT_Code/Code/Lib/hike/slow.c"
