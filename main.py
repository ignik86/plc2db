
import PlcSnap
config_file = 'config.xml'

if __name__ == '__main__':
    plc = PlcSnap.PLCClass(config_file)
    print(plc.readtag('stamp'))
