import os,time,json,logging
import os.path

logger=logging.getLogger('logger')

class Light():
    color=(0/255, 0/255, 0/255,.85)
    def __init__(self,name="default",pin=0,color=(0/255, 0/255, 0/255,.85)) -> None:
        self.name=name
        self.type='Lights'
        self.pin=pin
        self.mode="out"
        self.color=color
        self.trigger='None'
        self.load_error=False
        self.log={}
        self.unsafe_state_trigger=0
        self.state=0
        self.run_time=0
        self.last_state_change=time.time()
        self.initialize()

    def write(self):
        data={
            "device_name":self.name,
            "gpio_pin":self.pin,
            "run_time":self.run_time,
            "color":self.color,
            "trigger":self.trigger,
            "load_error":self.load_error}
        try:
            with open(rf"logs/devices/{self.name}.json","w") as write_file:
                json.dump(data, write_file,indent=0)
        except (json.decoder.JSONDecodeError,FileNotFoundError,OSError):
            logger.exception('Failed to write device data')

    def initialize(self):
        data=self.read()
        if data:
            self.name=data["device_name"]
            self.pin=int(data["gpio_pin"])
            self.run_time=float(data["run_time"])
            self.color=data["color"]
            self.trigger=data.get("trigger","high")
            self.load_error=data.get("load_error",False)
        else:
            self.load_error=True

    def read(self):
        try:
            with open(rf"logs/devices/{self.name}.json","r") as read_file:
                data = json.load(read_file)
        except (json.decoder.JSONDecodeError,FileNotFoundError,OSError):
            logger.exception('Failed to read device data')
            self.load_error=True
            data={}
        if not data:
            data=self.read_backup()
            if data:
                data['load_error']=True
                return data
        return data

    def read_backup(self):
        try:
            with open(rf"logs/devices/backups/{self.name}.json","r") as read_file:
                data = json.load(read_file)
        except (json.decoder.JSONDecodeError,FileNotFoundError,OSError):
            logger.exception('Failed to read device data')
            self.load_error=True
            data={}
        return data

    def on(self):
        if self.state==0:
            self.state=1
            self.last_state_change=time.time()

    def off(self):
        if self.state==1:
            self.state=0
            self.last_state_change=time.time()

    def update(self,*args):
        now=time.time()
        if self.state==1:
            self.run_time+=now-self.last_state_change
            self.last_state_change=now