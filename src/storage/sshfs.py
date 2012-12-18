from subprocess import call
import utils.configParser as configParser
from os.path import exists
from shutil import rmtree, copytree as rm, cp

# load the config
config = configParser.parse('sshfs.conf')['']

# mount the point (if necessary)
if call(['mountpoint', '-q', config['mountpoint']): 
        call(['sshfs', '-oPort=' + config['port'], config['host'] + ':/', config['mountpoint']])

# now implement functions
def store(path, PKGBUILD):
    '''
    This function takes a path and a PKGBUILD string and moves it to its proper place in
    the storage subsystem.
    '''
    # ensure the mountpoint is still mounted
    if not call(['mountpoint', '-q', config['mountpoint']]):
        call(['sshfs', '-oPort=' + config['port'], config['host'], config['mountpoint']])

    # delete whats already there
    if exists(config['mountpoint'] + '/' + config['basedir'] + '/' + path.split('/')[-1]):
        rm(config['mountpoint'] + '/' + config['basedir'])

    # move the new stuff over
    cp(path, config['mountpoint'] + '/' + config['basedir'] + '/' + path.split('/')[-1])

    # put the PKGBUILD in the new directory
    with open(config['mountpoint'] + '/' +  config['basedir'] + '/' + path.split('/')[-1] + '/' + 'PKGBUILD', 'w') as f:
        f.write(PKGBUILD)
