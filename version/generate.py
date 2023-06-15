from os import getcwd,walk
from os.path import join, normpath, relpath
from io import StringIO
import hashlib
import re

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
    #do not use on files >1 gb
    files = get_files()
    list_of_hashes = []
    for each_file in files:
        hash_md5 = hashlib.md5()
        with open(each_file, "rb") as f:
            for line in f.readlines():
                line.replace(b'\n',b'')
                line.replace(b'\r',b'')
                hash_md5.update(line)
        list_of_hashes.append(hash_md5.hexdigest())
    return alpha_num_sort(list_of_hashes)

def generate_checksum():
    file_hashes=get_hashes()
    hash_md5 = hashlib.md5()
    for file_hash in file_hashes:
        hash_md5.update(file_hash.encode('utf-8'))
    return hash_md5.hexdigest()

if __name__=='__main__':
    print(generate_checksum())