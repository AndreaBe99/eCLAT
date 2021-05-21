def prog_load_all(program, type=None, maps=None, dev=None, pinmaps=None):
    # bpftool prog { load | loadall } OBJ PATH [type TYPE] [map {idx IDX |  name  NAME}  MAP] [dev NAME] [pinmaps MAP_DIR]
    command = "bpftool prog loadall" + program.get_obj_name() + " " + program.get_prog_pin_path() + " "
    # PERCORSO FISSO: command += "/sys/fs/bpf/progs" + program.get_name() \
    if type != None:
        command += "type" + type + " "
    if maps != None:
        command += "map "
        if maps.get_idx() != None:
            command += "idx" + maps.get_idx() + " "
        elif maps.get_name() != None:
            command += "name" + maps.get_name() + " "
        else:
            # Ci deve essere per forza IDX o NAME
            print("ERRORE")
    if dev != None:
        command += "dev" + dev + " "
    if pinmaps != None:
        command += "pinmaps" + pinmaps
    
    return command


def net_attach(attach_type, dev, prog=None, flag_overwrite=None):
    # bpftool net attach ATTACH_TYPE PROG dev NAME [ overwrite ]
    # bpftool net detach ATTACH_TYPE dev NAME
    # PROG := {id PROG_ID | pinned FILE | tag PROG_TAG}
    # ATTACH_TYPE := {xdp | xdpgeneric | xdpdrv | xdpoffload}
    command = ""
    if attach_type in ["xdp", "xdpgeneric", "xdpdrv", "xdpoffload"]:
        command += "bpftool net attach" + attach_type + " " 
    else:
        print("ERRORE")

    if prog != None:
        if prog.split(" ")[0] in ["id", "pinned", "tag"]:
            command += prog + " "
        else:
            print("ERRORE")

    command += dev + " "

    if flag_overwrite != None:
        command += flag_overwrite

    return command


def map_update(map_obj, update_flags=None):
    # bpftool map update MAP [key DATA] [value VALUE] [UPDATE_FLAGS]
    # MAP := {id MAP_ID | pinned FILE | name MAP_NAME}
    # DATA := {[hex] BYTES}
    # VALUE := {DATA | MAP | PROG}
    # UPDATE_FLAGS := {any | exist | noexist}
    command = ""
    if map_obj.get_map().split(" ")[0] in ["id", "pinned", "tag"]:
        command = "bpftool map update" + map_obj.get_map() + " "
    else:
        print("ERRORE")

    if map_obj.get_key() != None:
        command += "key"
        if map_obj.get_key().split(" ")[0] == "hex":
            try:
                int(map_obj.get_key().split(" ")[1], 16)
                print('That is a valid hex value.')
            except:
                print('That is an invalid hex value.')
            
            command += "hex" + " "
        command += map_obj.get_key() + " "

    if map_obj.get_value() != None:
        command += "value" + map_obj.get_value() + " "
    
    if update_flags in ["any", "exist", "noexist"]:
        command += update_flags + " "
    else:
        print("ERRORE")
        
    return command

