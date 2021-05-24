# bpftool prog { load | loadall } OBJ PATH [type TYPE] [map {idx IDX |  name  NAME}  MAP] [dev NAME] [pinmaps MAP_DIR]
def prog_load_all(load_type, prog_obj, prog_path, type=None, map_idx=None, map_name=None, map_map=None, dev_name=None, pinmaps_map_dir=None):
    # load_type = "load" or "loadall" 
    command = "bpftool prog " + load_type + prog_obj + " " + prog_path + " "
    # Fixed Path???: command += ... +"/sys/fs/bpf/progs" + ...
    if type != None:
        command += "type" + type + " "

    if map_idx != None:
        command += "map idx" + map_idx + " " + map_map
    elif map_name != None:
        command += "map name" + map_name + " " + map_map

    if dev_name != None:
        command += "dev" + dev_name + " "

    if pinmaps_map_dir != None:
        command += "pinmaps" + pinmaps_map_dir
    
    return command



# bpftool net attach ATTACH_TYPE PROG dev NAME [ overwrite ]
# bpftool net detach ATTACH_TYPE dev NAME
##### PROG := {id PROG_ID | pinned FILE | tag PROG_TAG}
##### ATTACH_TYPE := {xdp | xdpgeneric | xdpdrv | xdpoffload}
def net_attach(attach_type, dev_name, prog=None, flag_overwrite=None):
    command = ""
    if attach_type in ["xdp", "xdpgeneric", "xdpdrv", "xdpoffload"]:
        command += "bpftool net attach" + attach_type + " " 
    else:
        #Placeholder
        print("ERRORE")

    if prog != None:
        if prog.split(" ")[0] in ["id", "pinned", "tag"]:
            command += prog + " "
        else:
            #Placeholder
            print("ERRORE")

    command += dev_name + " "

    if flag_overwrite != None:
        command += flag_overwrite

    return command



# bpftool map update MAP [key DATA] [value VALUE] [UPDATE_FLAGS]
##### MAP := {id MAP_ID | pinned FILE | name MAP_NAME}
##### DATA := {[hex] BYTES}
##### VALUE := {DATA | MAP | PROG}
##### UPDATE_FLAGS := {any | exist | noexist}
def map_update(map_map, key_data=None, value=None, update_flags=None):
    command = ""
    if map_map.split(" ")[0] in ["id", "pinned", "tag"]:
        command = "bpftool map update" + map_map + " "
    else:
        #Placeholder
        print("ERRORE")

    if key_data != None:
        command += "key"
        if key_data.split(" ")[0] == "hex":
            try:
                int(key_data.split(" ")[1], 16)
                #Placeholder
                print('That is a valid hex value.')
            except:
                #Placeholder
                print('That is an invalid hex value.')
            command += "hex" + " "
        command += key_data + " "

    if value != None:
        command += "value" + value + " "
    
    if update_flags in ["any", "exist", "noexist"]:
        command += update_flags + " "
    else:
        #Placeholder
        print("ERRORE")
        
    return command

