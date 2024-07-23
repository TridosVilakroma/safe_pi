import threading,time,weakref,sys,configparser,os,json
from requests.exceptions import HTTPError
from typing import Any
from functools import partial
try:
    import interface
except:
    import server.interface as interface
from kivy.clock import mainthread
from kivy.app import App

if os.name == 'nt':
    preferences_path='logs/configurations/hood_control.ini'

if os.name == 'posix':
    preferences_path='/home/pi/Pi-ro-safe/logs/configurations/hood_control.ini'


class MetaServerCache(type):

    @property
    def cached(cls):
        return {k:v for k,v in cls.__dict__.items() if not k.startswith('_') and not callable(getattr(cls,k))}

    def __setattr__(self, name: str, value: Any) -> None:
        if name in self.cached:
            package=self.cached[name]
            package.value=value
            package.stamp=time.time()
            return
        package=Observable(*value,time.time())
        return super().__setattr__(name, package)

    def __getattr__(self, name: str) -> Any:
        setattr(self,name)
        return self.name

    def __getattribute__(self, name: str) -> Any:
        item=super().__getattribute__(name)
        if isinstance(item,Observable):
            return item.value
        return item


class ServerCache(metaclass=MetaServerCache):
    pass


class Observable:
    def __init__(self,value,cache_time,stamp) -> None:
        self.observers={}
        self.stamp=stamp
        self._value=value

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self,value):
        self._value=value
        self.notify(self._value)

    def add_observer(self,observer:str,callback):
        if observer in self.observers.keys():
            return
        self.observers[observer]=callback

    def remove_observer(self,observer:str):
        if observer in self.observers.keys():
            del self.observers[observer]

    def notify(self,*args):
        for i in self.observers.values():
            if callable(i):
                i(*args)




class Handler:
    def __init__(self) -> None:
        self._config=[configparser.ConfigParser(),time.time()]
        self._config[0].read(preferences_path)
        self.interface=interface.ServerInterface()
        self.cache=ServerCache
        self.tasks=[]
        self.task_thread=threading.Thread()
        self.supervisor_busy=False
        self.auto_verify=True
        self.monitored_documents={}
        self.monitored_collections={}
        self.errors={
            "auth":False,
        }
        self.status_datums=[
            'Status',
            'online',
            'account',
            'devices']

        # self.interface.sign_in_user('calebstock91@gmail.com','test_password')
        # self.interface.fire_store_init()

    @property
    def config(self):
        if self._config[1]<time.time()-30:
            self._config[0].read(preferences_path)
            self._config[1]=time.time()
        return self._config[0]

    @property
    def saved_email(self):
        return self.config.get('account','email',fallback='')

    @property
    def saved_password(self):
        return self.config.get('account','password',fallback='')


    def get_and_cache_address(self,*args):
        print("shared_data/"+self.interface.user["localId"])
        v=self.interface.firestore_db.collection("shared_data").document(self.interface.user["localId"]).get().to_dict()['address']
        # v=self.interface.firestore_db.collection("shared_data").document(self.interface.user["localId"]).set({'address':'testing 101'})
        self.cache.cached['address'].value=(v)



    ##########     tasks     ##########

    def create_task(self,task,toast=False,*args):
        def prepared_task():
            r=task()
            if type(r)==HTTPError:
                self.register_error(r)
                return
            if callable(toast):
                toast()
        self.tasks.append(prepared_task)

    def create_supervisor_task(self,task,toast=False,*args):
        def prepared_task():
            print('running supervisor task')
            r=task()
            if type(r)==HTTPError:
                self.register_error(r,supervisor=True)
                return
            if callable(toast):
                toast()
            self.supervisor_busy=False
            self.errors['auth']=False
        self.tasks.insert(0,prepared_task)

    def run_task(self,*args):
        if self.tasks:
            self.task_thread=threading.Thread(target=self.tasks.pop(0),daemon=True)
            self.task_thread.start()

    def stop_task(self,task=None,*args):
        if task:
            self.tasks.remove(task)
            return
        if self.task_thread.is_alive():
            self.task_thread.kill()

    def update_tasks(self,*args):
        if self.task_thread.is_alive():
            return
        self.run_task()

    ##########     cache     ##########

    def cache_value(self,name:str,val:str='',cache_time:float=5.0,*args):
        setattr(self.cache,name,(val,cache_time))

    def on_document_snapshot(document_snapshot, changes, read_time):
        pass

    def on_collection_snapshot(collection_snapshot, changes, read_time):
        pass

    def monitor_document(self,document_id):
        pass

    def monitor_collection(self,collection_id):
        pass


    ##########     database     ##########

    def get_user_document(self,*args):
        def f():
            r=self.interface.get_user_document()
            print(r)
            print(type(r))
            if type(r)==HTTPError:
                return r
            if type(r)==dict:
                for k,v in r.items():
                    self.cache_value(k,v)
        self.create_task(f)

    ##########     gui     ##########

    @mainthread
    def _set_text(self,widget,cached_val,*args):
        if cached_val:
            text=cached_val[0]
        else:
            text=''
        widget().text=str(text)

    def text_setter(self,widget,cache_key:str,*args):
        '''bind a widgets text to a cache key'''
        w=weakref.ref(widget)
        if cache_key in self.cache.cached:
            self.cache.cached[cache_key].add_observer(str(id(widget)),partial(self._set_text,w))
        else:
            self.cache_value(cache_key)
            self.cache.cached[cache_key].add_observer(str(id(widget)),partial(self._set_text,w))
        return ''

    @mainthread
    def toast(self,msg:str='',level:str='info',*args):
        if not msg:
            return
        App.get_running_app().notifications.toast(msg,level)

    ##########     account     ##########

    def log_in(self,email:str,password:str,*args):
        self.create_task(lambda: self.interface.sign_in_user(email,password),partial(self.toast,'Logged In'))
        self.create_task(self.interface.fire_store_init)

    def create_account(self,email:str,password:str,*args):
        self.create_task(lambda: self.interface.register_user(email,password),partial(self.toast,'Verify Email Link\nTo Complete Account\nCreation'))
        self.create_task(self.interface.fire_store_init)
        self.create_task(self.interface.send_verification_email)

    def unlink_account(self,*args):
        self.pause_server_verification()


    ##########     utility     ##########

    def resolve_statuses(self,*args):

        #status
        if self.errors['auth']:
            self.cache_value('Status','Status: [color=ff0000]Offline')
        else:
            self.cache_value('Status','Status: [color=00ff00]Online')

        #online status
        if self.errors['auth']:
            self.cache_value('online','Online: [color=ff0000]Disconnected')
        else:
            self.cache_value('online','Online: [color=00ff00]Connected')

        #account status
        if self.errors['auth']:
            self.cache_value('account','Account: [color=ff0000]Errors')
        else:
            self.cache_value('account','Account: [color=00ff00]Success')

        #device status
        self.cache_value('devices','Connected Devices: [color=00ff00]0')

    def verify_server_connection(self,*args):
        if not self.auto_verify:
            return
        if any(not self.interface.user[i] for i in ['email','localId','idToken','refreshToken']):
            self.errors['auth']=True
        if (self.supervisor_busy or not self.errors['auth']):
            return
        if not (self.saved_email and self.saved_password):
            return
        self.supervisor_busy=True
        self.create_supervisor_task(self.interface.fire_store_init)
        self.create_supervisor_task(lambda: self.interface.sign_in_user(self.saved_email,self.saved_password))
        return

    def pause_server_verification(self,*args):
        self.auto_verify=False

    def resume_server_verification(self,*args):
        self.auto_verify=True

    def register_error(self,error,supervisor=False,*args):
        if supervisor:
            self.pause_server_verification()
            return
        error=json.loads(error.strerror)['error']['message'].split(maxsplit=1)[0]
        print(error)
        toast=self.toast
        if error=='ADMIN_ONLY_OPERATION':
            pass
        if error=='ARGUMENT_ERROR':
            pass
        if error=='APP_NOT_AUTHORIZED':
            pass
        if error=='APP_NOT_INSTALLED':
            pass
        if error=='CAPTCHA_CHECK_FAILED':
            pass
        if error=='CODE_EXPIRED':
            pass
        if error=='CORDOVA_NOT_READY':
            pass
        if error=='CORS_UNSUPPORTED':
            pass
        if error=='CREDENTIAL_ALREADY_IN_USE':
            pass
        if error=='CREDENTIAL_MISMATCH':
            pass
        if error=='CREDENTIAL_TOO_OLD_LOGIN_AGAIN':
            pass
        if error=='DEPENDENT_SDK_INIT_BEFORE_AUTH':
            pass
        if error=='DYNAMIC_LINK_NOT_ACTIVATED':
            pass
        if error=='EMAIL_CHANGE_NEEDS_VERIFICATION':
            pass
        if error=='EMAIL_EXISTS':
            pass
        if error=='EMAIL_NOT_FOUND':
            toast('[b][size=20]Email Or Password\nAre Incorrect','warning')
            pass
        if error=='EMULATOR_CONFIG_FAILED':
            pass
        if error=='EXPIRED_OOB_CODE':
            pass
        if error=='EXPIRED_POPUP_REQUEST':
            pass
        if error=='INTERNAL_ERROR':
            pass
        if error=='INVALID_API_KEY':
            pass
        if error=='INVALID_APP_CREDENTIAL':
            pass
        if error=='INVALID_APP_ID':
            pass
        if error=='INVALID_AUTH':
            pass
        if error=='INVALID_AUTH_EVENT':
            pass
        if error=='INVALID_CERT_HASH':
            pass
        if error=='INVALID_CODE':
            pass
        if error=='INVALID_CONTINUE_URI':
            pass
        if error=='INVALID_CORDOVA_CONFIGURATION':
            pass
        if error=='INVALID_CUSTOM_TOKEN':
            pass
        if error=='INVALID_DYNAMIC_LINK_DOMAIN':
            pass
        if error=='INVALID_EMAIL':
            toast('[b][size=20]Email Format Is Invalid\nVerify The Email Spelling','warning')
        if error=='INVALID_EMULATOR_SCHEME':
            pass
        if error=='INVALID_IDP_RESPONSE':
            pass
        if error=='INVALID_LOGIN_CREDENTIALS':
            pass
        if error=='INVALID_MESSAGE_PAYLOAD':
            pass
        if error=='INVALID_MFA_SESSION':
            pass
        if error=='INVALID_OAUTH_CLIENT_ID':
            pass
        if error=='INVALID_OAUTH_PROVIDER':
            pass
        if error=='INVALID_OOB_CODE':
            pass
        if error=='INVALID_ORIGIN':
            pass
        if error=='INVALID_PASSWORD':
            toast('[b][size=20]Email Or Password\nAre Incorrect','warning')
        if error=='INVALID_PERSISTENCE':
            pass
        if error=='INVALID_PHONE_NUMBER':
            pass
        if error=='INVALID_PROVIDER_ID':
            pass
        if error=='INVALID_RECIPIENT_EMAIL':
            pass
        if error=='INVALID_SENDER':
            pass
        if error=='INVALID_SESSION_INFO':
            pass
        if error=='INVALID_TENANT_ID':
            pass
        if error=='MFA_INFO_NOT_FOUND':
            pass
        if error=='MFA_REQUIRED':
            pass
        if error=='MISSING_ANDROID_PACKAGE_NAME':
            pass
        if error=='MISSING_APP_CREDENTIAL':
            pass
        if error=='MISSING_AUTH_DOMAIN':
            pass
        if error=='MISSING_CODE':
            pass
        if error=='MISSING_CONTINUE_URI':
            pass
        if error=='MISSING_IFRAME_START':
            pass
        if error=='MISSING_IOS_BUNDLE_ID':
            pass
        if error=='MISSING_OR_INVALID_NONCE':
            pass
        if error=='MISSING_MFA_INFO':
            pass
        if error=='MISSING_MFA_SESSION':
            pass
        if error=='MISSING_PHONE_NUMBER':
            pass
        if error=='MISSING_SESSION_INFO':
            pass
        if error=='MODULE_DESTROYED':
            pass
        if error=='NEED_CONFIRMATION':
            pass
        if error=='NETWORK_REQUEST_FAILED':
            pass
        if error=='NULL_USER':
            pass
        if error=='NO_AUTH_EVENT':
            pass
        if error=='NO_SUCH_PROVIDER':
            pass
        if error=='OPERATION_NOT_ALLOWED':
            pass
        if error=='OPERATION_NOT_SUPPORTED':
            pass
        if error=='POPUP_BLOCKED':
            pass
        if error=='POPUP_CLOSED_BY_USER':
            pass
        if error=='PROVIDER_ALREADY_LINKED':
            pass
        if error=='QUOTA_EXCEEDED':
            pass
        if error=='REDIRECT_CANCELLED_BY_USER':
            pass
        if error=='REDIRECT_OPERATION_PENDING':
            pass
        if error=='REJECTED_CREDENTIAL':
            pass
        if error=='SECOND_FACTOR_ALREADY_ENROLLED':
            pass
        if error=='SECOND_FACTOR_LIMIT_EXCEEDED':
            pass
        if error=='TENANT_ID_MISMATCH':
            pass
        if error=='TIMEOUT':
            pass
        if error=='TOKEN_EXPIRED':
            pass
        if error=='TOO_MANY_ATTEMPTS_TRY_LATER':
            toast('[b][size=20]Too Many Attempts Try Later','warning')
        if error=='UNAUTHORIZED_DOMAIN':
            pass
        if error=='UNSUPPORTED_FIRST_FACTOR':
            pass
        if error=='UNSUPPORTED_PERSISTENCE':
            pass
        if error=='UNSUPPORTED_TENANT_OPERATION':
            pass
        if error=='UNVERIFIED_EMAIL':
            pass
        if error=='USER_CANCELLED':
            pass
        if error=='USER_DELETED':
            pass
        if error=='USER_DISABLED':
            pass
        if error=='USER_MISMATCH':
            pass
        if error=='USER_SIGNED_OUT':
            pass
        if error=='WEAK_PASSWORD':
            pass
        if error=='WEB_STORAGE_UNSUPPORTED':
            pass
        if error=='ALREADY_INITIALIZED':
            pass
        if error=='RECAPTCHA_NOT_ENABLED':
            pass
        if error=='MISSING_RECAPTCHA_TOKEN':
            pass
        if error=='INVALID_RECAPTCHA_TOKEN':
            pass
        if error=='INVALID_RECAPTCHA_ACTION':
            pass
        if error=='MISSING_CLIENT_TYPE':
            pass
        if error=='MISSING_RECAPTCHA_VERSION':
            pass
        if error=='INVALID_RECAPTCHA_VERSION':
            pass
        if error=='INVALID_REQ_TYPE':
            pass

    def update(self,*args):
        self.verify_server_connection()
        self.update_tasks()
        self.resolve_statuses()




