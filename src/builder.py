from multiprocessing import Pipe, Process
from utils.importhelper import load
from os import listdir, chdir, getcwd
from subprocess import call

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
    def __init__(self):
        self.pkgs = []
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

def makepkg(order, pkg):
    '''
    This is where the magic happens. It takes a pkg object and runs makepkg in the package directory, making the package.
    It also updates the order's hasBuilt list. For now it just calls makepkg -s --noconfirm.
    '''
    #TODO: add a lot of features to the build process like a PKGBUILD mangle chain and error handling
    oldcwd = getcwd()
    chdir(config['basedir'] + '/' + pkg)
    ret = call(['makepkg', '-s', '--noconfirm'])
    
    # set the has built and error fields
    # makepkg returns 0 for ok and 1 for error
    if ret == 1:
        pkg.hasError = True
    pkg.hasBuilt = True
    
    # remove package from the notBuilt list
    n = 0
    for i in order.notBuilt:
        if i == pkg:
            break
    order.notBuilt.pop(n)

    return ret

def buildPkgs(pkgs):
    '''
    This function takes a list of package names and builds them in the proper order.
    '''
    # copy over all the packages from storage to the local dir
    for i in pkgs:
        storage.get(i, config['basedir'])

    # build the order struct
    order = buildOrder(Order())

    # loop until findBottom returns none
    bottom = findBottom(order)
    while bottom:
        makepkg(bottom)
        bottom = findBottom(order)
