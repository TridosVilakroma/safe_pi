import subprocess,random


def get_available():
        return 'test\ntest2'

def is_connected():
        return True

def get_ssid():
        return ''

def get_status():
        return ''

def get_signal():
        return random.randint(0,100)

def get_security():
        return random.choice(('wep','wpa'))

def connect_to(ssid,password):
        print(ssid,password)

def get_known():
        return 'test\ntest2'