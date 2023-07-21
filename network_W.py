import subprocess,random


def get_available():
        return 'test\ntest2\ntest3'

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
        return random.choice((True,False))

def connect_to_saved(ssid,*args):
        print(ssid)
        return random.choice((True,False))

def get_known():
        return 'test\ntest2'

def remove_profile(ssid,*args):
        return random.choice((True,False))

def disconnect_ssid(ssid,*args):
        return

def disconnect_wifi(*args):
        return

def connect_wifi(*args):
        return

def get_profiles_by_priority(*args):
        return 'test1\ntest2\ntest3\ntest4\ntest5\ntest6'

def set_profile_priority(ssid,priority,*args):
        # return
        print(ssid,' priority set to: ',priority)