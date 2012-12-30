from multiprocessing import Pipe, Process
from utils.importhelper import load
from os import listdir

config = {}
gpkginfo = None # dict is in form {pkg: (deps, reqby)}

'''
These classes below basically simulate structs as in C.
'''

class package:
    def __init__(self, name):
        self.name = name
        self.hasBuilt = False
        self.hasError = None
        self.config = None
        self.deps = []
        self.reqby = []

class buildOrder:
    def __init__(self, config):
        self.pkgs = []
        self.config = config

def processConfig(config):
    '''
    Does additional processing to the config.
    '''
    config['storage'] = map(lambda a: a.strip(), config['storage'].split(','))
    return config

def buildInitGPkgInfo():
    '''
    This functon builds the inital gpkginfo dict.

    '''
    for i in listdir(config['basedir']):
        # load the PKGBUILD
        pkgbuild = open(config['basedir'] + '/' + i + '/PKGBUILD').readlines()

        # enumerate over lines stripping and looking for depends, makedepends
        for i in pkgbuild:
            i = i.strip(i)
            if i.split('=')[0] == 'depends' or i.split('=')[0] == 'makedepsnds':
                

def getDeps(pkg):
    '''
    This function returns a deps, reqby topule
    '''
    if not gpkginfo:
        buildInitGPkgInfo()

def buildPkgs(pkgs):
    '''
    This function takes a list of package names and builds them in the proper order.
    '''
    # build and populate the order struct
    order = buildOrder()
    for i in pkgs:
        order.pkgs.append(package(i))
    
    # copy over all the packages from storage to the local dir
    for i in order.pkgs:
        storage.get(i, config['basedir'])

    # build the graph
    for i in order.pkgs:
        deps = getDeps(i)
