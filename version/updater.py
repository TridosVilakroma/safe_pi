from os import getcwd,walk
from os.path import join, normpath
import hashlib
import re

#check for remote version
'''server.py should handle this
The real time data base can store a version tag/integrity checksum'''

#download updates

#check download integrity

def alpha_num_sort(iterable):
    """ Sort the given iterable in the way that humans expect."""
    convert = lambda text: int(text) if text.isdigit() else text
    alphanum_key = lambda key: [ convert(c) for c in re.split('([0-9]+)', key) ]
    return sorted(iterable, key = alphanum_key)

def get_files():
    file_list=[]
    for dir_path,dir_names,file_names in walk(normpath(getcwd())):
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
    for i in file_hashes:
        print(i)
    hash_md5 = hashlib.md5()
    for file_hash in file_hashes:
        hash_md5.update(file_hash.encode('utf-8'))
    return hash_md5.hexdigest()


if __name__ == '__main__':
    print(generate_checksum())

#prompt user to update

#update

#prompt user to restart

#restart

#delete update download