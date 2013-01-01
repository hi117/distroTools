from multiprocessing import Pipe, Process
from utils.importhelper import load
from os import listdir

config = {}

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

class Order:
    def __init__(self, config):
        self.pkgs = []
        self.config = config
        self.notBuilt = []

def processConfig(config):
    '''
    Does additional processing to the config.
    '''
    config['storage'] = map(lambda a: a.strip(), config['storage'].split(','))
    return config

def getPkgFromOrder(order, pkg):
    '''
    This function takes a pkg by name and gets the package class from the order
    '''
    for i in order.pkgs:
        if i.name == pkg:
            return i
    return None

def buildOrder(order):
    '''
    This functon builds the inital gpkginfo dict.

    '''
    for p in listdir(config['basedir']):
        # load the PKGBUILD
        pkgbuild = open(config['basedir'] + '/' + p + '/PKGBUILD').readlines()

        # enumerate over lines stripping and looking for depends, makedepends
        dependancies = []
        for i in pkgbuild:
            i = i.strip(i)
            if i.split('=')[0] == 'depends' or i.split('=')[0] == 'makedepsnds':
                deps = map(lambda a: a.split("()'\""), i.split('=')[1].split(' '))
                for j in deps:
                    if not j in dependancies:
                        dependancies.apend(j)

        # get the pkg from the order and add the dependancies to it
        pkg = getPkgFromOrder(order, p)
        for i in dependancies:
            dep = getPkgFromOrder(order, i)
            if dep:
                pkg.deps.append(dep)
                dep.reqby.append(pkg)

    # populate the notBuilt list used for graph search starting
    order.notBuilt = order.pkgs

    return order

def findBottom(order, visited = []):
    '''
    This function finds a bottom and returns the pkg.
    '''
    # get a starting package if needed
    if len(visited) == 0:
        visited.append(order.notBuilt[0])
    else: # else we check if we are a valid package for being looked at
        if visited[-1].hasBuilt:
            return None

    # now we move down and see if we find a bottom
    for i in visited[-1].deps:
        # check for circular dependancies
        # a circular dependancy occurs when i is already in our visited list
        # it is handled by calling it a bottom
        if i in visited:
            return i
        a = findBottom(order, visited + i)
        if a:
            return a
    
    #  no bottom has been found, so we are the bottom
    return visited.pop()

def buildPkgs(pkgs):
    '''
    This function takes a list of package names and builds them in the proper order.
    '''
    # copy over all the packages from storage to the local dir
    for i in pkgs:
        storage.get(i, config['basedir'])

    # build the order struct
    order = buildOrder(Order())

    # find a bottom
    bottom = findBottom(order)
