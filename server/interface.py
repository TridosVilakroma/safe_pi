import pyrebase as Firebase
from requests.exceptions import HTTPError
try:
    import firestore
except:
    import server.firestore as firestore

class ServerInterface:
    def __init__(self) -> None:

        self.config={
            'apiKey': "AIzaSyDYLaE0PMm3yddp6spml8ANCZT-rpEotNs",
            'authDomain': "hood-control-67b78.firebaseapp.com",
            'databaseURL': "https://hood-control-67b78-default-rtdb.firebaseio.com",
            'projectId': "hood-control-67b78",
            'storageBucket': "hood-control-67b78.appspot.com",
            'messagingSenderId': "19231970603",
            'appId': "1:19231970603:web:a11433f93fdb9c1ce6216e",
            'measurementId': "G-5JCVCD9G1K"}

        self.firebase = firebase = Firebase.initialize_app(self.config)
        self.auth = firebase.auth()
        self.storage_bucket = firebase.storage()
        self.realtime_db = firebase.database()
        self.firestore_db=False
        self.user=self.user_template={
            "email"   :  "",
            "localId" :  "",
            "idToken" :  "",
            "localId" :  ""}


    @property
    def email(self):
        return self.user["email"]

    @property
    def path(self):
        return "users/" + self.user["localId"]

    @property
    def token(self):
        return self.user["idToken"]

    @property
    def uid(self):
        return self.user["localId"]

    def sign_in_user(self, email: str, password: str, *args):
        try:
            self.user = self.auth.sign_in_with_email_and_password(email, password)
        except HTTPError as e:
            print('httperror: ',e)

    def register_user(self, email: str, password: str, *args):
        try:
            self.user = self.auth.create_user_with_email_and_password(email, password)
        except HTTPError as e:
            print('httperror: ',e)

    def fire_store_init(self,*args):
        try:
            self.firestore = firestore.firestore_init(self.user,self.config['projectId'])
        except Exception as e:
            print('firestore exception: ',e)

    def send_verification_email(self):
        try:
            self.auth.send_email_verification(self.token)
        except HTTPError as e:
            print('firestore exception: ',e)

    def refresh_token(self,*args):
        try:
            refresh_response=self.auth.refresh(self.user['refreshToken'])
            self.user["userId"]=refresh_response["userId"]
            self.user["idToken"]=refresh_response["idToken"]
            self.user["refreshToken"]=refresh_response["refreshToken"]
        except HTTPError as e:
            print('firestore exception: ',e)

    # def set_version_info(self,*args):
    #     data=self.db.child('version').get().val()
    #     UpdateService.available_version=data['version']
    #     UpdateService.download_integity=data['checksum']
    #     if UpdateService.available_version!=UpdateService.current_version:
    #             UpdateService.update_available=1

    # def get_version_info(self, response):
    #     if 'version' in response['path']:
    #         UpdateService.available_version=response['data']
    #         if UpdateService.available_version!=UpdateService.current_version:
    #             UpdateService.update_available=1
    #     if 'checksum' in response['path']:
    #         UpdateService.download_integity=response['data']

