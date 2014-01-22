import logging

import hashlib
def unique_filename(text, extension=""):
    h = hashlib.sha256(text).hexdigest()
    if not extension: return h
    return "%s.%s" % (h[:len(extension)+2], extension)

import os
import errno
def make_sure_path_exists(path):
    if path:
        try:
            os.makedirs(path)
        except OSError as exception:
            if exception.errno != errno.EEXIST:
                raise

import subprocess
def shell(cmds):
    pipe = subprocess.PIPE
    P = subprocess.Popen(cmds,shell=True, stderr=pipe,stdout=pipe)
    results = P.communicate()
    return results


import tempfile, os, shutil, glob

class temp_workspace(object):
    ''' 
    Allows a temp working directory
    Cleans up after use, even with a failure in the block
    
    with temp_workspace():
        [do stuff]
    '''

    def _copy_function(self, f, dest):

        if not os.path.exists(f):
            raise IOError("File not found %s" % f)

        shutil.copy(f, dest)
        
        return dest

    def store(self, f, new_local_name=""):
        ''' 
        Copies files to the temp storage for use
        Returns a list of the files copied at the temp dest.
        '''
        
        local_dir = os.path.dirname(f)
        localized_f = os.path.join(self.local_dir, f)

        if not new_local_name:
            f_base      = os.path.basename(f)
            make_sure_path_exists(local_dir)

            dest = os.path.join(self.temp_dir, local_dir, f_base)
        else:
            dest = os.path.join(self.temp_dir, new_local_name)

        return self._copy_function(localized_f, dest)

    def save(self, f, new_local_name=""):
        ''' 
        Copies a file back to the local directory.
        Returns a list of files copied at the local dest.
        If new_local_names, then rename the files as they get copied
        WARNING: This overwrites same names
        '''
        local_dir = os.path.dirname(f)

        localized_f = os.path.join(self.temp_dir, f)
        f_base      = os.path.basename(f)

        if not new_local_name:
            dest = os.path.join(self.local_dir, local_dir, f_base)
        else:
            dest = os.path.join(self.local_dir, new_local_name)

        new_files_dest = self._copy_function(localized_f, dest)

    def __enter__(self):
        self.local_dir = os.getcwd()
        self.temp_dir  = tempfile.mkdtemp()
        os.chdir(self.temp_dir)
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type:
            logging.critical("%s in %s" % (exc_type,self.temp_dir))
            logging.critical(traceback)

        os.chdir(self.local_dir)
        shutil.rmtree(self.temp_dir)

    def __repr__(self):
        return self.temp_dir

    def shell(self):
        ''' Opens a shell at the current location '''
        os.system('bash')

class cache_result(object):
    ''' 
    Creates a cache in the local directory under name/

    with cache_result(name, f) as C:
        C(x) # will return f(x) as a string cached if possible
    '''
    def __init__(self, cache_name, func, ext=''):
        self.name = cache_name
        self.func = func
        self.extension = ext

        # Crate the cache directory if it doesn't exist
        make_sure_path_exists(self.name)

    def __enter__(self):
        self.local_dir = os.getcwd()
        self.working_dir = os.path.join(self.local_dir, self.name)
        return self

    def __call__(self, *args, **kwargs):
        # Create a filename from a string rep of the input args
        f_base = unique_filename(str(args))      
        self.f_save = os.path.join(self.working_dir, f_base)
        self.f_save += self.extension
    
        # Check if a force compute is needed
        force = False
        if 'force_compute' in kwargs and kwargs['force_compute']:
            force = True

        if not os.path.exists(self.f_save) or force:
            logging.info("~(caching) %s %s"%(self.name, args))
            result = self.func(*args)
            with open(self.f_save,'w') as FOUT:
                FOUT.write(str(result))

        # Return the result from the file
        with open(self.f_save) as FIN:
            raw = FIN.read()
        return raw

    def clear(self):
        # Clears the cache
        files = os.path.join(self.working_dir,'*')
        for f in glob.glob(files):
            os.remove(f)

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type:
            print "Cache failure", self.local_dir
            print traceback


if __name__ == "__main__":

    def squared(x): 
        return x**2

    with cache_result('foo', squared) as C:
        print "Function call", C(2)
        print "Function call", C(2)
        print "Function call", C(2,force_compute=True)
        print "HI"
        C.clear()

    with temp_workspace() as T:
        print "Inside tempspace", T

    # Now try with an error
    with temp_workspace() as T:
        print "Inside tempspace", T
        print "GOING TO DIVIDE BY ZERO"
        x = 1/0
        print "Still OK? Nope, won't make it"

