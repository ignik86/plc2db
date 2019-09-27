import xml.etree.ElementTree as ET
import snap7
import struct
import time

class PLCClass:

    def __init__(self, configfile):
        super(self.__class__, self).__init__()
        self.configfile = configfile
        self.config = XmlParse(self.configfile)

    def readtag(self, tagnr):

        plc = snap7.client.Client()
        plc.connect(self.config.ip(), 0, 2)
        db = plc.db_read(int(self.config.tagval(tagnr, 'dbnr')),
                         int(self.config.tagval(tagnr, 'startadress')),
                         int(self.config.tagval(tagnr, 'size')))
        if self.config.tagval(tagnr, 'type') == 'integer':
            val = struct.unpack('>I', db)
            return val[0]
        if self.config.tagval(tagnr, 'type') == 'short':
            val = struct.unpack('>H', db)
            return val[0]
        if self.config.tagval(tagnr, 'type') == 'float':
            val = struct.unpack('>f', db)
            return val[0]
        if self.config.tagval(tagnr, 'type') == 'byte':
            val = struct.unpack('>b', db)
            return val[0]
        if self.config.tagval(tagnr, 'type') == 'boolarray':
            val = []
            k=0
            while k < int(self.config.tagval(tagnr, 'size')):
                for i in range(0, 8):
                    j = 2 ** i
                    if db[k] & j == j:
                        val = val + [True]
                    else:
                        val = val + [False]
                k = k+1
            return val
        if self.config.tagval(tagnr, 'type') == 'string':
            val = str(db,'utf-8')
            return val

    def writetag(self,tagnr,val):

        plc = snap7.client.Client()
        plc.connect(self.config.ip(), 0, 2)
       #plc.db_write(int(self.config.tagval(tagnr, 'dbnr')),
                    # int(self.config.tagval(tagnr, 'startadress')),
                    # val)
        fmt = 'x'
        if self.config.tagval(tagnr, 'type') == 'integer':
            fmt = '>I'
        if self.config.tagval(tagnr, 'type') == 'short':
            fmt = '>H'
        if self.config.tagval(tagnr, 'type') == 'float':
            fmt = '>f'
        if self.config.tagval(tagnr, 'type') == 'byte':
            fmt = '>b'
        data = struct.pack(fmt, val)
        plc.db_write(int(self.config.tagval(tagnr, 'dbnr')),
                     int(self.config.tagval(tagnr, 'startadress')),
                     data)


class XmlParse:
    def __init__(self, file):
        super(self.__class__, self).__init__()
        self.tree = ET.parse(file)
        self.root = self.tree.getroot()

    def ip(self):
        ret = self.tree.find('plc').get('ip')
        return ret

    def tagval(self, id, str):
        ret = ''
        for tag in self.root.iter('tag'):
            if tag.attrib['id'] == id:
                    ret = tag.attrib[str]
        return ret

