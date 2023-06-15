#check for remote version
'''server.py should handle this
The real time data base can store a version tag/integrity checksum'''

#download updates

#check download integrity
from os import listdir, getcwd
from os.path import isfile, join, normpath, basename
import hashlib

import re

def alpha_num_sort(iterable):
    """ Sort the given iterable in the way that humans expect."""
    convert = lambda text: int(text) if text.isdigit() else text
    alphanum_key = lambda key: [ convert(c) for c in re.split('([0-9]+)', key) ]
    return sorted(iterable, key = alphanum_key)

def get_files():
    import glob
    for f in glob.glob('logs/**', recursive=True):
        print(f)

    return
    #need to return all files in given directory
    current_path = normpath(getcwd())
    return [join(current_path, f) for f in listdir(current_path) if isfile(join(current_path, f))]

def get_hashes():
    files = get_files()
    list_of_hashes = []
    for each_file in files:
        hash_md5 = hashlib.md5()
        with open(each_file, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        list_of_hashes.append(hash_md5.hexdigest())
    return alpha_num_sort(list_of_hashes)

def generate_checksum():
    file_hashes=get_hashes()
    hash_md5 = hashlib.md5()
    for file_hash in file_hashes:
        hash_md5.update(file_hash.encode('utf-8'))
    return hash_md5.hexdigest()


if __name__ == '__main__':
    get_files()
    # print(generate_checksum())

#prompt user to update

#update

#prompt user to restart

#restart

#delete update download