import general,time
from functools import partial
from notifications.banner import Banner
from notifications.toast import Toast

from kivy.animation import Animation
from kivy.uix.floatlayout import FloatLayout
from kivy.app import App

from kivy.graphics import Rectangle, Color, Line, Bezier

class Notifications(FloatLayout):
    def __init__(self,**kwargs) -> None:
        super(Notifications,self).__init__(**kwargs)

        #####    toast attributes    #####

        self._toast_widgets=[]
        self.processing_toast_que=False
        self.processing_toast=False
        self.toast_que=[]
        self.overflow=[]
        self.toast_animations={
            'push':partial(Animation,pos_hint={'x':-.05,'y':0},d=.4,t='out_back'),
            'clear':partial(Animation,pos_hint={'x':1},d=.35,t='in_back'),
            'shift_0' :partial(Animation,pos_hint={'x':-.01, 'y':.15},d=.4,t='out_back'),
            'shift_1' :partial(Animation,pos_hint={'x':-.01, 'y':.2} ,d=.4,t='out_back'),
            'shift_2' :partial(Animation,pos_hint={'x':-.01, 'y':.25},d=.4,t='out_back'),
            'shift_3' :partial(Animation,pos_hint={'x':-.01, 'y':.3} ,d=.4,t='out_back'),
            'shift_4' :partial(Animation,pos_hint={'x':-.01, 'y':.35},d=.4,t='out_back'),
            'shift_5' :partial(Animation,pos_hint={'x':-.01, 'y':.4} ,d=.4,t='out_back'),
            'shift_6' :partial(Animation,pos_hint={'x':-.01, 'y':.45},d=.4,t='out_back'),
            'shift_7' :partial(Animation,pos_hint={'x':-.01, 'y':.5} ,d=.4,t='out_back'),
            'shift_8' :partial(Animation,pos_hint={'x':-.01, 'y':.55},d=.4,t='out_back'),
            'shift_9' :partial(Animation,pos_hint={'x':-.01, 'y':.6} ,d=.4,t='out_back'),
            'shift_10':partial(Animation,pos_hint={'x':-.01, 'y':.65},d=.4,t='out_back'),
            'shift_11':partial(Animation,pos_hint={'x':-.01, 'y':.7} ,d=.4,t='out_back'),
            'fade_out':partial(Animation,opacity=.25       ,d=.4 ,t='out_quad'),
            'fade_in' :partial(Animation,opacity=1       ,d=.4,t='out_quad')}

        #####    banner attributes    #####

        self.current_banners=[]
        self.processing_banner=False
        self.banner_animations={
            'push':partial(Animation,pos_hint={'x':-3.05,'y':.975},d=.75,t='out_expo'),
            'clear':partial(Animation,pos_hint={'x':-3.05,'y':1.25},d=.35,t='in_expo')}

    #####    uncomment block below to see widget area    #####
    '''
        with self.canvas.before:
                self.colour = Color(1,1,1,1)
                self.rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self._update_rect, pos=self._update_rect)

    def _update_rect(self, instance, *args):
        self.rect.pos = instance.pos
        self.rect.size = instance.size
    '''

    #####    banner handling    #####

    @property
    def active_banner(self,*args):
        if len(self.current_banners)>0:
            return self.current_banners[0]
        else: return None

    def banner(self,msg:str='',level:str='info',value:int=0,*args):
        for i in self.current_banners:
            if i.text==msg:
                return
        b=Banner(level=level,text=msg,value=value)
        self.current_banners.append(b)
        self.sort_banners()
        return b

    def sort_banners(self,*args):
        critical=[i for i in self.current_banners if i.level=='critical']
        error=[i for i in self.current_banners if i.level=='error']
        warning=[i for i in self.current_banners if i.level=='warning']
        info=[i for i in self.current_banners if i.level=='info']
        critical.sort(key=lambda x:x.value);error.sort(key=lambda x:x.value)
        warning.sort(key=lambda x:x.value);info.sort(key=lambda x:x.value)
        self.current_banners=[]
        self.current_banners+=critical+error+warning+info

    def process_banner(self,*args):
        if self.processing_banner or not self.current_banners:
            return False
        for index,i in enumerate(self.current_banners):
            if i.remove_flag and index==0:
                self.current_banners.remove(i)
                clear=self.banner_animations['clear']()
                clear.start(i)
                clear.bind(on_complete=lambda *args: self.remove_widget(i))
                return
        if self.active_banner.parent:
            return
        for i in self.current_banners:
            if i in self.children:
                self.processing_banner=True
                clear=self.banner_animations['clear']()
                clear.start(i)
                clear.bind(on_complete=lambda *args: self.remove_widget(i))
                clear.bind(on_complete=lambda *args: setattr(self,'processing_banner',False))
                return
        self.processing_banner=True
        self.add_widget(self.active_banner)
        push=self.banner_animations['push']()
        push.start(self.active_banner)
        push.bind(on_complete=lambda *args: setattr(self,'processing_banner',False))



    def remove_banner(self,target:int=0,*args):
        '''Remove element from `current_banners`.

        Element will be removed via index or value.
        '''

        if type(target) == int:
            self.current_banners[target].remove_flag=True
        else:
            if target in self.current_banners:
                target.remove_flag=True

    #####    toast handling    #####

    def toast(self,msg:str='',level:str='info',*args):
        n=Toast(level=level,text=msg)
        self.toast_que.append(n)

    def process_toast_que(self):
        if self.processing_toast_que or not self.toast_que:
            return False
        self.processing_toast_que=True
        for index,i in enumerate(self._toast_widgets):
            Animation.cancel_all(i)
            shift=self.toast_animations[f'shift_{index}']()
            shift.start(i)
            fade_out=self.toast_animations['fade_out']()
            fade_out.start(i)
        if len(self._toast_widgets)>=10:
            child=self._toast_widgets[-1]
            Animation.cancel_all(child)
            clear=self.toast_animations['clear']()
            clear.start(child)
            clear.bind(on_complete=lambda *args: self.remove_toast(child))
            clear.bind(on_complete=lambda *args: self.overflow.append(child))
        n=self.toast_que.pop()
        n.life_time=time.time()
        self.add_widget(n)
        self._toast_widgets.insert(0,n)
        push=self.toast_animations['push']()
        push.start(n)
        push.bind(on_complete=lambda *args: setattr(self,'processing_toast_que',False))
        return True

    def remove_toast(self,toast,*args):
        self._toast_widgets.remove(toast)
        self.remove_widget(toast)

    def process_toast(self):
        if self.processing_toast or not self._toast_widgets:
            return False

        active=self._toast_widgets[0]
        toast_duration=time.time()-active.theme['time']
        if active.life_time>toast_duration:
            return False

        self.processing_toast=True

        Animation.cancel_all(active)
        clear=self.toast_animations['clear']()
        clear.start(active)
        clear.bind(on_complete=lambda *args: self.remove_toast(active))
        clear.bind(on_complete=lambda *args: setattr(self,'processing_toast',False))

        if len(self._toast_widgets)<=1:
            return False

        for index,i in enumerate(self._toast_widgets):
            if index==0:
                continue
            elif index==1:
                Animation.cancel_all(i)
                push=self.toast_animations['push']()
                push.start(i)
                fade_in=self.toast_animations['fade_in']()
                fade_in.start(i)
                i.life_time=time.time()
                continue
            Animation.cancel_all(i)
            shift=self.toast_animations[f'shift_{index-2}']()
            shift.start(i)
        if len(self._toast_widgets)<=10:
            if len(self.overflow)<1:
                return False
            child=self.overflow.pop()
            Animation.cancel_all(child)
            self.add_widget(child,len(self._toast_widgets))
            fade_out=self.toast_animations['fade_out']()
            fade_out.start(child)
            shift=self.toast_animations[f'shift_{len(self._toast_widgets)-2 }']()
            shift.start(child)
            self._toast_widgets.append(child)
        return True

    def update(self,*args):
        if not self.process_toast_que():
            self.process_toast()
        self.process_banner()