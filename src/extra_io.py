import os, errno

def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc: # Python >2.5
        if exc.errno == errno.EEXIST:
            pass
        else: raise

from subprocess import call, PIPE

def run_shell(cmd,args):
    status = call((cmd%args).split(), stdout=PIPE)
        
    if status:
        raise Exception("Command failed (%s) (%s) " % (cmd,args) )
    return status

import hashlib

def unique_filename(text, extension=""):
    h = hashlib.sha256(text).hexdigest()
    if not extension: return h
    return "%s.%s" % (h[:len(extension)+2], extension)

