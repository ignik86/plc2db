import xml.etree.ElementTree as ET
import PlcSnap
from sqlalchemy import create_engine
from sqlalchemy import MetaData
from sqlalchemy import orm
import time
import os, sys



config_file = '/home/pi/PLC2DB/config.xml'


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

    db_ip = tree.find('server').get('ip')
    login = tree.find('server').get('login')
    password = tree.find('server').get('password')
    db_name = tree.find('db').get('name')
    timeout = tree.find('tags').get('frequency')
    eng_str = 'mysql+mysqlconnector://%s:%s@%s/%s' % (login, password, db_ip, db_name)
    engine = create_engine(eng_str, echo=False)

    meta = MetaData(bind=engine, reflect=True)
    orm.Mapper(Values, meta.tables['values'])
    orm.Mapper(Tags, meta.tables['tags'])
    session = orm.Session(bind=engine)
    while True:
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
            time.sleep(int(timeout))


def clear():
    if os.name == 'posix':
        os.system('clear')

    elif os.name in ('ce', 'nt', 'dos'):
        os.system('cls')


if __name__ == '__main__':
    while True:
        try:
            main()
        except Exception:

            wait = 10
            for i in range(wait):
                print('error. Restart script in %s' % str(wait-i))
                time.sleep(1)
                clear()
            os.execl(sys.executable, sys.executable, *sys.argv)

