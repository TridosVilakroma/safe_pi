import hashlib,time,importlib,re,os,glob
from shutil import rmtree
from os import getcwd,walk
from os.path import join, normpath, relpath
from subprocess import run
from io import StringIO

update_available=0
download_integity=0
last_download=0
current_version=0
available_version=0
download_complete=0
checksum=0
update_prompt=0
reboot_prompt=0
usb_update_found=0
usb_update_invalid=0


#########usb update########

def usb_probe(*args):
    '''probe for usb with update data

    once data is found and the version is checked,
    (or the update is invalid), this func will
    short-cycle untill the usb is removed'''

    global usb_update_found,usb_update_invalid
    if glob.glob('/media/pi/*/update/Pi_ro_safe/version/version.py'):
        if usb_update_found or usb_update_invalid:
            return
        check_usb_version()
    else:
        usb_update_found=0
        usb_update_invalid=0

def check_usb_version(*args):
    global usb_update_found,usb_update_invalid
    try:
        from packaging.version import Version as VersionInstance
        from version.version import version
        version_path=glob.glob('/media/pi/*/update/Pi_ro_safe/version/version.py')[0]
        usb_version='0.0.0'
        with open(version_path,'r') as f:
            usb_version=f.readline().split('=')[1].replace("'","")
        if VersionInstance(usb_version) > VersionInstance(version):
            usb_update_found=1
            return True
        usb_update_found=0
        usb_update_invalid=1
        return False
    except:
        usb_update_found=0
        usb_update_invalid=1
        return False

def usb_update(*args):
    global reboot_prompt,usb_update_found
    usb_update_found=0
    try:
        update_path=glob.glob('/media/pi/*/update/Pi_ro_safe')[0]
        completed_update=run(f"git pull {update_path} update --allow-unrelated-histories",shell=True)
        if completed_update.returncode:
            #non-zero return code indicates update error
            reboot_prompt=0
        else:
            reboot_prompt=1
    except:
        pass

#########check for remote version########

'''server.py handles this
The real-time data-base stores a version tag and download-integrity checksum
it changes update_available to a 1 when the version tag is different from
the running apps current version'''

##########download updates##########

def update_folder_empty():
    if not os.path.exists('version/update'):
        os.makedirs('version/update')
    if any(os.scandir('version/update')):
        return False
    return True

def get_update():
    global last_download,download_complete
    if update_folder_empty():
        now=time.time()
        if now>last_download+86400: #attempt once a day to perserve bandwidth
            last_download=now
            completed_download=run(f"git clone https://github.com/TridosVilakroma/Pi-ro-safe.git version/update/Pi_ro_safe",shell=True)
            if completed_download.returncode:
                #non-zero return code indicates downloaod error
                remove_update_data()
                download_complete=0
            else:
                download_complete=1
    else:
        download_complete=1

##########check download integrity##########

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

##########prompt user to update##########

'''handled by main.py listen_to_UpdateService()
it is observing update_prompt
once update_prompt is set to 1 it pushes a message and
activates a NotificationBadge on the msg_icon'''

##########update##########

def update_system(*args):
    global reboot_prompt,update_prompt
    if  os.name=='nt':
        print('version/updater.py update_system(): update called')
        reboot_prompt=1
        update_prompt=0
        return
    completed_update=run(f"git pull version/update/Pi_ro_safe main --allow-unrelated-histories",shell=True)
    if completed_update.returncode:
        #non-zero return code indicates update error
        reboot_prompt=0
    else:
        reboot_prompt=1
        update_prompt=0

##########prompt user to restart##########

'''handled by main.py listen_to_UpdateService()
it is observing reboot_prompt
once reboot_prompt is set to 1 it pushes a message and
activates a NotificationBadge on the msg_icon'''

##########restart##########

def  reboot(*args):
    global reboot_prompt
    reboot_prompt=0
    if os.name == 'nt':
        print('version/updater.py reboot(): System reboot called')
    if os.name == 'posix':
        run('sudo reboot now',shell=True)

##########delete update download##########

def onerror(func, path, exc_info):
    """Error handler for ``shutil.rmtree``.

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
    try:
        download_complete=0
        rmtree('version/update/Pi_ro_safe',ignore_errors=False,onerror=onerror)
    except:
        print('version/updater.py remove_update_data(): failed to remove all update data')

##########updater logic service##########

def update(*args):
    global  update_prompt,checksum
    if update_available:
        print('version/updater.py update(): calling get_update()')
        get_update()
    else:
        print('version/updater.py update(): no update available')
    if update_folder_empty() or not download_complete:
        print('version/updater.py update(): download empty or not complete')
        return
    else:
        if available_version:
            print('version/updater.py update(): comparing version tags')
            try:
                from version.update.Pi_ro_safe.version.version import version as UPDATE_VERSION
                if available_version != UPDATE_VERSION:
                    print('version/updater.py update(): downloaded update version does not match hosted version; removing update data')
                    remove_update_data()
            except ModuleNotFoundError:
                print('version/updater.py update(): downloaded update version not found; removing update data')
                remove_update_data()
    if not checksum:
        if download_complete:
            print('version/updater.py update(): generating checksum')
            checksum=generate_checksum()
    if not all((checksum, download_integity, download_complete)):
        print('version/updater.py update(): missing one of (checksum, download_integity, download_complete)')
        return
    if checksum == download_integity:
        if not reboot_prompt:
            print('version/updater.py update(): checksum == download_integity')
            update_prompt=1
    else:
        update_prompt=0
        checksum=0
        print('version/updater.py update(): checksum does not match download_integrity; removing update data')
        remove_update_data()