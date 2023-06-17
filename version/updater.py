import hashlib
import re, os
from shutil import rmtree
from os import getcwd,walk
from os.path import join, normpath, relpath
from subprocess import run
from io import StringIO

#check for remote version
'''server.py should handle this
The real time data base can store a version tag/integrity checksum'''

#download updates

def get_update():
    run(f"git clone https://github.com/TridosVilakroma/Pi-ro-safe.git version/update/Pi-ro-safe")

#check download integrity

def alpha_num_sort(iterable):
    """ Sort the given iterable in the way that humans expect."""
    convert = lambda text: int(text) if text.isdigit() else text
    alphanum_key = lambda key: [ convert(c) for c in re.split('([0-9]+)', key) ]
    return sorted(iterable, key = alphanum_key)

def get_files():
    file_list=[]
    for dir_path,dir_names,file_names in walk("version/update"):
        if not file_names:
            #skip empty directories
            continue
        if '.' in dir_path:
            #skip hidden folders
            continue
        if '__pycache__' in dir_path:
            #skip python cache generated folders
            continue
        for file in file_names:
            if file[0] == '.':
                #skip hidden files
                continue
            file_list.append(join(dir_path, file))
    return file_list

def get_hashes():
    #do not use on files >1 gb
    files = get_files()
    list_of_hashes = []
    for each_file in files:
        hash_md5 = hashlib.md5()
        with open(each_file, "rb") as f:
            file=f.read()
            file=file.replace(b'\n',b'')
            file=file.replace(b'\r',b'')
            hash_md5.update(file)
        list_of_hashes.append(hash_md5.hexdigest())
    return alpha_num_sort(list_of_hashes)

def generate_checksum():
    file_hashes=get_hashes()
    hash_md5 = hashlib.md5()
    for file_hash in file_hashes:
        hash_md5.update(file_hash.encode('utf-8'))
    return hash_md5.hexdigest()

#prompt user to update

#update

def update():
    run(f"git pull version/update/Pi-ro-safe main --allow-unrelated-histories")

#prompt user to restart

#restart

def  reboot():
    if os.name == 'nt':
        print('version/updater.py reboot(): System reboot called')
    if os.name == 'posix':
        run('sudo reboot now)')

#delete update download

def onerror(func, path, exc_info):
    """
    Error handler for ``shutil.rmtree``.

    If the error is due to an access error (read only file)
    it attempts to add write permission and then retries.

    If the error is for another reason it re-raises the error.
    
    Usage : ``shutil.rmtree(path, onerror=onerror)``
    """
    import stat
    # Is the error an access error?
    if not os.access(path, os.W_OK):
        os.chmod(path, stat.S_IWUSR)
        func(path)
    else:
        raise

def remove_update_data():
    rmtree('version/update/Pi-ro-safe',ignore_errors=True,onerror=onerror)
