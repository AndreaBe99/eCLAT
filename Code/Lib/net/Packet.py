
def readU8(parametri = -1):
    if parametri == -1:
        return "hike_packet_read_u8("
    return parametri
    
def readU16(parametri = -1):
    if parametri == -1:
        return "hike_packet_read_u16("
    return parametri
    
def readU32(parametri = -1):
    if parametri == -1:
        return "hike_packet_read_u32("
    return parametri
    
def readU64(parametri = -1):
    if parametri == -1:
        return "hike_packet_read_u64("
    return parametri
    

def writeU8(parametri):
    return "hike_packet_write_u8(" + parametri[2:]

def writeU16(parametri):
    return "hike_packet_write_u16(" + parametri[2:]

def writeU32(parametri):
    return "hike_packet_write_u32(" + parametri[2:]

def writeU64(parametri):
    return "hike_packet_write_u64(" + parametri[2:]
