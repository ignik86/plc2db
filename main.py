import xml.etree.ElementTree as ET
import PlcSnap
from sqlalchemy import create_engine
from sqlalchemy import MetaData
from sqlalchemy import orm
from datetime import datetime

config_file = 'config.xml'


class Values(object):
    def __init__(self, tag_id, value):
        self.tag_id = tag_id
        self.value = value

    def __repr__(self):
        return "Value('%s')" % (self.value)


if __name__ == '__main__':
    plc = PlcSnap.PLCClass(config_file)
    tree = ET.parse(config_file)
    root = tree.getroot()
    engine = create_engine('mysql+mysqlconnector://root:MT0334!@172.24.15.181:3306/plc_tag', echo=True)

    meta = MetaData(bind=engine, reflect=True)
    orm.Mapper(Values, meta.tables['values'])
    session = orm.Session(bind=engine)

    for tag in root.iter('tag'):
        print(tag.attrib['name'] + ':' + str(plc.readtag(tag.attrib['id'])))
        value_table = Values(tag.attrib['id'], plc.readtag(tag.attrib['id']))
        session.add(value_table)
        session.commit()
        session.close()
