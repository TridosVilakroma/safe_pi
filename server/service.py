import threading,time
from typing import Any
from functools import partial
import interface


class MetaServerCache(type):

    @property
    def cached(cls):
        return {k:v for k,v in cls.__dict__.items() if not k.startswith('_') and not callable(getattr(cls,k))}

    def __setattr__(self, name: str, value: Any) -> None:
        package=(*value,time.time())
        return super().__setattr__(name, package)

    def __getattr__(self, name: str) -> Any:
        return ''

    def __getattribute__(self, name: str) -> Any:
        item=super().__getattribute__(name)
        if isinstance(item,tuple):
            return item[0]
        return item


class ServerCache(metaclass=MetaServerCache):

    @classmethod
    def purge_stale(cls,*args):
        p_lst=[]
        print('cls.cached: ',cls.cached)
        for k,v in cls.cached.items():
            if v[2]>v[1]+time.time():
                p_lst.append(k)
        for i in p_lst:
            delattr(cls,i)






class Handler:
    def __init__(self) -> None:
        self.interface=interface.ServerInterface()
        self.cache=ServerCache


    def cache_value(self,name:str,val:str='',cache_time:float=5.0,*args):
        setattr(self.cache,name,(val,cache_time))


    def _set(self,widget,prop:str,endpoint,*args):
        val=self.interface.uid
        func=partial(setattr,widget,prop,val)

    def update(self,*args):
        pass





h=Handler()
h.cache_value('hello','world',5.0)
h.cache.purge_stale()
print(h.cache.cached)
print(h.cache.hello)
