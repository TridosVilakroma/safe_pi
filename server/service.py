import threading,time,weakref,sys
from typing import Any
from functools import partial
try:
    import interface
except:
    import server.interface as interface
from kivy.clock import mainthread

class MetaServerCache(type):

    @property
    def cached(cls):
        return {k:v for k,v in cls.__dict__.items() if not k.startswith('_') and not callable(getattr(cls,k))}

    def __setattr__(self, name: str, value: Any) -> None:
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
        self.observers=[]
        self.stamp=stamp
        self._value=value

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self,value):
        self._value=value
        self.notify(self._value)

    def add_observer(self,observer):
        self.observers.append(observer)

    def remove_observer(self,observer):
        if observer in self.observers:
            self.observers.remove(observer)

    def notify(self,*args):
        for i in self.observers:
            if callable(i):
                i(*args)




class Handler:
    def __init__(self) -> None:
        self.interface=interface.ServerInterface()
        self.cache=ServerCache
        self.tasks=[]
        self.task_thread=threading.Thread()
        self.monitored_documents={}
        self.monitored_collections={}

        self.interface.sign_in_user('calebstock91@gmail.com','test_password')
        self.interface.fire_store_init()


    def get_and_cache_address(self,*args):
        print("shared_data/"+self.interface.user["localId"])
        v=self.interface.firestore_db.collection("shared_data").document(self.interface.user["localId"]).get().to_dict()['address']
        # v=self.interface.firestore_db.collection("shared_data").document(self.interface.user["localId"]).set({'address':'testing 101'})
        self.cache.cached['address'].value=(v)



    ##########     tasks     ##########

    def create_task(self,task,*args):
        def template(t):
            self.interface.task()
        self.tasks.append(partial(template,task))

    def run_task(self,task,*args):
        if self.tasks:
            self.task_thread=threading.Thread(target=self.tasks.pop(0),daemon=True)
            self.task_thread.start()

    def stop_task(self,task,*args):
        if self.task_thread.is_alive():
            self.task_thread.kill()

    def update_tasks(self,task,*args):
        if self.task_thread.is_alive():
            return

    ##########     cache     ##########

    def cache_value(self,name:str,val:str='',cache_time:float=5.0,*args):
        setattr(self.cache,name,(val,cache_time))

    ##########     gui     ##########

    @mainthread
    def _set_text(self,widget,text:str='',*args):
        widget().text=str(text)

    def text_setter(self,widget,cache_key:str,*args):
        '''bind a widgets text to a cache key'''
        w=weakref.ref(widget)
        if cache_key in self.cache.cached:
            self.cache.cached[cache_key].add_observer(partial(self._set_text,w))
        else:
            self.cache_value(cache_key)
            self.cache.cached[cache_key].add_observer(partial(self._set_text,w))
        return ''

    def _set(self,widget,prop:str,endpoint,*args):
        val=self.interface.uid
        func=partial(setattr,widget,prop,val)

    def on_document_snapshot(document_snapshot, changes, read_time):
        pass

    def on_collection_snapshot(collection_snapshot, changes, read_time):
        pass

    def monitor_document(self,document_id):
        pass

    def monitor_collection(self,collection_id):
        pass

    def update(self,*args):
        pass
        #self.cache.purge_stale()
        #self.update_tasks()




# h=Handler()
# h.cache_value('test','test_val')
# h.cache.test.add_observer(lambda x:print(x))
# h.cache.test.value='setting'
# time.sleep(1)
# h.cache.test.value='setting_again'
