import subprocess


def get_available():
    process=subprocess.run(['nmcli','-g','SSID','dev','wifi'],stdout=subprocess.PIPE)
    if process.returncode == 0:
        return process.stdout.decode('utf-8')
    else:
        return ''

def is_connected():
    pass

def get_ssid():
    process=subprocess.run(['nmcli','-g','name','con','show','--active'],stdout=subprocess.PIPE)
    if process.returncode == 0:
        return process.stdout.decode('utf-8')
    else:
        return ''

def get_signal():
    process=subprocess.run("nmcli -f IN-USE,SIGNAL,SSID device wifi | awk '/^\*/{if (NR!=1) {print $2}}'",shell=True,stdout=subprocess.PIPE)
    if process.returncode == 0:
        return process.stdout.decode('utf-8')
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
    return is_connected_to(ssid)

def connect_to_saved(ssid: str):
    if not is_wifi_available(ssid):
        return False
    subprocess.call(['nmcli', 'c', 'up', ssid])
    return is_connected_to(ssid)