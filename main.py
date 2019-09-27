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


class Tags(object):
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return "Tag('%s')" % (self.name)


def main():

    plc = PlcSnap.PLCClass(config_file)
    tree = ET.parse(config_file)
    root = tree.getroot()
    engine = create_engine('mysql+mysqlconnector://root:MT0334!@172.24.15.181:3306/plc_tag', echo=False)

    meta = MetaData(bind=engine, reflect=True)
    orm.Mapper(Values, meta.tables['values'])
    orm.Mapper(Tags, meta.tables['tags'])
    session = orm.Session(bind=engine)

    for tag in root.iter('tag'):

        q = session.query(Tags).filter(Tags.name == tag.attrib['name'])
        record = q.all()
        if len(record) == 0:
            tags_table = Tags(tag.attrib['name'])
            session.add(tags_table)
            session.commit()
        q = session.query(Tags).filter(Tags.name == tag.attrib['name'])
        record = q.all()
        value_table = Values(record[0].id, plc.readtag(tag.attrib['name']))

        session.add(value_table)
        session.commit()
        session.close()


if __name__ == '__main__':
    main()
