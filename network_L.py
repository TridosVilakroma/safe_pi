import subprocess


def get_available():
    process=subprocess.run(['nmcli','-g','SSID','dev','wifi','list','--rescan','yes'],stdout=subprocess.PIPE)
    if process.returncode == 0:
        return process.stdout.decode('utf-8')
    else:
        return ''

def is_connected():
    process=subprocess.run(['nmcli','-g','state','general'],stdout=subprocess.PIPE)
    if process.returncode == 0:
        return  True if process.stdout.decode('utf-8').strip()=='connected' else False
    else:
        return False

def get_ssid():
    process=subprocess.run(['nmcli','-g','name','con','show','--active'],stdout=subprocess.PIPE)
    if process.returncode == 0:
        return process.stdout.decode('utf-8').strip()
    else:
        return ''

def get_status():
    process=subprocess.run(['nmcli','-g','state','general'],stdout=subprocess.PIPE)
    if process.returncode == 0:
        return process.stdout.decode('utf-8').strip()
    else:
        return ''

def get_signal():
    process=subprocess.run("nmcli -f IN-USE,SIGNAL,SSID device wifi | awk '/^\*/{if (NR!=1) {print $2}}'",shell=True,stdout=subprocess.PIPE)
    if process.returncode == 0:
        return process.stdout.decode('utf-8').strip()
    else:
        return ''

def get_security():
    return
    # process=subprocess.run("nmcli -f IN-USE,SIGNAL,SSID device wifi | awk '/^\*/{if (NR!=1) {print $2}}'",shell=True,stdout=subprocess.PIPE)
    # if process.returncode == 0:
    #     return process.stdout.decode('utf-8').strip()
    # else:
    #     return ''

def get_known():
    process=subprocess.run(['nmcli','-g','name','con','show'],stdout=subprocess.PIPE)
    if process.returncode == 0:
        return process.stdout.decode('utf-8').strip()
    else:
        return ''

def remove_profile(ssid,*args):
    process=subprocess.run(['nmcli','con','delete',ssid],stdout=subprocess.PIPE)
    if process.returncode == 0:
        return process.stdout.decode('utf-8').strip()
    else:
        return ''

def disconnect_ssid(ssid,*args):
    process=subprocess.run(['nmcli','con','down',ssid],stdout=subprocess.PIPE)
    if process.returncode == 0:
        return process.stdout.decode('utf-8').strip()
    else:
        return ''

def disconnect_wifi(*args):
    process=subprocess.run(['sudo','nmcli','radio','wifi','off'],stdout=subprocess.PIPE)
    if process.returncode == 0:
        return process.stdout.decode('utf-8').strip()
    else:
        return ''

def connect_wifi(*args):
    process=subprocess.run(['sudo','nmcli','radio','wifi','on'],stdout=subprocess.PIPE)
    if process.returncode == 0:
        return process.stdout.decode('utf-8').strip()
    else:
        return ''

def get_profiles_by_priority():
    process=subprocess.run('nmcli -g name con | sort -nr',shell=True,stdout=subprocess.PIPE)
    if process.returncode == 0:
        return process.stdout.decode('utf-8').strip()
    else:
        return ''

def set_profile_priority(ssid,priority,*args):
    process=subprocess.run(['nmcli','con','modify',ssid,'connection.autoconnect-priority',str(priority)],stdout=subprocess.PIPE)
    if process.returncode == 0:
        return process.stdout.decode('utf-8').strip()
    else:
        return ''




#########################################################################################################
def what_wifi():
    process = subprocess.run(['nmcli', '-t', '-f', 'ACTIVE,SSID', 'dev', 'wifi'], stdout=subprocess.PIPE)
    if process.returncode == 0:
        return process.stdout.decode('utf-8').strip().split(':')[1]
    else:
        return ''

def is_connected_to(ssid: str):
    return what_wifi() == ssid

def scan_wifi():
    process = subprocess.run(['nmcli', '-t', '-f', 'SSID,SECURITY,SIGNAL', 'dev', 'wifi'], stdout=subprocess.PIPE)
    if process.returncode == 0:
        return process.stdout.decode('utf-8').strip().split('\n')
    else:
        return []
        
def is_wifi_available(ssid: str):
    return ssid in [x.split(':')[0] for x in scan_wifi()]

def connect_to(ssid: str, password: str):
    if not is_wifi_available(ssid):
        return False
    subprocess.call(['nmcli', 'd', 'wifi', 'connect', ssid, 'password', password])
    return get_ssid() == ssid

def connect_to_saved(ssid: str,*args):
    if not is_wifi_available(ssid):
        return False
    subprocess.call(['nmcli', 'c', 'up', ssid])
    return get_ssid() == ssid