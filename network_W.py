import subprocess,random


def get_available():
        return 'test\ntest2'

def is_connected():
        return True

def get_ssid():
        return 'test'

def get_status():
        return ''

def get_signal():
        return random.randint(0,100)

def get_security():
        return random.choice(('wep','wpa'))

def connect_to(ssid,password):
        print(ssid,password)

def connect_to_saved(ssid,*args):
        print(ssid)

def get_known():
        return 'test\ntest2'

def remove_profile(ssid,*args):
        return ''