
RD_VERSION = 0x00
GET_VALUE = 0x01

VCC = 65536

def getVersion(dev):
    dev.send([RD_VERSION])
    raw = dev.read(3)
    return raw[1] + raw[2] * 256

def getValue(dev):
    dev.send([GET_VALUE])
    raw = dev.read(3)
    return VCC - (raw[1] + raw[2] * 256)

