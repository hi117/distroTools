from subprocess import call

# load the config
# TODO implement config :3
host=('ec2-54-243-153-106.compute-1.amazonaws.com','4342')
mountpoint='storage.mount'

# mount the point (if necessary)
if call(['mountpoint','-q',mountpoint]): call(['sshfs','-oPort='+host[1],host[0],mountpoint])

# now implement functions
def store(path,PKGBUILD):
    '''
    This function takes a path and a PKGBUILD string and moves it to its proper place in
    the storage subsystem.
    '''
    
