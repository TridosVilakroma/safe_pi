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
            'fade_in' :partial(Animation,opacity=1       ,d=.4,t='out_quad')
        }

        #uncomment block below to see widget area
    #     with self.canvas.before:
    #             self.colour = Color(1,1,1,1)
    #             self.rect = Rectangle(size=self.size, pos=self.pos)
    #     self.bind(size=self._update_rect, pos=self._update_rect)

    # def _update_rect(self, instance, *args):
    #     self.rect.pos = instance.pos
    #     self.rect.size = instance.size


    #####    banner handling    #####

    def banner(self,msg:str=''):
        pass


    #####    toast handling    #####

    def toast(self,msg:str='',level:str='info',*args):
        n=Toast(level=level,text=msg)
        self.toast_que.append(n)

    def process_toast_que(self):
        if self.processing_toast_que or not self.toast_que:
            return False
        self.processing_toast_que=True
        for index,i in enumerate(self.children):
            Animation.cancel_all(i)
            shift=self.toast_animations[f'shift_{index}']()
            shift.start(i)
            fade_out=self.toast_animations['fade_out']()
            fade_out.start(i)
        if len(self.children)>=11:
            child=self.children[-1]
            Animation.cancel_all(child)
            clear=self.toast_animations['clear']()
            clear.start(child)
            clear.bind(on_complete=lambda *args: self.remove_widget(child))
            clear.bind(on_complete=lambda *args: self.overflow.append(child))
        n=self.toast_que.pop()
        n.life_time=time.time()
        self.add_widget(n)
        push=self.toast_animations['push']()
        push.start(n)
        push.bind(on_complete=lambda *args: setattr(self,'processing_toast_que',False))
        return True

    def process_toast(self):
        if self.processing_toast or not self.children:
            return False

        active=self.children[0]
        toast_duration=time.time()-active.theme['time']
        if active.life_time>toast_duration:
            return False

        self.processing_toast=True

        Animation.cancel_all(active)
        clear=self.toast_animations['clear']()
        clear.start(active)
        clear.bind(on_complete=lambda *args: self.remove_widget(active))
        clear.bind(on_complete=lambda *args: setattr(self,'processing_toast',False))

        if len(self.children)<=1:
            return False

        for index,i in enumerate(self.children):
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
        if len(self.children)<=11:
            if len(self.overflow)<1:
                return False
            child=self.overflow.pop()
            Animation.cancel_all(child)
            self.add_widget(child,len(self.children))
            fade_out=self.toast_animations['fade_out']()
            fade_out.start(child)
            shift=self.toast_animations[f'shift_{len(self.children)-2 }']()
            shift.start(child)
        return True

    def update(self,*args):
        if not self.process_toast_que():
            self.process_toast()