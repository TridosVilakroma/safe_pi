import pyrebase as Firebase
import kivy.uix.filechooser as FileChooser
import threading as th
import os,random
import version.updater as UpdateService
try:
    import firestore
except:
    import server.firestore as firestore


#   TODO: 
#       . Make firebase account with fire safe email
#       . Change config object for app with new config data
#       . On firebase start Auth, Realtime database, and storage 
#           then configure their rules respectively
#       . Create debounce function for writing to database
#       . Implement 4
#       

# Report naming convention
# mm-dd-yyyy
# Easily manage and sort relavent reports 


reports_dir = r"logs/sys_report"

schema = {
    "lights_on": False,
    "fans_on": False,
    "sys_report_list": [],
    "messages": []
}

#####test config
# config = {
#   'apiKey': "AIzaSyCwsQ6EHLZ4XcnM65ef3-Q42oiwnwZWoSY",
#   'authDomain': "hood-control.firebaseapp.com",
#   'databaseURL': "https://hood-control-default-rtdb.firebaseio.com",
#   'projectId': "hood-control",
#   'storageBucket': "hood-control.appspot.com",
#   'messagingSenderId': "501458540776",
#   'appId': "1:501458540776:web:b60a1d59d2d313753b515d"
# }

config = {
  'apiKey': "AIzaSyDYLaE0PMm3yddp6spml8ANCZT-rpEotNs",
  'authDomain': "hood-control-67b78.firebaseapp.com",
  'databaseURL': "https://hood-control-67b78-default-rtdb.firebaseio.com",
  'projectId': "hood-control-67b78",
  'storageBucket': "hood-control-67b78.appspot.com",
  'messagingSenderId': "19231970603",
  'appId': "1:19231970603:web:a11433f93fdb9c1ce6216e",
  'measurementId': "G-5JCVCD9G1K"
}



class Db_service():

    def __init__(self) -> None:
        # self.devices is a namespace for the
        # String values of database keys
        # To ensure naming consistency
        self.devices = self.Devices()

        # Init firebase instance
        firebase = Firebase.initialize_app(config)

        # Init database service
        self.db = firebase.database()
        
        # Init storage bucket service
        self.sb = firebase.storage()

        # Init auth service
        self.auth = firebase.auth()

        # Init null firestore service
        self.firestore=False

        self._device_requests={
            'fans':0,
            'lights':0,
            'dry_contact':0,
            'maint_override':0,
            'maint_override_light':0}

        self.device_requests=self._device_requests.copy()

        self.active_streams=[]


    def authUser(self, email: str, password: str) -> None:
        '''Attempts to sign in.
        If user is not found, will try creating an account.
        '''
        try:
            self.user = self.auth.sign_in_with_email_and_password(email, password)
            try:
                self.firestore = firestore.firestore_init(self.user,config['projectId'])
            except:
                self.firestore=False


        except Exception as e:
            # Assumption is that any exception is from email not being found
            # TODO Should check error message to confirm email is not found
            print(f'server.py authUser(): {e}')
            self.user = self.auth.create_user_with_email_and_password(email, password)
            # print(self.user)


        finally:
            self.email = self.user["email"]
            self.path = "users/" + self.user["localId"]
            self.token = self.user["idToken"]
            self.uid = self.user["localId"]
            # self.db_version_stream = self.db.child('version').stream(self.version_stream_handler,self.token)
            # self.db_req_fans_stream = self.db.child(self.path).child(self.devices.req_fans).stream(self.req_fans_stream_handler,self.token)
            # self.db_req_lights_stream = self.db.child(self.path).child(self.devices.req_lights).stream(self.req_lights_stream_handler,self.token)
            # self.toggleDevice(self.devices.req_lights,0)
            # #add streams to a list for easy closing
            # self.active_streams.extend((self.db_version_stream,self.db_req_fans_stream,self.db_req_lights_stream))
            # # self.toggleDevice(self.db_exhaust_stream,0)
            # self.db.child(self.path).update({"email": self.email}, self.token)
            # self.set_version_info()

            ''' TODO Token expires after 1 hour.
            Add recurring timer or interval to refresh token every 45-55 min.
            self.auth.refresh(self.token)
            '''

    def refresh_token(self,*args):
        self.user=self.auth.refresh(self.user['refreshToken'])

    def set_version_info(self,*args):
        data=self.db.child('version').get().val()
        UpdateService.available_version=data['version']
        UpdateService.download_integity=data['checksum']
        if UpdateService.available_version!=UpdateService.current_version:
                UpdateService.update_available=1

    def version_stream_handler(self, response):
        if 'version' in response['path']:
            UpdateService.available_version=response['data']
            if UpdateService.available_version!=UpdateService.current_version:
                UpdateService.update_available=1
        if 'checksum' in response['path']:
            UpdateService.download_integity=response['data']

    def req_fans_stream_handler(self, response):
        if response["data"]==0:
            return
        self.device_requests['fans']=response["data"]

    def req_lights_stream_handler(self, response):
        if response["data"]==0:
            return
        self.device_requests['lights']=response["data"]

    def reset_reqs(self):
        for i in self.device_requests:
            self.device_requests[i]=0
        try:
            self.toggleDevice(self.devices.req_fans , 0)
            self.toggleDevice(self.devices.req_lights , 0)
        except Exception as e:
            print(f'server.py reset_reqs(): {e}')

    def message_stream_handler(self, response):
        print(response)
        print(response["event"]) # put
        print(response["path"]) # /-K7yGTTEp7O549EzTYtI
        print(response["data"]) # {'title': 'Pyrebase', "body": "etc..."}
        '''TODO Add message stream functionality here
        '''

    def getUserEmail(self) -> str:
        if self.user["email"]:
            return self.user["email"]
        else:
            return "Email not found"

    def getCurrentUser(self):
        print(self.auth.current_user)


    def toggleDevice(self, device: str, status: int):
        data = {device: status}
        self.db.child(self.path).update(data, self.token)
    

    def addReport(self):
        with open(reports_dir) as report:
            report.read()
        self.sb.child(self["user"]).put(report, self["user"])


    def getReport(self, file):
        self.sb.child(self["user"]).list_files()

    
    def delReport(self, name):
        self.sb.child(self["user"] + '/' + name).delete()
    

    # Get list of fire suppression system reports saved in storage bucket
    def getCloudReportList(self):
        unSyncedReports = []
        localReports = []
        cloudReports = []

        if len(cloudReports) == len(localReports):
            return
        
        elif len(cloudReports) > len(localReports):
            # do some type of
            pass
        reports = self.sb.list_files()
        for report in reports:
            print(report.name)
            
            # print(report.metadata)
            # print(report.public_url)
            # localReports.append(dir(report))
            
        return localReports.copy()
    
    def clean_exit(self):
        for i in self.active_streams:
            try:
                i.close()
            except Exception as e:
                print(f'server.py clean_exit(): {e}')



    class Devices:
        '''This namespace contains string
        values for database key name consistency
        '''
        def __init__(self) -> None:
            self.exhaust = 'exhaust'
            self.req_fans='req_fans'
            self.lights = 'lights'
            self.req_lights = 'req_lights'
            self.mau = 'mau'


server = Db_service()