import os
import os.path
from multiprocessing import Process,Pipe
from importhelper import load
from kyotocabinet import *
import debug as storage

db = DB()
assert db.open('pkgverdb.kch', DB.OWRITER | DB.OREADER | DB.OCREATE), 'error opening db'

def buildpkg(data):
    '''
    this function takes a pkgname and a pkgversion and turns a PKGBUILD.in into a PKGBUILD
    it replaces %n with data[0], %v with data[1], and %% with %
    '''
    # determine the PKGBUILD.in to use
    if not data[0] in os.listdir('pkgs'): 
        print(data[0]+' not in directory')
        return
    path='pkgs/'+data[0]
    PKGBUILD=open(path+'/PKGBUILD.in','r').read().replace('%n',data[0]).replace('%v',data[1]).replace('%%','%')
    
    # send it to the storage module
    storage.store(path,PKGBUILD)

def process(data):
    '''
    data is a touple of (package,version)
    this funciton determines if an update is needed and builds it
    '''
    # determine if the version they gave is newer than the current version
    ver=''
    for i in data[1]:
        if i.isdigit():
            ver+=i
    vercur=''
    if db[data[0]]:
        for i in db[data[0]]:
            if i.isdigit():
                vercur+=i
    if vercur == '': vercur='-1'
    if int(ver) > int(vercur):
        # the version is newer
        buildpkg(data)
        db[data[0]]=data[1]


# create a pipe for other processes to use
recvp, sendp = Pipe()

# load the hoppers
modules=[]
for i in os.listdir('hoppers'):
    if os.path.isdir('hoppers/'+i):
        continue
    modules.append(load('hoppers/'+i))

# run the hoppers
hopperp=[]
for i in modules:
    print("Starting "+i.__str__())
    p = Process(target=i.run, args=(sendp,))
    p.start()
    hopperp.append(p)

# listen on pipe, when a connection is recieved, process it and check the process list
# NOBODY SHOULD CLOSE THE DAMN PIPE
while len(hopperp)!=0:
    data=recvp.recv()
    process(data)
    while n<len(hopperp):
        if hopperp[n].is_alive():
            hopperp[n].join()
            hopperp.pop(n)
        else:
            n+=1
