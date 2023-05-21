import os,time,json
import device_classes.mau as mau
import device_classes.exhaust as exhaust
import device_classes.light as light
import device_classes.drycontact as drycontact
import device_classes.gas_valve as gas_valve
import device_classes.micro_switch as micro_switch
import device_classes.heat_sensor as heat_sensor
import device_classes.switch_light as switch_light
import device_classes.switch_fans as switch_fans
if os.name == 'nt':
    import RPi_test.GPIO as GPIO
else:
    import RPi.GPIO as GPIO

heat_sensor_timer=300
#there are only 19 GPIO pins available for input/output.
#pins 0-8[BCM] are set as pull-up (use as input exclusively; not outputs)
#the additional 15 are grounds, constant powers, and reserved for hats.
available_pins=[8,10,11,12,13,15,16,18,19,
                21,22,23,32,33,35,36,37,38,40]#i for i in range(2,28)]

GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)

off=0
on=1
devices=[]
def get_devices():
    def load_devices():
        try:
            with open(rf"logs/devices/device_list.json","r") as read_file:
                data = json.load(read_file)
            return data
        except FileNotFoundError:
            print("logic.get_devices().load_devices(): FileNotFoundError; Creating file")
            with open(rf"logs/devices/device_list.json","w+") as read_file:
                data={}
                json.dump(data, read_file,indent=0)
            return load_devices()


    loaded_devices=load_devices()
    for d in loaded_devices:
        if d != "default" and not any(j for j in devices if j.name == d):
            i=eval(f"{loaded_devices[d]}(name=\"{d}\")")
            if i.pin in available_pins:
                available_pins.remove(i.pin)
                set_pin_mode(i)
            elif i.pin==0:
                print(f"logic.get_devices(): {i}.pin == 0")
            devices.append(i)

def set_pin_mode(device):
    if device.mode=="in":
        GPIO.setup(device.pin,GPIO.IN,pull_up_down = GPIO.PUD_DOWN)
    elif device.mode=="out":
        GPIO.setup(device.pin, GPIO.OUT,initial=GPIO.LOW)
    else:
        print(f"logic.set_pin_mode(): {device}.mode is not \"in\" or \"out\"")

def exfans_on(Logic_instance):
    for i in (i for i in devices if isinstance(i,exhaust.Exhaust)):
        if i.pin!=0:
            Logic_instance.pin_states[i.pin]=1
            i.on()

def exfans_off(Logic_instance):
    for i in (i for i in devices if isinstance(i,exhaust.Exhaust)):
        Logic_instance.pin_states[i.pin]=0
        i.off()

def maufans_on(Logic_instance):
    for i in (i for i in devices if isinstance(i,mau.Mau)):
        if i.pin!=0:
            Logic_instance.pin_states[i.pin]=1
            i.on()

def maufans_off(Logic_instance):
    for i in (i for i in devices if isinstance(i,mau.Mau)):
        Logic_instance.pin_states[i.pin]=0
        i.off()

def lights_on(Logic_instance):
    for i in (i for i in devices if isinstance(i,light.Light)):
        if i.pin!=0:
            Logic_instance.pin_states[i.pin]=1
            i.on()

def lights_off(Logic_instance):
    for i in (i for i in devices if isinstance(i,light.Light)):
        Logic_instance.pin_states[i.pin]=0
        i.off()

def dry_on(Logic_instance):
    for i in (i for i in devices if isinstance(i,drycontact.DryContact)):
        if i.pin!=0:
            Logic_instance.pin_states[i.pin]=1
            i.on()

def dry_off(Logic_instance):
    for i in (i for i in devices if isinstance(i,drycontact.DryContact)):
        Logic_instance.pin_states[i.pin]=0
        i.off()

def gv_on(Logic_instance):
    for i in (i for i in devices if isinstance(i,gas_valve.GasValve)):
        if i.pin!=0 and i.latched:
            Logic_instance.pin_states[i.pin]=1
            i.on()

def gv_off(Logic_instance):
    for i in (i for i in devices if isinstance(i,gas_valve.GasValve)):
        Logic_instance.pin_states[i.pin]=0
        i.off()

def gv_reset_all(*args):
    for i in (i for i in devices if isinstance(i,gas_valve.GasValve)):
        i.latched=True

def save_devices(*args):
    for i in devices:
        i.write()

def update_devices(*args):
    for i in devices:
        i.update()

def pin_off(pin):
    func = GPIO.gpio_function(pin)
    if func==GPIO.OUT:
        GPIO.output(pin,off)

dry_contact=12
lights_pin=7
if os.name == 'nt':
    def heat_sensor_active():
        for i in (i for i in devices if isinstance(i,heat_sensor.HeatSensor)):
            if GPIO.input(i.pin,'h'):
                return True
        return False
    def micro_switch_active():
        for i in (i for i in devices if isinstance(i,micro_switch.MicroSwitch)):
            if GPIO.input(i.pin,'m'):
                return True
        return False
    def fan_switch_on():
        for i in (i for i in devices if isinstance(i,switch_fans.SwitchFans)):
            if GPIO.input(i.pin,'f'):
                return True
        return False
    def light_switch_on():
        for i in (i for i in devices if isinstance(i,switch_light.SwitchLight)):
            if GPIO.input(i.pin,'l'):
                return True
        return False
if os.name == 'posix':
    def heat_sensor_active():
        for i in (i for i in devices if isinstance(i,heat_sensor.HeatSensor)):
            if GPIO.input(i.pin):
                return True
        return False
    def micro_switch_active():
        for i in (i for i in devices if isinstance(i,micro_switch.MicroSwitch)):
            if not GPIO.input(i.pin):
                return True
        return False
    def fan_switch_on():
        for i in (i for i in devices if isinstance(i,switch_fans.SwitchFans)):
            if GPIO.input(i.pin):
                return True
        return False
    def light_switch_on():
        for i in (i for i in devices if isinstance(i,switch_light.SwitchLight)):
            if GPIO.input(i.pin):
                return True
        return False
def clean_exit():
    all_pins=[8,10,11,12,13,15,16,18,19,
              21,22,23,32,33,35,36,37,38,40]
    GPIO.setup(all_pins, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)

def clean_list(list,element):
    while True:
        try:
            list.remove(element)
        except ValueError:
            break

class Logic():
    def __init__(self) -> None:
        self.pin_states={}
        self.aux_state=[]
        self.state='Normal'
        self.running=False
        self.shut_off=False
        self.sensor_target=time.time()

        '''two dictionaries are used to share data between two threads.
        moli: main out logic in, is written too in main and read in logic.
        milo: main in logic out, is written too in logic and read in main.
        '''
        self.troubles={
            'heat_override':0,
            'short_duration':0,
            'gv_trip':0,
            'actuation':0
        }

        self.moli={
            'exhaust':off,
            'mau':off,
            'lights':off,
            'dry_contact':off,
            'maint_override':off,
            'maint_override_light':off
        }
        self.milo={
            'exhaust':off,
            'mau':off,
            'lights':off,
            'heat_sensor':off,
            'dry_contact':off,
            'micro_switch':off,
            'troubles':self.troubles
        }

    def normal(self):
        if micro_switch_active():
            print('micro_switch')
            self.state='Fire'
            self.milo['micro_switch']=on
        elif self.moli['maint_override']==1:
            dry_on(self)
            gv_on(self)
            exfans_off(self)
            maufans_off(self)
            if self.moli['maint_override_light']==1:
                lights_on(self)
            elif self.moli['maint_override_light']==0:
                lights_off(self)
        else:

            dry_on(self)
            gv_on(self)

            if self.moli['exhaust']==on or fan_switch_on():
                exfans_on(self)
                self.milo['exhaust']=on
            elif self.moli['exhaust']==off or not fan_switch_on():
                if 'heat_sensor' not in self.aux_state:
                    exfans_off(self)
                    self.milo['exhaust']=off
            if self.moli['mau']==on or fan_switch_on():
                maufans_on(self)
                self.milo['mau']=on
            elif self.moli['mau']==off or not fan_switch_on():
                maufans_off(self)
                self.milo['mau']=off
            if heat_sensor_active():
                self.milo['heat_sensor']=on
                self.heat_trip()
            else:
                self.milo['heat_sensor']=off
            if self.moli['lights']==on or light_switch_on():
                lights_on(self)
                self.milo['lights']=on
            elif self.moli['lights']==off or not light_switch_on():
                lights_off(self)
                self.milo['lights']=off

    def fire(self):
        exfans_on(self)
        maufans_off(self)
        lights_off(self)
        dry_off(self)
        gv_off(self)
        if not micro_switch_active():
            self.state='Normal'
            self.milo['micro_switch']=off

    def heat_trip(self):
        self.sensor_target=time.time()+heat_sensor_timer
        self.aux_state.append('heat_sensor')
        print('heat trip')

    def heat_sensor(self):
            if self.sensor_target>=time.time():
                exfans_on(self)
                maufans_on(self)
                self.milo['exhaust']=on
                self.milo['mau']=on
                print('heat timer active')
            else:
                if self.moli['exhaust']==off and self.moli['mau']==off:
                    exfans_off(self)
                    maufans_off(self)
                    self.milo['exhaust']=off
                    self.milo['mau']=off
                clean_list(self.aux_state,'heat_sensor')

    def trouble(self):
    #heat sensor active
        if heat_sensor_active() and not self.moli['exhaust']==1:
            self.milo['troubles']['heat_override']=1
        else:
            self.milo['troubles']['heat_override']=0
    #heat timer
        if heat_sensor_timer==10:
            self.milo['troubles']['short_duration']=1
        else:
            self.milo['troubles']['short_duration']=0
    #gas valve unlatched
        if any(i for i in devices if isinstance(i,gas_valve.GasValve) and i.pin!=0 and not i.latched):
            self.milo['troubles']['gv_trip']=1
        else:
            self.milo['troubles']['gv_trip']=0
    #micro switch released
        if self.state=='Fire':
            self.milo['troubles']['actuation']=1
        else:
            self.milo['troubles']['actuation']=0

    def state_manager(self):
        if self.state=='Fire':
            self.fire()
            print("fired state")
        elif self.state=='Normal':
            self.normal()
            print("normal state")

    def auxillary(self):
        self.trouble()
        if 'heat_sensor' in self.aux_state and self.state=='Normal':
            if not self.moli['maint_override']==1:
                self.heat_sensor()

    def set_pins(self):
        for i in available_pins:
            GPIO.setup(i,GPIO.IN,pull_up_down = GPIO.PUD_DOWN)
        for pin,state in self.pin_states.items():
            if GPIO.gpio_function(pin)==GPIO.IN:
                continue
            if GPIO.gpio_function(pin)==GPIO.OUT:
                GPIO.output(pin,state)
        self.pin_states={}


    def update(self):
        self.state_manager()
        self.auxillary()
        self.set_pins()

get_devices()
fs=Logic()
def logic():
    while True:
        fs.update()
        time.sleep(.5)

if __name__=='__main__':
    try:
        logic()
    finally:
        clean_exit()