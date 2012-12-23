import os
import os.path
from multiprocessing import Process,Pipe
from utils.importhelper import load
from kyotocabinet import *
from utils.configParser import parse as confParse

db = DB()
assert db.open('pkgverdb.kch', DB.OWRITER | DB.OREADER | DB.OCREATE), 'error opening db'

config = {}

def processConfig(config):
    config['hoppers'] = map(lambda a: a.strip(), config['hoppers'].split(','))
    config['storages'] = map(lambda a: a.strip(), config['storages'].split(','))
    return config

def buildpkg(data):
    '''
    this function takes a pkgname and a pkgversion and turns a PKGBUILD.in into a PKGBUILD
    it replaces %n with data[0], %v with data[1], and %% with %
    '''
    # determine the PKGBUILD.in to use
    if not data[0] in os.listdir(config['pkgdir']): 
        print(data[0] + ' not in directory')
        return
    path = 'pkgs/'+data[0]
    PKGBUILD = open(path + '/PKGBUILD.in', 'r').read().replace('%n', data[0]).replace('%v', data[1]).replace('%r', data[2]).replace('%%', '%')
    
    # send it to the storage modules
    for i in storages:
        i.store(path, PKGBUILD)

def process(data):
    '''
    data is a touple of (package, version, rev)
    this funciton determines if an update is needed and builds it
    '''
    print('Recieved data: ' + ','.join(data))
    # determine if the version they gave is newer than the current version
    ver = ''
    for i in data[1]:
        if i.isdigit():
            ver += i

    rev = int(data[2])
    revcur = '1'

    vercur = ''
    if db[data[0]]:
        for i in db[data[0]].split(',')[0]:
            if i.isdigit():
                vercur += i
        # grab the revision number
        revcur = int(db[data[0]].split(',')[1])

    if vercur == '': vercur = '-1'

    if int(ver) > int(vercur):
        if rev > int(revcur):
            # the version is newer
            buildpkg(data)
            db[data[0]] = ','.join([data[1], data[2]])

# parse the configuration file for options
config = confParse('updater.conf')['']

# do additional processing of the config
config = processConfig(config)

# create a pipe for other processes to use
recvp, sendp = Pipe()

# load the hoppers
modules = []
for i in config['hoppers']:
    modules.append(load(config['hopperdir'] + '/' + i + '.py'))

# load the storage modules
storages = []
for i in config['storages']:
    print('Loading storage module: ' + i)
    storages.append(load(config['storagedir'] + '/' + i + '.py'))

# run the hoppers
hopperp = []
for i in modules:
    print("Starting " + i.__str__())
    p = Process(target = i.run, args = (sendp,))
    p.start()
    hopperp.append(p)

# listen on pipe, when a connection is recieved, process it and check the process list
# NOBODY SHOULD CLOSE THE PIPE
while len(hopperp) != 0:
    data = recvp.recv()
    process(data)
    n = 0
    while n < len(hopperp):
        if not hopperp[n].is_alive():
            hopperp[n].join()
            hopperp.pop(n)
        else:
            n += 1
