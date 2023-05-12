import os,json,importlib
import logic



custom_packages=[]
for i in next(os.walk('logs/custom/packages'))[1]:
    custom_device_path=f'logs.custom.packages.{i}.{i}'
    custom_packages.append(importlib.import_module(custom_device_path))

#there are only 19 GPIO pins available for input/output.
#pins 0-8[BCM] are set as pull-up (use as input exclusively; not outputs)
#the additional 15 are grounds, constant powers, and reserved for hats.
available_pins=[8,10,11,12,13,15,16,18,19,
                21,22,23,32,33,35,36,37,38,40]#i for i in range(2,28)]
devices=[]
def get_devices():
    def load_devices():
        try:
            with open(rf"logs/custom/devices/device_list.json","r") as read_file:
                data = json.load(read_file)
            return data
        except FileNotFoundError:
            print("custom_logic.get_devices().load_devices(): FileNotFoundError; Creating file")
            with open(rf"logs/custom/devices/device_list.json","w+") as read_file:
                data={}
                json.dump(data, read_file,indent=0)
            return load_devices()


    loaded_devices=load_devices()
    for d in loaded_devices:
        if d != "default" and not any(j for j in devices if j.name == d):
            device_module=None
            for p in custom_packages:
                if loaded_devices[d] in p.__name__:
                    device_module=p
                    break
                else:
                    continue
            if not device_module:
                raise IndexError
            device_class=getattr(device_module,str(device_module.__name__).split('.')[-1])
            i=device_class(name=d)
            if i.pin in available_pins:
                available_pins.remove(i.pin)
                logic.set_pin_mode(i)
            elif i.pin==0:
                print(f"logic.get_devices(): {i}.pin == 0")
            devices.append(i)

def pin_off(pin):
    return

def pin_on(pin):
    return






def update(*args):
    print(logic.fs.cilo)