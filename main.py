import os,json,time,shutil,math,random,subprocess
import re,string,importlib,ast,glob,pathlib
import traceback,errno
from datetime import datetime,timedelta
from kivy.config import Config
from copy import deepcopy
import segno

import logging,logging_config
logger=logging.getLogger('logger')

import utils.dir_tree_builder
utils.dir_tree_builder.build_logs_tree()

from device_classes.exhaust import Exhaust
from device_classes.mau import Mau
from device_classes.light import Light
from device_classes.drycontact import DryContact
from device_classes.gas_valve import GasValve
from device_classes.micro_switch import MicroSwitch
from device_classes.switch_light import SwitchLight
from device_classes.switch_fans import SwitchFans
from device_classes.heat_sensor import HeatSensor
from device_classes.manometer import Manometer

if os.name=='posix':
    import manometer.manometer as _manometer
    import network_L as network
if os.name=='nt':
    import network_W as network
from messages import messages
from server.server import server
import version.updater as UpdateService
from version.version import version as VERSION
UpdateService.current_version=VERSION
from notifications.handler import Notifications as Notifications
from utils.color_themes import palette

Config.set('kivy', 'keyboard_mode', 'systemanddock')
if os.name=='posix':
    Config.set('graphics', 'fullscreen', 'auto')
    Config.set('graphics', 'borderless', '1')
else:
    Config.set('graphics', 'width', '1280')
    Config.set('graphics', 'height', '800')

import kivy
import logic,lang_dict,pindex,utils.general as general
if os.name == 'nt':
    import RPi_test.GPIO as GPIO
else:
    import RPi.GPIO as GPIO
from kivy.uix.widget import Widget
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.animation import Animation
from kivy.app import App
from kivy.uix.image import Image
from kivy.graphics import BorderImage
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.checkbox import CheckBox
from kivy.uix.bubble import Bubble, BubbleButton
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.pagelayout import PageLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.stacklayout import StackLayout
from kivy.uix.slider import Slider
from kivy.core.window import Window
import threading
from threading import Thread
from kivy.uix.screenmanager import NoTransition
from kivy.uix.screenmanager import SlideTransition
from kivy.uix.screenmanager import FallOutTransition
from kivy.uix.screenmanager import RiseInTransition
from kivy.clock import Clock,mainthread
from functools import partial
from kivy.uix.behaviors import ButtonBehavior,DragBehavior
from kivy.uix.scrollview import ScrollView
from kivy.uix.recycleview import RecycleView
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.uix.recycleboxlayout import RecycleLayout,RecycleBoxLayout
from kivy.graphics import Rectangle, Color, Line, Bezier
from kivy.properties import ListProperty,StringProperty,NumericProperty,ColorProperty,OptionProperty,BooleanProperty,ObjectProperty
import configparser
from kivy.uix.settings import SettingsWithNoMenu
from kivy.uix.settings import SettingsWithSidebar
from kivy.effects.scroll import ScrollEffect
from kivy.uix.effectwidget import EffectWidget
from kivy.uix.effectwidget import HorizontalBlurEffect, VerticalBlurEffect
from kivy.uix.popup import Popup
from kivy.uix.scatter import Scatter
from kivy.uix.scatterlayout import ScatterLayout
from kivy.graphics.transformation import Matrix
from kivy.input.providers.mouse import MouseMotionEvent
from kivy.uix.carousel import Carousel
from kivy.uix.textinput import TextInput
from kivy.uix.vkeyboard import VKeyboard
from kivy.uix.spinner import Spinner,SpinnerOption
from kivy.graphics import RoundedRectangle
from kivy.uix.progressbar import ProgressBar
from circle_progress_bar import CircularProgressBar
from kivy.uix.filechooser import FileChooserIconView, FileChooserListView
from kivy.graphics.context_instructions import PopMatrix,PushMatrix,Rotate,Scale
from kivy.uix.accordion import Accordion, AccordionItem
from kivy.metrics import sp

kivy.require('2.0.0')
current_language=lang_dict.english

if os.name == 'nt':
    preferences_path='logs/configurations/hood_control.ini'
if os.name == 'posix':
    preferences_path='/home/pi/Pi-ro-safe/logs/configurations/hood_control.ini'

background_image=r'media/patrick-tomasso-GXXYkSwndP4-unsplash.jpg'
white_gradient=r'media/white_filter.png'
msg_icon_image=r'media/msg_icon.png'
language_image=r'media/higer_res_thick.png'
schedule_icon_image=r'media/schedule_icon.png'
trouble_icon=r'media/trouble icon_high_res.png'
trouble_icon_dull=r'media/trouble icon_dull_high_res.png'
logo=r'media/fs.png'
report_current=r'logs/sys_report/report.jpg'
report_original=r'logs/sys_report/original_report.jpg'
qr_link =r'media/frame.png'
add_device_icon=r'media/icons8-edit-64.png'
add_device_down=r'media/icons8-edit-64_down.png'
delete_normal=r'media/delete_normal.png'
delete_down=r'media/delete_down.png'
reset_valve=r'media/redo.png'
gray_seperator_line=r'media/line_gray.png'
gray_seperator_line_vertical=r'media/line_gray_vertical.png'
black_seperator_line=r'media/line_black.png'
settings_icon=r'media/menu_lines.png'
menu_lines_vertical=r'media/menu_lines_vertical.png'
red_dot=r'media/red_dot.png'
opaque_bubble=r'media/opaque_bubble.png'
uid_qr=r'logs/configurations/uid_qr.png'
app_icon_source=r'media/app_icon.png'
square_bubble=r'media/square_bubble_.png'
hc_mockup=r'media/hc_admin_mockup.png'
store_badges=r'media/store_badges.png'
visible_black=r'media/visible_black.png'
hidden_black=r'media/hidden_black.png'
slider_handle_yellow=r'media/slider_handle_yellow.png'
overlay_x_icon=r'media/popup_x_white.png'
overlay_x_icon_black=r'media/popup_x.png'
add_schedule_icon=r'media/add_icon.png'
edit_schedule_icon=r'media/edit_icon.png'

#<<<<<<<<<< CUSTOM WIDGETS >>>>>>>>>>#

class AutoWrapTextInput(TextInput):
    '''A multiline `TextInput` that unfocuses with the 'enter' key'''

    def __init__(self, **kwargs):
        super(AutoWrapTextInput,self).__init__(**kwargs)

    def _key_down(self, key, repeat=False):
        if key[2] == 'enter':
            self.focus=False
            return
        return super(AutoWrapTextInput,self)._key_down(key, repeat)

class RoundedButton(Button):
    def __init__(self,**kwargs):
        super(RoundedButton,self).__init__(**kwargs)
        self.bg_color=kwargs.get("background_color",palette('base'))
        self.background_color = (self.bg_color[0], self.bg_color[1], self.bg_color[2], 0)  # Invisible background color to regular button

        with self.canvas.before:
            if self.background_down=="":
                self.shape_color = Color(self.bg_color[0]*.5, self.bg_color[1]*.5, self.bg_color[2]*.5, self.bg_color[3])
            else:
                self.shape_color = Color(self.bg_color[0], self.bg_color[1], self.bg_color[2], self.bg_color[3])

            self.shape = RoundedRectangle(pos=self.pos, size=self.size, radius=[20])
            self.bind(pos=self.update_shape, size=self.update_shape,state=self.color_swap)

    def update_shape(self, *args):
        self.shape.pos = self.pos
        self.shape.size = self.size
    def color_swap(self,*args):
        if self.state=="normal":
            if self.background_normal=="":
                self.shape_color.rgba = self.bg_color[0], self.bg_color[1], self.bg_color[2], self.bg_color[3]
            else:
                self.shape_color.rgba = self.bg_color[0]*.5, self.bg_color[1]*.5, self.bg_color[2]*.5, self.bg_color[3]
        if self.state=="down":
            if self.background_down=="":
                self.shape_color.rgba = self.bg_color[0], self.bg_color[1], self.bg_color[2], self.bg_color[3]
            else:
                self.shape_color.rgba = self.bg_color[0]*.5, self.bg_color[1]*.5, self.bg_color[2]*.5, self.bg_color[3]

class PauseTouch(Widget):
    '''widget that intercepts all touch events.

    timeout is how long touch will be intercepted for; defaults to 1 second.
    If timeout is set to 0 or less, touch will be intercepted until `unpause` is called.

    WARNING: do not add this widget to any other widgets. It will be added to the `Window`
    instance automatically.

    example usage:

    PauseTouch(3)

    will intercept all touch events for 3 seconds.
    '''

    def __init__(self,timeout=1, **kwargs):
        super(PauseTouch,self).__init__(**kwargs)
        Window.add_widget(self)
        if timeout >0:
            Clock.schedule_once(self.unpause,timeout)

    def unpause(self,*args):
        if self in Window.children:
            Window.remove_widget(self)

    def on_touch_down(self, touch):
        return True

class CirclePulseEmit(Widget):

    radius=NumericProperty(0)
    color=ListProperty([0,0,0,0])

    def __init__(self,quantity=1,style='slow_pulse', **kwargs):
        super(CirclePulseEmit,self).__init__(**kwargs)
        self.quantity=quantity+1
        self.style=style
        with self.canvas:
            self.circ_color=Color(*palette('dark_shade'))
            self.circle=Line(circle=(150, 150,0),width=1)

    def emit(self,*args):
        if self.quantity<1:
            self.clear()
            return
        self.quantity-=1
        if self.style=='slow_pulse':
            pulse_anim=Animation(radius=max(self.width,self.height),d=1.25)
        elif self.style=='quick':
            self.circ_color.rgba=palette('dark_shade',1)
            pulse_anim=Animation(radius=max(self.width,self.height)*.4,d=.225,t='in_out_quint')
        pulse_anim.bind(on_complete=self.reset_props)
        pulse_anim.start(self)
        fade_anim=Animation(color=[0,0,0,0],d=1.25,t='in_quad')
        fade_anim.start(self)

    def reset_props(self,*args):
        self.radius=0
        self.color=[0,0,0,1]
        self.circle.width=.5
        self.emit()

    def on_radius(self,*args):
        self.circle.circle=(self.center_x,self.center_y,self.radius)

    def on_color(self,*args):
        self.circ_color.rgba=(self.color)

    def align(self,*args):
        self.center=self.parent.center
        self.size=self.parent.size

    def on_parent(self,*args):
        parent=self.parent
        if not parent:
            return
        self.center=parent.center
        parent.bind(size=self.align)
        parent.bind(pos=self.align)
        if hasattr(parent,'widgets'):
            parent.widgets['circle_pulse_emit']=self
        self.emit()

    def clear(self,*args):
        parent=self.parent
        if not parent:
            return
        parent.unbind(size=self.align,pos=self.align)
        if hasattr(parent,'widgets'):
            if 'circle_pulse_emit' in parent.widgets:
                del parent.widgets['circle_pulse_emit']
        parent.remove_widget(self)

class MarkupSpinnerOption(SpinnerOption):
    def __init__(self, **kwargs):
        kwargs['markup']=True
        super(MarkupSpinnerOption,self).__init__(**kwargs)

class MarkupSpinner(Spinner):
    def __init__(self, **kwargs):
        super(MarkupSpinner,self).__init__(**kwargs)
        self.option_cls = MarkupSpinnerOption
        self.option_cls.option_color=self.background_color

    def _update_dropdown(self, *largs):
        super(MarkupSpinner,self)._update_dropdown(*largs)
        for i in self._dropdown.children[0].children:
            i.background_color=self.background_color
            i.background_color[3]=.99

class PinPop(Popup):
    def __init__(self,name, **kwargs):
        super().__init__(size_hint=(.8, .8),
        background = 'atlas://data/images/defaulttheme/button',
        title=current_language[f'{name}_overlay'],
        title_color=[0, 0, 0, 1],
        title_size='38',
        title_align='center',
        separator_color=palette('primary',.5),
        **kwargs)
        self.widgets={}
        self.overlay_layout=FloatLayout()
        self.add_widget(self.overlay_layout)

class ScatterImage(Image,Scatter):

    def reset(self):
        self.transform= Matrix().scale(1, 1, 1)

    def on_transform_with_touch(self,touch):
        if self.scale<1:
            return
        return super(ScatterImage, self).on_transform_with_touch(touch)

    def on_touch_up(self, touch):
        self.reset()
        return super(ScatterImage, self).on_touch_up(touch)

class OutlineScroll(ScrollView):
    def __init__(self,bg_color=palette('dark_shade',1), **kwargs):
        super(OutlineScroll,self).__init__(**kwargs)
        self.bind(pos=self.update_rect)
        self.bind(size=self.update_rect)
        with self.canvas.before:
                    Color(*bg_color)
                    self.rect = Rectangle(pos=self.center,size=(self.width,self.height))
    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = (self.size[0], self.size[1])

class OutlineAutoScroll(ScrollView):
    def __init__(self,bg_color=palette('dark_shade',1), **kwargs):
        super(OutlineAutoScroll,self).__init__(**kwargs)
        if os.name=='nt':
            self.scroll_speed=10
        else:self.scroll_speed=.01
        self.auto=False
        self.bind(pos=self.update_rect)
        self.bind(size=self.update_rect)
        with self.canvas.before:
                    Color(*bg_color)
                    self.rect = Rectangle(pos=self.center,size=(self.width,self.height))
    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = (self.size[0], self.size[1])

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            touch.grab(self)
        return super(OutlineAutoScroll, self).on_touch_down(touch)

    def on_touch_up(self, touch):
        if touch.grab_current is self:
            touch.ungrab(self)
            self.auto=False
        return super(OutlineAutoScroll, self).on_touch_up(touch)

    def on_touch_move(self, touch):
        if not self.auto:
            return super(OutlineAutoScroll, self).on_touch_move(touch)
        if self.height>=self.viewport_size[1]:
            return super(OutlineAutoScroll, self).on_touch_move(touch)
        if touch.grab_current is self:
            if touch.pos[1]>self.y+self.height*.85:
                if self.scroll_y<1.1:
                    self.scroll_y+=self.convert_distance_to_scroll(dx=0,dy=self.scroll_speed)[1]
            elif touch.pos[1]<self.y+self.height*.15:
                if self.scroll_y>-.1:
                    self.scroll_y-=self.convert_distance_to_scroll(dx=0,dy=self.scroll_speed)[1]
        return super(OutlineAutoScroll, self).on_touch_move(touch)

class IconButton(ButtonBehavior, Image):
    #uncomment block of code to see hit boxes for your button

    # def __init__(self, **kwargs):
    #     super(IconButton,self).__init__(**kwargs)
    #     with self.canvas.before:
    #             self.colour = Color(*palette('dark_shade',1))
    #             self.rect = Rectangle(size=self.size, pos=self.pos)
    #     self.bind(size=self._update_rect, pos=self._update_rect)

    # def _update_rect(self, instance, *args):
    #     self.rect.pos = instance.pos
    #     self.rect.size = instance.size
    pass

class ServicesStackLayout(StackLayout):
    def __init__(self, **kwargs):
        super(ServicesStackLayout,self).__init__(**kwargs)
        self.blocking_touch=False
        self.flicker_anim=Animation(opacity=.2,d=.75,t='in_quad')+Animation(opacity=1,d=.75,t='out_quad')
        self.fade_in=Animation(opacity=1,d=1.5,t='in_quad')
        self.fade_out=Animation(opacity=0,d=1.5,t='in_quad')

    @property
    def sub_children(self):
        l=[]
        for child in self.children:
            for _sub_child in child.children:
                l.append(_sub_child)
        return l

    def add_widget(self, widget,load=False,index=0):
        layout=FloatLayout(
            size=widget.size,
            size_hint=(None,None))
        title=Label(
            markup=True,
            pos_hint={'center_x':.5,"top":0},
            text='[size=14][color=#000000][b]'+widget.data['title'],
            halign='center',
            size_hint_y=None)
        title.bind(width=lambda *x: title.setter('text_size')(title, (title.width, None)))
        title.bind(texture_size=lambda *x: title.setter('height')(title, title.texture_size[1]))
        layout.add_widget(widget)
        layout.add_widget(title)
        if load:
            return super(ServicesStackLayout,self).add_widget(layout,index)
        pause=PauseTouch(0)
        amnt=len(self.children)
        widget.opacity=0
        if 9>amnt>2:
            for _index,i in enumerate(reversed(self.children),1):
                anim=Animation(opacity=1,d=_index*.1)
                anim.start(i)
                anim.bind(on_complete=lambda *args,i=i: self.flicker_anim.start(i))
            fade=Animation(opacity=1,d=(amnt*.1)+1.5,t='in_quad')
            fade.start(widget)
            fade.bind(on_complete=pause.unpause)
            return super(ServicesStackLayout,self).add_widget(layout,index)
        elif 17>amnt>8:
            for _index,i in enumerate(reversed(self.children),1):
                anim=Animation(opacity=1,d=_index*.05)
                anim.start(i)
                anim.bind(on_complete=lambda *args,i=i: self.flicker_anim.start(i))
            fade=Animation(opacity=1,d=(amnt*.05)+1.5,t='in_quad')
            fade.start(widget)
            fade.bind(on_complete=pause.unpause)
            return super(ServicesStackLayout,self).add_widget(layout,index)
        elif amnt>2:
            for _index,i in enumerate(reversed(self.children),1):
                anim=Animation(opacity=1,d=_index*.025)
                anim.start(i)
                anim.bind(on_complete=lambda *args,i=i: self.flicker_anim.start(i))
            fade=Animation(opacity=1,d=(amnt*.025)+1.5,t='in_quad')
            fade.start(widget)
            fade.bind(on_complete=pause.unpause)
            return super(ServicesStackLayout,self).add_widget(layout,index)
        self.fade_in.start(widget)
        self.fade_in.bind(on_complete=pause.unpause)
        return super(ServicesStackLayout,self).add_widget(layout,index)

    def remove_widget(self, widget,unload=False):
        if unload:
            self._remove_widget(widget)
            return
        pause=PauseTouch(1.5)
        self.fade_out.start(widget)
        Clock.schedule_once(lambda *args:self._remove_widget(widget),1.5)

    def _remove_widget(self,widget,*args):
        super(ServicesStackLayout,self).remove_widget(widget.parent)
        widget.parent.remove_widget(widget)

    def clear_widgets(self, children=None,unload=False):
        if children is None or children is self.children:
            children = self.children[:]
        remove_widget = self._remove_widget if unload else self.remove_widget
        for child in self.sub_children:
            remove_widget(child)

class DraggableRoundedButton(DragBehavior,Button):
    def _do_touch_up(self, touch, *largs):
        return super(DragBehavior, self)._do_touch_up(self, touch, *largs)

class RoundedToggleButton(ToggleButton):
    '''`RoundedToggleButton` has two key differences from `ToggleButton`
    
     1- `RoundedToggleButton` stores background_color as `self.bg_color`;
     it uses this to keep its round shape colored correctly.
     
     2- `RoundedToggleButton` toggles on_release.
     this is accomplisehed by overwriting these methods:

    `def _do_press(self):`
        pass

    `def _do_release(self, *args):`
        if (not self.allow_no_selection and
                self.group and self.state == 'down'):
            return

        self._release_group(self)
        self.state = 'normal' if self.state == 'down' else 'down'
    '''

    def __init__(self,**kwargs):
        if 'second_color' in kwargs:
            self.second_color=kwargs.pop('second_color')
        else:self.second_color=None
        super(RoundedToggleButton,self).__init__(**kwargs)
        self.bg_color=kwargs["background_color"]
        self.background_color = (self.bg_color[0], self.bg_color[1], self.bg_color[2], 0)  # Invisible background color to regular button

        with self.canvas.before:
            if self.background_normal=="":
                self.shape_color = Color(self.bg_color[0], self.bg_color[1], self.bg_color[2], self.bg_color[3])
            if self.background_down=="":
                if self.second_color:
                    self.shape_color = Color(*self.second_color)
                else:
                    self.shape_color = Color(self.bg_color[0]*.5, self.bg_color[1]*.5, self.bg_color[2]*.5, self.bg_color[3])
            self.shape = RoundedRectangle(pos=self.pos, size=self.size, radius=[20])
            self.bind(pos=self.update_shape, size=self.update_shape)
        self.bind(state=self.color_swap)
    def update_shape(self, *args):
        self.shape.pos = self.pos
        self.shape.size = self.size
    def color_swap(self,*args):
        if self.state=="normal":
            if self.background_normal=="":
                self.shape_color.rgba = self.bg_color[0], self.bg_color[1], self.bg_color[2], self.bg_color[3]
            else:
                if self.second_color:
                    self.shape_color.rgba = self.second_color[0],self.second_color[1],self.second_color[2],self.second_color[3]
                else:
                    self.shape_color.rgba = self.bg_color[0]*.5, self.bg_color[1]*.5, self.bg_color[2]*.5, self.bg_color[3]
        if self.state=="down":
            if self.background_down=="":
                self.shape_color.rgba = self.bg_color[0], self.bg_color[1], self.bg_color[2], self.bg_color[3]
            else:
                if self.second_color:
                    self.shape_color.rgba = self.second_color[0],self.second_color[1],self.second_color[2],self.second_color[3]
                else:
                    self.shape_color.rgba = self.bg_color[0]*.5, self.bg_color[1]*.5, self.bg_color[2]*.5, self.bg_color[3]

    def _do_press(self):
        pass

    def _do_release(self, *args):
        if (not self.allow_no_selection and
                self.group and self.state == 'down'):
            return

        self._release_group(self)
        self.state = 'normal' if self.state == 'down' else 'down'

class LayoutButton(FloatLayout,RoundedButton):
    pass

class trouble_template(Button):
    def __init__(self,trouble_tag,trouble_text='',link_text=None,ref_tag=None, **kwargs):
        self.trouble_tag=trouble_tag
        self.trouble_text=trouble_text
        self.link_text=link_text
        self.ref_tag=ref_tag
        if link_text == None:
            link_text=''
        else:
            link_text='\n'+str(current_language[link_text])
        if trouble_text!='':
            trouble_text=current_language[trouble_text]
        super().__init__(text=f'''[size=24][b]{current_language[trouble_tag]}[/b][/size]
        [size=18][i]{trouble_text}[/i][/size][size=30][color=#de2500][i][ref={ref_tag}]{link_text}[/ref][/i][/color][/size]''',
        markup=True,
        size_hint_y=None,
        size_hint_x=1,
        color = palette('dark_shade',1),
        background_down='',
        background_normal='',
        background_color=palette('primary',.85),
        **kwargs)
        
        self.bind(pos=self.update_rect)
        self.bind(size=self.update_rect)
        self.bind(state=self.color_swap)
        with self.canvas.before:
            Color(*palette('primary',.85))
            self.rect = Rectangle(pos=self.center,size=(self.width,self.height))
    def color_swap(self,*args):
        if self.state=="normal":
            self.background_color=palette('primary',.85)
        if self.state=="down":
            self.background_color=((250/255)*.5, (220/255)*.5, (42/255)*.5,(.85)*.5)
    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = (self.size[0], self.size[1])
    def translate(self,current_language):
        try:
            if self.link_text == None:
                link_text=''
            else:
                link_text='\n'+str(current_language[self.link_text])
            if self.trouble_text!='':
                trouble_text=current_language[self.trouble_text]
            else:
                trouble_text=''
            self.text=f'''[size=24][b]{current_language[self.trouble_tag]}[/b][/size]
            [size=18][i]{trouble_text}[/i][/size][size=30][color=#de2500][i][ref={self.ref_tag}]{link_text}[/ref][/i][/color][/size]'''
        except KeyError:
                    logger.exception(f'main.py CLASS=trouble_template translate():  {self} has no entry in selected lanuage dict')

class ScrollItemTemplate(Button):
    def __init__(self,Item_tag,Item_text='',link_text=None,ref_tag=None,color=palette('primary',.85),**kwargs):
        if link_text == None:
            link_text=''
        else:
            link_text='\n'+str(link_text)
        super().__init__(text=f'''[size=24][b]{Item_tag}[/b][/size]
        [size=18][i]{Item_text}[/i][/size][size=30][color=#de2500][i][ref={ref_tag}]{link_text}[/ref][/i][/color][/size]''',
        markup=True,
        size_hint_y=None,
        size_hint_x=1,
        color = palette('dark_shade',1),
        **kwargs)
        self.bind(pos=self.update_rect)
        self.bind(size=self.update_rect)
        with self.canvas.before:
            Color(color[0],color[1],color[2],color[3])
            self.rect = Rectangle(pos=self.center,size=(self.width,self.height))
    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = (self.size[0], self.size[1])

class RoundedScrollItemTemplate(RoundedButton): 
    def __init__(self,Item_tag,color=palette('primary',.85),**kwargs):
        if color==palette('primary',.9):
            text_color= '#000000'
        else:
            text_color= '#ffffff'
        super(RoundedScrollItemTemplate,self).__init__(text=f'''[color={text_color}][size=24][b]{Item_tag}[/b][/size][/color]''',
        markup=True,
        size_hint_y=None,
        size_hint_x=1,
        background_down='',
        background_color=color,
        **kwargs)

class DisplayLabel(Label):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(pos=self.update_rect)
        self.bind(size=self.update_rect)
        with self.canvas.before:
                    Color(*palette('light_tint',1))
                    self.rect = Rectangle(pos=self.center,size=(self.width,self.height))
    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = (self.size[0], self.size[1])
    def update_text(self,text,*args):
        self.text=f'[size=25][color=#000000]{text}[/color][/size]'

class ExactLabel(Label):
    def __init__(self,label_color=palette('dark_shade',0), **kwargs):
        super().__init__(**kwargs)
        self.size_hint=(None,None)
        with self.canvas.before:
                    Color(label_color[0],label_color[1],label_color[2],label_color[3])
                    self.rect = Rectangle(pos=self.center,size=(self.width,self.height))
        self.bind(pos=self.update_rect)
        self.bind(size=self.update_rect)
        Clock.schedule_once(self.align_to_parent)

    def align_to_parent(self,*args):
        if self.parent:
            self.size=self.parent.size
    def update_rect(self, *args):
        self.size=self.texture_size
        self.rect.pos = self.pos
        self.rect.size = (self.texture_size[0], self.texture_size[1])

class MinimumBoundingLabel(Label):
    def __init__(self, **kwargs):
        super(MinimumBoundingLabel,self).__init__(**kwargs)
        self.size_hint=(None,None)
    #uncomment to see bounding boxes
    #     with self.canvas.before:
    #         self.colour = Color(*palette('dark_shade',1))
    #         self.rect = Rectangle(size=self.size, pos=self.pos)

    #     self.bg_color=palette('dark_shade',1)
    #     self.bind(size=self._update_rect, pos=self._update_rect)

    # def _update_rect(self, instance, *args):
    #     self.rect.pos = instance.pos
    #     self.rect.size = instance.size

    # def on_bg_color(self, *args):
    #     self.colour.rgb=self.bg_color

    def on_texture_size(self,*args):
        self.size=self.texture_size

class EventpassGridLayout(GridLayout):
    pass

class ColorProgressBar(ProgressBar):
    def __init__(self, **kwargs):
        super(ColorProgressBar).__init__(**kwargs)

        with self.canvas.before:
            self.background=BorderImage

class BoxLayoutColor(BoxLayout):
    def __init__(self, **kwargs):
        super(BoxLayoutColor,self).__init__(**kwargs)

        with self.canvas.before:
                Color(*palette('dark_shade',.95))
                self.rect = Rectangle(size=self.size, pos=self.pos)

        self.bind(size=self._update_rect, pos=self._update_rect)

    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size

class RelativeLayoutColor(RelativeLayout):
    def __init__(self,bg_color= palette('secondary',.95),**kwargs):
        super(RelativeLayoutColor,self).__init__(**kwargs)
        self.bg_color=bg_color

        with self.canvas.before:
            self.colour=Color(*bg_color)
            self.rect = Rectangle(size=self.size, pos=self.pos)

        self.bind(size=self._update_rect, pos=self._update_rect)

    def _update_rect(self, instance, *args):
        self.rect.pos = instance.pos
        self.rect.size = instance.size

class LabelColor(Label):
    bg_color=ColorProperty()
    def __init__(self,bg_color= palette('secondary',.95),**kwargs):
        super(LabelColor,self).__init__(**kwargs)

        with self.canvas.before:
            self.colour = Color(*bg_color)
            self.rect = Rectangle(size=self.size, pos=self.pos)

        self.bg_color=bg_color
        self.bind(size=self._update_rect, pos=self._update_rect)

    def _update_rect(self, instance, *args):
        self.rect.pos = instance.pos
        self.rect.size = instance.size

    def on_bg_color(self, *args):
        self.colour.rgb=self.bg_color

    @property
    def alpha_value(self):
        return self.colour.rgba[3]
    @alpha_value.setter
    def alpha_value(self,value):
        self.colour.rgba[3]=value

class RoundedLabelColor(Label):
    bg_color=ColorProperty()
    def __init__(self,bg_color= palette('secondary',.95),**kwargs):
        super(RoundedLabelColor,self).__init__(**kwargs)
        self.bg_color=bg_color


        with self.canvas.before:
            self.shape_color = Color(*self.bg_color)
            self.shape = RoundedRectangle(pos=self.pos, size=self.size, radius=[20])
            self.bind(pos=self.update_shape, size=self.update_shape)

    def update_shape(self, *args):
        self.shape.pos = self.pos
        self.shape.size = self.size

    def on_bg_color(self, *args):
        #before __init__ is called the bg_color changes, so we wait untill __init__() to proceed
        if hasattr(self,'shape_color'):
            self.shape_color.rgba=self.bg_color

class ImageGhost(Image):
        def __init__(self,touch, **kwargs):
            super(ImageGhost,self).__init__(**kwargs)
            self.screen=App.get_running_app().context_screen.get_screen('network')
            self.opacity=.85
            self.bind(texture=self._on_texture_)
            self.size_hint=(None,None)

        def _on_texture_(self,img,texture,*args):
            self.texture.flip_vertical()
            self.size=self.texture_size

        def on_touch_up(self, touch):
            if touch.grab_current is self:
                touch.ungrab(self)
                if self.parent:
                    self.parent.remove_widget(self)
            return super(ImageGhost, self).on_touch_up(touch)

        def on_touch_move(self, touch):
            if touch.grab_current is self:
                self.center=touch.pos
                if not self.parent:
                    self.screen.widgets['side_bar_auto_status_scroll'].auto=True
                    self.screen.add_widget(self)
            return super(ImageGhost, self).on_touch_move(touch)

class DraggableRoundedLabelColor(RoundedLabelColor):
    '''for use in single column gridlayouts in scrollviews'''

    def __init__(self,index, **kwargs):
        self.index=index
        self._new_move=True
        self.drop_points=[]
        if 'func' in kwargs:
            self.func=kwargs.pop('func')
        else:self.func=None
        super(DraggableRoundedLabelColor, self).__init__(**kwargs)
        self.pluck=Animation(size_hint_x=.275,d=.035,t='out_back')
        self.plant=Animation(size_hint_x=1,d=.035,t='in_quad')
        self.plant&=Animation(height=40,d=.035,t='in_quad')

    def _avatar(self,touch,*args):
        image=self.export_as_image(flip_vertical=False)
        avatar=ImageGhost(touch)
        avatar.texture=image.texture
        touch.grab(avatar)
        return avatar

    def add_drop_points(self,*args):
        self.drop_points=[]
        layout=self.parent
        self.btns=btns=layout.children
        index=0
        for point in range(len(btns)+1):
            if point==self.index or point==self.index+1:
                continue
            drop_point=Label(
                size_hint_y=None,
                height=1)
            self.drop_points.append(drop_point)
            layout.add_widget(drop_point, index=point+index)
            layout.rows_minimum[index]=0
            index+=1

    def remove_drop_points(self,layout,*args):
        for i in layout.children:
            if isinstance(i,DraggableRoundedLabelColor):
                continue
            layout.remove_widget(i)
        self.drop_points=[]

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            self.bg_color=palette('highlight')
            touch.grab(self)
            self.avatar=self._avatar(touch)
        return super(DraggableRoundedLabelColor, self).on_touch_down(touch)

    def on_touch_up(self, touch):
        if touch.grab_current is self:
            for dp in self.drop_points:
                if self._collide_with(dp):
                    self.set_index(dp)
            self.remove_drop_points(self.parent)
            self._new_move=True
            self.bg_color=palette('secondary',1)
            self.opacity=1
            touch.ungrab(self)

        return super(DraggableRoundedLabelColor, self).on_touch_up(touch)

    def on_touch_move(self, touch):
        if touch.grab_current is self:
            if self._new_move:
                self._new_move=False
                self.opacity=0
                self.add_drop_points()
        return super(DraggableRoundedLabelColor, self).on_touch_move(touch)

    def set_index(self,point,*args):
        p=self.parent
        p.remove_widget(self)
        for index,btn in enumerate(p.children):
            if point==btn:
                insert_index=index
        p.add_widget(self,index=insert_index)
        self.remove_drop_points(p)
        for index,profile in enumerate(self.parent.children):
                profile.text=profile.text[12:]
                network.set_profile_priority(profile.text,index)
        App.get_running_app().context_screen.get_screen('network').get_auto_networks()

    def _collide_with(self,wid):
        avatar=self.avatar
        transformed_pos=wid.to_window(*wid.pos)
        tx=transformed_pos[0]
        ty=transformed_pos[1]
        if avatar.right < tx:
            return False
        if avatar.x > tx+wid.width:
            return False
        if avatar.top < ty:
            return False
        if avatar.y > ty+wid.height:
            return False
        return True

class RoundedColorLayout(FloatLayout):
    bg_color=ColorProperty()
    def __init__(self,bg_color= palette('secondary',.95),**kwargs):
        super(RoundedColorLayout,self).__init__(**kwargs)
        self.bg_color=bg_color

        with self.canvas:#.before:
            self.shape_color = Color(*self.bg_color)
            self.shape = RoundedRectangle(pos=self.pos, size=self.size, radius=[20])
            self.bind(pos=self.update_shape, size=self.update_shape)

    def update_shape(self, *args):
        self.shape.pos = self.pos
        self.shape.size = self.size

class RoundedColorLayoutButton(ButtonBehavior,RoundedColorLayout):
    def __init__(self, bg_color=palette('secondary', 0.95), **kwargs):
        super(RoundedColorLayoutButton,self).__init__(bg_color=bg_color, **kwargs)

class RoundedColorLayoutModal(FloatLayout):
    bg_color=ColorProperty()
    def __init__(self,bg_color= palette('secondary',.95),**kwargs):
        super(RoundedColorLayoutModal,self).__init__(**kwargs)
        self.bg_color=bg_color

        with self.canvas:
            self.shape_color = Color(*self.bg_color)
            self.shape = RoundedRectangle(pos=self.pos, size=self.size, radius=[20])
            self.bind(pos=self.update_shape, size=self.update_shape)

    def update_shape(self, *args):
        self.shape.pos = self.pos
        self.shape.size = self.size

class ExpandableRoundedColorLayout(ButtonBehavior,RoundedColorLayout):

    expanded=BooleanProperty(defaultvalue=False)
    animating=BooleanProperty(defaultvalue=False)

    def __init__(self,**kwargs):
        self._expanded=False
        self.original_pos=kwargs['pos_hint']
        self.original_size=kwargs['size_hint']
        if 'locked' in kwargs:
            self.locked=self._lock_callback=kwargs.pop('locked')
        if 'expanded_pos' in kwargs:
            self.expanded_pos=kwargs.pop('expanded_pos')
        if 'expanded_size' in kwargs:
            self.expanded_size=kwargs.pop('expanded_size')
        if 'modal_dim' in kwargs:
            self.modal_dim=kwargs.pop('modal_dim')
            Clock.schedule_once(self._set_modal_dim)
            self._apply_dim=Animation(rgba=self.modal_dim)
            self._remove_dim=Animation(rgba=palette('dark_shade',0),d=.2)
        self.move_anim=Animation(pos_hint=self.expanded_pos,d=.15,t='in_out_quad')
        self.move_anim.bind(on_complete=self.set_expanded_true)
        self.return_anim=Animation(pos_hint=self.original_pos,d=.15,t='out_back')
        self.return_anim.bind(on_complete=self.set_expanded_false)
        self.grow_anim=Animation(size_hint=self.expanded_size,d=.15,t='in_out_quad')
        self.grow_anim.bind(on_complete=self.set_expanded_true)
        self.shrink_anim=Animation(size_hint=self.original_size,d=.15,t='out_back')
        self.shrink_anim.bind(on_complete=self.set_expanded_false)
        super(ExpandableRoundedColorLayout,self).__init__(**kwargs)

    def lock(self,*args):
        self.locked=self._lock_callback

    def unlock(self,*args):
        if hasattr(self,'locked'):
            del self.locked

    def _set_modal_dim(self,*args):
        with self.canvas.before:
            self._dim=Color(*palette('dark_shade',0))
            self._dim_rect=Rectangle(size=Window.size)

    def on_touch_down(self, touch):
        if not self._expanded:
            pass
        elif not self.collide_point(*touch.pos):
            self.shrink()
            super(ExpandableRoundedColorLayout,self).on_touch_down(touch)
            return True
        return super(ExpandableRoundedColorLayout,self).on_touch_down(touch)

    def on_release(self,*args):
        if hasattr(self,'locked'):
            self.locked(self.expand)
            return
        self.expand()

    def shrink(self,*args):
        if self._expanded:
            Animation.stop_all(self)
            self.animating=not self.animating
            self._expanded=False
            self.shrink_anim.start(self)
            self.return_anim.start(self)

    def expand(self,*args):
        if not self._expanded:
            Animation.stop_all(self)
            self.animating=not self.animating
            parent=self.parent
            parent.remove_widget(self)
            parent.add_widget(self)
            self._expanded=True
            if hasattr(self,'expanded_size'):
                self.grow_anim.start(self)
            if hasattr(self, 'expanded_pos'):
                self.move_anim.start(self)

    def set_expanded_true(self,*args):
        self.expanded=True
        if hasattr(self,'modal_dim'):
            self._remove_dim.cancel_all(self._dim)
            self._apply_dim.start(self._dim)
            self._dim_rect.size=Window.size

    def set_expanded_false(self,*args):
        self.expanded=False
        if hasattr(self,'modal_dim'):
            self._apply_dim.cancel_all(self._dim)
            self._remove_dim.start(self._dim)

class AnalyticExpandable(ExpandableRoundedColorLayout):
    def __init__(self, **kwargs):
        super(AnalyticExpandable,self).__init__(**kwargs)

    def on_touch_down(self, touch):
        if not self._expanded:
            pass
        return ButtonBehavior.on_touch_down(self,touch)

class ClockText(ButtonBehavior,LabelColor):
    def __init__(self, **kwargs):
        super(ClockText,self).__init__(**kwargs)
        self.clock_stack={}
        self.anim_length=.5
        self.animated=False
        self.angle=0
        self.anim_lngth=1
        self.time_size=120
        with self.canvas.before:
            PushMatrix()
            self.rotation = Rotate(angle=self.angle, origin=self.center)
        with self.canvas.after:
            PopMatrix()
        self.blink_bool=True
        self.bind(on_release=self.animate)
        self.bind(center=self._update)
        self.bind(font_size=self._update)

    def animate(self,*args):
        if self.opacity!=1:
            return
        if self.animated:
            if self.time_size==35:
                self._delete_clock()
                self.animated=False
                self.unrotate()
                self.unslide()
                self.text_unshrink()
                self.unmorph()
        else:
            if self.time_size==120:
                self._create_clock()
                self.animated=True
                self.rotate()
                self.slide()
                self.text_shrink()
                self.morph()

    def _return(self,*args):
        if self.opacity==0:
            self.fade_in()
            App.get_running_app().context_screen.get_screen('main').widgets['widget_carousel'].fade_out()
        if self.time_size==35:
            self.animated=False
            self.unrotate()
            self.unslide()
            self.text_unshrink()
            self.unmorph()
            App.get_running_app().context_screen.get_screen('main').widgets['widget_carousel'].fade_out()

    def _bounce(self,*args):
        wc=App.get_running_app().context_screen.get_screen('main').widgets['widget_carousel']
        if wc.skip_bounce:
            wc.skip_bounce=False
            return
        wc.bounce()

    def _create_clock(self,*args):
        Clock.schedule_once(self._return,10)
        self.clock_stack['event'] = self._return
        Clock.schedule_once(self._bounce,4)
        self.clock_stack['bounce'] = self._bounce

    def _delete_clock(self,*args):
        if 'event' in self.clock_stack:
            Clock.unschedule(self.clock_stack['event'])
        if 'bounce' in self.clock_stack:
            Clock.unschedule(self.clock_stack['bounce'])

    def morph(self):
        anim=Animation(size_hint=(.05,.255),duration=self.anim_lngth/2)
        anim.start(self)
    def unmorph(self):
        anim=Animation(size_hint=(.475,.22),duration=self.anim_lngth/2,t='in_quad')
        anim.start(self)

    def text_shrink(self):
        anim=Animation(time_size=35,duration=self.anim_lngth/2)
        anim.start(self)
    def text_unshrink(self):
        anim=Animation(time_size=120,duration=self.anim_lngth/2)
        anim.start(self)

    def slide(self):
        anim=Animation(pos_hint={'center_x':.05,'center_y':.265},duration=self.anim_lngth/2)
        anim.start(self)
    def unslide(self):
        anim=Animation(pos_hint={'center_x':.5,'center_y':.265},duration=self.anim_lngth/2)
        anim.start(self)

    def rotate(self):
        anim=Animation(angle=-90,duration=self.anim_lngth/2,t='in_quad')
        anim.start(self.rotation)
    def unrotate(self):
        anim=Animation(angle=0,duration=self.anim_lngth/2,t='in_quad')
        anim.start(self.rotation)

    def blink(self):
        self.blink_bool=not self.blink_bool
        if self.blink_bool:
            return '[color=#909090]:[/color]'
        return ':'

    def fade(self,*args):
        if self.opacity==0:
            self.fade_in()
        elif self.opacity==1:
            self.fade_out()

    def fade_in(self,*args):
        self.add_parent()
        anim=Animation(opacity=1,d=self.anim_length)
        anim.start(self)

    def fade_out(self):
        anim=Animation(opacity=0,d=self.anim_length)
        anim.bind(on_complete=partial(self.rm_parent,instance=self))
        anim.start(self)

    def rm_parent(*args,instance=None):
        if instance.parent:
            instance.parent.remove_widget(instance)

    def add_parent(self):
        if not self.parent:
            App.get_running_app().context_screen.get_screen('main').widgets['container'].add_widget(self)

    def _update(self,*args):
        self.rotation.origin=self.center
        self.update()

    def update(self, *args):
        #12hour + zero(0) padded decimal minute + am/pm
        self.text =f"[size={int(self.time_size)}][b][color=c0c0c0]{time.strftime('%I'+self.blink()+'%M'+' %p')}"

class Messenger(ButtonBehavior,FloatLayout,LabelColor):
    def __init__(self, **kwargs):
        super(Messenger,self).__init__(**kwargs)
        self.clock_stack={}
        self.widgets={}
        self.anim_d=.25
        self.place_holder=Label()
        self.bind(on_release=self.undock)
        self.docked=True

    def on_parent(self,_self,parent,*args):
        if parent:
            return
        wc=App.get_running_app().context_screen.get_screen('main').widgets['widget_carousel']
        wc.opacity=0

    def undock(self,*args):
        if self.size_hint==[1,1]:
            self.docked=False
            cg=App.get_running_app().context_screen.get_screen('main')
            cgw=cg.widgets
            cl=cgw['clock_label']
            msg=cgw['messenger_button']
            cl._delete_clock()
            self.size_hint =(.475,.22)
            self.pos_hint = {'center_x':.5, 'center_y':.265}
            self.switch_parent()
            self.expand()
            self.align_center()
            self.opaque()
            self.darken()
            msg.clear_widgets()

    def redock(self,*args):
        if self.pos_hint=={'center_x':.5,'center_y':.55}:
            cg=App.get_running_app().context_screen.get_screen('main')
            cgw=cg.widgets
            cl=cgw['clock_label']
            msg=cgw['messenger_button']
            if hasattr(self,'pop_wid_event'):
                self.pop_wid_event.cancel()
            self.contract()
            self.align_bottom()
            self.unopaque()
            self.lighten()
            msg.clear_widgets()
            cgw['message_label'].text=f'[size=50][color=#ffffff][b]{messages.active_messages[0].card}'
            cl._return()

    def switch_parent(self,*args):
        cg=App.get_running_app().context_screen.get_screen('main')
        cgw=cg.widgets
        cl=cgw['clock_label']
        msg=cgw['messenger_button']
        main_screen=App.get_running_app().context_screen.get_screen('main')
        widget_carousel=main_screen.widgets['widget_carousel']
        if self.parent==main_screen:
            if self.place_holder.parent:
                self.place_holder.parent.parent.remove_widget(self.place_holder)
            self.parent.remove_widget(self)
            widget_carousel.add_widget(self)
            widget_carousel.index=-1
            msg.add_widget(cgw['message_label'])
        elif self.parent.parent==widget_carousel:
            self.parent.parent.remove_widget(self)
            main_screen.add_widget(self)
            if not self.place_holder.parent:
                widget_carousel.add_widget(self.place_holder)
                widget_carousel.index=-1
        else:
            logger.debug('main.py Messenger switch_parent(): Messenger object has no parent')

    def expand(self,*args):
        anim=Animation(size_hint=(.9,.8),d=self.anim_d,t='in_back')
        anim.start(self)

    def contract(self,*args):
        anim=Animation(size_hint=(.475,.22),d=self.anim_d,t='in_back')
        anim.bind(on_complete=self.switch_parent)
        anim.start(self)

    def fill_slide(self,*args):
        self.size_hint =(1,1)
        self.pos_hint = {'center_x':.5, 'center_y':.5}

    def align_center(self,*args):
        anim=Animation(pos_hint={'center_x':.5,'center_y':.55},d=self.anim_d)
        anim.bind(on_complete=self.populate_widgets)
        anim.start(self)

    def align_bottom(self,*args):
        anim=Animation(pos_hint={'center_x':.5,'center_y':.265},d=self.anim_d,t='in_back')
        anim.bind(on_complete=self.fill_slide)
        anim.bind(on_complete=lambda *args:setattr(self,'docked',True))
        anim.start(self)

    def opaque(self,*args):
        anim=Animation(alpha_value=.85,d=self.anim_d)
        anim.start(self)

    def unopaque(self,*args):
        anim=Animation(alpha_value=.3,d=self.anim_d)
        anim.start(self)

    def darken(self,*args):
        anim=Animation(bg_color=[0,0,0,.85],d=self.anim_d)
        anim.start(self)

    def lighten(self,*args):
        anim=Animation(bg_color=[.7,.7,.7,.3],d=self.anim_d)
        anim.start(self)

    def populate_widgets(self,*args):
        self.clear_widgets()
        scroll_color=palette('base',.85)
        yellow=palette('primary',.9)

        cg=App.get_running_app().context_screen.get_screen('main')
        cgw=cg.widgets

        msg_back=RoundedButton(text=current_language['msg_back'],
            size_hint =(.4, .1),
            pos_hint = {'x':.06, 'y':.015},
            background_normal='',
            background_color=yellow,
            markup=True)
        self.widgets['msg_back']=msg_back
        msg_back.ref='msg_back'
        msg_back.bind(on_release=self.redock)

        msg_seperator_line=Image(
            source=gray_seperator_line,
            allow_stretch=True,
            keep_ratio=False,
            color=palette('base',1),
            size_hint =(.5, .001),
            pos_hint = {'x':.01, 'y':.87})
        self.widgets['msg_seperator_line']=msg_seperator_line

        message_title=Label(
            text=current_language['message_title'],
            markup=True,
            size_hint =(1,1),
            pos_hint = {'center_x':.25, 'center_y':.95})
        self.widgets['message_title']=message_title
        message_title.ref='message_title'

        msg_scroll=OutlineScroll(
            size_hint =(.4,.8),
            pos_hint = {'center_x':.75, 'center_y':.45},
            bg_color=scroll_color,
            bar_width=8,
            bar_color=yellow,
            do_scroll_y=True,
            do_scroll_x=False)

        scroll_layout = GridLayout(
            cols=1,
            spacing=10,
            size_hint_y=None,
            padding=5)
        # Make sure the height is such that there is something to scroll.
        scroll_layout.bind(minimum_height=scroll_layout.setter('height'))
        self.widgets['scroll_layout']=scroll_layout
        scroll_layout.widgets=[]
        for i in messages.active_messages:
            btn = RoundedButton(
                background_normal='',
                background_color=palette('secondary',1),
                text=i.name,
                size_hint_y=None,
                height=40)
            btn.bind(on_release=partial(self.load_selected_msg,i))
            scroll_layout.add_widget(btn)
            scroll_layout.widgets.append(btn)
            btn.message=i
            btn.widgets={}
            if not i.seen:
                btn.add_widget(NotificationBadge(rel_pos=(-.1,.8)))

        msg_scroll_title=LabelColor(
            bg_color=scroll_color,
            text=current_language['msg_scroll_title'],
            markup=True,
            size_hint =(.4,.1),
            pos_hint = {'center_x':.75, 'center_y':.9})
        self.widgets['msg_scroll_title']=msg_scroll_title
        msg_scroll_title.ref='msg_scroll_title'

        self.load_selected_msg(messages.active_messages[0])

        msg_scroll.add_widget(scroll_layout)

        self.add_widget(msg_back)
        self.add_widget(msg_seperator_line)
        self.add_widget(message_title)
        self.add_widget(msg_scroll)
        self.add_widget(msg_scroll_title)

    def load_selected_msg(self,message,*args):
        self.filter_badges()
        message.seen=True
        try:
            self.remove_widget(self.widgets['selected_msg_title'])
            self.remove_widget(self.widgets['selected_msg_body'])
            self.remove_widget(self.widgets['selected_msg_button'])
        except KeyError:
            pass
        selected_msg_title=Label(
            text=f'[size=26][color=#ffffff][b][i][u]{message.title}',
            markup=True,
            halign='center',
            size_hint =(.4,.1),
            pos_hint = {'center_x':.25, 'center_y':.8})
        self.widgets['selected_msg_title']=selected_msg_title
        selected_msg_title.ref='selected_msg_title'
        self.add_widget(selected_msg_title)

        selected_msg_body=Label(
            text=f'[size=20][color=#ffffff]{message.body}',
            markup=True,
            halign='center',
            size_hint =(.4,.1),
            pos_hint = {'center_x':.25, 'center_y':.5})
        self.widgets['selected_msg_body']=selected_msg_body
        selected_msg_body.ref='selected_msg_body'
        self.add_widget(selected_msg_body)

        if hasattr(message,'callbacks'):
            selected_msg_button=RoundedButton(
                text=f'[size=30][color=#000000][b]{message.name}',
                size_hint =(.4, .1),
                pos_hint = {'x':.06, 'y':.215},
                background_normal='',
                background_color=palette('base',.85),
                markup=True)
            self.widgets['selected_msg_button']=selected_msg_button
            for i in message.callbacks:
                selected_msg_button.bind(on_release=i)
            self.add_widget(selected_msg_button)

    def filter_badges(self,*args):
        for btn in self.widgets['scroll_layout'].widgets:
            if btn.message.seen:
                if 'notification_badge' in btn.widgets:
                    btn.widgets['notification_badge'].clear()

    def evoke(self,*args):
        cg=App.get_running_app().context_screen.get_screen('main')
        wc=cg.widgets['widget_carousel']
        cl=cg.widgets['clock_label']

        if cl.time_size!=120 or cl.opacity!=1:
            return
        if len(messages.active_messages)<2:
            return
        if not App.get_running_app().config_.getboolean('preferences','evoke'):
            return
        if messages.active_messages[0].gravity>=10\
            or random.randint(0,45)-messages.active_messages[0].gravity<=0:
                cg.widget_fade()
                cl.fade()
                self.evoke_fade_in_1=Clock.schedule_once(cg.widget_fade,5)
                self.clock_stack['widget_fade']=cg.widget_fade
                self.evoke_fade_in_2=Clock.schedule_once(cl.fade,5)
                self.clock_stack['fade']=cl.fade
                if wc.opacity==0:
                    cg.widgets['widget_carousel'].index=1

    def cancel_evoke_fade_in(self,*args):
        if hasattr(self,'self.evoke_fade_in_1'):
            self.evoke_fade_in_1.cancel()
        if hasattr(self,'self.evoke_fade_in_2'):
            self.evoke_fade_in_2.cancel()

    def schedule_refresh(self,*args):
        self.pop_wid_event=Clock.schedule_once(self.populate_widgets,1)

    def _delete_clock(self,*args):
        if 'widget_fade' in self.clock_stack:
            Clock.unschedule(self.clock_stack['widget_fade'])
        if 'fade' in self.clock_stack:
            Clock.unschedule(self.clock_stack['fade'])

    def on_touch_down(self, touch):
        self._delete_clock()
        if not self.pos_hint=={'center_x':.5,'center_y':.55}:
            pass
        elif not self.collide_point(*touch.pos):
            self.redock()
            super().on_touch_down(touch)
            return True
        return super().on_touch_down(touch)

class BigWheel(Carousel):
    def __init__(self,y_reduction=35, **kwargs):
        super(BigWheel,self).__init__(**kwargs)
        self.y_reduction=y_reduction
        self.anim=Animation()

    def on_index(self,*args):
        super(BigWheel,self).on_index()
        self.anim.cancel_all(self)

    def _position_visible_slides(self, *args):
        slides, index = self.slides, self.index
        no_of_slides = len(slides) - 1
        if not slides:
            return
        x, y, width, height = self.x, self.y, self.width, self.height
        _offset, direction = self._offset, self.direction[0]
        _prev, _next, _current = self._prev, self._next, self._current
        get_slide_container = self.get_slide_container
        last_slide = get_slide_container(slides[-1])
        first_slide = get_slide_container(slides[0])
        skip_next = False
        _loop = self.loop

        if direction in 'rl':
            xoff = x + _offset
            x_prev = {'l': xoff + width, 'r': xoff - width}
            x_next = {'l': xoff - width, 'r': xoff + width}
            if _prev:
                _prev.pos = (x_prev[direction], y)
            elif _loop and _next and index == 0:
                # if first slide is moving to right with direction set to right
                # or toward left with direction set to left
                if ((_offset > 0 and direction == 'r') or
                        (_offset < 0 and direction == 'l')):
                    # put last_slide before first slide
                    last_slide.pos = (x_prev[direction], y)
                    skip_next = True
            if _current:
                _current.pos = (xoff, y)
            if skip_next:
                return
            if _next:
                _next.pos = (x_next[direction], y)
            elif _loop and _prev and index == no_of_slides:
                if ((_offset < 0 and direction == 'r') or
                        (_offset > 0 and direction == 'l')):
                    first_slide.pos = (x_next[direction], y)
        if direction in 'tb':
            yoff = y + _offset

            y_prev = {'t': yoff - height, 'b': yoff + height}
            y_next = {'t': yoff + height, 'b': yoff - height}
            if _prev:
                _prev.pos = (x, y_prev[direction]+self.y_reduction)
            elif _loop and _next and index == 0:
                if ((_offset > 0 and direction == 't') or
                        (_offset < 0 and direction == 'b')):
                    last_slide.pos = (x, y_prev[direction]+self.y_reduction)
                    skip_next = True
            if _current:
                _current.pos = (x, yoff)
            if skip_next:
                return
            if _next:
                _next.pos = (x, y_next[direction]-self.y_reduction)
            elif _loop and _prev and index == no_of_slides:
                if ((_offset < 0 and direction == 't') or
                        (_offset > 0 and direction == 'b')):
                    first_slide.pos = (x, y_next[direction]-self.y_reduction)

    def _insert_visible_slides(self, _next_slide=None, _prev_slide=None):
        get_slide_container = self.get_slide_container

        previous_slide = _prev_slide if _prev_slide else self.previous_slide
        if previous_slide:
            self._prev = get_slide_container(previous_slide)
        else:
            self._prev = None

        current_slide = self.current_slide
        if current_slide:
            self._current = get_slide_container(current_slide)
        else:
            self._current = None

        next_slide = _next_slide if _next_slide else self.next_slide
        if next_slide:
            self._next = get_slide_container(next_slide)
        else:
            self._next = None

        if self._prev_equals_next:
            setattr(self, '_prev' if self._prioritize_next else '_next', None)

        super_remove = super(Carousel, self).remove_widget
        for container in self.slides_container:
            super_remove(container)

        if self._prev and self._prev.parent is not self:
            super(Carousel, self).add_widget(self._prev)
        if self._next and self._next.parent is not self:
            super(Carousel, self).add_widget(self._next)
        if self._current:
            super(Carousel, self).add_widget(self._current)

    def on__offset(self, *args):
        self._trigger_position_visible_slides()
        # if reached full offset, switch index to next or prev
        direction = self.direction[0]
        _offset = self._offset
        width = self.width
        height = self.height
        index = self.index
        if self._skip_slide is not None or index is None:
            return

        # Move to next slide?
        if (direction == 'r' and _offset <= -width) or \
                (direction == 'l' and _offset >= width) or \
                (direction == 't' and _offset-self.y_reduction <= - height) or \
                (direction == 'b' and _offset >= height):
            if self.next_slide:
                self.index += 1

        # Move to previous slide?
        elif (direction == 'r' and _offset >= width) or \
                (direction == 'l' and _offset <= -width) or \
                (direction == 't' and _offset+self.y_reduction >= height) or \
                (direction == 'b' and _offset <= -height):
            if self.previous_slide:
                self.index -= 1

        elif self._prev_equals_next:
            new_value = (_offset < 0) is (direction in 'rt')
            if self._prioritize_next is not new_value:
                self._prioritize_next = new_value
                if new_value is (self._next is None):
                    self._prev, self._next = self._next, self._prev

    def _start_animation(self, *args, **kwargs):
        # compute target offset for ease back, next or prev
        new_offset = 0
        direction = kwargs.get('direction', self.direction)[0]
        is_horizontal = direction in 'rl'
        extent = self.width if is_horizontal else self.height
        min_move = kwargs.get('min_move', self.min_move)
        _offset = kwargs.get('offset', self._offset)

        if _offset < min_move * -extent:
            new_offset = -extent
        elif _offset > min_move * extent:
            new_offset = extent

        # if new_offset is 0, it wasnt enough to go next/prev
        dur = self.anim_move_duration
        if new_offset == 0:
            dur = self.anim_cancel_duration

        # detect edge cases if not looping
        len_slides = len(self.slides)
        index = self.index
        if not self.loop or len_slides == 1:
            is_first = (index == 0)
            is_last = (index == len_slides - 1)
            if direction in 'rt':
                towards_prev = (new_offset > 0)
                towards_next = (new_offset < 0)
            else:
                towards_prev = (new_offset < 0)
                towards_next = (new_offset > 0)
            if (is_first and towards_prev) or (is_last and towards_next):
                new_offset = 0

        self.anim = Animation(_offset=new_offset, d=dur, t=self.anim_type)
        self.anim.cancel_all(self)

        def _cmp(*l):
            if self._skip_slide is not None:
                self.index = self._skip_slide
                self._skip_slide = None

        self.anim.bind(on_complete=_cmp)
        self.anim.start(self)

class BigWheelClock(Carousel):
    clock_stack={}
    def __init__(self,y_reduction=60, **kwargs):
        super(BigWheelClock,self).__init__(**kwargs)
        self.y_reduction=y_reduction
        self.anim=Animation()

    def on_touch_move(self, touch):
        cl=App.get_running_app().context_screen.get_screen('main').widgets['clock_label']
        cl._delete_clock()
        cl._create_clock()
        return super().on_touch_move(touch)

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            touch.grab(self)
        return super().on_touch_down(touch)

    def on_touch_up(self, touch):
        if touch.grab_current is self:
            touch.ungrab(self)
        return super().on_touch_up(touch)

    def _set_sys_time(*args):
        if Clock.get_boottime()>20:
            if App.get_running_app().context_screen.has_screen('main'):
                w=App.get_running_app().context_screen.get_screen('main').widgets
                h=w['hour_wheel'].index+1
                m=w['minute_wheel'].index
                p='pm' if w['ampm_wheel'].index % 2 else 'am'
                if os.name=='posix':
                        os.system(f'sudo date -s {h}:{m}{p}')
                else:
                    logger.debug(f'main.py BigWheelClock _set_sys_time(): \n  >>time set: {h}:{str(m).zfill(2)}{p}')

    def _create_clock(self,*args):
        Clock.schedule_once(self._set_sys_time, 2)
        self.clock_stack['event'] = self._set_sys_time

    def _delete_clock(self,*args):
        if 'event' in self.clock_stack:
            Clock.unschedule(self.clock_stack['event'])

    def on_index(self,*args):
        super(BigWheelClock,self).on_index()
        self.anim.cancel_all(self)
        self._delete_clock()#if timer exists, restart it
        self._create_clock()#start timer to call self._set_sys_time()


    def set_index(self,*args,cat=None):
        h=int(time.strftime('%I'))
        m=int(time.strftime('%M'))
        p=time.strftime('%p')
        if cat=='hour':
            for index,i in enumerate(self.slides):
                index+=1
                if index==h:
                    self.index=index-1
                    return
        elif cat =='minute':
            for index,i in enumerate(self.slides):
                if index==m:
                    self.index=index
                    return
        elif cat =='ampm':
            for index,i in enumerate(self.slides):
                if i.text[-2:]==p:
                    self.index=index
                    return

    def _position_visible_slides(self, *args):
        slides, index = self.slides, self.index
        no_of_slides = len(slides) - 1
        if not slides:
            return
        x, y, width, height = self.x, self.y, self.width, self.height
        _offset, direction = self._offset, self.direction[0]
        _prev, _next, _current = self._prev, self._next, self._current
        get_slide_container = self.get_slide_container
        last_slide = get_slide_container(slides[-1])
        first_slide = get_slide_container(slides[0])
        skip_next = False
        _loop = self.loop

        if direction in 'rl':
            xoff = x + _offset
            x_prev = {'l': xoff + width, 'r': xoff - width}
            x_next = {'l': xoff - width, 'r': xoff + width}
            if _prev:
                _prev.pos = (x_prev[direction], y)
            elif _loop and _next and index == 0:
                # if first slide is moving to right with direction set to right
                # or toward left with direction set to left
                if ((_offset > 0 and direction == 'r') or
                        (_offset < 0 and direction == 'l')):
                    # put last_slide before first slide
                    last_slide.pos = (x_prev[direction], y)
                    skip_next = True
            if _current:
                _current.pos = (xoff, y)
            if skip_next:
                return
            if _next:
                _next.pos = (x_next[direction], y)
            elif _loop and _prev and index == no_of_slides:
                if ((_offset < 0 and direction == 'r') or
                        (_offset > 0 and direction == 'l')):
                    first_slide.pos = (x_next[direction], y)
        if direction in 'tb':
            yoff = y + _offset

            y_prev = {'t': yoff - height, 'b': yoff + height}
            y_next = {'t': yoff + height, 'b': yoff - height}
            if _prev:
                _prev.pos = (x, y_prev[direction]+self.y_reduction)
            elif _loop and _next and index == 0:
                if ((_offset > 0 and direction == 't') or
                        (_offset < 0 and direction == 'b')):
                    last_slide.pos = (x, y_prev[direction]+self.y_reduction)
                    skip_next = True
            if _current:
                _current.pos = (x, yoff)
            if skip_next:
                return
            if _next:
                _next.pos = (x, y_next[direction]-self.y_reduction)
            elif _loop and _prev and index == no_of_slides:
                if ((_offset < 0 and direction == 't') or
                        (_offset > 0 and direction == 'b')):
                    first_slide.pos = (x, y_next[direction]-self.y_reduction)

    def _insert_visible_slides(self, _next_slide=None, _prev_slide=None):
        get_slide_container = self.get_slide_container

        previous_slide = _prev_slide if _prev_slide else self.previous_slide
        if previous_slide:
            self._prev = get_slide_container(previous_slide)
        else:
            self._prev = None

        current_slide = self.current_slide
        if current_slide:
            self._current = get_slide_container(current_slide)
        else:
            self._current = None

        next_slide = _next_slide if _next_slide else self.next_slide
        if next_slide:
            self._next = get_slide_container(next_slide)
        else:
            self._next = None

        if self._prev_equals_next:
            setattr(self, '_prev' if self._prioritize_next else '_next', None)

        super_remove = super(Carousel, self).remove_widget
        for container in self.slides_container:
            super_remove(container)

        if self._prev and self._prev.parent is not self:
            super(Carousel, self).add_widget(self._prev)
        if self._next and self._next.parent is not self:
            super(Carousel, self).add_widget(self._next)
        if self._current:
            super(Carousel, self).add_widget(self._current)

    def on__offset(self, *args):
        self._trigger_position_visible_slides()
        # if reached full offset, switch index to next or prev
        direction = self.direction[0]
        _offset = self._offset
        width = self.width
        height = self.height
        index = self.index
        if self._skip_slide is not None or index is None:
            return

        # Move to next slide?
        if (direction == 'r' and _offset <= -width) or \
                (direction == 'l' and _offset >= width) or \
                (direction == 't' and _offset-self.y_reduction <= - height) or \
                (direction == 'b' and _offset >= height):
            if self.next_slide:
                self.index += 1

        # Move to previous slide?
        elif (direction == 'r' and _offset >= width) or \
                (direction == 'l' and _offset <= -width) or \
                (direction == 't' and _offset+self.y_reduction >= height) or \
                (direction == 'b' and _offset <= -height):
            if self.previous_slide:
                self.index -= 1

        elif self._prev_equals_next:
            new_value = (_offset < 0) is (direction in 'rt')
            if self._prioritize_next is not new_value:
                self._prioritize_next = new_value
                if new_value is (self._next is None):
                    self._prev, self._next = self._next, self._prev

    def _start_animation(self, *args, **kwargs):
        # compute target offset for ease back, next or prev
        new_offset = 0
        direction = kwargs.get('direction', self.direction)[0]
        is_horizontal = direction in 'rl'
        extent = self.width if is_horizontal else self.height
        min_move = kwargs.get('min_move', self.min_move)
        _offset = kwargs.get('offset', self._offset)

        if _offset < min_move * -extent:
            new_offset = -extent
        elif _offset > min_move * extent:
            new_offset = extent

        # if new_offset is 0, it wasnt enough to go next/prev
        dur = self.anim_move_duration
        if new_offset == 0:
            dur = self.anim_cancel_duration

        # detect edge cases if not looping
        len_slides = len(self.slides)
        index = self.index
        if not self.loop or len_slides == 1:
            is_first = (index == 0)
            is_last = (index == len_slides - 1)
            if direction in 'rt':
                towards_prev = (new_offset > 0)
                towards_next = (new_offset < 0)
            else:
                towards_prev = (new_offset < 0)
                towards_next = (new_offset > 0)
            if (is_first and towards_prev) or (is_last and towards_next):
                new_offset = 0

        self.anim = Animation(_offset=new_offset, d=dur, t=self.anim_type)
        self.anim.cancel_all(self)

        def _cmp(*l):
            if self._skip_slide is not None:
                self.index = self._skip_slide
                self._skip_slide = None

        self.anim.bind(on_complete=_cmp)
        self.anim.start(self)

class AnimatedCarousel(Carousel):
    def __init__(self, **kwargs):
        super(AnimatedCarousel,self).__init__(**kwargs)
        self.opacity=0
        self.anim_length=.5
        self.skip_bounce=False

    def on_touch_move(self, touch):
        cl=App.get_running_app().context_screen.get_screen('main').widgets['clock_label']
        cl._delete_clock()
        cl._create_clock()
        return super().on_touch_move(touch)

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            touch.grab(self)
        return super().on_touch_down(touch)

    def on_touch_up(self, touch):
        if touch.grab_current is self:
            touch.ungrab(self)
        return super().on_touch_up(touch)

    def fade_in(self):
        anim=Animation(opacity=1,d=self.anim_length)
        anim.start(self)

    def fade_out(self):
        anim=Animation(opacity=0,d=self.anim_length/2)
        anim.bind(on_complete=partial(self.rm_parent,instance=self))
        anim.start(self)

    def rm_parent(*args,instance=None):
        if instance.parent:
            instance.parent.remove_widget(instance)

    def on_touch_down(self, touch):
        if self.opacity==1 and self._offset==0:
            return super(AnimatedCarousel,self).on_touch_down(touch)

    def bounce(self,*args):
        anim=Animation(_offset=-100,d=.5,t='out_quad')+Animation(_offset=0,d=.25,t='in_quad')
        anim.start(self)

    def bounce_progress(self,progress,*args):
        def out(progress):
            p = 1.-progress / 1.
            # if p < (.25 / 2.75):
            #     return -7.5625 * p * p + progress
            if p < (1.0 / 2.75):
                return 7.5625 * p * p + (progress-p)
            if p < (2.0 / 2.75):
                p -= (1.5 / 2.75)
                return 7.5625 * p * p + .75 
            elif p < (2.5 / 2.75):
                p -= (2.25 / 2.75)
                return 7.5625 * p * p + .9375
            else:
                p -= (2.625 / 2.75)
                return 7.5625 * p * p + .984375
        return 1.0-out(progress)

class NotificationBadge(ButtonBehavior,Image):
    '''`NotificationBadge` to add to widgets that need interaction.
    
    References to `self` are automatically added to `parent.widgets` under `key` 'notification_badge',
    and cleared when `self.clear()` is called'''

    def __init__(self,rel_pos=(.55,.675),rel_size=(.3,.3),**kwargs):
        source=red_dot
        super(NotificationBadge,self).__init__(
            source=source,
            allow_stretch=False,
            keep_ratio=True,
            **kwargs)
        self.opacity=.9
        self.rel_x=rel_pos[0]
        self.rel_y=rel_pos[1]
        self.rel_width=rel_size[0]
        self.rel_height=rel_size[1]

    def align(self,*args):
        parent=self.parent
        self.width=parent.width*self.rel_width
        self.height=parent.height*self.rel_height
        self.y=parent.y+parent.height*self.rel_y
        self.x=parent.x+parent.width*self.rel_x

    def on_parent(self,*args):
        if not self.parent:
            return
        parent=self.parent
        self.width=parent.width*self.rel_width
        self.height=parent.height*self.rel_height
        self.y=parent.y+parent.height*self.rel_y
        self.x=parent.x+parent.width*self.rel_x
        parent.bind(size=self.align)
        parent.bind(pos=self.align)
        if hasattr(parent,'widgets'):
            parent.widgets['notification_badge']=self

    def clear(self,*args):
        self.parent.unbind(size=self.align,pos=self.align)
        if hasattr(self.parent,'widgets'):
            if 'notification_badge' in self.parent.widgets:
                del self.parent.widgets['notification_badge']
        self.parent.remove_widget(self)

class PreLoader(CircularProgressBar):
    def __init__(self,rel_pos=(.5,.5),rel_size=.5,**kwargs):
        if 'speed' in kwargs:
            self.speed=kwargs.pop('speed')
        else:self.speed=750
        if 'length' in kwargs:
            self.length=kwargs.pop('length')
        else:self.length=200
        if 'ref' in kwargs:
            self.ref=kwargs.pop('ref')
        else:self.ref='preloader'
        if 'color' in kwargs:
            _color=kwargs.pop('color')
        else:_color=palette('light_tint',1)

        super().__init__(**kwargs)
        self._progress_colour=_color
        self.background_colour=palette('light_tint',0)
        self.rel_x=rel_pos[0]
        self.rel_y=rel_pos[1]
        self.rel_size=rel_size

    def align(self,*args):
        parent=self.parent
        self.widget_size=int(parent.width*self.rel_size)
        self.y=parent.y+parent.height*self.rel_y
        self.x=parent.x+parent.width*self.rel_x

    def on_parent(self,*args):
        if not self.parent:
            self.clear()
            return
        parent=self.parent
        self._parent=parent
        self.widget_size=int(parent.width*self.rel_size)
        self.y=parent.y+parent.height*self.rel_y
        self.x=parent.x+parent.width*self.rel_x
        parent.bind(size=self.align)
        parent.bind(pos=self.align)
        Clock.schedule_once(self.start_update,.2)
        if hasattr(parent,'widgets'):
            parent.widgets[self.ref]=self

    def clear(self,*args):
        p=self.parent if self.parent else self._parent
        p.unbind(size=self.align,pos=self.align)
        if hasattr(p,'widgets'):
            if self.ref in p.widgets:
                del p.widgets[self.ref]
        p.remove_widget(self)

    def start_update(self,*args):
        self.update_clock=Clock.schedule_interval(self.update,0)

    def stop_update(self,*args):
        Clock.unschedule(self.update_clock)

    def update(self,delta,*args):
        if self._angle_start>=360:
            self._angle_start=0
            self.value=self.length
        self.value+=self.speed*delta
        self._angle_start=((self.value-self.length)*.001)*360

class MenuBubble(Bubble):
    def __init__(self, **kwargs):
        if 'ref' in kwargs:
            self.ref=kwargs.pop('ref')
        else:self.ref='menu_bubble'
        super(MenuBubble,self).__init__(**kwargs)

    def align(self,*args):
        parent=self.parent
        # optimize layout by preventing looking at the same attribute in a loop
        w, h = parent.size
        x, y = parent.pos
        # size
        shw, shh = self.size_hint
        shw_min, shh_min = self.size_hint_min
        shw_max, shh_max = self.size_hint_max

        if shw is not None and shh is not None:
            c_w = shw * w
            c_h = shh * h

            if shw_min is not None and c_w < shw_min:
                c_w = shw_min
            elif shw_max is not None and c_w > shw_max:
                c_w = shw_max

            if shh_min is not None and c_h < shh_min:
                c_h = shh_min
            elif shh_max is not None and c_h > shh_max:
                c_h = shh_max
            self.size = c_w, c_h
        elif shw is not None:
            c_w = shw * w

            if shw_min is not None and c_w < shw_min:
                c_w = shw_min
            elif shw_max is not None and c_w > shw_max:
                c_w = shw_max
            self.width = c_w
        elif shh is not None:
            c_h = shh * h

            if shh_min is not None and c_h < shh_min:
                c_h = shh_min
            elif shh_max is not None and c_h > shh_max:
                c_h = shh_max
            self.height = c_h

        # pos
        for key, value in self.pos_hint.items():
            if key == 'x':
                self.x = x + value * w
            elif key == 'right':
                self.right = x + value * w
            elif key == 'pos':
                self.pos = x + value[0] * w, y + value[1] * h
            elif key == 'y':
                self.y = y + value * h
            elif key == 'top':
                self.top = y + value * h
            elif key == 'center':
                self.center = x + value[0] * w, y + value[1] * h
            elif key == 'center_x':
                self.center_x = x + value * w
            elif key == 'center_y':
                self.center_y = y + value * h

    def on_parent(self,*args):
        if not self.parent:
            self.clear()
            return
        parent=self.parent
        self._parent=parent
        if hasattr(parent,'widgets'):
            parent.widgets[self.ref]=self
        if hasattr(parent,'do_layout'):
            return
        self.align()
        parent.bind(size=self.align)
        parent.bind(pos=self.align)

    def clear(self,*args):
        p=self.parent if self.parent else self._parent
        p.unbind(size=self.align,pos=self.align)
        if hasattr(p,'widgets'):
            if self.ref in p.widgets:
                del p.widgets[self.ref]
        p.remove_widget(self)

    def on_touch_down(self, touch):
        if not self.collide_point(*touch.pos):
            if hasattr(self,'parent'):
                self.parent.remove_widget(self)
            super(MenuBubble,self).on_touch_down(touch)
            return True
        return super(MenuBubble,self).on_touch_down(touch)

class ScrollMenuBubble(Bubble):
    def __init__(self,trackee_widget,scrollview,**kwargs):
        if 'ref' in kwargs:
            self.ref=kwargs.pop('ref')
        else:self.ref='menu_bubble'
        super(ScrollMenuBubble,self).__init__(**kwargs)
        self.trackee_widget=trackee_widget
        self._scroll=scrollview
        self._size_hint=(self.size_hint[0],self.size_hint[1])
        self._pos_hint=deepcopy(self.pos_hint)
        self.size_hint,self.pos_hint=(None,None),{}

    def align(self,*args):
        tw=self.trackee_widget
        # optimize layout by preventing looking at the same attribute in a loop
        w, h = tw.size
        x, y = tw.to_window(*tw.pos)
        # size
        shw, shh = self._size_hint
        shw_min, shh_min = self.size_hint_min
        shw_max, shh_max = self.size_hint_max

        if shw is not None and shh is not None:
            c_w = shw * w
            c_h = shh * h

            if shw_min is not None and c_w < shw_min:
                c_w = shw_min
            elif shw_max is not None and c_w > shw_max:
                c_w = shw_max

            if shh_min is not None and c_h < shh_min:
                c_h = shh_min
            elif shh_max is not None and c_h > shh_max:
                c_h = shh_max
            self.size = c_w, c_h
        elif shw is not None:
            c_w = shw * w

            if shw_min is not None and c_w < shw_min:
                c_w = shw_min
            elif shw_max is not None and c_w > shw_max:
                c_w = shw_max
            self.width = c_w
        elif shh is not None:
            c_h = shh * h

            if shh_min is not None and c_h < shh_min:
                c_h = shh_min
            elif shh_max is not None and c_h > shh_max:
                c_h = shh_max
            self.height = c_h

        # pos
        for key, value in self._pos_hint.items():
            if key == 'x':
                self.x = x + value * w
            elif key == 'right':
                self.right = x + value * w
            elif key == 'pos':
                self.pos = x + value[0] * w, y + value[1] * h
            elif key == 'y':
                self.y = y + value * h
            elif key == 'top':
                self.top = y + value * h
            elif key == 'center':
                self.center = x + value[0] * w, y + value[1] * h
            elif key == 'center_x':
                self.center_x = x + value * w
            elif key == 'center_y':
                self.center_y = y + value * h

    def on_parent(self,*args):
        if not self.parent:
            self.clear()
            return
        tw=self.trackee_widget
        if not hasattr(tw,'widgets'):
            tw.widgets={}
        parent=self.parent
        self._parent=parent
        if hasattr(parent,'widgets'):
            parent.widgets[self.ref]=self
        self.align()
        self._scroll.bind(scroll_y=self.align)

    def clear(self,*args):
        p=self.parent if self.parent else self._parent
        self.trackee_widget.unbind(size=self.align,pos=self.align)
        if hasattr(p,'widgets'):
            if self.ref in p.widgets:
                del p.widgets[self.ref]
        p.remove_widget(self)

    def on_touch_down(self, touch):
        if not self.collide_point(*touch.pos):
            if hasattr(self,'parent'):
                self.parent.remove_widget(self)
            super(ScrollMenuBubble,self).on_touch_down(touch)
            return True
        return super(ScrollMenuBubble,self).on_touch_down(touch)

class PinLock(RoundedColorLayoutModal):
    end_point_one=ListProperty([])
    end_point_two=ListProperty([])
    def __init__(self,callback=None,hidden=True,**kwargs):
        if 'set_pin' in kwargs:
            self.set_pin=kwargs.pop('set_pin')
        if 'alt_pin' in kwargs:
            self.alt_pin=kwargs.pop('alt_pin')
        super(PinLock,self).__init__(bg_color=palette('secondary',1),**kwargs)
        self.hidden=hidden
        self.widgets={}
        self.pin=[]
        self.entry_slots={
            1:None,
            2:None,
            3:None,
            4:None,
            5:None,
            6:None}
        self.size_hint=(.5,.6)
        self.pos_hint={'center_x':.5,'center_y':.5}
        self.callback=callback
        with self.canvas.before:
            Color(*palette('dark_shade',.65))
            Rectangle(size=Window.size)

        title=Label(
            text='[size=20][color=#ffffff][b]Admin Pin Entry',
            markup=True,
            size_hint =(.4, .05),
            pos_hint = {'center_x':.5, 'center_y':.925},)
        self.widgets['title']=title
        title.ref='title'

        overlay_x=IconButton(
            source=overlay_x_icon,
            size_hint=(.1,.1),
            pos_hint={'x':.90,'y':.88})
        overlay_x.bind(on_release=self.clear)
        self.widgets['overlay_x']=overlay_x

        seperator=Image(
            source=gray_seperator_line,
            allow_stretch=True,
            keep_ratio=False,
            size_hint =(.9, .005),
            pos_hint = {'x':.05, 'y':.85})
        self.widgets['seperator']=seperator

        entry_one=MinimumBoundingLabel(
            text='[size=35][b]-',
            markup=True,
            size_hint =(.15, .15),
            pos_hint = {'center_x':.25, 'center_y':.7},)
        self.widgets['entry_one']=entry_one
        self.entry_slots[1]=entry_one

        entry_two=MinimumBoundingLabel(
            text='[size=35][b]-',
            markup=True,
            size_hint =(.15, .15),
            pos_hint = {'center_x':.35, 'center_y':.7},)
        self.widgets['entry_two']=entry_two
        self.entry_slots[2]=entry_two

        entry_three=MinimumBoundingLabel(
            text='[size=35][b]-',
            markup=True,
            size_hint =(.15, .15),
            pos_hint = {'center_x':.45, 'center_y':.7},)
        self.widgets['entry_three']=entry_three
        self.entry_slots[3]=entry_three

        entry_four=MinimumBoundingLabel(
            text='[size=35][b]-',
            markup=True,
            size_hint =(.15, .15),
            pos_hint = {'center_x':.55, 'center_y':.7},)
        self.widgets['entry_four']=entry_four
        self.entry_slots[4]=entry_four

        entry_five=MinimumBoundingLabel(
            text='[size=35][b]-',
            markup=True,
            size_hint =(.15, .15),
            pos_hint = {'center_x':.65, 'center_y':.7},)
        self.widgets['entry_five']=entry_five
        self.entry_slots[5]=entry_five

        entry_six=MinimumBoundingLabel(
            text='[size=35][b]-',
            markup=True,
            size_hint =(.15, .15),
            pos_hint = {'center_x':.75, 'center_y':.7},)
        self.widgets['entry_six']=entry_six
        self.entry_slots[6]=entry_six

        hidden_button=IconButton(
            source=hidden_black,
            size_hint =(.1, .1),
            pos_hint = {'center_x':.9, 'center_y':.7})
        self.widgets['hidden_button']=hidden_button
        hidden_button.bind(on_release=self.visibility)

        num_pad=RelativeLayout(size_hint =(.75, .65),
            pos_hint = {'center_x':.5, 'y':0})
        self.widgets['num_pad']=num_pad

        one=RoundedButton(text="[size=35][b][color=#000000] 1 [/color][/b][/size]",
            size_hint =(.15, .15),
            pos_hint = {'x':.05, 'y':.65},
            background_down='',
            background_color=palette('neutral',.85),
            markup=True)
        one.value=1
        self.widgets['one']=one
        one.bind(on_release=self.entry_func)

        two=RoundedButton(text="[size=35][b][color=#000000] 2 [/color][/b][/size]",
            size_hint =(.15, .15),
            pos_hint = {'x':.3, 'y':.65},
            background_down='',
            background_color=palette('neutral',.85),
            markup=True)
        two.value=2
        self.widgets['two']=two
        two.bind(on_release=self.entry_func)

        three=RoundedButton(text="[size=35][b][color=#000000] 3 [/color][/b][/size]",
            size_hint =(.15, .15),
            pos_hint = {'x':.55, 'y':.65},
            background_down='',
            background_color=palette('neutral',.85),
            markup=True)
        three.value=3
        self.widgets['three']=three
        three.bind(on_release=self.entry_func)

        four=RoundedButton(text="[size=35][b][color=#000000] 4 [/color][/b][/size]",
            size_hint =(.15, .15),
            pos_hint = {'x':.05, 'y':.45},
            background_down='',
            background_color=palette('neutral',.85),
            markup=True)
        four.value=4
        self.widgets['four']=four
        four.bind(on_release=self.entry_func)

        five=RoundedButton(text="[size=35][b][color=#000000] 5 [/color][/b][/size]",
            size_hint =(.15, .15),
            pos_hint = {'x':.3, 'y':.45},
            background_down='',
            background_color=palette('neutral',.85),
            markup=True)
        five.value=5
        self.widgets['five']=five
        five.bind(on_release=self.entry_func)

        six=RoundedButton(text="[size=35][b][color=#000000] 6 [/color][/b][/size]",
            size_hint =(.15, .15),
            pos_hint = {'x':.55, 'y':.45},
            background_down='',
            background_color=palette('neutral',.85),
            markup=True)
        six.value=6
        self.widgets['six']=six
        six.bind(on_release=self.entry_func)

        seven=RoundedButton(text="[size=35][b][color=#000000] 7 [/color][/b][/size]",
            size_hint =(.15, .15),
            pos_hint = {'x':.05, 'y':.25},
            background_down='',
            background_color=palette('neutral',.85),
            markup=True)
        seven.value=7
        self.widgets['seven']=seven
        seven.bind(on_release=self.entry_func)

        eight=RoundedButton(text="[size=35][b][color=#000000] 8 [/color][/b][/size]",
            size_hint =(.15, .15),
            pos_hint = {'x':.3, 'y':.25},
            background_down='',
            background_color=palette('neutral',.85),
            markup=True)
        eight.value=8
        self.widgets['eight']=eight
        eight.bind(on_release=self.entry_func)

        nine=RoundedButton(text="[size=35][b][color=#000000] 9 [/color][/b][/size]",
            size_hint =(.15, .15),
            pos_hint = {'x':.55, 'y':.25},
            background_down='',
            background_color=palette('neutral',.85),
            markup=True)
        nine.value=9
        self.widgets['nine']=nine
        nine.bind(on_release=self.entry_func)

        zero=RoundedButton(text="[size=35][b][color=#000000] 0 [/color][/b][/size]",
            size_hint =(.15, .15),
            pos_hint = {'x':.05, 'y':.05},
            background_down='',
            background_color=palette('neutral',.85),
            markup=True)
        zero.value=0
        self.widgets['zero']=zero
        zero.bind(on_release=self.entry_func)

        backspace=RoundedButton(text="[size=35][b][color=#000000] <- [/color][/b][/size]",
            size_hint =(.4, .15),
            pos_hint = {'x':.3, 'y':.05},
            background_down='',
            background_color=palette('highlight',.85),
            markup=True)
        self.widgets['backspace']=backspace
        backspace.bind(on_release=self.backspace_func)

        enter=RoundedButton(text="[size=35][b][color=#000000] -> [/color][/b][/size]",
            size_hint =(.15, .75),
            pos_hint = {'right':.95, 'y':.05},
            background_down='',
            background_color=palette('complement',.85),
            markup=True)
        self.widgets['enter']=enter
        enter.bind(on_release=self.enter_func)

        self.add_widget(title)
        self.add_widget(overlay_x)
        self.add_widget(seperator)
        self.add_widget(entry_one)
        self.add_widget(entry_two)
        self.add_widget(entry_three)
        self.add_widget(entry_four)
        self.add_widget(entry_five)
        self.add_widget(entry_six)
        self.add_widget(hidden_button)
        self.add_widget(num_pad)
        num_pad.add_widget(one)
        num_pad.add_widget(two)
        num_pad.add_widget(three)
        num_pad.add_widget(four)
        num_pad.add_widget(five)
        num_pad.add_widget(six)
        num_pad.add_widget(seven)
        num_pad.add_widget(eight)
        num_pad.add_widget(nine)
        num_pad.add_widget(zero)
        num_pad.add_widget(backspace)
        num_pad.add_widget(enter)

    def visibility(self,*args):
        self.hidden = not self.hidden
        if self.hidden:
            self.widgets['hidden_button'].source=hidden_black
        elif not self.hidden:
            self.widgets['hidden_button'].source=visible_black
        for i,v in enumerate(self.pin):
            if self.hidden:
                self.entry_slots[i+1].text='[size=35][b]*'
            else:
                self.entry_slots[i+1].text=f'[size=35][b]{v}'

    def entry_func(self,button):
        if len(self.pin)>=6:
            return
        val=button.value
        self.pin.append(val)
        for i,v in enumerate(self.pin):
            if self.hidden:
                self.entry_slots[i+1].text='[size=35][b]*'
            else:
                self.entry_slots[i+1].text=f'[size=35][b]{v}'

    def backspace_func(self,button):
        if len(self.pin)<1:
            return
        del self.pin[-1]
        self.entry_slots[len(self.pin)+1].text='[size=35][b]-'

    def enter_func(self,button):
        if len(self.pin)<1:
            return
        pin=''.join(str(x) for x in self.pin)
        self.pin_to_set=pin
        self.pin=[]
        for i in self.entry_slots.values():
            i.text='[size=35][b]-'
        if hasattr(self,'set_pin'):
            if self.set_pin:
                self.clear_with_success()
                return
            else: return
        if hasattr(self,'alt_pin'):
            if self.alt_pin:
                if pin==self.alt_pin:
                    self.clear_with_success()
                else:
                    App.get_running_app().notifications.toast('[b][size=20]Pins do not match','error')
                    return
        if pin==App.get_running_app().config_.get('account','admin_pin',fallback='000000'):
            self.clear_with_success()

    def clear_with_success(self,*args):
        self.check_one_start=[self.center_x-100,self.center_y-50]
        self.check_one_end  =[self.center_x,self.center_y-125]
        self.check_two_start=[self.center_x,self.center_y-125]
        self.check_two_end  =[self.center_x+100,self.center_y+75]
        fade=Animation(opacity=0,d=.25)
        fade.start(self.widgets['num_pad'])
        for i in self.entry_slots.values():
            fade.start(i)
        fade.start(self.widgets['hidden_button'])
        with self.canvas.after:
            Color(*palette('complement'))
            self.check_one=Line(width=3)
            self.check_two=Line(width=3)
        self.end_point_one=self.check_one_start
        self.end_point_two=self.check_two_start
        down=Animation(end_point_one=self.check_one_end,d=.25,t='out_sine')
        down+=Animation(end_point_two=self.check_two_end,d=.25,t='in_cubic')
        down.start(self)
        self.schedule_clear()

    def on_end_point_one(self,*args):
        points = self.check_one_start
        points.extend(self.end_point_one)

        # remove the old line
        self.canvas.after.remove(self.check_one)

        # draw the updated line
        with self.canvas.after:
            self.check_one = Line(points=points, width=3)

    def on_end_point_two(self,*args):
        if self.end_point_one!=self.check_one_end:
            return
        points = self.check_two_start
        points.extend(self.end_point_two)

        # remove the old line
        self.canvas.after.remove(self.check_two)

        # draw the updated line
        with self.canvas.after:
            self.check_two = Line(points=points, width=3)

    def schedule_clear(self,*args):
        Clock.schedule_once(self.clear,.85)
        Clock.schedule_once(self.unlock,.85)

    def unlock(self,*args):
        try:
            if hasattr(self,'set_pin'):
                self.callback(alt_pin=self.pin_to_set)
                return
            if hasattr(self,'alt_pin'):
                self.callback(self.pin_to_set)
                return
            self.callback()
        except TypeError as e:
            logger.exception(f'main.py PinLock unlock(): callback {self.callback} failed to execute')

    def clear(self,*args):
        if hasattr(self,'parent'):
            if self.parent is None:
                return
            self.parent.remove_widget(self)

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            touch.grab(self)
        super(PinLock, self).on_touch_down(touch)
        return True

    def on_touch_up(self, touch):
        if not self.collide_point(*touch.pos):
            if touch.grab_current is self:
                touch.ungrab(self)
            self.clear()
        super(PinLock, self).on_touch_up(touch)
        return True

class ExpandableIcon(ExpandableRoundedColorLayout,Image):
    pass

class EmailInput(TextInput):
    minimum_email_req=re.compile(r'\S+[@]\S+[.]\S+')

    def __init__(self, **kwargs):
        super(EmailInput,self).__init__(**kwargs)
        self.bind(focus=self._text_validation)
        self.contains_valid_email=False

    def insert_text(self, substring, from_undo=False):
        return super(EmailInput,self).insert_text(substring, from_undo)

    def _text_validation(self,button,focused,*args):
        if focused:
            self.foreground_color=palette('dark_shade',1)
            return
        t=self.minimum_email_req.match(self.text)
        if t:
            self.contains_valid_email=True
            self.foreground_color=palette('dark_shade',1)
        else:
            self.contains_valid_email=False
            self.foreground_color=palette('highlight',1)

class ScreenSaver(ButtonBehavior,Label):
    '''ScreenSaver implements a software level screen saver.

    call `ScreenSaver.start` in the apps `build` method to
    init the screen saver service app-wide.
    '''
    clock_events={}
    active_screensavers=[]
    timeout=600
    brightness='50'
    dim_flag=0
    pause_flag=0

    @classmethod
    def start(cls,*args,**kwargs):
        '''binds the `on_touch_down` event of `Window`
        to the screen saver service, and calls the service once without a touch event.

        `timeout` can be passed an integer to set the timeout
        before a screen saver is triggered.

        e.g. timeout=60 to set screensaver
        to trigger after one minute of inactivity.
        '''
        if 'timeout' in kwargs:
            cls.timeout=kwargs['timeout']

        Window.bind(on_touch_down=cls.service)
        cls.service()

    @classmethod
    def pause(cls,*args):
        '''Unschedules any previously scheduled screen saver timer.
        Leaves the Window binding in place, however stops `service`
        from creating new timeout events.
        '''
        cls.delete_clock()
        cls.pause_flag=1
        for i in cls.active_screensavers:
            i.clear()

    @classmethod
    def resume(cls,*args):
        '''removes `pause_flag` and calls `service`'''
        cls.pause_flag=0
        cls.service()

    @classmethod
    def service(cls,*args):
        '''Unschedules any previously scheduled screen saver timer,
        then schedules a new timer event to trigger a screen saver 
        in the future.
        Skips all clock calls when `pause_flag` == `True`
        '''
        if cls.pause_flag:
            return
        cls.delete_clock()
        cls.create_clock()

    @classmethod
    def create_clock(cls,*args):
        timer=Clock.schedule_once(cls.trigger_screen_saver, cls.timeout)
        cls.clock_events['timer']=timer

    @classmethod
    def delete_clock(cls,*args):
        if 'timer' in cls.clock_events:
            Clock.unschedule(cls.clock_events['timer'])

    @classmethod
    def trigger_screen_saver(cls,*args):
        s=ScreenSaver()
        cls.active_screensavers.append(s)
        Window.add_widget(s)
        # TODO get screen ddc/ci communication working
        # then uncomment line below
        # Thread(target=cls.capture_brightness,daemon=True).start()

    @staticmethod
    def _dim(*args):
        subprocess.run(['ddcutil','setvcp','10','20','--bus','20'],stdout=subprocess.PIPE)

    @classmethod
    def _brighten(cls,*args):
        subprocess.run(['ddcutil','setvcp','10',cls.brightness,'--bus','20'],stdout=subprocess.PIPE)

    @classmethod
    def capture_brightness(cls,*args):
        if os.name=='nt':
            return
        val=str(subprocess.check_output(r"ddcutil getvcp 10 --bus 20 --terse | sed 's/^.*C \([0-9]\+\).*/\1/'",shell=True))
        if val.isdigit():
            cls.brightness=val
            cls._dim()
            cls.dim_flag=1

    def __init__(self, **kwargs):
        super(ScreenSaver,self).__init__(**kwargs)
        with self.canvas.before:
            self.canvas_color=Color(*palette('dark_shade',0))
            Rectangle(size=Window.size)
        Animation(rgba=palette('dark_shade',1),d=2,t='out_sine').start(self.canvas_color)

    def clear(self,*args):
        cls=ScreenSaver
        if cls.dim_flag:
            cls.dim_flag=0
            Thread(target=cls._brighten,daemon=True).start()
        if hasattr(self,'parent'):
            if self.parent is None:
                return
            self.parent.remove_widget(self)

    def on_touch_up(self, touch):
        self.clear()
        super(ScreenSaver, self).on_touch_up(touch)
        return True

class ResizeLabel(Label):
    def __init__(self, **kwargs):
        super(ResizeLabel,self).__init__(**kwargs)

class FileRecycleView(RecycleView):
    def __init__(self, **kwargs):
        super(FileRecycleView,self).__init__(**kwargs)
        self.layout=self.FileRecycleViewLayout()
        self.add_widget(self.layout)
        self.viewclass=self.FileRecycleViewLabel


    class FileRecycleViewLayout(RecycleBoxLayout):
        def __init__(self, **kwargs):
            super(FileRecycleView.FileRecycleViewLayout,self).__init__(
                **kwargs,
                default_size=(0, 250),
                default_size_hint=(1, None),
                size_hint_y=None,
                orientation='vertical')
            self.bind(minimum_height=self._min)

        def _min(self, inst, val):
            self.height = val

    class FileRecycleViewLabel(RecycleDataViewBehavior, RoundedLabelColor):
        def __init__(self, **kwargs):
            super(FileRecycleView.FileRecycleViewLabel,self).__init__(
                **kwargs,
                markup=True,
                size_hint=(1,1))
            self.bind(size=self.setter('text_size'))

        def refresh_view_attrs(self, rv, index, data):
            self.set_color(data['color'])
            return super(FileRecycleView.FileRecycleViewLabel,self).refresh_view_attrs(rv, index, data)

        def set_color(self,color,*args):
            self.bg_color=color

class DenseRoundedColorLayout(ButtonBehavior,RoundedColorLayout):
    '''Does not allow touch to pass through'''

    # Layouts do not intercept touch events,
    # however with a colored background
    # the assumption is that it is blocking
    # widgets behind it, so we explicitly
    # capture the touch to meet expectations

    def __init__(self, bg_color=palette('secondary', 0.95), **kwargs):
        super(DenseRoundedColorLayout,self).__init__(bg_color=bg_color, **kwargs)

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            super(DenseRoundedColorLayout,self).on_touch_down(touch)
            return True
        return super(DenseRoundedColorLayout,self).on_touch_down(touch)

class ModalDenseRoundedColorLayout(DenseRoundedColorLayout):

    dim_saturation=NumericProperty(0)

    def __init__(self, bg_color=palette('secondary', 0.95),call_back=None,fade_in=False, **kwargs):
        self.register_event_type('on_expanded')
        self.target_size_hint=kwargs['size_hint']
        super(ModalDenseRoundedColorLayout,self).__init__(bg_color, **kwargs)
        self.widgets={}
        self.fade_in=fade_in
        self.call_back=call_back
        if fade_in:
            with self.canvas.before:
                self.dim_color=Color(*palette('dark_shade',0))
                Rectangle(size=Window.size)
        else:
            with self.canvas.before:
                self.dim_color=Color(*palette('dark_shade',.65))
                Rectangle(size=Window.size)

    def on_expanded(self,*args):
        '''overwrite to add children once expanded'''
        pass

    def on_dim_saturation(self,*args):
        self.dim_color.rgba=palette('dark_shade',self.dim_saturation)

    def on_touch_down(self, touch):
        super(ModalDenseRoundedColorLayout, self).on_touch_down(touch)
        return True

    def on_touch_up(self, touch):
        if self.collide_point(*touch.pos):
            return True
        super(ModalDenseRoundedColorLayout, self).on_touch_up(touch)
        return True

    def on_parent(self,*args):
        parent=self.parent
        if not parent:
            return
        if self.fade_in:
            Clock.schedule_once(self.animate_dim)
            if self.target_size_hint:
                self.size_hint=(0,0)
                Clock.schedule_once(self.animate_size)

    def animate_size(self,*args):
        a=Animation(size_hint=self.target_size_hint,d=.5,t='out_sine')
        a.bind(on_complete=lambda *args:(Window.dispatch_children('on_expanded')))
        a.start(self)

    def animate_dim(self,*args):
        Animation(dim_saturation=.9,d=1).start(self)

    def animate_success_clear(self,*args):
        self.clear_widgets()
        a=Animation(size_hint=(0,0),d=.5,t='in_back')
        a.bind(on_complete=self.clear)
        a.start(self)
        Animation(dim_saturation=0,d=.5).start(self)

    def clear(self,*args,cb=False):
        #cb == call self.callback if True
        self.dim_saturation=0
        if hasattr(self,'parent'):
            if self.parent is None:
                return
            self.parent.remove_widget(self)
        if self.call_back and cb:
            self.call_back()

class ScheduleCreationLayout(ModalDenseRoundedColorLayout):

    dim_saturation=NumericProperty(0)

    def __init__(self, bg_color=palette('secondary', 0.95),call_back=None,fade_in=False,data={}, **kwargs):
        self.target_size_hint=kwargs['size_hint']
        super(ScheduleCreationLayout,self).__init__(bg_color,call_back=call_back,fade_in=fade_in, **kwargs)
        self.widgets={}
        self.fade_in=fade_in
        self.call_back=call_back
        self.service_data=data
        if fade_in:
            with self.canvas.before:
                self.dim_color=Color(*palette('dark_shade',0))
                Rectangle(size=Window.size)
        else:
            with self.canvas.before:
                self.dim_color=Color(*palette('dark_shade',.65))
                Rectangle(size=Window.size)

    def populate_details(self,*args):
        service_details={
        "title":f"{self.service_data['title']}",
        "icon":f"{self.service_data['icon']}",
        "intervals":self.service_data['intervals'],
        "default_interval":self.service_data['default_interval'],
        "default_increment":self.service_data["default_increment"],
        "default_locked":self.service_data["default_locked"]
        }

        ##### top #####

        schedule_details_title=Label(
            text=current_language['schedule_details_title'],
            markup=True,
            size_hint =(.4, .05),
            pos_hint = {'center_x':.5, 'center_y':.925},)
        schedule_details_title.ref='schedule_details_title'

        schedule_details_name_label_top=MinimumBoundingLabel(
            text= '[size=18][color=#000000][b]'+service_details['title'],
            markup=True,
            pos_hint = {'center_x':.5, 'center_y':.85},)

        schedule_details_x_icon=IconButton(
            source=overlay_x_icon_black,
            size_hint=(.08,.08),
            pos_hint={'x':.92,'y':.9})
        self.widgets['schedule_details_x_icon']=schedule_details_x_icon
        schedule_details_x_icon.bind(on_release=lambda *args:self.clear(cb=True))

        ##### left #####

        schedule_details_interval_label=MinimumBoundingLabel(
            text= current_language['schedule_details_interval_label'],
            markup=True,
            pos_hint = {'x':.05, 'center_y':.75},)
        schedule_details_interval_label.ref='schedule_details_interval_label'

        schedule_details_interval_input_left=MarkupSpinner(
            disabled=False,
            text=f'[b][size=16]{service_details["default_interval"]}',
            markup=True,
            values=(f'[b][size=16]{i}' for i in service_details['intervals']),
            size_hint =(.15, .05),
            pos_hint = {'right':.325, 'center_y':.75},
            background_down='',
            background_color=palette('highlight',.85))
        schedule_details_interval_input_left.values.append('[b][size=16]Custom')
        schedule_details_interval_input_left.increment=service_details["default_increment"]
        self.widgets['schedule_details_interval_input_left']=schedule_details_interval_input_left
        schedule_details_interval_input_left.bind(text=self.filter_custom_interval)

        schedule_details_interval_input_right=MarkupSpinner(
            disabled=False,
            text=f'[b][size=16]{service_details["default_increment"]}',
            markup=True,
            values=('[b][size=16]Day(s)','[b][size=16]Week(s)','[b][size=16]Month(s)','[b][size=16]Year(s)'),
            size_hint =(.15, .05),
            pos_hint = {'right':.475, 'center_y':.75},
            background_down='',
            background_color=palette('highlight',.85))
        self.widgets['schedule_details_interval_input_right']=schedule_details_interval_input_right
        schedule_details_interval_input_right.bind(text=self.interval_translate)

        schedule_details_interval_input_left_textinput=TextInput(
            disabled=False,
            multiline=False,
            hint_text='Enter Custom Interval',
            font_size=32,
            pos_hint={'center_x':.5, 'center_y':.6},
            size_hint=(.8, .1),
            input_filter='int')
        self.widgets['schedule_details_interval_input_left_textinput']=schedule_details_interval_input_left_textinput
        schedule_details_interval_input_left_textinput.bind(focus=self.schedule_details_interval_input_left_textinput_clear)

        schedule_details_start_label=MinimumBoundingLabel(
            text= current_language['schedule_details_start_label'],
            markup=True,
            pos_hint = {'x':.05, 'center_y':.65},)
        schedule_details_start_label.ref='schedule_details_start_label'

        schedule_details_start_input=MarkupSpinner(
            disabled=False,
            text='[b][size=16]Not Currently Due',
            markup=True,
            values=('[b][size=16]Due Now','[b][size=16]Not Currently Due'),
            size_hint =(.3, .05),
            pos_hint = {'right':.475, 'center_y':.65},
            background_down='',
            background_color=palette('highlight',.85))
        self.widgets['schedule_details_start_input']=schedule_details_start_input

        schedule_details_expire_label=MinimumBoundingLabel(
            text= current_language['schedule_details_expire_label'],
            markup=True,
            pos_hint = {'x':.05, 'center_y':.55},)
        schedule_details_expire_label.ref='schedule_details_expire_label'

        schedule_details_expire_input_left=MarkupSpinner(
            disabled=False,
            text='[b][size=16]Schedule Does Not Expire',
            markup=True,
            values=('[b][size=16]1','[b][size=16]2','[b][size=16]3','[b][size=16]Custom','[b][size=16]No Expiration'),
            size_hint =(.30, .05),
            pos_hint = {'right':.475, 'center_y':.55},
            background_down='',
            background_color=palette('highlight',.85))
        self.widgets['schedule_details_expire_input_left']=schedule_details_expire_input_left
        schedule_details_expire_input_left.bind(text=self.filter_custom_expiration)

        schedule_details_expire_input_right=MarkupSpinner(
            disabled=False,
            text='[b][size=16]Year(s)',
            markup=True,
            values=('[b][size=16]Day(s)','[b][size=16]Week(s)','[b][size=16]Month(s)','[b][size=16]Year(s)','[b][size=16]No Expiration'),
            size_hint =(.15, .05),
            pos_hint = {'right':.475, 'center_y':.55},
            background_down='',
            background_color=palette('highlight',.85))
        self.widgets['schedule_details_expire_input_right']=schedule_details_expire_input_right
        schedule_details_expire_input_right.bind(text=self.filter_custom_expiration_right)

        schedule_details_expire_input_left_textinput=TextInput(
            disabled=False,
            multiline=False,
            hint_text='Enter Custom Expiration',
            font_size=32,
            pos_hint={'center_x':.5, 'center_y':.6},
            size_hint=(.8, .1),
            input_filter='int')
        self.widgets['schedule_details_expire_input_left_textinput']=schedule_details_expire_input_left_textinput
        schedule_details_expire_input_left_textinput.bind(focus=self.schedule_details_expire_input_left_textinput_clear)

        schedule_details_icon_label=MinimumBoundingLabel(
            text= current_language['schedule_details_icon_label'],
            markup=True,
            pos_hint = {'x':.05, 'center_y':.4},)
        schedule_details_icon_label.ref='schedule_details_icon_label'

        schedule_details_icon_input=ExpandableIcon(
            source=service_details['icon'],
            size_hint=(.15,.15),
            pos_hint = {'center_x':.35, 'center_y':.4},
            expanded_size=(1,1),
            expanded_pos = {'center_x':.5, 'center_y':.5},
            bg_color=palette('light_tint',0))
        self.widgets['schedule_details_icon_input']=schedule_details_icon_input
        schedule_details_icon_input.bind(expanded=self.schedule_details_icon_input_populate)
        schedule_details_icon_input.bind(animating=partial(general.stripargs,schedule_details_icon_input.clear_widgets))
        schedule_details_icon_input.bind(animating=lambda *args:setattr(schedule_details_icon_input,'color',(1,1,1,0)))
        schedule_details_icon_input.bind(animating=lambda *args:setattr(schedule_details_icon_input,'opacity',0))

        schedule_details_icon_input_x_icon=IconButton(
            source=overlay_x_icon_black,
            size_hint=(.08,.08),
            pos_hint={'x':.92,'y':.9})
        self.widgets['schedule_details_icon_input_x_icon']=schedule_details_icon_input_x_icon
        schedule_details_icon_input_x_icon.bind(on_release=schedule_details_icon_input.shrink)

        schedule_details_icon_select_layout=StackLayout(
            size_hint=(.9,.8),
            spacing=10,
            pos_hint={'center_x':.5,'center_y':.45})
        self.widgets['schedule_details_icon_select_layout']=schedule_details_icon_select_layout

        ##### middle #####

        schedule_details_seperator_line=Image(
            source=gray_seperator_line_vertical,
            allow_stretch=True,
            keep_ratio=False,
            size_hint =(.0015, .5),
            pos_hint = {'center_x':.5, 'center_y':.55})

        ##### right #####

        schedule_details_hidden_button=IconButton(
            color=(1,1,1,0),
            source=hidden_black,
            size_hint =(.07, .07),
            pos_hint = {'center_x':.8375, 'center_y':.825},
            disabled=True)
        self.widgets['schedule_details_hidden_button']=schedule_details_hidden_button
        schedule_details_hidden_button.bind(on_release=self.schedule_details_vendor_pin_visibility)

        schedule_details_custom_pin_label=MinimumBoundingLabel(
            text= current_language['schedule_details_custom_pin_label'],
            markup=True,
            pos_hint = {'x':.55, 'center_y':.75},)
        schedule_details_custom_pin_label.ref='schedule_details_custom_pin_label'

        schedule_details_custom_pin_input=RoundedButton(
            text=current_language['schedule_details_custom_pin_input'],
            size_hint =(.275, .07),
            pos_hint = {'right':.975, 'center_y':.75},
            background_normal='',
            background_color=palette('secondary',.85),
            markup=True,
            disabled=True)
        schedule_details_custom_pin_input.password=''
        schedule_details_title.ref='schedule_details_custom_pin_input'
        self.widgets['schedule_details_custom_pin_input']=schedule_details_custom_pin_input
        schedule_details_custom_pin_input.bind(on_release=self.set_vendor_pin)

        schedule_details_locked_label=MinimumBoundingLabel(
            text= current_language['schedule_details_locked_label'],
            markup=True,
            pos_hint = {'x':.55, 'center_y':.65},)
        schedule_details_locked_label.ref='schedule_details_locked_label'

        schedule_details_locked_input=MarkupSpinner(
            disabled=False,
            text=f'[b][size=16]{service_details["default_locked"]}',
            markup=True,
            values=('[b][size=16]Admin Pin Required','[b][size=16]Add Vendor Pin','[b][size=16]No Pin Required'),
            size_hint =(.3, .05),
            pos_hint = {'right':.975, 'center_y':.65},
            background_down='',
            background_color=palette('highlight',.85))
        self.widgets['schedule_details_locked_input']=schedule_details_locked_input
        schedule_details_locked_input.bind(text=self.schedule_details_locked_input_validate)

        schedule_details_vendor_name_label=MinimumBoundingLabel(
            text= current_language['schedule_details_vendor_name_label'],
            markup=True,
            pos_hint = {'x':.55, 'center_y':.55},)
        schedule_details_vendor_name_label.ref='schedule_details_vendor_name_label'

        schedule_details_vendor_name_input=TextInput(
            disabled=False,
            multiline=False,
            hint_text='Enter Vendor Name - (Optional)',
            size_hint =(.4, .05),
            pos_hint = {'x':.55, 'center_y':.50})
        self.widgets['schedule_details_vendor_name_input']=schedule_details_vendor_name_input
        schedule_details_vendor_name_input.bind(focus=self.schedule_details_vendor_name_input_clear)

        schedule_details_notes_label=MinimumBoundingLabel(
            text= current_language['schedule_details_notes_label'],
            markup=True,
            pos_hint = {'x':.55, 'center_y':.45},)
        schedule_details_notes_label.ref='schedule_details_notes_label'

        schedule_details_notes_input=AutoWrapTextInput(
            disabled=False,
            multiline=True,
            hint_text='Additional Schedule/Vendor Notes',
            size_hint =(.4, .15),
            pos_hint = {'x':.55, 'center_y':.35})
        self.widgets['schedule_details_notes_input']=schedule_details_notes_input
        schedule_details_notes_input.bind(focus=self.schedule_details_notes_input_clear)

        ##### bottom #####

        schedule_details_name_label=MinimumBoundingLabel(
            text= '[size=18][color=#000000][b][i]'+service_details['title'],
            markup=True,
            pos_hint = {'center_x':.5, 'center_y':.2},)

        save_button=RoundedButton(
            text=current_language['schedule_save_button'],
            size_hint =(.7, .1),
            pos_hint = {'center_x':.5, 'y':.05},
            background_down='',
            background_color=palette('neutral',.85),
            markup=True)
        schedule_details_title.ref='schedule_save_button'
        save_button.bind(on_release=self.animate_success_clear)
        save_button.bind(on_release=self.add_service)

        self.add_widget(schedule_details_title)
        self.add_widget(schedule_details_x_icon)
        self.add_widget(schedule_details_name_label_top)
        self.add_widget(schedule_details_interval_label)
        self.add_widget(schedule_details_interval_input_left)
        self.add_widget(schedule_details_interval_input_right)
        self.add_widget(schedule_details_locked_label)
        self.add_widget(schedule_details_locked_input)
        self.add_widget(schedule_details_hidden_button)
        self.add_widget(schedule_details_custom_pin_label)
        self.add_widget(schedule_details_custom_pin_input)
        self.add_widget(schedule_details_vendor_name_label)
        self.add_widget(schedule_details_vendor_name_input)
        self.add_widget(schedule_details_notes_label)
        self.add_widget(schedule_details_notes_input)
        self.add_widget(schedule_details_start_label)
        self.add_widget(schedule_details_start_input)
        self.add_widget(schedule_details_expire_label)
        self.add_widget(schedule_details_expire_input_left)
        # self.add_widget(schedule_details_expire_input_right)
        self.add_widget(schedule_details_icon_label)
        self.add_widget(schedule_details_icon_input)
        self.add_widget(schedule_details_seperator_line)
        self.add_widget(schedule_details_name_label)
        self.add_widget(save_button)

    def add_service(self,*args):
        w=self.widgets
        _strip=general.strip_markup

        _interval=_strip(w['schedule_details_interval_input_left'].text)
        _interval_coefficient=_strip(w['schedule_details_interval_input_right'].text)
        if _interval_coefficient=='Day(s)':
            _interval_coefficient=1
        elif _interval_coefficient=='Week(s)':
            _interval_coefficient=7
        elif _interval_coefficient=='Month(s)':
            _interval_coefficient=30
        elif _interval_coefficient=='Year(s)':
            _interval_coefficient=365
        _interval=str(timedelta(int(int(_interval)*_interval_coefficient)).days)

        _start_date=_strip(w['schedule_details_start_input'].text)
        if _start_date=='No Start Date':
            _start_date=0
        elif _start_date=='Current Date':
            _start_date=datetime.now().isoformat()
        elif _start_date=='Due Now':
            _start_date=datetime.now().isoformat()

        _expiration=_strip(w['schedule_details_expire_input_left'].text)
        _expiration_coefficient=_strip(w['schedule_details_expire_input_right'].text)
        if _expiration=='Schedule Does Not Expire':
            _expiration=''
        else:
            if _expiration_coefficient=='Day(s)':
                _expiration_coefficient=1
            elif _expiration_coefficient=='Week(s)':
                _expiration_coefficient=7
            elif _expiration_coefficient=='Month(s)':
                _expiration_coefficient=30
            elif _expiration_coefficient=='Year(s)':
                _expiration_coefficient=365
            _expiration=str(timedelta(int(int(_expiration)*_expiration_coefficient)).days)

        _service_date=_strip(w['schedule_details_start_input'].text)
        if _service_date!='Due Now':
            _service_date=datetime.now().isoformat()
        else:
            _service_date=''

        _increment=_strip(w['schedule_details_interval_input_right'].text)
        _increment=_increment.lower()[:-3]

        _security=_strip(w['schedule_details_locked_input'].text)
        if _security=='No Pin Required':
            _security=''
        elif _security=='Add Vendor Pin':
            _security='vendor'
        elif _security=='Admin Pin Required':
            _security='admin'

        _notes=_strip(w['schedule_details_notes_input'].text)
        if not _notes:
            _notes="Schedule Created"

        service_details={
            "title"              :  _strip(self.service_data['title']),
            "icon"               :  _strip(w['schedule_details_icon_input'].source),
            "increment"          :  _increment,
            "current_interval"   :  _interval,
            "creation_date"      :  datetime.now().isoformat(),
            "expiration"         :  _expiration,
            "service_date"       :  _service_date,
            "security"           :  _security,
            "vendor_name"        :  _strip(w['schedule_details_vendor_name_input'].text),
            "vendor_pin"         :  _strip(w['schedule_details_custom_pin_input'].password),
            "notes"              :  {str(datetime.now()):_notes}
            }

        App.get_running_app().context_screen.get_screen('main').save_service_details(service_details)
        App.get_running_app().context_screen.get_screen('main').load_service_details()

    def interval_translate(self,_,text,*args):
        w=self.widgets
        t=general.strip_markup(text)
        x=w['schedule_details_interval_input_left']
        xi=x.increment
        xt=general.strip_markup(x.text)
        if t == xi:
            return
        #traslation neccessary
        key=f"{xi}_{t}"
        d={
            "Day(s)_Week(s)"    :  .143,
            "Day(s)_Month(s)"   :  .033,
            "Day(s)_Year(s)"    :  .00273972602,
            "Week(s)_Day(s)"    :   7,
            "Week(s)_Month(s)"  :  .25,
            "Week(s)_Year(s)"   :  .01923076923,
            "Month(s)_Day(s)"   :   30,
            "Month(s)_Week(s)"  :   4,
            "Month(s)_Year(s)"  :  .08333333333,
            "Year(s)_Day(s)"    :   365,
            "Year(s)_Week(s)"   :   52,
            "Year(s)_Month(s)"  :   12
        }
        Clock.schedule_once(lambda *args:setattr(x,'text','[b][size=16]'+str(max(int(float(xt)*d[key]),1))))
        Clock.schedule_once(lambda *args:setattr(x,'increment',t))
        Clock.schedule_once(self.interval_input_left_value_setter)

    def interval_input_left_value_setter(self,*args):
        w=self.widgets
        x=w['schedule_details_interval_input_left']
        t=general.strip_markup(w['schedule_details_interval_input_right'].text)
        d={
            "Day(s)"     :  ["1","2","3","4","5","6","7"],
            "Week(s)"    :  ["1","2","3","4"],
            "Month(s)"   :  ["1","2","3","4","5","6","7","8","9","10","11","12"],
            "Year(s)"    :  ["1","2","3"],
        }
        _vals=d[t]
        _vals.append('Custom')
        x.values=(f'[b][size=16]{i}' for i in _vals)

    def filter_custom_interval(self,_,text,*args):
        w=self.widgets
        x=w['schedule_details_interval_input_left']
        t=general.strip_markup(text)
        kb=w['schedule_details_interval_input_left_textinput']
        if t!='Custom':
            return
        self.add_widget(kb)
        kb.focused=True

    def schedule_details_interval_input_left_textinput_clear(self,_,focused,*args):
        if focused:
            return
        w=self.widgets
        x=w['schedule_details_interval_input_left']
        ti=w['schedule_details_interval_input_left_textinput']
        t=ti.text
        if len(t)>8:
            t=t[:8]
        t=f'[b][size=16]{t}'
        Clock.schedule_once(lambda *args:setattr(x,'text',t))
        ti.text=''
        ti.parent.remove_widget(ti)

    def filter_custom_expiration(self,_,text,*args):
        w=self.widgets
        x=w['schedule_details_expire_input_left']
        z=w['schedule_details_expire_input_right']
        t=general.strip_markup(text)
        kb=w['schedule_details_expire_input_left_textinput']
        if t in ('Schedule Does Not Expire','No Expiration') :
            x.pos_hint['right']=.475
            x.size_hint_x=.3
            z.text='[b][size=16]Year(s)'
            if z in self.children:
                self.remove_widget(z)
            if t=='No Expiration':
                x.text='[b][size=16]Schedule Does Not Expire'
            return
        else:
            x.pos_hint['right']=.325
            x.size_hint_x=.15
            if z not in self.children:
                self.add_widget(z)

        if t!='Custom':
            return
        self.add_widget(kb)
        kb.focused=True

    def schedule_details_expire_input_left_textinput_clear(self,_,focused,*args):
        if focused:
            return
        w=self.widgets
        x=w['schedule_details_expire_input_left']
        ti=w['schedule_details_expire_input_left_textinput']
        t=ti.text
        if len(t)>8:
            t=t[:8]
        t=f'[b][size=16]{t}'
        Clock.schedule_once(lambda *args:setattr(x,'text',t))
        ti.text=''
        ti.parent.remove_widget(ti)

    def filter_custom_expiration_right(self,_,text,*args):
        w=self.widgets
        x=w['schedule_details_expire_input_right']
        z=w['schedule_details_expire_input_left']
        t=general.strip_markup(text)
        if t!='No Expiration':
            return
        z.text='[b][size=16]Schedule Does Not Expire'

    def set_vendor_pin(self,*args):
        def set_pin(*args):
            pl=PinLock(set_pin=True,callback=confirm_pin)
            pl.widgets['title'].text='[size=20][color=#ffffff][b]Enter New Pin'
            self.add_widget(pl)

        def confirm_pin(**kwargs):
            if not 'alt_pin' in kwargs:
                App.get_running_app().notifications.toast('Error','warning')
                return
            pin=kwargs.pop('alt_pin')
            pl=PinLock(alt_pin=pin,callback=save_pin)
            pl.widgets['title'].text='[size=20][color=#ffffff][b]Confirm New Pin'
            self.add_widget(pl)

        def save_pin(pin,*args):
            w=self.widgets
            b=w['schedule_details_custom_pin_input']
            b.password=pin
            b.text=f'[b][size=20][color=#000000]* * * * * *'
            hb=w['schedule_details_hidden_button']
            hb.color=(1,1,1,1)
            hb.disabled=False

        set_pin()

    def schedule_details_locked_input_validate(self,button,text,*args):
        w=self.widgets
        b=w['schedule_details_custom_pin_input']
        hb=w['schedule_details_hidden_button']
        hb.color=(1,1,1,0)
        hb.disabled=True
        if text=='[b][size=16]Add Vendor Pin':
            b.disabled=False
            b.password=''
            b.bg_color=palette('base',.85)
            b.text="[size=20][b][color=#000000]Create Pin"
        else:
            b.disabled=True
            b.bg_color=palette('secondary',.85)
            b.text=current_language['schedule_details_custom_pin_input']

        b.color_swap()

    def on_dim_saturation(self,*args):
        self.dim_color.rgba=palette('dark_shade',self.dim_saturation)

    def on_parent(self,*args):
        parent=self.parent
        if not parent:
            return
        if self.fade_in:
            Clock.schedule_once(self.animate_dim,1.5)
            if self.target_size_hint:
                self.size_hint=(0,0)
                Clock.schedule_once(self.animate_size,2.25)

    def animate_size(self,*args):
        a=Animation(size_hint=self.target_size_hint,d=.5,t='out_sine')
        a.bind(on_complete=self.populate_details)
        a.start(self)

    def animate_dim(self,*args):
        Animation(dim_saturation=.9,d=1).start(self)

    def animate_success_clear(self,*args):
        self.clear_widgets()
        a=Animation(size_hint=(0,0),d=.5,t='in_back')
        a.bind(on_complete=self.clear)
        a.start(self)
        Animation(dim_saturation=0,d=.5).start(self)

    def clear(self,*args,cb=False):
        #cb == call self.callback if True
        self.dim_saturation=0
        if hasattr(self,'parent'):
            if self.parent is None:
                return
            self.parent.remove_widget(self)
        if self.call_back and cb:
            self.call_back()

    def on_touch_down(self, touch):
        super(ScheduleCreationLayout, self).on_touch_down(touch)
        return True

    def on_touch_up(self, touch):
        if self.collide_point(*touch.pos):
            return True
        super(ScheduleCreationLayout, self).on_touch_up(touch)
        return True

    def schedule_details_icon_input_populate(self,*args):
        darken=Animation(rgba=palette('light_tint',.95),d=.25)
        lighten=Animation(rgba=palette('light_tint',.0),d=.05)
        fade_in=Animation(opacity=1,d=.75)
        w=self.widgets
        icon=w['schedule_details_icon_input']
        layout=w['schedule_details_icon_select_layout']
        layout.clear_widgets()
        icon.clear_widgets()
        fade_in.start(icon)
        if icon.expanded:
            self.remove_widget(icon)
            self.add_widget(icon)#needed to draw children on top
            darken.start(icon.shape_color)
            _icons_to_add=[]
            icon_dir=pathlib.Path('media/schedule_icons')
            for i in os.listdir(icon_dir):
                _icons_to_add.append(pathlib.Path(icon_dir).joinpath(pathlib.Path(i)))
            ratio=icon.width/8
            for i in _icons_to_add:
                pib=PathIconButton(
                        source=str(i),
                        size_hint=(None,None),
                        size=(ratio,ratio))
                pib.bind(on_release=icon.shrink)
                pib.bind(on_release=lambda *args,i=str(i):setattr(icon,'source',i))
                layout.add_widget(pib)
            all_widgets=[
                w['schedule_details_icon_input_x_icon'],
                w['schedule_details_icon_select_layout']
                ]
            for i in all_widgets:
                icon.add_widget(i)
        elif not icon.expanded:
            icon.color=(1,1,1,1)
            lighten.start(icon.shape_color)

    def schedule_details_vendor_name_input_clear(self,button,focused,*args):
        w=self.widgets
        vni=w['schedule_details_vendor_name_input']
        p=vni.parent
        if p:
            p.remove_widget(vni)
            p.add_widget(vni)
        if focused:
            vni.font_size=32
            vni.pos_hint={'center_x':.5, 'center_y':.6}
            vni.size_hint=(.8, .1)
        else:
            vni.font_size=15
            vni.pos_hint={'x':.55, 'center_y':.50}
            vni.size_hint=(.4, .05)

    def schedule_details_notes_input_clear(self,button,focused,*args):
        w=self.widgets
        ni=w['schedule_details_notes_input']
        p=ni.parent
        if p:
            p.remove_widget(ni)
            p.add_widget(ni)
        if focused:
            ni.font_size=32
            ni.pos_hint={'center_x':.5, 'center_y':.7}
            ni.size_hint=(.8, .35)
        else:
            ni.font_size=15
            ni.pos_hint={'x':.55, 'center_y':.35}
            ni.size_hint=(.4, .15)

    def schedule_details_vendor_pin_visibility(self,*args):
        w=self.widgets
        hb=w['schedule_details_hidden_button']
        pib=w['schedule_details_custom_pin_input']
        if hb.source==visible_black:
            hb.source=hidden_black
            pib.text='[b][size=20][color=#000000]* * * * * *'
        else:
            hb.source=visible_black
            pib.text=f"[size=20][b][color=#000000]{pib.password}"

class OutlineModalScroll(ScrollView):
    def __init__(self,bg_color=palette('dark_shade',1), **kwargs):
        super(OutlineModalScroll,self).__init__(**kwargs)
        self.x_btn=IconButton(
            source=overlay_x_icon,
            size_hint=(.08,.08),
            pos_hint={'x':.92,'y':.88})
        self.x_btn.bind(on_release=self.clear)
        self.bind(pos=self.update_rect)
        self.bind(size=self.update_rect)
        with self.canvas:
                    Color(*bg_color)
                    self.rect = Rectangle(pos=self.center,size=(self.width,self.height))

    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = (self.size[0], self.size[1])

    def on_parent(self,_self,parent):
        if parent:
            self.scroll_y=1
            self.last_parent=parent
            self._dim=LabelColor(bg_color=palette('dark_shade',.65))
            parent.add_widget(self._dim)
            Clock.schedule_once(lambda *args:parent.add_widget(self.x_btn))
        else:
            if self._dim in self.last_parent.children:
                self.last_parent.remove_widget(self._dim)
            if self.x_btn in self.last_parent.children:
                self.last_parent.remove_widget(self.x_btn)

    def clear(self,*args):
        if hasattr(self,'parent'):
            if self.parent is None:
                return
            self.parent.remove_widget(self)

    def on_touch_down(self, touch):
        super(OutlineModalScroll,self).on_touch_down(touch)
        return True

    def on_touch_up(self, touch):
        if super(OutlineModalScroll,self).on_touch_up(touch):
            return True
        self.clear()
        return False

class FloatImage(FloatLayout,Image):
    pass

class ServicesIconButton(IconButton):
    def __init__(self,data, **kwargs):
        super(ServicesIconButton,self).__init__(**kwargs)
        self.data=data
        self.pos_hint={'center_x':.5,'center_y':.5}

    def on_state(self,button,state,*args):
        if state=='down':
            self.color=palette('primary',.65)
            self.add_widget(CirclePulseEmit(0,style='quick'))
        else:
            self.color=palette('light_tint',1)

class PathIconButton(IconButton):
    def __init__(self, **kwargs):
        super(PathIconButton,self).__init__(**kwargs)

    def on_state(self,button,state,*args):
        if state=='down':
            self.color=palette('primary',.65)
            self.add_widget(CirclePulseEmit(0,style='quick'))
        else:
            self.color=palette('light_tint',1)

#<<<<<<<<<< SCREENS >>>>>>>>>>#

class ControlGrid(Screen):
    def fans_switch(self,button,*args):
        if button.state == 'down':
            logic.fs.moli['exhaust']=1
            logic.fs.moli['mau']=1
        elif button.state == 'normal':
            logic.fs.moli['exhaust']=0
            logic.fs.moli['mau']=0

    def lights_switch(self,button,*args):
        if button.state == 'down':
            logic.fs.moli['lights']=1
        elif button.state == 'normal':
            logic.fs.moli['lights']=0

    def _keyboard_closed(self):
        logger.info("main.py ControlGrid _keyboard_closed(): keyboard unbound")

    def __init__(self, **kwargs):
        super(ControlGrid, self).__init__(**kwargs)
        self.cols = 2
        self.widgets={}
        self.ud={}
        bg_image = Image(source=background_image, allow_stretch=True, keep_ratio=False)
        self._keyboard=Window.request_keyboard(self._keyboard_closed, self, 'text')
        self.current_section='main'
        self.scheduled_services=[]
        self.schedule_dock_close_anim=Animation(pos_hint={'center_x':1.3},d=.5,t='in_out_back')
        self.schedule_dock_open_anim=Animation(pos_hint={'center_x':.825},d=.5,t='out_back')

        self.value_up=Animation(value=1000,d=18,t='in_out_quad')
        self.value_down=Animation(value=0,d=1,t='in_out_circ')
        self.fade=Animation(opacity=0,d=1)
        self._fade_in=Animation(opacity=1,d=.5)

        def remove_ramp(*args):
            if 'ramp_progress' in self.widgets:
                self.remove_widget(self.widgets['ramp_progress'])
                del self.widgets['ramp_progress']
            if 'event_bar' in self.ud:
                Clock.unschedule(self.ud['event_bar'])
                del self.ud['event_bar']
            if 'ramp_text' in self.widgets:
                self.remove_widget(self.widgets['ramp_text'])
                del self.widgets['ramp_text']
        self.fade.bind(on_complete=remove_ramp)

        fans=RoundedToggleButton(text=current_language['fans'],
                    size_hint =(.45, .5),
                    pos_hint = {'x':.03, 'y':.4},
                    background_down='',
                    background_color=palette('accent',.85),
                    markup=True)
        self.widgets['fans']=fans
        fans.ref='fans'
        fans.bind(state=self.fans_switch)
        fans.bind(state=self.ramp_animate)

        lights=RoundedToggleButton(text=current_language['lights'],
                    size_hint =(.45, .5),
                    pos_hint = {'x':.52, 'y':.4},
                    background_down='',
                    background_color=palette('primary',.85),
                    markup=True)
        self.widgets['lights']=lights
        lights.ref='lights'
        lights.bind(state=self.lights_switch)

        clock_label=ClockText(
            markup=True,
            size_hint =(.475,.22),
            pos_hint = {'center_x':.5, 'center_y':.265},
            bg_color=palette('secondary',.65))
        self.widgets['clock_label']=clock_label
        clock_label.bind(on_release=self.widget_fade)

        widget_carousel=AnimatedCarousel(
            size_hint =(.475,.22),
            pos_hint = {'center_x':.5, 'center_y':.265},
            loop=True,
            ignore_perpendicular_swipes=True)
        self.widgets['widget_carousel']=widget_carousel

        clock_set_layout=RelativeLayoutColor(bg_color= palette('secondary',.85))

        hour_wheel=BigWheelClock(
            size_hint =(.25, .9),
            pos_hint = {'x':.0, 'center_y':.5},
            direction='top',
            loop=True)
        self.widgets['hour_wheel']=hour_wheel

        for i in range(12):
            _hour=Label(
                text=f'[size=80][b][color=c0c0c0]{i+1}',
                markup=True,)
            hour_wheel.add_widget(_hour)

        delimiter_dots=Label(
            size_hint =(.25, .9),
            pos_hint = {'x':.2, 'center_y':.5},
            text=f'[size=80][b][color=c0c0c0]:',
            markup=True)

        minute_wheel=BigWheelClock(
            size_hint =(.25, .9),
            pos_hint = {'x':.4, 'center_y':.5},
            direction='top',
            loop=True)
        self.widgets['minute_wheel']=minute_wheel

        for i in range(60):
            i=str(i)
            _minute=Label(
                text=f'[size=80][b][color=c0c0c0]{i.zfill(2)}',
                markup=True)
            minute_wheel.add_widget(_minute)

        ampm_wheel=BigWheelClock(
            size_hint =(.25, .9),
            pos_hint = {'x':.7, 'center_y':.5},
            direction='top',
            loop=True,
            y_reduction=70)
        self.widgets['ampm_wheel']=ampm_wheel

        for i in ['AM','PM','AM','PM']:
            _ampm=Label(
                text=f'[size=60][b][color=c0c0c0]{i}',
                markup=True)
            ampm_wheel.add_widget(_ampm)

        messenger_button=Messenger(
            bg_color=palette('neutral',.3),
            size_hint =(1,1),
            pos_hint = {'center_x':.5, 'center_y':.5})
        self.widgets['messenger_button']=messenger_button
        fans.bind(state=self.widgets['messenger_button'].evoke)
        lights.bind(state=self.widgets['messenger_button'].evoke)

        message_label=Label(
            text=current_language['message_label'],
            markup=True,
            size_hint =(1,1),
            pos_hint = {'center_x':.5, 'center_y':.5},
            halign='center',
            valign='center')
        message_label.bind(size=message_label.setter('text_size'))
        self.widgets['message_label']=message_label
        message_label.ref='message_label'

        settings_button=RoundedButton(
                    size_hint =(.18, .1),
                    pos_hint = {'x':.02, 'y':.015},
                    background_down='',
                    background_color=palette('light_tint',.9),
                    markup=True)
        self.widgets['settings_button']=settings_button
        settings_button.bind(on_release=self.open_settings)

        seperator_line=Image(source=gray_seperator_line,
                    allow_stretch=True,
                    keep_ratio=False,
                    size_hint =(.98, .001),
                    pos_hint = {'x':.01, 'y':.13})
        self.widgets['seperator_line']=seperator_line

        menu_icon=Image(source=settings_icon,
                    allow_stretch=True,
                    keep_ratio=False,
                    size_hint =(.135, .038),
                    pos_hint = {'x':.043, 'y':.045})
        self.widgets['menu_icon']=menu_icon
        menu_icon.center=settings_button.center

        trouble_button=IconButton(source=trouble_icon_dull, allow_stretch=True, keep_ratio=True)
        trouble_button.size_hint =(.10, .10)
        trouble_button.pos_hint = {'x':.75, 'y':.02}
        self.widgets['trouble_button']=trouble_button
        trouble_button.bind(on_release=self.open_trouble)
        trouble_button.color=palette('light_tint',.15)

        schedule_button=IconButton(source=schedule_icon_image, allow_stretch=True, keep_ratio=True)
        schedule_button.size_hint =(.10, .10)
        schedule_button.pos_hint = {'x':.61, 'y':.02}
        self.widgets['schedule_button']=schedule_button
        schedule_button.bind(on_release=self.schedule_icon_func)
        schedule_button.color=palette('light_tint',.65)

        msg_icon=IconButton(source=msg_icon_image, allow_stretch=True, keep_ratio=True)
        msg_icon.size_hint =(.10, .10)
        msg_icon.pos_hint = {'x':.47, 'y':.02}
        self.widgets['msg_icon']=msg_icon
        msg_icon.bind(on_release=self.msg_icon_func)
        msg_icon.color=palette('light_tint',.65)
        msg_icon.widgets={}
        Clock.schedule_once(self.start_nb_clock,5)

        fs_logo=IconButton(source=logo,
                size_hint_x=.1,
                size_hint_y=.1,
                allow_stretch=True,
                keep_ratio=True,
                pos_hint = {'x':.89, 'y':.02},
                color=palette('neutral'))
        self.widgets['fs_logo']=fs_logo
        fs_logo.bind(on_release=self.about_func)

        overlay_menu=Popup(
            size_hint=(.8, .8),
            background = 'atlas://data/images/defaulttheme/bubble',
            title_color=[0, 0, 0, 1],
            title_size='38',
            title_align='center',
            separator_color=palette('highlight', .5))
        overlay_menu.bind(on_touch_down=overlay_menu.dismiss)
        self.widgets['overlay_menu']=overlay_menu

        overlay_layout=FloatLayout()
        self.widgets['overlay_layout']=overlay_layout

        overlay_x=IconButton(
            source=overlay_x_icon,
            size_hint=(.1,.1),
            pos_hint={'x':.95,'y':.98})
        overlay_x.bind(on_release=overlay_menu.dismiss)
        self.widgets['overlay_x']=overlay_x

        container=FloatLayout(
            size_hint =(1, 1),
            pos_hint = {'center_x':.5, 'center_y':.5})
        self.widgets['container']=container

        tray_container=FloatLayout(
            size_hint =(1, 1),
            pos_hint = {'center_x':.5, 'center_y':.5})
        self.widgets['tray_container']=tray_container

        ########## schedule widgets ##########

        schedule_box=RoundedColorLayoutModal(
            bg_color=palette('light_tint',.9),
            size_hint =(.95, .825),
            pos_hint = {'center_x':.5, 'center_y':.565},)
        self.widgets['schedule_box']=schedule_box

        schedule_x=IconButton(
            source=overlay_x_icon_black,
            size_hint=(.1,.1),
            pos_hint={'x':.915,'y':.89})
        schedule_x.bind(on_release=self.schedule_icon_func)
        self.widgets['schedule_x']=schedule_x

        schedule_title=Label(
            text=current_language['schedule_title'],
            markup=True,
            size_hint =(.4, .05),
            pos_hint = {'x':.05, 'center_y':.925},)
        self.widgets['schedule_title']=schedule_title
        schedule_title.ref='schedule_title'

        schedule_box_layout=ServicesStackLayout(
            size_hint=(.9,.8),
            spacing=[20,35],
            pos_hint={'center_x':.5,'center_y':.45})
        self.widgets['schedule_box_layout']=schedule_box_layout

        schedule_dock=DenseRoundedColorLayout(
            bg_color=palette('secondary',.95),
            size_hint =(.6, .725),
            pos_hint = {'center_x':1.3, 'center_y':.51})
        self.widgets['schedule_dock']=schedule_dock
        schedule_dock.bind(on_release=self.schedule_dock_handle_func)

        schedule_dock_handle=RoundedButton(
            size_hint =(.055,.425),
            pos_hint = {'center_x':.06, 'center_y':.5},
            background_down='',
            background_color=palette('light_tint',.9),
            markup=True)
        self.widgets['schedule_dock_handle']=schedule_dock_handle
        schedule_dock_handle.bind(on_release=self.schedule_dock_handle_func)

        schedule_dock_handle_lines=Image(
            source=menu_lines_vertical,
            allow_stretch=True,
            keep_ratio=False,
            size_hint =(.0325,.325),
            pos_hint = {'center_x':.06, 'center_y':.5})
        self.widgets['schedule_dock_handle_lines']=schedule_dock_handle_lines

        schedule_dock_scroll=OutlineScroll(
            size_hint =(.65,.9),
            pos_hint = {'x':.125, 'center_y':.5},
            bg_color=palette('secondary',.85),
            bar_width=8,
            bar_color=palette('primary',.35),
            bar_inactive_color=palette('primary',.15),
            do_scroll_y=True,
            do_scroll_x=False)
        self.widgets['schedule_dock_scroll']=schedule_dock_scroll

        schedule_dock_scroll_layout=GridLayout(
            cols=1,
            spacing=10,
            size_hint_y=None,
            padding=5)
        schedule_dock_scroll_layout.bind(minimum_height=lambda layout,min_height:setattr(layout,'height',min_height))
        self.widgets['schedule_dock_scroll_layout']=schedule_dock_scroll_layout

        schedule_add_button=IconButton(source=add_schedule_icon, allow_stretch=True, keep_ratio=True)
        schedule_add_button.size_hint =(.10, .10)
        schedule_add_button.pos_hint = {'x':.61, 'y':.02}
        self.widgets['schedule_add_button']=schedule_add_button
        schedule_add_button.bind(on_release=self.schedule_dock_handle_func)
        schedule_add_button.color=palette('light_tint',.65)

        schedule_edit_button=IconButton(source=edit_schedule_icon, allow_stretch=True, keep_ratio=True)
        schedule_edit_button.size_hint =(.10, .10)
        schedule_edit_button.pos_hint = {'x':.75, 'y':.02}
        self.widgets['schedule_edit_button']=schedule_edit_button
        schedule_edit_button.bind(on_release=self.schedule_edit_icon_func)
        schedule_edit_button.color=palette('light_tint',.65)

        add_service_icon=ServicesIconButton(
            source=add_schedule_icon,
            size_hint=(None,None),
            data={'title':"Add Schedule"})
        self.widgets['add_service_icon']=add_service_icon
        add_service_icon.bind(on_release=self.schedule_dock_handle_func)

        schedule_box.add_widget(schedule_title)
        schedule_box.add_widget(schedule_box_layout)

        overlay_menu.add_widget(overlay_layout)
        clock_set_layout.add_widget(hour_wheel)
        clock_set_layout.add_widget(delimiter_dots)
        clock_set_layout.add_widget(minute_wheel)
        clock_set_layout.add_widget(ampm_wheel)
        widget_carousel.add_widget(clock_set_layout)
        messenger_button.add_widget(message_label)
        widget_carousel.add_widget(messenger_button)

        container.add_widget(fans)
        container.add_widget(lights)
        container.add_widget(clock_label)

        tray_container.add_widget(settings_button)
        tray_container.add_widget(seperator_line)
        tray_container.add_widget(menu_icon)
        tray_container.add_widget(trouble_button)
        tray_container.add_widget(schedule_button)
        tray_container.add_widget(msg_icon)
        tray_container.add_widget(fs_logo)

        schedule_dock_scroll.add_widget(schedule_dock_scroll_layout)

        schedule_dock.add_widget(schedule_dock_handle)
        schedule_dock.add_widget(schedule_dock_handle_lines)
        schedule_dock.add_widget(schedule_dock_scroll)

        self.add_widget(bg_image)
        self.add_widget(container)
        self.add_widget(tray_container)
        self.add_widget(schedule_dock)

    def ramp_animate(self,button,*args):
        fb=self.widgets['fans'] #fans button

        def fade_out(*args):
            if 'ramp_progress' not in self.widgets:
                return
            if 'ramp_text' not in self.widgets:
                return

            self.fade.cancel(self.widgets['ramp_progress'])
            self.fade.cancel(self.widgets['ramp_text'])
            self.fade.start(self.widgets['ramp_progress'])
            self.fade.start(self.widgets['ramp_text'])
            self.value_up.cancel(self.widgets['ramp_progress'])
            if self.widgets['ramp_progress'].value<1000:
                self.value_down.start(self.widgets['ramp_progress'])


        def fade_in(*args):
            if 'ramp_progress' not in self.widgets:
                ramp_progress=CircularProgressBar()
                ramp_progress.widget_size=int(fb.height*.9)
                ramp_progress._background_colour=(0,0,0,0)
                ramp_progress._progress_colour=palette('secondary',.85)
                self.widgets['ramp_progress']=ramp_progress
                ramp_progress.pos=self.widgets['fans'].center
                ramp_progress.opacity=0
                self.add_widget(ramp_progress)
            self.value_down.cancel(self.widgets['ramp_progress'])
            self.value_up.start(self.widgets['ramp_progress'])

            if 'ramp_text' not in self.widgets:
                ramp_text=Label(
                    text=current_language['ramp_text'],
                    markup=True,
                    pos = (
                        fb.right-fb.width/2-50,
                        fb.top-fb.height/5*3-50))
                self.widgets['ramp_text']=ramp_text
                ramp_text.ref='ramp_text'
                ramp_text.opacity=0
                self.add_widget(ramp_text)

            def progress_bar_update(dt,*args):
                self.widgets['ramp_progress'].pos=self.widgets['fans'].center
                self.widgets['ramp_text'].pos=(
                    fb.right-fb.width/2-self.widgets['ramp_text'].width/2,
                    fb.top-fb.height/5*3-self.widgets['ramp_text'].height/2)
                if self.widgets['ramp_progress'].value >= 1000: # Checks to see if progress_bar.value has met 1000
                    fade_out()
                    return False # Returning False schedule is canceled and won't repeat

            if 'event_bar' not in self.ud:
                Clock.schedule_interval(progress_bar_update,.01)
                self.ud['event_bar'] = progress_bar_update

            self.fade.cancel(self.widgets['ramp_progress'])
            self.fade.cancel(self.widgets['ramp_text'])
            if self.widgets['ramp_text'].opacity<1:
                self._fade_in.start(self.widgets['ramp_text'])
            if self.widgets['ramp_progress'].opacity<1:
                self._fade_in.start(self.widgets['ramp_progress'])

        if button.state=='normal':
            #if fans are turned off
            fade_out()
        if button.state=='down':
            #if fans are turned on
            fade_in()

    def widget_fade(self,*args):
        if not (self.widgets['clock_label'].opacity==0 or self.widgets['clock_label'].opacity==1):
            return
        if self.widgets['clock_label'].time_size==35 or self.widgets['clock_label'].time_size==120:
            if self.widgets['widget_carousel'] not in self.children:
                self.update_msg_card()
                self.add_widget(self.widgets['widget_carousel'],-2)
                self.widgets['widget_carousel'].index=0
                self.widgets['widget_carousel'].fade_in()
                self.widgets['hour_wheel'].set_index(cat='hour')
                self.widgets['minute_wheel'].set_index(cat='minute')
                self.widgets['ampm_wheel'].set_index(cat='ampm')
            else:
                if self.widgets['widget_carousel'].opacity!=1:
                    return
                self.widgets['widget_carousel'].fade_out()

    def open_settings(self,button):
        self.parent.transition = SlideTransition(direction='right')
        self.manager.current='settings'
    def open_trouble(self,button):
        self.parent.transition = SlideTransition(direction='down')
        self.manager.current='trouble'
    def update_msg_card(self,*args):
        self.widgets['message_label'].text=f'[size=50][color=#ffffff][b]{messages.active_messages[0].card}'

    def msg_icon_func (self,button):
        w=self.widgets
        if not w['messenger_button'].docked:
            #should be inaccessible..
            return
        if w['clock_label'].time_size==120 and w['clock_label'].opacity==1:
            #nothing animated, all set in standard positions
            if self.current_section=='schedule':
                #scheduler opened
                w['clock_label'].animate()
                self.widget_fade()
                self.widgets['widget_carousel'].index=1
                w['messenger_button'].undock()
                return
            w['clock_label'].animate()
            self.widget_fade()
            self.widgets['widget_carousel'].index=1
            Clock.schedule_once(w['messenger_button'].undock,.5)
        if w['clock_label'].time_size==120 and w['clock_label'].opacity==0:
            #evoke message triggered
            w['clock_label']._delete_clock()
            w['messenger_button'].cancel_evoke_fade_in()
            w['clock_label'].animated=True
            w['clock_label'].rotate()
            w['clock_label'].slide()
            w['clock_label'].text_shrink()
            w['clock_label'].morph()
            w['clock_label'].add_parent()
            Clock.schedule_once(w['clock_label'].fade_in,.25)
            w['messenger_button'].undock()
        if w['clock_label'].time_size==35 and w['clock_label'].opacity==1:
            #widget carousel being accessed
            w['clock_label']._delete_clock()
            if w['widget_carousel'].index==0:
                #carousel current is clock setter
                w['widget_carousel'].load_slide(w['messenger_button'])
                Clock.schedule_once(w['messenger_button'].undock,.55)
            elif w['widget_carousel'].index==1:
                #carousel current is message button
                w['messenger_button'].undock()

    def schedule_icon_func (self,*args):
        container_fade_out=Animation(opacity=0,d=.5)
        container_fade_in=Animation(opacity=1,d=.5)
        w=self.widgets
        container=w['container']

        def _swap_widgets(*args):
            container.clear_widgets()
            Clock.schedule_once(self.load_service_details,0)
            if App.get_running_app().limited:
                if w['schedule_x'] in w['schedule_box'].children:
                    w['schedule_box'].remove_widget(w['schedule_x'])
            else:
                if w['schedule_x'] not in w['schedule_box'].children:
                    w['schedule_box'].add_widget(w['schedule_x'])
            container.add_widget(w['schedule_box'])
            container_fade_in.start(container)

        if self.current_section=='main':
            self.current_section='schedule'
            self.schedule_tray_widget_swap('in')
            container_fade_out.start(container)
            container_fade_out.bind(on_complete=_swap_widgets)
        else:
            self.current_section='main'
            self.schedule_tray_widget_swap('out')
            container_fade_out.start(container)
            container_fade_out.bind(on_complete=self.load_active_container)

    def schedule_dock_handle_func(self,*args):
        d=self.widgets['schedule_dock']
        if d.pos_hint['center_x']==.825:
            self.schedule_dock_close_anim.start(self.widgets['schedule_dock'])
        elif d.pos_hint['center_x']==1.3:
            self.schedule_scroll_populate()
            self.schedule_dock_open_anim.start(self.widgets['schedule_dock'])

    def schedule_edit_icon_func (self,*args):
        if App.get_running_app().admin_mode_start>time.time():
            pass
        else:
            Window.add_widget(PinLock(partial(print,'here')))

    def schedule_tray_widget_swap (self,mode='out'):
        container_fade_out=Animation(opacity=0,d=.5)
        container_fade_in=Animation(opacity=1,d=.5)
        w=self.widgets
        container=w['tray_container']

        def _swap_widgets_in(*args):
            container.clear_widgets()
            in_widgets=[
                w['settings_button'],
                w['seperator_line'],
                w['menu_icon'],
                w['msg_icon'],
                w['schedule_add_button'],
                w['schedule_edit_button'],
                w['fs_logo']]
            for i in in_widgets:
                container.add_widget(i)
            container_fade_in.start(container)

        def _swap_widgets_out(*args):
            container.clear_widgets()
            out_widgets=[
                w['settings_button'],
                w['seperator_line'],
                w['menu_icon'],
                w['trouble_button'],
                w['schedule_button'],
                w['msg_icon'],
                w['fs_logo']]
            for i in out_widgets:
                container.add_widget(i)
            container_fade_in.start(container)

        container_fade_out.start(container)
        if mode=='in':
            container_fade_out.bind(on_complete=_swap_widgets_in)
        if mode=='out':
            container_fade_out.bind(on_complete=_swap_widgets_out)

    def schedule_scroll_populate(self,*args):
        w=self.widgets
        layout=w['schedule_dock_scroll_layout']
        layout.scroll_y=1
        layout.clear_widgets()
        services_path='schedule/available_services.json'
        try:
            with open(services_path,'r') as f:
                services=json.load(f)
        except OSError:
            return
        try:
            for i in services.values():
                card=RoundedColorLayout(
                    bg_color=palette('light_tint',.85),
                    size_hint =(1, None),
                    height=150)
                title=MinimumBoundingLabel(
                    text=f"[color=#000000][size=24][b]{i['title']}",
                    pos_hint = {'center_x':.525, 'center_y':.7},
                    markup=True)
                icon=Image(
                    source=i['icon'],
                    size_hint =(.4,.4),
                    pos_hint={'center_x':.1,'center_y':.7})
                add_button=RoundedButton(
                    text='[color=#ffffff][size=18]Add Service',
                    size_hint =(.7, .3),
                    pos_hint = {'center_x':.5, 'y':.05},
                    background_normal='',
                    background_color=palette('dark_shade',.85),
                    markup=True)
                add_button.bind(on_release=partial(self.add_service_prompt_details,i))
                add_button.bind(on_release=self.schedule_dock_handle_func)
                card.add_widget(title)
                card.add_widget(icon)
                card.add_widget(add_button)
                layout.add_widget(card)
        except Exception as e:
            logger.exception(e)

    def add_service_prompt_details(self,details,*args):
        w=self.widgets
        layout=w['schedule_box_layout']
        ratio=layout.width/11
        service_icon=ServicesIconButton(
            source=details['icon'],
            size=(ratio,ratio),
            size_hint=(None,None),
            data=details)
        service_icon.add_widget(CirclePulseEmit(6))
        layout.add_widget(service_icon,index=1)
        if w['add_service_icon'] in layout.sub_children:
            layout.remove_widget(w['add_service_icon'],unload=True)

        details_box=ScheduleCreationLayout(
            bg_color=palette('light_tint',.95),
            size_hint =(.775, .875),
            pos_hint = {'center_x':.5, 'center_y':.5},
            fade_in=True,
            call_back=partial(self.service_not_saved_reset,service_icon),
            data=details)
        details_box.target=service_icon
        self.add_widget(details_box)

    def service_not_saved_reset(self,service_icon,*args):
        w=self.widgets
        x=w['add_service_icon']
        w['schedule_box_layout'].remove_widget(service_icon,unload=True)
        if x not in w['schedule_box_layout'].sub_children:
            w['schedule_box_layout'].add_widget(x,load=True)

    def save_service_details(self,data,*args):
        try:
            with open('logs/configurations/scheduled_services.json','r+') as f:
                loaded_data = json.load(f)
                loaded_data.append(data)
                f.seek(0)
                json.dump(loaded_data, f, indent=4)
                f.truncate()
        except Exception as e:
            logger.exception(e)
            print(Exception)
            print('e: ',e)

    def load_service_details(self,*args):
        try:
            with open('logs/configurations/scheduled_services.json','r') as f:
                loaded_data = json.load(f)
        except Exception as e:
            logger.exception(e)
            print(Exception)
            print('e: ',e)
            return
        w=self.widgets
        layout=w['schedule_box_layout']
        layout.clear_widgets(unload=True)
        ratio=layout.width/9.25
        for i in  loaded_data:
            service_icon=ServicesIconButton(
                source=i['icon'],
                size=(ratio,ratio),
                size_hint=(None,None),
                data=i)
            service_icon.bind(on_release=self.open_schedule_detail_view)
            layout.add_widget(service_icon,load=True)
        if w['add_service_icon'] not in layout.sub_children:
            asi=w['add_service_icon']
            asi.size=(ratio,ratio)
            layout.add_widget(asi,load=True)

    def load_active_container(self,*args):
        container_fade_in=Animation(opacity=1,d=.5)
        w=self.widgets
        container=w['container']
        container.clear_widgets()
        active_widgets=[
            w['fans'],
            w['lights'],
            w['clock_label']]
        for i in active_widgets:
            container.add_widget(i)
        container_fade_in.start(container)

    def open_schedule_detail_view(self,icon,*args):
        layout=ModalDenseRoundedColorLayout(
            bg_color=palette('light_tint'),
            size_hint =(.775, .875),
            pos_hint = {'center_x':.5, 'center_y':.5},
            fade_in=True)
        self.add_widget(layout)
        layout._icon=icon
        layout.bind(on_expanded=self.populate_schedule_detail_view)

    def populate_schedule_detail_view(self,layout,*args):
        w=self.widgets
        data=layout._icon.data
        x_btn=IconButton(
            source=overlay_x_icon_black,
            size_hint=(.08,.08),
            pos_hint={'x':.92,'y':.9})
        x_btn.bind(on_release=layout.clear)

        ##### top #####

        view_title=Label(
            text='[size=24][color=#000000][b]'+data['title']+' Details',
            markup=True,
            size_hint =(.4, .05),
            pos_hint = {'center_x':.5, 'center_y':.925},)
        view_title.ref='view_title'

        view_title_seperator=LabelColor(
            size_hint =(.8, .002),
            pos_hint = {'center_x':.5, 'center_y':.875},
            bg_color=palette('additional'))
        view_title.ref='view_title'


        layout.add_widget(x_btn)
        layout.add_widget(view_title)
        layout.add_widget(view_title_seperator)

    def msg_icon_notifications(self,*args):
        unseen_messages=[i for i in messages.active_messages if i.seen==False]
        messenger=self.widgets['messenger_button']
        if any(unseen_messages):
            if 'notification_badge' not in self.widgets['msg_icon'].widgets:
                self.widgets['msg_icon'].add_widget(NotificationBadge())
            if messenger.pos_hint=={'center_x':.5,'center_y':.55}:#undocked
                if 'scroll_layout' in messenger.widgets:
                    listed_messages=[i.message for i in messenger.widgets['scroll_layout'].widgets]
                    if any([i for i in unseen_messages if i not in listed_messages]):
                        messenger.populate_widgets()
            if messenger.size_hint==[1,1]:#docked
                self.widgets['message_label'].text=f'[size=50][color=#ffffff][b]{messages.active_messages[0].card}'
        else:
            if 'notification_badge' in self.widgets['msg_icon'].widgets:
                self.widgets['msg_icon'].widgets['notification_badge'].clear()
    def start_nb_clock(self,*args):
        Clock.schedule_interval(self.msg_icon_notifications,.75)

    def about_overlay(self):
        overlay_menu=self.widgets['overlay_menu']
        overlay_menu.background_color=palette('dark_shade',.75)
        overlay_menu.title=''
        overlay_menu.separator_height=0
        overlay_menu.auto_dismiss=True
        self.widgets['overlay_layout'].clear_widgets()
        self.widgets['overlay_layout'].add_widget(self.widgets['overlay_x'])

        about_text=Label(
            text=current_language['about_overlay_text'],
            markup=True,
            size_hint =(1,.6),
            pos_hint = {'x':0, 'y':.4},)
        self.widgets['about_text']=about_text
        about_text.ref='about_overlay_text'

        version_info=Label(text=current_language['version_info_white'],
                markup=True,
                pos_hint = {'x':-.05, 'center_y':.6})
        version_info.ref='version_info'

        about_qr=Image(source=qr_link,
            allow_stretch=False,
            keep_ratio=True,
            size_hint =(.45,.45),
            pos_hint = {'x':.6, 'y':.58})

        qr_label=Label(text='[size=16][color=#ffffff]firesafeextinguisher.com[/color][/size]',
                markup=True,
                pos_hint = {'x':.33, 'center_y':.55})
        qr_label.ref='qr_label'

        about_back_button=RoundedButton(text=current_language['about_back'],
                        size_hint =(.9, .25),
                        pos_hint = {'x':.05, 'y':.05},
                        background_normal='',
                        background_color=palette('primary',.9),
                        markup=True)
        self.widgets['about_back_button']=about_back_button
        about_back_button.ref='about_back'

        def about_overlay_close(button):
            self.widgets['overlay_menu'].dismiss()
        about_back_button.bind(on_release=about_overlay_close)

        self.widgets['overlay_layout'].add_widget(about_text)
        self.widgets['overlay_layout'].add_widget(version_info)
        self.widgets['overlay_layout'].add_widget(about_qr)
        self.widgets['overlay_layout'].add_widget(qr_label)
        self.widgets['overlay_layout'].add_widget(about_back_button)
        self.widgets['overlay_menu'].open()

    def about_func (self,button):
        self.about_overlay()

    def on_pre_leave(self, *args):
        self.widgets['messenger_button'].redock()
        if not App.get_running_app().limited:
            if self.current_section=='schedule':
                self.schedule_icon_func()

    def on_pre_enter(self, *args):
        if App.get_running_app().limited:
            if self.current_section!='schedule':
                self.schedule_icon_func()
            self.widgets['schedule_button'].disabled=False
            self.widgets['schedule_button'].opacity=1
        else:
            if self.current_section=='schedule':
                self.schedule_icon_func()
            self.widgets['schedule_button'].disabled=True
            self.widgets['schedule_button'].opacity=.3

class ActuationScreen(Screen):
    def __init__(self, **kwargs):
        super(ActuationScreen,self).__init__(**kwargs)
        self.cols = 2
        self.widgets={}
        bg_image = Image(source=background_image, allow_stretch=True, keep_ratio=False)

        alert=RoundedLabelColor(text=current_language['alert'],
                    size_hint =(.96, .45),
                    pos_hint = {'x':.02, 'y':.5},
                    bg_color=palette('highlight',.85),
                    markup=True)
        self.widgets['alert']=alert
        alert.ref='alert'

        action_box=RoundedColorLayout(
            bg_color=palette('secondary',.85),
            size_hint =(.35, .40),
            pos_hint = {'x':.02, 'center_y':.25},)
        self.widgets['action_box']=action_box

        with action_box.canvas.before:
           Color(*palette('secondary',1))
           action_box.msg_lines=Line(points=[100,100,100,100],width=1.5,group='action')

        def update_action_box_lines(*args):
            #vertical left section
            x1=int(action_box.width*.025+action_box.x)
            y1=int(action_box.height*.05+action_box.y)
            x2=int(action_box.width*.025+action_box.x)
            y2=int(action_box.height*.95+action_box.y)

            #horizontal top section
            x3=int(action_box.width*.025+action_box.x)
            y3=int(action_box.height*.95+action_box.y)
            x4=int(action_box.width*.975+action_box.x)
            y4=int(action_box.height*.95+action_box.y)

            #vertical right section
            x5=int(action_box.width*.975+action_box.x)
            y5=int(action_box.height*.95+action_box.y)
            x6=int(action_box.width*.975+action_box.x)
            y6=int(action_box.height*.05+action_box.y)

            #horizontal bottom section
            x7=int(action_box.width*.975+action_box.x)
            y7=int(action_box.height*.05+action_box.y)
            x8=int(action_box.width*.025+action_box.x)
            y8=int(action_box.height*.05+action_box.y)

            action_box.msg_lines.points=(x1,y1,x2,y2,x3,y3,x4,y4,x5,y5,x6,y6,x7,y7,x8,y8)
        action_box.bind(pos=update_action_box_lines, size=update_action_box_lines)

        acknowledge=RoundedToggleButton(
            text=current_language['acknowledge'],
            size_hint =(.85, .20),
            pos_hint = {'center_x':.5, 'center_y':.725},
            # background_normal='',
            background_down='',
            background_color=palette('secondary',.85),
            markup=True)
        self.widgets['acknowledge']=acknowledge
        acknowledge.ref='acknowledge'
        acknowledge.bind(state=self.acknowledge_func)

        service=RoundedButton(
            text=current_language['service'],
            size_hint =(.85, .20),
            pos_hint = {'center_x':.5, 'center_y':.275},
            # background_normal='',
            background_down='',
            background_color=palette('secondary',.85),
            markup=True)
        self.widgets['service']=service
        service.ref='service'
        service.bind(on_release=self.service_func)

        dialogue_box=RoundedColorLayout(
            bg_color=palette('secondary',.9),
            size_hint =(.5, .40),
            pos_hint = {'center_x':.7, 'center_y':.25},)
        self.widgets['dialogue_box']=dialogue_box

        with dialogue_box.canvas.before:
           Color(*palette('secondary',1))
           dialogue_box.msg_lines=Line(points=[100,100,100,100],width=1.5,group='action')

        def update_dialogue_box_lines(*args):
            #vertical left section
            x1=int(dialogue_box.width*.025+dialogue_box.x)
            y1=int(dialogue_box.height*.05+dialogue_box.y)
            x2=int(dialogue_box.width*.025+dialogue_box.x)
            y2=int(dialogue_box.height*.75+dialogue_box.y)

            #horizontal top section
            x3=int(dialogue_box.width*.025+dialogue_box.x)
            y3=int(dialogue_box.height*.75+dialogue_box.y)
            x4=int(dialogue_box.width*.975+dialogue_box.x)
            y4=int(dialogue_box.height*.75+dialogue_box.y)

            #vertical right section
            x5=int(dialogue_box.width*.975+dialogue_box.x)
            y5=int(dialogue_box.height*.75+dialogue_box.y)
            x6=int(dialogue_box.width*.975+dialogue_box.x)
            y6=int(dialogue_box.height*.05+dialogue_box.y)

            #horizontal bottom section
            x7=int(dialogue_box.width*.975+dialogue_box.x)
            y7=int(dialogue_box.height*.05+dialogue_box.y)
            x8=int(dialogue_box.width*.025+dialogue_box.x)
            y8=int(dialogue_box.height*.05+dialogue_box.y)

            dialogue_box.msg_lines.points=(x1,y1,x2,y2,x3,y3,x4,y4,x5,y5,x6,y6,x7,y7,x8,y8)
        dialogue_box.bind(pos=update_dialogue_box_lines, size=update_dialogue_box_lines)

        dialogue_title=RoundedLabelColor(
            bg_color=palette('secondary',.0),
            size_hint =(.9, .2),
            pos_hint = {'center_x':.5, 'center_y':.875},
            text=current_language['acknowledge'],
            markup=True)
        self.widgets['dialogue_title']=dialogue_title
        dialogue_title.ref='dialogue_title'

        dialogue_body=RoundedLabelColor(
            bg_color=palette('secondary',.0),
            size_hint =(.9, .5),
            pos_hint = {'center_x':.5, 'center_y':.35},
            text=current_language['acknowledge'],
            markup=True)
        self.widgets['dialogue_body']=dialogue_body
        dialogue_body.ref='dialogue_body'

        self.pulse()

        overlay_menu=Popup(
            size_hint=(.8, .8),
            background = 'atlas://data/images/defaulttheme/bubble',
            title_color=[0, 0, 0, 1],
            title_size='38',
            title_align='center',
            separator_color=palette('highlight', .5))
        self.widgets['overlay_menu']=overlay_menu

        overlay_layout=FloatLayout()
        self.widgets['overlay_layout']=overlay_layout

        overlay_menu.add_widget(overlay_layout)

        self.add_widget(bg_image)
        self.add_widget(alert)
        self.add_widget(action_box)
        action_box.add_widget(acknowledge)
        action_box.add_widget(service)
        self.add_widget(dialogue_box)
        dialogue_box.add_widget(dialogue_title)
        dialogue_box.add_widget(dialogue_body)

    def on_pre_enter(self,*args):
        self.anime.cancel_all(self.widgets['alert'])
        self.pulse()
        self.widgets['acknowledge'].text=current_language['acknowledge']
        self.widgets['acknowledge'].disabled=False
        if self.widgets['acknowledge'].state=='down':
            self.widgets['acknowledge'].trigger_action()

    def acknowledge_func(self,button,*args):
        if self.widgets['acknowledge'].state=='normal':
            return
        logger.info('actuation acknowledged')
        self.anime.cancel_all(self.widgets['alert'])
        self.widgets['alert'].bg_color=palette('highlight',.85)
        # self.widgets['alert'].text=current_language['alert_acknowledged']
        button.text="[size=28][color=#ffffff]Acknowledged"
        button.disabled=True

    def service_func(self,*args):
        self.service_overlay()

    def pulse(self):
            self.anime = Animation(bg_color=palette('light_tint',.85), duration=.1)+Animation(bg_color=palette('highlight',1), duration=1.5,t='out_cubic')
            self.anime.repeat = True
            self.anime.start(self.widgets['alert'])

    def service_overlay(self):
        overlay_menu=self.widgets['overlay_menu']
        overlay_menu.background_color=palette('dark_shade',.8)
        overlay_menu.title=''
        overlay_menu.separator_height=0
        overlay_menu.auto_dismiss=True
        self.widgets['overlay_layout'].clear_widgets()

        service_back_button=RoundedButton(
            text=current_language['about_back'],
            size_hint =(.9, .1),
            pos_hint = {'x':.05, 'y':.05},
            background_normal='',
            background_color=palette('primary',.9),
            markup=True)
        self.widgets['service_back_button']=service_back_button
        service_back_button.ref='about_back'

        service_enter_button=RoundedButton(
            text=current_language['enter'],
            size_hint =(.9, .1),
            pos_hint = {'x':.05, 'y':.45},
            background_normal='',
            background_color=palette('secondary',1),
            markup=True)
        self.widgets['service_enter_button']=service_enter_button
        service_back_button.ref='enter'

        pin_layout=FloatLayout(
            size_hint =(.5, .25),
            pos_hint = {'center_x':.5, 'center_y':.75})
        self.widgets['pin_layout']=pin_layout

        with pin_layout.canvas.before:
           Color(*palette('secondary',1))
           pin_layout.box_lines=Line(points=[100,100,100,100],width=1.5,group='action')
           pin_layout.divider_line1=Line(points=[100,100,100,100],width=1.5,group='action')
           pin_layout.divider_line2=Line(points=[100,100,100,100],width=1.5,group='action')
           pin_layout.divider_line3=Line(points=[100,100,100,100],width=1.5,group='action')

        def update_pin_layout_lines(*args):
            #vertical left section
            x1=int(pin_layout.width*0+pin_layout.x)
            y1=int(pin_layout.height*0+pin_layout.y)
            x2=int(pin_layout.width*0+pin_layout.x)
            y2=int(pin_layout.height*1+pin_layout.y)

            #horizontal top section
            x3=int(pin_layout.width*0+pin_layout.x)
            y3=int(pin_layout.height*1+pin_layout.y)
            x4=int(pin_layout.width*1+pin_layout.x)
            y4=int(pin_layout.height*1+pin_layout.y)

            #vertical right section
            x5=int(pin_layout.width*1+pin_layout.x)
            y5=int(pin_layout.height*1+pin_layout.y)
            x6=int(pin_layout.width*1+pin_layout.x)
            y6=int(pin_layout.height*0+pin_layout.y)

            #horizontal bottom section
            x7=int(pin_layout.width*1+pin_layout.x)
            y7=int(pin_layout.height*0+pin_layout.y)
            x8=int(pin_layout.width*0+pin_layout.x)
            y8=int(pin_layout.height*0+pin_layout.y)

            #divider lines
            x9=int(pin_layout.width*.25+pin_layout.x)
            y9=int(pin_layout.height*0+pin_layout.y)
            x10=int(pin_layout.width*.25+pin_layout.x)
            y10=int(pin_layout.height*1+pin_layout.y)

            x11=int(pin_layout.width*.5+pin_layout.x)
            y11=int(pin_layout.height*0+pin_layout.y)
            x12=int(pin_layout.width*.5+pin_layout.x)
            y12=int(pin_layout.height*1+pin_layout.y)

            x13=int(pin_layout.width*.75+pin_layout.x)
            y13=int(pin_layout.height*0+pin_layout.y)
            x14=int(pin_layout.width*.75+pin_layout.x)
            y14=int(pin_layout.height*1+pin_layout.y)

            pin_layout.box_lines.points=(x1,y1,x2,y2,x3,y3,x4,y4,x5,y5,x6,y6,x7,y7,x8,y8)
            pin_layout.divider_line1.points=(x9,y9,x10,y10)
            pin_layout.divider_line2.points=(x11,y11,x12,y12)
            pin_layout.divider_line3.points=(x13,y13,x14,y14)
        pin_layout.bind(pos=update_pin_layout_lines, size=update_pin_layout_lines)

        pin_1=BigWheel(
            size_hint =(.25, .975),
            pos_hint = {'center_x':.125, 'center_y':.495},
            direction='top',
            loop=True,
            y_reduction=60
            )
        self.widgets['pin_1']=pin_1

        for i in range(10):
            _digit=Label(
                text=f'[size=80][b][color=c0c0c0]{i}',
                markup=True,)
            pin_1.add_widget(_digit)
        
        pin_2=BigWheel(
            size_hint =(.25, .975),
            pos_hint = {'center_x':.375, 'center_y':.495},
            direction='top',
            loop=True,
            y_reduction=60
            )
        self.widgets['pin_2']=pin_2

        for i in range(10):
            _digit=Label(
                text=f'[size=80][b][color=c0c0c0]{i}',
                markup=True,)
            pin_2.add_widget(_digit)

        pin_3=BigWheel(
            size_hint =(.25, .975),
            pos_hint = {'center_x':.625, 'center_y':.495},
            direction='top',
            loop=True,
            y_reduction=60
            )
        self.widgets['pin_3']=pin_3

        for i in range(10):
            _digit=Label(
                text=f'[size=80][b][color=c0c0c0]{i}',
                markup=True,)
            pin_3.add_widget(_digit)

        pin_4=BigWheel(
            size_hint =(.25, .975),
            pos_hint = {'center_x':.875, 'center_y':.495},
            direction='top',
            loop=True,
            y_reduction=60
            )
        self.widgets['pin_4']=pin_4

        for i in range(10):
            _digit=Label(
                text=f'[size=80][b][color=c0c0c0]{i}',
                markup=True,)
            pin_4.add_widget(_digit)

        def service_overlay_close(button):
            self.widgets['overlay_menu'].dismiss()
        service_back_button.bind(on_release=service_overlay_close)

        def return_to_actuationscreen(*args):
            App.get_running_app().service_pin_entered=False

        def service_enter_func(*args):
            pin=''.join(
                (str(pin_1.index),
                str(pin_2.index),
                str(pin_3.index),
                str(pin_4.index)))
            pin_1.index,pin_2.index,pin_3.index,pin_4.index=0,0,0,0
            if pin!='1000':
                return
            App.get_running_app().service_pin_entered=True
            self.parent.transition = SlideTransition(direction='right')
            App.get_running_app().context_screen.current='main'
            Clock.schedule_once(return_to_actuationscreen,300)
            self.widgets['overlay_menu'].dismiss()

        service_enter_button.bind(on_release=service_enter_func)

        pin_layout.add_widget(pin_1)
        pin_layout.add_widget(pin_2)
        pin_layout.add_widget(pin_3)
        pin_layout.add_widget(pin_4)

        self.widgets['overlay_layout'].add_widget(pin_layout)
        self.widgets['overlay_layout'].add_widget(service_enter_button)
        self.widgets['overlay_layout'].add_widget(service_back_button)
        self.widgets['overlay_menu'].open()

class SettingsScreen(Screen):
    def __init__(self, **kwargs):
        super(SettingsScreen,self).__init__(**kwargs)
        self.cols = 2
        self.widgets={}
        bg_image = Image(source=background_image, allow_stretch=True, keep_ratio=False)

        back=RoundedButton(text=current_language['settings_back'],
                        size_hint =(.4, .1),
                        pos_hint = {'x':.06, 'y':.015},
                        background_down='',
                        background_color=palette('neutral',.9),
                        markup=True)
        self.widgets['back']=back
        back.ref='settings_back'
        back.bind(on_release=self.settings_back)

        version_info=RoundedButton(text=current_language['version_info'],
                markup=True,
                background_normal='',
                background_color=palette('primary',.5),
                size_hint =(.18, .1),
                pos_hint = {'x':.75, 'y':.015},)
        version_info.ref='version_info'
        version_info.bind(on_release=self.about_func)

        analytics=RoundedButton(
            text=current_language['analytics'],
            size_hint =(.9, .18),
            pos_hint = {'x':.05, 'y':.78},
            background_down='',
            background_color=palette('base',.9),
            markup=True)
        self.widgets['analytics']=analytics
        analytics.ref='analytics'
        analytics.bind(on_release=self.device_analytics)
        analytics.disabled=True#delete this line and change button color to commented out color

        sys_report=RoundedButton(text=current_language['sys_report'],
                        size_hint =(.9, .18),
                        pos_hint = {'x':.05, 'y':.51},
                        background_normal='',
                        background_color=palette('primary',.9),
                        markup=True)
        self.widgets['sys_report']=sys_report
        sys_report.ref='sys_report'
        sys_report.bind(on_release=self.sys_report)

        preferences=RoundedButton(text=current_language['preferences'],
                        size_hint =(.9, .18),
                        pos_hint = {'x':.05, 'y':.24},
                        background_down='',
                        background_color=palette('neutral',.9),
                        markup=True)
        self.widgets['preferences']=preferences
        preferences.ref='preferences'
        preferences.bind(on_release=self.preferences_func)

        overlay_menu=Popup(
            size_hint=(.8, .8),
            background = 'atlas://data/images/defaulttheme/button',
            title_color=[0, 0, 0, 1],
            title_size='38',
            title_align='center',
            separator_color=palette('highlight', .5))
        self.widgets['overlay_menu']=overlay_menu

        overlay_layout=FloatLayout()
        self.widgets['overlay_layout']=overlay_layout

        overlay_x=IconButton(
            source=overlay_x_icon,
            size_hint=(.1,.1),
            pos_hint={'x':.95,'y':.98})
        overlay_x.bind(on_release=overlay_menu.dismiss)
        self.widgets['overlay_x']=overlay_x

        seperator_line=Image(source=gray_seperator_line,
                    allow_stretch=True,
                    keep_ratio=False,
                    size_hint =(.98, .001),
                    pos_hint = {'x':.01, 'y':.13})

        language_button=IconButton(source=language_image, allow_stretch=True, keep_ratio=True)
        language_button.size_hint =(.10, .10)
        language_button.pos_hint = {'x':.61, 'y':.02}
        self.widgets['language_button']=language_button
        language_button.bind(on_release=self.language_func)
        language_button.color=palette('light_tint',.65)

        overlay_menu.add_widget(overlay_layout)
        self.add_widget(bg_image)
        self.add_widget(back)
        self.add_widget(version_info)
        self.add_widget(analytics)
        self.add_widget(sys_report)
        self.add_widget(preferences)
        self.add_widget(seperator_line)
        self.add_widget(language_button)

    def settings_back (self,button):
        self.parent.transition = SlideTransition(direction='left')
        self.manager.current='main'
    def device_analytics (self,button):
        self.parent.transition = SlideTransition(direction='down')
        self.manager.current='analytics'
    def sys_report (self,button):
        self.parent.transition = SlideTransition(direction='down')
        self.manager.current='report'
    def preferences_func (self,button):
        self.parent.transition = SlideTransition(direction='up')
        self.manager.current='preferences'
    def language_func (self,button):
        self.language_overlay()

    def language_overlay(self):
        overlay_menu=self.widgets['overlay_menu']
        overlay_menu.background_color=palette('dark_shade',0)
        overlay_menu.auto_dismiss=True
        overlay_menu.title=''
        overlay_menu.separator_height=0
        self.widgets['overlay_layout'].clear_widgets()

        english=RoundedButton(text="[size=30][b][color=#000000]  English [/color][/b][/size]",
                        size_hint =(.96, .125),
                        pos_hint = {'x':.02, 'y':.7},
                        background_normal='',
                        background_color=palette('primary',.9),
                        markup=True)
        self.widgets['english']=english

        spanish=RoundedButton(text="[size=30][b][color=#000000]  Español [/color][/b][/size]",
                        size_hint =(.96, .125),
                        pos_hint = {'x':.02, 'y':.3},
                        background_normal='',
                        background_color=palette('primary',.9),
                        markup=True)
        self.widgets['spanish']=spanish

        def english_func(button):
            global current_language
            config=App.get_running_app().config_
            current_language=lang_dict.english
            config.set('preferences','language','english')
            with open(preferences_path,'w') as configfile:
                config.write(configfile)
            language_setter()
            self.widgets['overlay_menu'].dismiss()
        english.bind(on_release=english_func)

        def spanish_func(button):
            global current_language
            config=App.get_running_app().config_
            current_language=lang_dict.spanish
            config.set('preferences','language','spanish')
            with open(preferences_path,'w') as configfile:
                config.write(configfile)
            language_setter()
            self.widgets['overlay_menu'].dismiss()
        spanish.bind(on_release=spanish_func)

        self.widgets['overlay_layout'].add_widget(english)
        self.widgets['overlay_layout'].add_widget(spanish)
        self.widgets['overlay_menu'].open()

    def about_overlay(self):
        overlay_menu=self.widgets['overlay_menu']
        overlay_menu.background_color=palette('dark_shade',.75)
        overlay_menu.title=''
        overlay_menu.separator_height=0
        overlay_menu.auto_dismiss=True
        self.widgets['overlay_layout'].clear_widgets()
        self.widgets['overlay_layout'].add_widget(self.widgets['overlay_x'])

        about_text=Label(
            text=current_language['about_overlay_text'],
            markup=True,
            size_hint =(1,.6),
            pos_hint = {'x':0, 'y':.4},)
        self.widgets['about_text']=about_text
        about_text.ref='about_overlay_text'

        version_info=Label(text=current_language['version_info_white'],
                markup=True,
                pos_hint = {'x':-.05, 'center_y':.6})
        version_info.ref='version_info'

        about_qr=Image(source=qr_link,
            allow_stretch=False,
            keep_ratio=True,
            size_hint =(.45,.45),
            pos_hint = {'x':.6, 'y':.58})

        qr_label=Label(text='[size=16][color=#ffffff]firesafeextinguisher.com[/color][/size]',
                markup=True,
                pos_hint = {'x':.33, 'center_y':.55})
        qr_label.ref='qr_label'

        about_back_button=RoundedButton(text=current_language['about_back'],
                        size_hint =(.9, .25),
                        pos_hint = {'x':.05, 'y':.05},
                        background_normal='',
                        background_color=palette('primary',.9),
                        markup=True)
        self.widgets['about_back_button']=about_back_button
        about_back_button.ref='about_back'

        def about_overlay_close(button):
            self.widgets['overlay_menu'].dismiss()
        about_back_button.bind(on_release=about_overlay_close)

        self.widgets['overlay_layout'].add_widget(about_text)
        self.widgets['overlay_layout'].add_widget(version_info)
        self.widgets['overlay_layout'].add_widget(about_qr)
        self.widgets['overlay_layout'].add_widget(qr_label)
        self.widgets['overlay_layout'].add_widget(about_back_button)
        self.widgets['overlay_menu'].open()

    def about_func (self,button):
        self.about_overlay()

class ReportScreen(Screen):
    def __init__(self, **kwargs):
        super(ReportScreen,self).__init__(**kwargs)
        self.cols = 2
        self.widgets={}

        bg_image = Image(source=background_image, allow_stretch=True, keep_ratio=False)
        self.widgets['bg_image']=bg_image

        back=RoundedButton(text=current_language['report_back'],
                    size_hint =(.4, .1),
                    pos_hint = {'x':.06, 'y':.015},
                    background_down='',
                    background_color=palette('neutral',.85),
                    markup=True)
        self.widgets['back']=back
        back.ref='report_back'
        back.bind(on_release=self.Report_back)

        back_main=RoundedButton(text=current_language['report_back_main'],
                        size_hint =(.4, .1),
                        pos_hint = {'x':.52, 'y':.015},
                        background_normal='',
                        background_color=palette('primary',.9),
                        markup=True)
        self.widgets['back_main']=back_main
        back_main.ref='report_back_main'
        back_main.bind(on_release=self.Report_back_main)

        date_label=DisplayLabel(
            text='',
            markup=True,
            size_hint =(.14, .05),
            pos_hint = {'center_x':.883, 'center_y':.843})
        self.widgets['date_label']=date_label

        pending_watermark=Label(
            text=current_language['pending_watermark'],
            markup=True,
            size_hint =(1,1),
            pos_hint = {'center_x':.5, 'center_y':.75})
        pending_watermark.opacity=.6
        self.widgets['pending_watermark']=pending_watermark
        pending_watermark.ref='pending_watermark'

        pending_watermark2=Label(
            text=current_language['pending_watermark'],
            markup=True,
            size_hint =(1,1),
            pos_hint = {'center_x':.5, 'center_y':.5})
        pending_watermark2.opacity=.6
        self.widgets['pending_watermark2']=pending_watermark2
        pending_watermark2.ref='pending_watermark'

        pending_watermark3=Label(
            text=current_language['pending_watermark'],
            markup=True,
            size_hint =(1,1),
            pos_hint = {'center_x':.5, 'center_y':.25})
        pending_watermark3.opacity=.6
        self.widgets['pending_watermark3']=pending_watermark3
        pending_watermark.ref='pending_watermark'

        report_image=Image(
            source=report_current,
            nocache=True)
        self.widgets['report_image']=report_image

        no_report_info_title=Label(
            text=current_language['no_report_info_title'],
            markup=True,
            size_hint =(1,1),
            pos_hint = {'center_x':.5, 'center_y':.85})
        self.widgets['no_report_info_title']=no_report_info_title
        no_report_info_title.ref='no_report_info_title'

        no_report_info=LabelColor(
            text=current_language['no_report_info'],
            halign="center",
            markup=True,
            size_hint =(1,1),
            pos_hint = {'center_x':.5, 'center_y':.5})
        self.widgets['no_report_info']=no_report_info
        no_report_info.ref='no_report_info'

        scroll_layout=RelativeLayout(
            size_hint_y=2.5,
            size_hint_x=.95)
        self.widgets['scroll_layout']=scroll_layout

        report_scroll=ScrollView(
            bar_width=8,
            do_scroll_y=True,
            do_scroll_x=False,
            size_hint_y=1,
            size_hint_x=.95,
            pos_hint = {'center_x':.525, 'center_y':.5})
        report_scroll.bar_color=palette('primary',.75)
        report_scroll.bar_inactive_color=palette('primary',.55)
        self.widgets['report_scroll']=report_scroll

        report_scatter = Scatter(
            size_hint=(None, None),
            size=self.widgets['report_image'].size,
            pos_hint = {'center_x':.5, 'center_y':.55},
            do_rotation=False,
            scale_min=1,
            scale_max=3,
            auto_bring_to_front=False)
        self.widgets['report_scatter']=report_scatter

        seperator_line=Image(source=gray_seperator_line,
                    allow_stretch=True,
                    keep_ratio=False,
                    size_hint =(.98, .001),
                    pos_hint = {'x':.01, 'y':.13})
        self.widgets['seperator_line']=seperator_line

        self.add_widget(bg_image)
        scroll_layout.add_widget(report_image)
        report_scroll.add_widget(scroll_layout)
        if report_image.texture:
            self.add_widget(report_scroll)
        else:
            self.add_widget(no_report_info)
            self.add_widget(no_report_info_title)
        self.add_widget(back)
        self.add_widget(back_main)
        self.add_widget(seperator_line)

    def archive_report(self,*args):
        if not os.path.exists('logs/sys_report/report.jpg'):
            return False
        report_image=FloatImage(
            nocache=True,
            size_hint=(None,None))

        def resize(*args):
            if report_image.texture==None:
                return
            report_image.size=report_image.texture.size

        report_image.bind(texture=resize)
        report_image.source=report_current

        date_label=DisplayLabel(
            text='',
            markup=True,
            size_hint =(.13, .013),
            pos_hint = {'center_x':.875, 'center_y':.945})

        config=App.get_running_app().config_
        saved_date=config.get("documents","inspection_date",fallback='Original')
        date_label.text=f'[size=32][color=#000000]{saved_date}[/color]'

        report_image.add_widget(date_label)
        if not os.path.exists('logs/documents/system_reports'):
            pathlib.Path('logs/documents/system_reports').mkdir(parents=True, exist_ok=True)
        Clock.schedule_once(lambda *args:report_image.export_to_png(f'logs/documents/system_reports/{saved_date}.jpg',0))
        return True

    def create_current_report(self,*args):
        if not os.path.exists('logs/sys_report/report.jpg'):
            return False
        report_image=FloatImage(
            nocache=True,
            size_hint=(None,None))

        def resize(*args):
            if report_image.texture==None:
                return
            report_image.size=report_image.texture.size

        report_image.bind(texture=resize)
        report_image.source=report_current

        date_label=DisplayLabel(
            text='',
            markup=True,
            size_hint =(.13, .013),
            pos_hint = {'center_x':.875, 'center_y':.945})

        config=App.get_running_app().config_
        saved_date=config["documents"]["inspection_date"]
        date_label.text=f'[size=32][color=#000000]{saved_date}[/color]'

        report_image.add_widget(date_label)
        Clock.schedule_once(lambda *args:report_image.export_to_png('logs/sys_report/report.jpg',0))
        return True

    def imprint_state_labels(self,*args):
        if not os.path.exists('logs/sys_report/report.jpg'):
            return False
        report_image=FloatImage(
            nocache=True,
            size_hint=(None,None))

        def resize(*args):
            if report_image.texture==None:
                return
            report_image.size=report_image.texture.size

        report_image.bind(texture=resize)
        report_image.source=report_current

        # st_label=DisplayLabel(
        #     text='',
        #     markup=True,
        #     size_hint =(.05, .013),
        #     pos_hint = {'center_x':.4225, 'center_y':.8555})

        st_zip_label=DisplayLabel(
            text='',
            markup=True,
            size_hint =(.02225, .013),
            pos_hint = {'center_x':.76775, 'center_y':.874})

        config=App.get_running_app().config_
        report_state=config.get("config","report_state",fallback='KY')
        # st_label.text=f'[color=#000000][size=32]{report_state}'
        st_zip_label.text=f'[b][color=#000000][size=26]{report_state}'

        # report_image.add_widget(st_label)
        report_image.add_widget(st_zip_label)
        Clock.schedule_once(lambda *args:report_image.export_to_png('logs/sys_report/report.jpg',0))
        return True

    def check_pending(self):
        if App.get_running_app().report_pending==False:
            if self.widgets['pending_watermark'] in self.widgets['scroll_layout'].children:
                self.widgets['scroll_layout'].remove_widget(self.widgets['pending_watermark'])
                self.widgets['scroll_layout'].remove_widget(self.widgets['pending_watermark2'])
                self.widgets['scroll_layout'].remove_widget(self.widgets['pending_watermark3'])
        else:
            if self.widgets['pending_watermark'] not in self.widgets['scroll_layout'].children:
                self.widgets['scroll_layout'].add_widget(self.widgets['pending_watermark'])
                self.widgets['scroll_layout'].add_widget(self.widgets['pending_watermark2'])
                self.widgets['scroll_layout'].add_widget(self.widgets['pending_watermark3'])

    def on_pre_enter(self):
        self.check_pending()
        self.refresh_widget()
    def on_leave(self, *args):
        self.widgets['report_scroll'].scroll_y=1
    def Report_back (self,button):
        self.parent.transition = SlideTransition(direction='up')
        self.manager.current='settings'
    def Report_back_main (self,button):
        self.parent.transition = SlideTransition(direction='left')
        self.manager.current='main'
    def refresh_widget(self):
        self.clear_widgets()
        self.widgets['report_image'].reload()
        self.widgets['report_scroll'].scroll_y=1
        self.add_widget(self.widgets['bg_image'])
        if self.widgets['report_image'].texture:
            self.add_widget(self.widgets['report_scroll'])
        else:
            self.add_widget(self.widgets['no_report_info'])
            self.add_widget(self.widgets['no_report_info_title'])
        self.add_widget(self.widgets['back'])
        self.add_widget(self.widgets['back_main'])
        self.add_widget(self.widgets['seperator_line'])

class DevicesScreen(Screen):
    def __init__(self, **kw):
        super(DevicesScreen,self).__init__(**kw)
        bg_image = Image(source=background_image, allow_stretch=True, keep_ratio=False)
        self.widgets={}
        self.ud={}
        self.unlocked=False

        back=RoundedButton(text=current_language['report_back'],
                    size_hint =(.4, .1),
                    pos_hint = {'x':.06, 'y':.015},
                    background_down='',
                    background_color=palette('neutral',.85),
                    markup=True)
        self.widgets['back']=back
        back.ref='report_back'
        back.bind(on_release=self.devices_back)

        back_main=RoundedButton(text=current_language['report_back_main'],
                        size_hint =(.4, .1),
                        pos_hint = {'x':.52, 'y':.015},
                        background_normal='',
                        background_color=palette('primary',.9),
                        markup=True)
        self.widgets['back_main']=back_main
        back_main.ref='report_back_main'
        back_main.bind(on_release=self.devices_back_main)

        device_details=ScrollItemTemplate(current_language['no_device'],color=palette('base',.85))
        self.widgets['device_details']=device_details
        device_details.ref='no_device'

        device_layout=EventpassGridLayout(
            size_hint_y=None,
            size_hint_x=1,
            cols=1,
            padding=10,
            spacing=(1,5))
        self.widgets['device_layout']=device_layout
        device_layout.bind(minimum_height=device_layout.setter('height'))

        device_scroll=ScrollView(
            bar_width=8,
            do_scroll_y=True,
            do_scroll_x=False,
            # size_hint_y=None,
            # size_hint_x=1,
            size_hint =(.9, .80),
            pos_hint = {'center_x':.5, 'y':.18})
        device_scroll.bar_color=palette('primary',.75)
        device_scroll.bar_inactive_color=palette('primary',.55)
        self.widgets['device_scroll']=device_scroll

        overlay_menu=Popup(
            size_hint=(.98, .98),
            background = 'atlas://data/images/defaulttheme/button',
            title_color=[0, 0, 0, 1],
            title_size='30',
            title_align='center',
            separator_color=palette('highlight', .5))
        overlay_menu.bind(on_open=self.resize)
        self.widgets['overlay_menu']=overlay_menu

        overlay_layout=FloatLayout()
        self.widgets['overlay_layout']=overlay_layout

        overlay_menu.add_widget(overlay_layout)

        seperator_line=Image(source=gray_seperator_line,
                    allow_stretch=True,
                    keep_ratio=False,
                    size_hint =(.98, .001),
                    pos_hint = {'x':.01, 'y':.13})

        batch_add_layout=ExpandableRoundedColorLayout(
            size_hint =(.1, .15),
            pos_hint = {'center_x':.5, 'center_y':1.5},
            expanded_size=(.9,.8),
            expanded_pos = {'center_x':.5, 'center_y':.55},
            bg_color=palette('dark_shade',.85))
        batch_add_layout.widgets={}
        self.widgets['batch_add_layout']=batch_add_layout
        batch_add_layout.bind(expanded=self.batch_add_layout_populate)
        batch_add_layout.bind(animating=partial(general.stripargs,batch_add_layout.clear_widgets))

        batch_add_title=Label(
            text="[size=20][color=#ffffff][b]Device Batch Add",
            markup=True,
            size_hint =(1, 1),
            pos_hint = {'center_x':.5, 'center_y':.925},)
        self.widgets['batch_add_title']=batch_add_title
        batch_add_title.ref='batch_add_title'

        batch_add_seperator=Image(
            source=gray_seperator_line,
            allow_stretch=True,
            keep_ratio=False,
            size_hint =(.9, .005),
            pos_hint = {'x':.05, 'y':.85})
        self.widgets['batch_add_seperator']=batch_add_seperator

        batch_add_expand_button=RoundedButton(
            size_hint =(.5, .075),
            pos_hint = {'center_x':.5, 'center_y':.075},
            background_down='',
            background_color=palette('light_tint',.9),
            markup=True)
        self.widgets['batch_add_expand_button']=batch_add_expand_button
        batch_add_expand_button.bind(on_release=batch_add_layout.shrink)

        batch_add_expand_lines=Image(
            source=settings_icon,
            allow_stretch=True,
            keep_ratio=False,
            size_hint =(.4, .035),
            pos_hint = {'center_x':.5, 'center_y':.075})
        batch_add_expand_lines.center=batch_add_expand_button.center
        self.widgets['batch_add_expand_lines']=batch_add_expand_lines

        batch_add_vertical_seperator=Image(
            source=gray_seperator_line_vertical,
            allow_stretch=True,
            keep_ratio=False,
            size_hint =(.0005, .6),
            pos_hint = {'center_x':.6, 'center_y':.475})
        self.widgets['batch_add_vertical_seperator']=batch_add_vertical_seperator

        batch_add_instructions=LabelColor(
            bg_color=palette('dark_shade',1),
            text=current_language['batch_add_instructions'],
            markup=True,
            size_hint =(.3, .6),
            pos_hint = {'center_x':.2, 'center_y':.475},)
        self.widgets['batch_add_instructions']=batch_add_instructions
        batch_add_instructions.ref='batch_add_instructions'

        with batch_add_instructions.canvas.after:
           batch_add_instructions.status_lines=Line(rounded_rectangle=(100, 100, 200, 200, 10, 10, 10, 10, 100))

        def update_lines(*args):
            x=int(batch_add_instructions.x)
            y=int(batch_add_instructions.y)
            width=int(batch_add_instructions.width*1)
            height=int(batch_add_instructions.height*1)
            batch_add_instructions.status_lines.rounded_rectangle=(x, y, width, height, 10, 10, 10, 10, 100)
        batch_add_instructions.bind(pos=update_lines, size=update_lines)

        batches_scroll=OutlineScroll(
            size_hint =(.175,.6),
            pos_hint = {'center_x':.475, 'center_y':.475},
            bg_color=palette('light_tint',.15),
            bar_width=8,
            bar_color=palette('primary',.9),
            bar_inactive_color=palette('primary',.35),
            do_scroll_y=True,
            do_scroll_x=False)
        self.widgets['batches_scroll']=batches_scroll

        batches_scroll_layout=GridLayout(
            cols=1,
            spacing=10,
            size_hint_y=None,
            padding=5)
        batches_scroll_layout.bind(minimum_height=lambda layout,min_height:setattr(layout,'height',min_height))
        self.widgets['batches_scroll_layout']=batches_scroll_layout

        batches_device_info_scroll=OutlineScroll(
            size_hint =(.3125,.6),
            pos_hint = {'center_x':.79375, 'center_y':.475},
            bg_color=palette('light_tint',.15),
            bar_width=8,
            bar_color=palette('primary',.9),
            bar_inactive_color=palette('primary',.35),
            do_scroll_y=True,
            do_scroll_x=False)
        self.widgets['batches_device_info_scroll']=batches_device_info_scroll

        batches_device_info_scroll_layout=GridLayout(
            cols=1,
            spacing=50,
            size_hint_y=None,
            padding=5)
        batches_device_info_scroll_layout.bind(minimum_height=lambda layout,min_height:setattr(layout,'height',min_height))
        self.widgets['batches_device_info_scroll_layout']=batches_device_info_scroll_layout

        batch_blue_relay_4_button=RoundedButton(
            text='[b][size=16][color=#000000]Four Channel\nBlue Relay Board',
            background_normal='',
            background_color=palette('accent',.8),
            markup=True,
            size_hint_y=None,
            height=60,
            halign='center')
        self.widgets['batch_blue_relay_4_button']=batch_blue_relay_4_button
        batch_blue_relay_4_button.bind(on_release=partial(self.get_batch_info,"blue_relay_4"))

        batch_blue_relay_6_button=RoundedButton(
            text='[b][size=16][color=#000000]Six Channel\nBlue Relay Board',
            background_normal='',
            background_color=palette('accent',.8),
            markup=True,
            size_hint_y=None,
            height=60,
            halign='center')
        self.widgets['batch_blue_relay_6_button']=batch_blue_relay_6_button
        batch_blue_relay_6_button.bind(on_release=partial(self.get_batch_info,"blue_relay_6"))

        basic_inputs_button=RoundedButton(
            text='[b][size=16][color=#000000]Basic Input Devices',
            background_normal='',
            background_color=palette('accent',.8),
            markup=True,
            size_hint_y=None,
            height=60,
            halign='center')
        self.widgets['basic_inputs_button']=basic_inputs_button
        basic_inputs_button.bind(on_release=partial(self.get_batch_info,"basic_inputs"))

        batches_scroll_layout.add_widget(batch_blue_relay_4_button)
        batches_scroll_layout.add_widget(batch_blue_relay_6_button)
        batches_scroll_layout.add_widget(basic_inputs_button)
        batches_scroll.add_widget(batches_scroll_layout)
        batches_device_info_scroll.add_widget(batches_device_info_scroll_layout)
        device_layout.add_widget(device_details)
        device_scroll.add_widget(device_layout)
        self.add_widget(bg_image)
        self.add_widget(back)
        self.add_widget(back_main)
        self.add_widget(device_scroll)
        self.add_widget(seperator_line)
        self.add_widget(batch_add_layout)

    def get_batch_info(self,batch,*args):
        layout=self.widgets['batches_device_info_scroll_layout']
        layout.clear_widgets()
        b=importlib.import_module(f'device_classes.batches.{batch}')
        layout.add_widget(Label())
        for i in b.info:
            l=Label(
                text='[size=16]'+i,
                markup=True,
                halign='center')
            layout.add_widget(l)
            layout.add_widget(Label())
        add_batch_button=RoundedButton(
            size_hint_y=None,
            height=75,
            text='[b][size=16][color=#000000]Add Batch',
            background_normal='',
            background_color=palette('accent',.8),
            markup=True)
        add_batch_button.bind(on_release=partial(self.add_batch,batch))
        layout.add_widget(add_batch_button)
        layout.add_widget(Label())

    def batch_add_layout_populate(self,*args):
        darken=Animation(rgba=palette('dark_shade',.95))
        lighten=Animation(rgba=palette('dark_shade',.85))
        batch_add_layout=self.widgets['batch_add_layout']
        batch_add_layout.clear_widgets()
        if batch_add_layout.expanded:
            self.remove_widget(batch_add_layout)
            self.add_widget(batch_add_layout)#needed to draw children on top
            darken.start(batch_add_layout.shape_color)
            w=self.widgets
            w['batches_device_info_scroll_layout'].clear_widgets()
            all_widgets=[
                w['batch_add_title'],
                w['batch_add_seperator'],
                w['batch_add_expand_button'],
                w['batch_add_expand_lines'],
                w['batch_add_vertical_seperator'],
                w['batch_add_instructions'],
                w['batches_scroll'],
                w['batches_device_info_scroll']]
            for i in all_widgets:
                batch_add_layout.add_widget(i)
        elif not batch_add_layout.expanded:
            lighten.start(batch_add_layout.shape_color)

    def add_batch(self,batch,*args):
        b=importlib.import_module(f'device_classes.batches.{batch}')
        class InfoShelf():
            def __init__(self,device) -> None:
                self.name=device['device_name']
                self.type=device['type']
                self.pin=device['gpio_pin']
                self.color=device['color']
                self.run_time=0
                self.trigger=device['trigger']
                self.device_types={
                    "Exfan":"exhaust.Exhaust",
                    "MAU":"mau.Mau",
                    "Light":"light.Light",
                    "Dry":"drycontact.DryContact",
                    "GV":"gas_valve.GasValve",
                    "Micro":"micro_switch.MicroSwitch",
                    "Heat":"heat_sensor.HeatSensor",
                    "Light Switch":"switch_light.SwitchLight",
                    "Fans Switch":"switch_fans.SwitchFans",
                    "Manometer":"manometer.Manometer"}
        result=True
        for i in b.devices:
            if self.new_device_save(InfoShelf(i)) == False:
                result=False
        if result:
            App.get_running_app().notifications.toast(f'[size=20]Batch Added','info')
        else:
            App.get_running_app().notifications.toast(f'[size=20]Failed to add all devices','error')

    def resize(self,popup,*args):
        pass

    def info_overlay(self,device,open=True):
        overlay_menu=self.widgets['overlay_menu']
        overlay_menu.title=f'{device.name} Details'
        overlay_menu.separator_height=0
        overlay_menu.auto_dismiss=True
        self.widgets['overlay_layout'].clear_widgets()

        info_add_icon=IconButton(source=add_device_icon,
                        size_hint =(.15, .15),
                        pos_hint = {'x':.85, 'y':.95})
        self.widgets['info_add_icon']=info_add_icon
        info_add_icon.color=palette('light_tint',.5)
        info_add_icon.bind(on_release=partial(self.info_add_icon_func,device))
        info_add_icon.bind(state=self.icon_change)

        delete_icon=IconButton(source=delete_normal,
                        size_hint =(.2, .2),
                        pos_hint = {'x':.0, 'y':.90})
        self.widgets['delete_icon']=delete_icon
        delete_icon.color=palette('light_tint',.8)
        delete_icon.bind(on_release=partial(self.delete_icon_func,device))
        delete_icon.bind(state=self.delete_icon_change)


        info_type=MinimumBoundingLabel(
            text=f"[size=18]Device Type:                         {device.type}[/size]",
            color=palette('dark_shade',1),
            pos_hint = {'x':.1, 'y':.85},
            markup=True)

        info_pin=MinimumBoundingLabel(
            text=f"[size=18]Device GPIO Pin:                 {device.pin}[/size]",
            color=palette('dark_shade',1),
            pos_hint = {'x':.1, 'y':.75},
            markup=True)

        info_run_time=MinimumBoundingLabel(
            text=f"[size=18]Device Run Time:                {general.Convert_time(device.run_time)}[/size]",
            color=palette('dark_shade',1),
            pos_hint = {'x':.1, 'y':.65},
            markup=True)

        info_trigger=MinimumBoundingLabel(
            text=f"[size=18]Device Trigger State:         {device.trigger.capitalize()}[/size]",
            color=palette('dark_shade',1),
            pos_hint = {'x':.1, 'y':.55},
            markup=True)

        info_loading_error=MinimumBoundingLabel(text=f"[size=18]Device failed to load all details correctly[/size]",
                color=palette('dark_shade',1),
                pos_hint = {'center_x':.5, 'y':.3},
                markup=True)
        self.widgets['info_loading_error']=info_loading_error

        info_admin_hint=MinimumBoundingLabel(text=f"[size=18]Enable Admin mode to edit device[/size]",
                color=palette('dark_shade',1),
                pos_hint = {'center_x':.5, 'y':.2},
                markup=True)
        self.widgets['info_admin_hint']=info_admin_hint

        info_back_button=RoundedButton(text=current_language['about_back'],
                        size_hint =(.9, .15),
                        pos_hint = {'x':.05, 'y':.025},
                        background_down='',
                        background_color=palette('highlight',.85),
                        markup=True)
        self.widgets['info_back_button']=info_back_button
        info_back_button.ref='about_back'
        info_back_button.bind(on_release=self.info_overlay_close)

        info_gv_reset=IconButton(source=reset_valve,
                        size_hint =(.12, .12),
                        pos_hint = {'x':.15, 'y':.98})
        info_gv_reset.color=palette('light_tint',.8)
        self.widgets['info_gv_reset']=info_gv_reset
        info_gv_reset.bind(on_release=partial(self.info_gv_reset_func,device))

        info_heat_timer_reset=IconButton(source=reset_valve,
                        size_hint =(.12, .12),
                        pos_hint = {'x':.15, 'y':.98})
        info_heat_timer_reset.color=palette('light_tint',.8)
        self.widgets['info_heat_timer_reset']=info_heat_timer_reset
        info_heat_timer_reset.bind(on_release=partial(self.info_heat_timer_reset_func,device))

        self.widgets['overlay_layout'].add_widget(info_add_icon)
        self.widgets['overlay_layout'].add_widget(delete_icon)
        self.widgets['overlay_layout'].add_widget(info_type)
        self.widgets['overlay_layout'].add_widget(info_pin)
        self.widgets['overlay_layout'].add_widget(info_run_time)
        self.widgets['overlay_layout'].add_widget(info_trigger)
        self.widgets['overlay_layout'].add_widget(info_back_button)
        if hasattr(device,'load_error'):
            if device.load_error:
                self.widgets['overlay_layout'].add_widget(info_loading_error)
        if isinstance(device,GasValve) :
            self.widgets['overlay_layout'].add_widget(info_gv_reset)
        if isinstance(device,HeatSensor) :
            self.widgets['overlay_layout'].add_widget(info_heat_timer_reset)
        if open:
            self.widgets['overlay_menu'].open()
        self.check_admin_mode()

    def info_gv_reset_func(self,device,*args):
        device.latched=True

    def info_heat_timer_reset_func(self,device,*args):
        logic.fs.heat_timer_clear()
        if logic.fs.milo['troubles']['heat_override']==0:
            App.get_running_app().notifications.toast(f'[size=20]Heat Sensor\nOverride Cleared','info')
        elif logic.fs.milo['troubles']['heat_override']==1:
            App.get_running_app().notifications.toast(f'[size=20]Heat Sensor Active\nFailed to Clear','warning')

    def delete_device_overlay(self,device,open=True):
        overlay_menu=self.widgets['overlay_menu']
        overlay_menu.title=f'Delete {device.name}?'
        overlay_menu.separator_height=0
        overlay_menu.auto_dismiss=True
        self.widgets['overlay_layout'].clear_widgets()

        delete_back_button=RoundedButton(text=current_language['cancel_button'],
                        size_hint =(.9, .15),
                        pos_hint = {'x':.05, 'y':.025},
                        background_normal='',
                        background_down='',
                        background_color=palette('primary',.9),
                        markup=True)
        self.widgets['delete_back_button']=delete_back_button
        delete_back_button.ref='cancel_button'
        delete_back_button.bind(on_release=partial(self.delete_overlay_close,device))

        delete_confirm_button=RoundedButton(text="Delete",
                        size_hint =(.4, .10),
                        pos_hint = {'x':.3, 'y':.35},
                        background_down='',
                        background_color=palette('highlight',1),
                        markup=True)
        self.widgets['delete_confirm_button']=delete_confirm_button
        delete_confirm_button.ref='about_back'
        delete_confirm_button.bind(on_press=partial(self.create_clock,device),on_touch_up=self.delete_clock)

        delete_device_text=MinimumBoundingLabel(text=f"""[size=18][color=#000000]Deleting device will remove all existing data and
terminate the associated GPIO pin usage immediately.
        
Only proceed if necessary; This action cannot be undone.[/color][/size]""",
                        color=palette('dark_shade',1),
                        pos_hint = {'center_x':.5, 'center_y':.7},
                        markup=True)

        delete_progress=CircularProgressBar()
        delete_progress._widget_size=200
        delete_progress._progress_colour=palette('highlight',1)
        self.widgets['delete_progress']=delete_progress

        self.widgets['overlay_layout'].add_widget(delete_back_button)
        self.widgets['overlay_layout'].add_widget(delete_confirm_button)
        self.widgets['overlay_layout'].add_widget(delete_device_text)
        self.widgets['overlay_layout'].add_widget(delete_progress)
        if open:
            self.widgets['overlay_menu'].open()

    def progress_bar_update(self,dt,*args):
        self.widgets['delete_progress'].pos=self.widgets['delete_confirm_button'].last_touch.pos
        if not self.widgets['delete_progress'].parent:
            self.widgets['overlay_layout'].add_widget(self.widgets['delete_progress'])
        if self.widgets['delete_progress'].value >= 1000: # Checks to see if progress_bar.value has met 1000
            return False # Returning False schedule is canceled and won't repeat
        self.widgets['delete_progress'].value += 1000/2*dt # Updates progress_bar's progress

    def delete_overlay_close(self,device,button):
        self.info_overlay(device,False)

    def delete_device_confirm(self,device,*args):
        logic.devices.remove(device)
        logic.pin_off(device.pin)
        if device.pin in logic._available_pins:
            logic.available_pins.append(device.pin)
        logic.available_pins.sort()
        os.remove(rf"logs/devices/{device.name}.json")
        with open(rf"logs/devices/device_list.json","r+") as read_file:
            d_list=json.load(read_file)
            del d_list[device.name]
            read_file.seek(0)
            json.dump(d_list,read_file,indent=0)
            read_file.truncate()
        self.aggregate_devices()
        self.widgets['overlay_menu'].dismiss()

    def create_clock(self,device,*args):
        scheduled_delete=partial(self.delete_device_confirm,device)
        Clock.schedule_once(scheduled_delete, 2)
        self.ud['event'] = scheduled_delete
        Clock.schedule_interval(self.progress_bar_update,.0001)
        self.ud['event_bar'] = self.progress_bar_update

    def delete_clock(self,*args):
        if 'event' in self.ud:
            Clock.unschedule(self.ud['event'])
        if 'event_bar' in self.ud:
            Clock.unschedule(self.ud['event_bar'])
            self.widgets['delete_progress'].value=0
            self.widgets['overlay_layout'].remove_widget(self.widgets['delete_progress'])

    def info_overlay_close(self,button):
        self.widgets['overlay_menu'].dismiss()

    def info_add_icon_func(self,device,button):
        if App.get_running_app().admin_mode_start>time.time() or self.unlocked:
            self.edit_device_overlay(device)
        else:
            Window.add_widget(PinLock(partial(self.unlock_callback,partial(self.edit_device_overlay,device))))


    def delete_icon_func(self,device,button):
        if App.get_running_app().admin_mode_start>time.time() or self.unlocked:
            self.delete_device_overlay(device,open=False)
        else:
            Window.add_widget(PinLock(partial(self.unlock_callback,partial(self.delete_device_overlay,device,open=False))))

    def icon_change(self,button,state):
        if state=='down':
            button.source=add_device_down
        else:
            button.source=add_device_icon
    def delete_icon_change(self,button,state):
        if state=='down':
            button.source=delete_down
        else:
            button.source=delete_normal

    def new_device_overlay(self,open=True):
        class InfoShelf():
            def __init__(self) -> None:
                self.name='default'
                self.type='Exfan'
                self.pin=0
                self.color=palette('dark_shade',.85)
                self.run_time=0
                self.trigger="High"
                self.device_types={
                    "Exfan":"exhaust.Exhaust",
                    "MAU":"mau.Mau",
                    "Light":"light.Light",
                    "Dry":"drycontact.DryContact",
                    "GV":"gas_valve.GasValve",
                    "Micro":"micro_switch.MicroSwitch",
                    "Heat":"heat_sensor.HeatSensor",
                    "Light Switch":"switch_light.SwitchLight",
                    "Fans Switch":"switch_fans.SwitchFans",
                    "Manometer":"manometer.Manometer"}
        current_device=InfoShelf()

        overlay_menu=self.widgets['overlay_menu']
        lay_out=self.widgets['overlay_layout']
        overlay_menu.title='Configure New Device'
        overlay_menu.separator_height=0
        overlay_menu.auto_dismiss=True
        self.widgets['overlay_layout'].clear_widgets()

        new_device_back_button=RoundedButton(text=current_language['about_back'],
                        size_hint =(.4, .15),
                        pos_hint = {'x':.05, 'y':.025},
                        background_down='',
                        background_color=palette('highlight',.85),
                        markup=True)
        self.widgets['new_device_back_button']=new_device_back_button
        new_device_back_button.ref='about_back'
        new_device_back_button.bind(on_release=self.new_device_overlay_close)

        new_device_save_button=RoundedButton(text=current_language['save'],
                        size_hint =(.4, .15),
                        pos_hint = {'x':.55, 'y':.025},
                        background_down='',
                        background_color=palette('complement',.85),
                        markup=True)
        self.widgets['new_device_save_button']=new_device_save_button
        new_device_save_button.ref='save'
        new_device_save_button.bind(on_release=partial(self.new_device_save,current_device))

        get_name_label=MinimumBoundingLabel(text="[size=18]Device Name:[/size]",
                        pos_hint = {'x':.1, 'y':.9},
                        color = palette('dark_shade',1),
                        markup=True)

        get_name=TextInput(multiline=False,
                        focus=False,
                        hint_text="Device name is required",
                        size_hint =(.5, .055),
                        pos_hint = {'x':.40, 'y':.9})
        self.widgets['get_name']=get_name
        get_name.bind(on_text_validate=partial(self.get_name_func,current_device))
        get_name.bind(text=partial(self.get_name_func,current_device))

        get_device_label=MinimumBoundingLabel(text="[size=18]Device Type:[/size]",
                        pos_hint = {'x':.1, 'y':.8},
                        color = palette('dark_shade',1),
                        markup=True)

        get_device_type=Spinner(
                        text="Exfan",
                        values=("Exfan","MAU","Heat","Light","Dry","GV","Micro","Light Switch","Fans Switch","Manometer"),
                        size_hint =(.5, .05),
                        pos_hint = {'x':.40, 'y':.8})
        self.widgets['get_device_type']=get_device_type
        get_device_type.bind(text=partial(self.get_device_type_func,current_device))
        get_device_type.bind(text=partial(self.set_default_name))
        get_device_type.bind(text=partial(self.set_default_pin,current_device))

        get_device_pin_label=MinimumBoundingLabel(text="[size=18]Device I/O Pin:[/size]",
                        pos_hint = {'x':.1, 'y':.7},
                        color = palette('dark_shade',1),
                        markup=True)

        get_device_pin=Spinner(
                        text="Select GPIO Pin",
                        values=(general.pin_decode(i) for i in logic.available_pins),
                        size_hint =(.5, .05),
                        pos_hint = {'x':.40, 'y':.7})
        get_device_pin.bind(text=partial(self.get_device_pin_func,current_device))
        self.widgets['get_device_pin']=get_device_pin

        get_advanced_device_pin_label=MinimumBoundingLabel(text="[size=18]Advanced Device I/O Pin:[/size]",
                        pos_hint = {'x':.1, 'y':.6},
                        color = palette('dark_shade',1),
                        markup=True)

        get_advanced_device_pin=Spinner(
            text="Select GPIO Pin",
            values=(general.pin_decode(i) for i in range(1,41) if i not in (1,2,4,6,9,14,17,20,25,30,34,39)),#eliminate 3.3v,5v,and ground pins
            size_hint =(.5, .05),
            pos_hint = {'x':.40, 'y':.6},
            disabled=True)
        get_advanced_device_pin.bind(text=partial(self.get_advanced_device_pin_func,current_device))
        self.widgets['get_advanced_device_pin']=get_advanced_device_pin

        get_trigger_label=MinimumBoundingLabel(text="[size=18]Device Pin Trigger State:[/size]",
                        pos_hint = {'x':.1, 'y':.5},
                        color = palette('dark_shade',1),
                        markup=True)

        get_trigger_state=Spinner(
            text="High",
            values=("High","Low"),
            size_hint =(.5, .05),
            pos_hint = {'x':.40, 'y':.5},
            disabled=True)
        get_trigger_state.bind(text=partial(self.get_trigger_state_func,current_device))
        self.widgets['get_trigger_state']=get_trigger_state

        advanced_toggle=RoundedToggleButton(
            text='Enable Advanced Pin Selection',
            size_hint =(.5, .05),
            pos_hint = {'x':.40, 'y':.4},
            # background_normal='',
            background_down='',
            background_color=palette('primary',.75),
            markup=True)
        self.widgets['advanced_toggle']=advanced_toggle
        advanced_toggle.bind(state=partial(self.advanced_toggle_func,current_device))

        lay_out.add_widget(get_name_label)
        lay_out.add_widget(get_name)
        lay_out.add_widget(get_device_label)
        lay_out.add_widget(get_device_type)
        lay_out.add_widget(get_device_pin_label)
        lay_out.add_widget(get_device_pin)
        lay_out.add_widget(get_advanced_device_pin_label)
        lay_out.add_widget(get_advanced_device_pin)
        lay_out.add_widget(get_trigger_label)
        lay_out.add_widget(get_trigger_state)
        lay_out.add_widget(advanced_toggle)
        lay_out.add_widget(new_device_back_button)
        lay_out.add_widget(new_device_save_button)
        if open:
            self.set_default_name()
            overlay_menu.open()

    def new_device_overlay_close(self,button):
        self.widgets['overlay_menu'].dismiss()

    def new_device_save(self,current_device,*args):
        toast=App.get_running_app().notifications.toast
        if current_device.name in [general.strip_markup(i.text) for i in self.widgets['device_layout'].children]:
            logger.error("main.new_device_save(): can not save device; device name already taken")
            toast('[b][size=20]Device name already exists','error')
            return False
        if current_device.name=="default" or re.search('^\s*$',current_device.name):
            logger.error("main.new_device_save(): can not save device without name")
            toast('[b][size=20]Can not save without\ndevice name','error')
            return False
        if current_device.pin==0 or all((not isinstance(current_device.pin,int), current_device.type!='Manometer')):
            logger.error("main.new_device_save(): can not save device without pin designation")
            toast('[b][size=20]Can not save without\npin designation','error')
            return False
        data={
            "device_name":current_device.name,
            "gpio_pin":current_device.pin,
            "run_time":current_device.run_time,
            "color":current_device.color,
            "trigger":current_device.trigger.lower()}
        with open(rf"logs/devices/{current_device.name}.json","w+") as write_file:
            json.dump(data, write_file,indent=0)
        with open(rf"logs/devices/backups/{current_device.name}.json","w+") as write_file:
            json.dump(data, write_file,indent=0)
        with open(rf"logs/devices/device_list.json","r+") as read_file:
            d_list=json.load(read_file)
            d_list[current_device.name]=current_device.device_types[current_device.type]
            read_file.seek(0)
            json.dump(d_list,read_file,indent=0)
            read_file.truncate()
        self.aggregate_devices()
        self.widgets['overlay_menu'].dismiss()

    def get_name_func(self,current_device,button,*args):
        current_device.name=button.text
    def set_default_name(self,*args):
        name_input=self.widgets['get_name']
        gdt=self.widgets['get_device_type']
        default_values={"Exfan":'Exhaust Fan',
                        "MAU":'Makeup Air Fan',
                        "Heat":'Heat Sensor',
                        "Light":'Lights',
                        "Dry":'Dry Contact',
                        "GV":'Gas Valve',
                        "Micro":'Fire System Micro Switch',
                        "Light Switch":'Light Switch',
                        "Fans Switch":'Fans Switch',
                        "Manometer":"Manometer"}
        if name_input.text!='' and name_input.text.translate({ord(ch): None for ch in '-0123456789'}) not in default_values.values():
            return
        name_input.text=default_values[gdt.text]
        if name_input.text in [general.strip_markup(i.text) for i in self.widgets['device_layout'].children]:
            temp_name=name_input.text
            temp_name+='-'
            auto_increment=2
            while temp_name+str(auto_increment) in [general.strip_markup(i.text) for i in self.widgets['device_layout'].children]:
                auto_increment+=1
            name_input.text=temp_name+str(auto_increment)

    def set_default_pin(self,device,button,device_type,*args):
        pin_select_button=self.widgets['get_device_pin']
        if device_type=="Manometer":
            device.pin=(3,5)
            pin_select_button.disabled=True
            pin_select_button.text='3(sda),5(scl)'
        elif pin_select_button.text=='3(sda),5(scl)':
            pin_select_button.disabled=False
            pin_select_button.text="Select GPIO Pin"


    def get_device_type_func(self,current_device,button,value):
        current_device.type=value
        if value=="Exfan":
            current_device.color=palette('dark_shade',.85)
        elif value=="MAU":
            current_device.color=palette('dark_shade',.85)
        elif value=="Light":
            current_device.color=palette('dark_shade',.85)
        elif value=="Dry":
            current_device.color=palette('dark_shade',.85)
        elif value=="GV":
            current_device.color=palette('dark_shade',.85)
        elif value=="Micro":
            current_device.color=palette('highlight',.85)
        elif value=="Heat":
            current_device.color=palette('dark_shade',.85)
        elif value=="Light Switch":
            current_device.color=palette('dark_shade',.85)
        elif value=="Fans Switch":
            current_device.color=palette('dark_shade',.85)
        elif value=="Manometer":
            current_device.color=palette('dark_shade',.85)
    def get_device_pin_func(self,current_device,button,value):
        if current_device.type=='Manometer':
            return
        if value=='Select GPIO Pin':
            return
        #value is get_device_pin.text
        #string is split to pull out BOARD int
        current_device.pin=int(value.split()[1])
    def get_advanced_device_pin_func(self,current_device,button,value):
        if current_device.type=='Manometer':
            return
        if value=='Select GPIO Pin':
            return
        #value is get_device_pin.text
        #string is split to pull out BOARD int
        current_device.pin=int(value.split()[1])
    def get_trigger_state_func(self,current_device,button,value):
        current_device.trigger=value.lower()

    def advanced_toggle_func(self,current_device,button,state,*args):
        w=self.widgets
        normal_select=w['get_device_pin']
        adv_select=w['get_advanced_device_pin']
        trigger_select=w['get_trigger_state']
        current_device.pin=0
        if state=='down':
            normal_select.disabled=True
            normal_select.text='Select GPIO Pin'
            adv_select.disabled=False
            trigger_select.disabled=False
        else:
            normal_select.disabled=False
            adv_select.disabled=True
            adv_select.text='Select GPIO Pin'
            trigger_select.disabled=True

    def edit_device_overlay(self,device):
        class InfoShelf():
            def __init__(self,device) -> None:
                self.name=device.name
                if isinstance(device,Exhaust):
                    self.type="Exfan"
                elif isinstance(device,Mau):
                    self.type="MAU"
                elif isinstance(device,Light):
                    self.type="Light"
                elif isinstance(device,DryContact):
                    self.type="Dry"
                elif isinstance(device,GasValve):
                    self.type="GV"
                elif isinstance(device,MicroSwitch):
                    self.type="Micro"
                elif isinstance(device,HeatSensor):
                    self.type="Heat"
                elif isinstance(device,SwitchLight):
                    self.type="Light Switch"
                elif isinstance(device,SwitchFans):
                    self.type="Fans Switch"
                elif isinstance(device,Manometer):
                    self.type="Manometer"
                self.pin=device.pin
                self.color=device.color
                self.run_time=device.run_time
                self.trigger=device.trigger
                self.device_types={
                    "Exfan":"exhaust.Exhaust",
                    "MAU":"mau.Mau",
                    "Light":"light.Light",
                    "Dry":"drycontact.DryContact",
                    "GV":"gas_valve.GasValve",
                    "Micro":"micro_switch.MicroSwitch",
                    "Heat":"heat_sensor.HeatSensor",
                    "Light Switch":"switch_light.SwitchLight",
                    "Fans Switch":"switch_fans.SwitchFans",
                    "Manometer":"manometer.Manometer"}
        current_device=InfoShelf(device)

        overlay_menu=self.widgets['overlay_menu']
        lay_out=self.widgets['overlay_layout']
        overlay_menu.title='Edit Device Configuration'
        overlay_menu.separator_height=0
        overlay_menu.auto_dismiss=True
        self.widgets['overlay_layout'].clear_widgets()

        edit_device_back_button=RoundedButton(text=current_language['about_back'],
                        size_hint =(.4, .15),
                        pos_hint = {'x':.05, 'y':.025},
                        background_down='',
                        background_color=palette('highlight',.85),
                        markup=True)
        self.widgets['edit_device_back_button']=edit_device_back_button
        edit_device_back_button.ref='about_back'
        edit_device_back_button.bind(on_release=partial(self.edit_device_overlay_close,device))

        edit_device_save_button=RoundedButton(text=current_language['save'],
                        size_hint =(.4, .15),
                        pos_hint = {'x':.55, 'y':.025},
                        # background_normal='',
                        background_down='',
                        background_color=palette('complement',.85),
                        markup=True)
        self.widgets['edit_device_save_button']=edit_device_save_button
        edit_device_save_button.ref='save'
        edit_device_save_button.bind(on_release=partial(self.edit_device_save,current_device,device))

        get_name_label=MinimumBoundingLabel(text="[size=18]Device Name:[/size]",
                        pos_hint = {'x':.05, 'y':.9},
                        color = palette('dark_shade',1),
                        markup=True)

        get_name=TextInput(multiline=False,
                        focus=False,
                        text=f"{device.name}",
                        size_hint =(.5, .055),
                        pos_hint = {'x':.40, 'y':.9})
        get_name.bind(on_text_validate=partial(self.edit_name_func,current_device))
        get_name.bind(text=partial(self.edit_name_func,current_device))

        get_device_label=MinimumBoundingLabel(text="[size=18]Device Type: (Locked)[/size]",
                        pos_hint = {'x':.05, 'y':.8},
                        color = palette('dark_shade',1),
                        markup=True)

        get_device_type=Spinner(
                        disabled=True,
                        text=current_device.type,
                        values=("Exfan","MAU","Heat","Light","Dry","Micro","Light Switch","Fans Switch","Manometer"),
                        size_hint =(.5, .05),
                        pos_hint = {'x':.40, 'y':.8})
        get_device_type.bind(text=partial(self.edit_device_type_func,current_device))

        get_device_pin_label=MinimumBoundingLabel(text="[size=18]Device I/O Pin:[/size]",
                        pos_hint = {'x':.05, 'y':.7},
                        color = palette('dark_shade',1),
                        markup=True)

        edit_device_pin=Spinner(
                        text=general.pin_decode(str(device.pin)),
                        values=(general.pin_decode(i) for i in logic.available_pins),
                        size_hint =(.5, .05),
                        pos_hint = {'x':.40, 'y':.7})
        edit_device_pin.bind(text=partial(self.edit_device_pin_func,current_device))
        self.widgets['edit_device_pin']=edit_device_pin

        get_advanced_device_pin_label=MinimumBoundingLabel(text="[size=18]Advanced Device I/O Pin:[/size]",
                        pos_hint = {'x':.05, 'y':.6},
                        color = palette('dark_shade',1),
                        markup=True)

        edit_advanced_device_pin=Spinner(
            text="Select GPIO Pin",
            values=(general.pin_decode(i) for i in range(1,41) if i not in (1,2,4,6,9,14,17,20,25,30,34,39)),#eliminate 3.3v,5v,and ground pins
            size_hint =(.5, .05),
            pos_hint = {'x':.40, 'y':.6},
            disabled=True)
        edit_advanced_device_pin.bind(text=partial(self.edit_advanced_device_pin_func,current_device))
        self.widgets['edit_advanced_device_pin']=edit_advanced_device_pin

        edit_trigger_label=MinimumBoundingLabel(text="[size=18]Device Pin Trigger State:[/size]",
                        pos_hint = {'x':.05, 'y':.5},
                        color = palette('dark_shade',1),
                        markup=True)

        edit_trigger_state=Spinner(
            text=device.trigger.capitalize(),
            values=("High","Low"),
            size_hint =(.5, .05),
            pos_hint = {'x':.40, 'y':.5},
            disabled=True)
        edit_trigger_state.bind(text=partial(self.edit_trigger_state_func,current_device))
        self.widgets['edit_trigger_state']=edit_trigger_state

        edit_advanced_toggle=RoundedToggleButton(
            text='Enable Advanced Pin Selection',
            size_hint =(.5, .05),
            pos_hint = {'x':.40, 'y':.4},
            # background_normal='',
            background_down='',
            background_color=palette('primary',.75),
            markup=True)
        self.widgets['edit_advanced_toggle']=edit_advanced_toggle
        edit_advanced_toggle.bind(state=partial(self.edit_advanced_toggle_func,current_device))

        lay_out.add_widget(get_name_label)
        lay_out.add_widget(get_name)
        lay_out.add_widget(get_device_label)
        lay_out.add_widget(get_device_type)
        lay_out.add_widget(get_device_pin_label)
        lay_out.add_widget(edit_device_pin)
        lay_out.add_widget(get_advanced_device_pin_label)
        lay_out.add_widget(edit_advanced_device_pin)
        lay_out.add_widget(edit_trigger_label)
        lay_out.add_widget(edit_trigger_state)
        lay_out.add_widget(edit_advanced_toggle)
        lay_out.add_widget(edit_device_back_button)
        lay_out.add_widget(edit_device_save_button)

    def edit_device_overlay_close(self,device,button):
        self.info_overlay(device,open=False)

    def edit_device_save(self,current_device,device,button):
        toast=App.get_running_app().notifications.toast
        w=self.widgets
        pin_select=w['edit_device_pin']
        adv_pin_select=w['edit_advanced_device_pin']
        if device.name!=current_device.name and \
            current_device.name in [general.strip_markup(i.text) for i in self.widgets['device_layout'].children]:
            logger.error("main.edit_device_save(): can not save device; device name already taken")
            toast('[b][size=20]Device name already exists','error')
            return
        if current_device.name=="default" or re.search('^\s*$',current_device.name):
            logger.error("main.edit_device_save(): can not save device without name")
            toast('[b][size=20]Can not save without\ndevice name','error')
            return
        if current_device.pin==0 or \
            all((not isinstance(current_device.pin,int), current_device.type!='Manometer')) or \
            all((pin_select.text=='Select GPIO Pin',adv_pin_select.text=='Select GPIO Pin')):
            logger.error("main.edit_device_save(): can not save device without pin designation")
            toast('[b][size=20]Can not save without\npin designation','error')
            return
        if current_device.trigger not in ('low','high'):
            logger.error("main.edit_device_save(): can not save device without trigger state")
            toast('[b][size=20]Can not save without\ntrigger state','error')
            return
        data={
            "device_name":current_device.name,
            "gpio_pin":current_device.pin,
            "run_time":current_device.run_time,
            "color":current_device.color,
            "trigger":current_device.trigger,
            "load_error":False}
        if device.name!=current_device.name:
            os.rename(rf"logs/devices/{device.name}.json",rf"logs/devices/{current_device.name}.json")
        with open(rf"logs/devices/{current_device.name}.json","w") as write_file:
            json.dump(data, write_file,indent=0)
        with open(rf"logs/devices/backups/{current_device.name}.json","w") as write_file:
            json.dump(data, write_file,indent=0)
        with open(rf"logs/devices/device_list.json","r+") as read_file:
            d_list=json.load(read_file)
            if device.name!=current_device.name:
                d_list[current_device.name]=d_list.pop(device.name)
            else:
                d_list[current_device.name]=current_device.device_types[current_device.type]
            read_file.seek(0)
            json.dump(d_list,read_file,indent=0)
            read_file.truncate()
        device.name=current_device.name
        if device.pin != current_device.pin:
            if device.pin in logic._available_pins:
                logic.available_pins.append(device.pin)
            if current_device.pin in logic.available_pins:
                logic.available_pins.remove(current_device.pin)
            logic.available_pins.sort()
            logic.pin_off(device.pin)
            device.pin=current_device.pin
            logic.set_pin_mode(device)
        device.trigger = current_device.trigger
        device.load_error = False
        self.aggregate_devices()
        self.info_overlay(device,open=False)

    def edit_name_func(self,current_device,button,*args):
        current_device.name=button.text
    def edit_device_type_func(self,current_device,button,value):
        current_device.type=value
        if value=="Exfan":
            current_device.color=palette('dark_shade',.85)
        elif value=="MAU":
            current_device.color=palette('dark_shade',.85)
        elif value=="Light":
            current_device.color=palette('dark_shade',.85)
        elif value=="Dry":
            current_device.color=palette('dark_shade',.85)
        elif value=="GV":
            current_device.color=palette('dark_shade',.85)
        elif value=="Micro":
            current_device.color=palette('highlight',.85)
        elif value=="Heat":
            current_device.color=palette('dark_shade',.85)
        elif value=="Light Switch":
            current_device.color=palette('dark_shade',.85)
        elif value=="Fans Switch":
            current_device.color=palette('dark_shade',.85)
        elif value=="Manometer":
            current_device.color=palette('dark_shade',.85)
    def edit_device_pin_func(self,current_device,button,value):
        if current_device.type=='Manometer':
            return
        if value=='Select GPIO Pin':
            return
        #value is get_device_pin.text
        #string is split to pull out BOARD int
        current_device.pin=int(value.split()[1])
    def edit_advanced_device_pin_func(self,current_device,button,value):
        if current_device.type=='Manometer':
            return
        if value=='Select GPIO Pin':
            return
        #value is get_device_pin.text
        #string is split to pull out BOARD int
        current_device.pin=int(value.split()[1])
    def edit_trigger_state_func(self,current_device,button,value):
        current_device.trigger=value.lower()

    def edit_advanced_toggle_func(self,current_device,button,state,*args):
        w=self.widgets
        normal_select=w['edit_device_pin']
        adv_select=w['edit_advanced_device_pin']
        trigger_select=w['edit_trigger_state']
        if state=='down':
            normal_select.disabled=True
            normal_select.text='Select GPIO Pin'
            adv_select.disabled=False
            trigger_select.disabled=False
        else:
            normal_select.disabled=False
            normal_select.text=general.pin_decode(str(current_device.pin))
            adv_select.disabled=True
            adv_select.text='Select GPIO Pin'
            trigger_select.disabled=True

    def devices_back (self,button):
        self.widgets['device_scroll'].scroll_y=1
        self.parent.transition = SlideTransition(direction='right')
        self.manager.current='preferences'
    def devices_back_main (self,button):
        self.widgets['device_scroll'].scroll_y=1
        self.parent.transition = SlideTransition(direction='down')
        self.manager.current='main'
    def info_func (self,device,button):
        self.info_overlay(device)

    def aggregate_devices(self):
        logic.get_devices()
        if logic.devices:
            self.widgets['device_layout'].clear_widgets()
            for i in logic.devices:
                device=RoundedScrollItemTemplate(i.name,color=i.color)
                self.widgets['device_layout'].add_widget(device)
                device.bind(on_release=partial(self.info_func,i))
                if hasattr(i,'load_error'):
                    if i.load_error:
                        device.add_widget(NotificationBadge((-.1375,.7)))
        else:
            logger.info("main.py aggregate_devices(): no devices")
            self.widgets['device_layout'].clear_widgets()
            self.widgets['device_layout'].add_widget(self.widgets['device_details'])
        new_device=RoundedScrollItemTemplate(
                        '[/color][color=#000000]Add Device +',
                        color=palette('neutral',.85))
        self.widgets['device_layout'].add_widget(new_device)
        new_device.bind(on_release=self.new_device_func)

    def new_device_func(self,button):
        if App.get_running_app().admin_mode_start>time.time() or self.unlocked:
            self.new_device_overlay()
        else:
            self.add_widget(PinLock(partial(self.unlock_callback,self.new_device_overlay)))

    def prompt_unlock(self,button,touch,*args):
        if not button.collide_point(*touch.pos):
            return
        if self.unlocked:
            return
        for widget in self.children:
            if type(widget)==PinLock:
                return
        self.add_widget(PinLock(self.unlock))

    def unlock(self,*args):
        self.unlocked=True
        self.check_admin_mode()

    def unlock_callback(self,callback,*args):
        self.unlock()
        callback()

    def check_admin_mode(self):
        if App.get_running_app().admin_mode_start>time.time() or self.unlocked:
            if 'info_add_icon' in  self.widgets:
                self.widgets['info_add_icon'].color=palette('light_tint',.5)
            if 'delete_icon' in self.widgets:
                self.widgets['delete_icon'].color=palette('light_tint',.8)
            if 'info_admin_hint' in self.widgets:
                self.widgets['overlay_layout'].remove_widget(self.widgets['info_admin_hint'])
        else:
            if 'info_admin_hint' in self.widgets:
                self.widgets['overlay_layout'].add_widget(self.widgets['info_admin_hint'])
            if 'info_add_icon' in  self.widgets:
                self.widgets['info_add_icon'].color=palette('light_tint',.15)
            if 'delete_icon' in self.widgets:
                self.widgets['delete_icon'].color=palette('light_tint',.15)

    def on_pre_enter(self):
        self.unlocked=False
        self.aggregate_devices()

    def on_leave(self):
        self.widgets['batch_add_layout'].shrink()

class TrainScreen(Screen):
    def __init__(self, **kw):
        super(TrainScreen,self).__init__(**kw)
        bg_image = Image(source=background_image, allow_stretch=True, keep_ratio=False)
        self.widgets={}

        back=RoundedButton(text=current_language['report_back'],
                    size_hint =(.4, .1),
                    pos_hint = {'x':.06, 'y':.015},
                    background_down='',
                    background_color=palette('neutral',.85),
                    markup=True)
        self.widgets['back']=back
        back.ref='report_back'
        back.bind(on_release=self.train_back)

        back_main=RoundedButton(text=current_language['report_back_main'],
                        size_hint =(.4, .1),
                        pos_hint = {'x':.52, 'y':.015},
                        background_normal='',
                        background_color=palette('primary',.9),
                        markup=True)
        self.widgets['back_main']=back_main
        back_main.ref='report_back_main'
        back_main.bind(on_release=self.train_back_main)

        train_details=ScrollItemTemplate(current_language['no_train'],color=palette('base',.85))
        self.widgets['train_details']=train_details
        train_details.ref='no_train'

        train_layout=EventpassGridLayout(
            size_hint_y=None,
            size_hint_x=1,
            cols=1,
            padding=10,
            spacing=(1,5)
            )
        self.widgets['train_layout']=train_layout
        train_layout.bind(minimum_height=train_layout.setter('height'))

        train_scroll=ScrollView(
            bar_width=8,
            do_scroll_y=True,
            do_scroll_x=False,
            size_hint_y=None,
            size_hint_x=1,
            size_hint =(.9, .80),
            pos_hint = {'center_x':.5, 'y':.18}
            )
        self.widgets['train_scroll']=train_scroll

        seperator_line=Image(source=gray_seperator_line,
                    allow_stretch=True,
                    keep_ratio=False,
                    size_hint =(.98, .001),
                    pos_hint = {'x':.01, 'y':.13})

        train_layout.add_widget(train_details)
        train_scroll.add_widget(train_layout)
        self.add_widget(bg_image)
        self.add_widget(back)
        self.add_widget(back_main)
        self.add_widget(train_scroll)
        self.add_widget(seperator_line)

    def train_back (self,button):
        self.parent.transition = SlideTransition(direction='right')
        self.manager.current='preferences'
    def train_back_main (self,button):
            self.parent.transition = SlideTransition(direction='down')
            self.manager.current='main'

class PreferenceScreen(Screen):
    def __init__(self, **kwargs):
        super(PreferenceScreen,self).__init__(**kwargs)
        self.cols = 2
        self.widgets={}
        self.ud={}
        bg_image = Image(source=background_image, allow_stretch=True, keep_ratio=False)
        self.duration_flag=0

        back=RoundedButton(text=current_language['preferences_back'],
                        size_hint =(.4, .1),
                        pos_hint = {'x':.06, 'y':.015},
                        background_down='',
                        background_color=palette('neutral',.9),
                        markup=True)
        self.widgets['back']=back
        back.ref='preferences_back'
        back.bind(on_release=self.settings_back)

        back_main=RoundedButton(text=current_language['preferences_back_main'],
                        size_hint =(.4, .1),
                        pos_hint = {'x':.52, 'y':.015},
                        background_normal='',
                        background_color=palette('primary',.9),
                        markup=True)
        self.widgets['back_main']=back_main
        back_main.ref='preferences_back_main'
        back_main.bind(on_release=self.settings_back_main)

        pref_scroll=ScrollView(
            bar_width=8,
            do_scroll_y=True,
            do_scroll_x=False,
            size_hint =(.9, .85),
            pos_hint = {'center_x':.5, 'y':.14})
        pref_scroll.bar_color=palette('primary',.75)
        pref_scroll.bar_inactive_color=palette('primary',.55)
        self.widgets['pref_scroll']=pref_scroll

        scroll_layout=EventpassGridLayout(
            size_hint_y=1.25,
            size_hint_x=.95,
            cols=2,
            padding=10,
            spacing=(35,35))
        self.widgets['scroll_layout']=scroll_layout
        scroll_layout.bind(minimum_height=scroll_layout.setter('height'))

        advanced_settings=RoundedButton(text=current_language['advanced_settings'],
                        size_hint =(1, 1),
                        #pos_hint = {'x':.01, 'y':.9},
                        background_down='',
                        background_color=palette('neutral',.9),
                        markup=True)
        self.widgets['advanced_settings']=advanced_settings
        advanced_settings.ref='advanced_settings'
        advanced_settings.bind(on_release=self.advanced_settings_func)

        general_settings=RoundedButton(text=current_language['general_settings'],
                        size_hint =(1, 1),
                        #pos_hint = {'x':.01, 'y':.9},
                        background_down='',
                        background_color=palette('neutral',.9),
                        markup=True)
        self.widgets['general_settings']=general_settings
        general_settings.ref='general_settings'
        general_settings.bind(on_release=self.general_settings_func)

        train=RoundedButton(text=current_language['train'],
                        size_hint =(1, 1),
                        pos_hint = {'x':.01, 'y':.6},
                        background_down='',
                        disabled=True,
                        background_color=palette('base',.9),
                        markup=True)
        self.widgets['train']=train
        train.ref='train'
        train.bind(on_release=self.train_func)

        about=RoundedButton(text=current_language['about'],
                        size_hint =(1, 1),
                        pos_hint = {'x':.01, 'y':.7},
                        background_down='',
                        background_color=palette('neutral',.9),
                        markup=True)
        self.widgets['about']=about
        about.ref='about'
        about.bind(on_release=self.about_func)

        account=RoundedButton(text=current_language['account'],
                        size_hint =(1, 1),
                        pos_hint = {'x':.01, 'y':.7},
                        background_down='',
                        background_color=palette('base',.9),
                        markup=True)
        self.widgets['account']=account
        account.ref='account'
        account.bind(on_release=self.account_func)
        account.disabled=True

        network=RoundedButton(text=current_language['network'],
                        size_hint =(1, 1),
                        pos_hint = {'x':.01, 'y':.7},
                        background_down='',
                        background_color=palette('neutral',.9),
                        markup=True)
        self.widgets['network']=network
        network.ref='network'
        network.bind(on_release=self.network_func)

        clean_mode=RoundedButton(text=current_language['clean_mode'],
                        size_hint =(1, 1),
                        pos_hint = {'x':.01, 'y':.8},
                        background_down='',
                        background_color=palette('neutral',.9),
                        markup=True)
        self.widgets['clean_mode']=clean_mode
        clean_mode.ref='clean_mode'
        clean_mode.bind(on_release=self.clean_mode_func)

        commission=RoundedButton(text=current_language['commission'],
                        size_hint =(1, 1),
                        pos_hint = {'x':.01, 'y':.5},
                        background_down='',
                        background_color=palette('neutral',.9),
                        markup=True)
        self.widgets['commission']=commission
        commission.ref='commission'
        commission.bind(on_release=self.commission_func)

        logs=RoundedButton(
            text=current_language['logs'],
            size_hint =(.9, .18),
            pos_hint = {'x':.05, 'y':.78},
            background_down='',
            background_color=palette('neutral',.9),
            markup=True)
        self.widgets['logs']=logs
        logs.ref='logs'
        logs.bind(on_release=self.device_logs)

        pins=RoundedButton(text=current_language['pins'],
                        size_hint =(1, 1),
                        pos_hint = {'x':.01, 'y':.4},
                        background_down='',
                        background_color=palette('neutral',.9),
                        markup=True)
        self.widgets['pins']=pins
        pins.ref='pins'
        pins.bind(on_release=self.pins_func)

        self.blur = EffectWidget()

        overlay_menu=Popup(
            size_hint=(.8, .8),
            background = 'atlas://data/images/defaulttheme/bubble',
            title_color=[0, 0, 0, 1],
            title_size='38',
            title_align='center',
            separator_color=palette('highlight', .5))
        self.widgets['overlay_menu']=overlay_menu
        overlay_menu.ref='heat_overlay'

        overlay_layout=FloatLayout()
        self.widgets['overlay_layout']=overlay_layout

        overlay_x=IconButton(
            source=overlay_x_icon,
            size_hint=(.1,.1),
            pos_hint={'x':.95,'y':.98})
        overlay_x.bind(on_release=overlay_menu.dismiss)
        self.widgets['overlay_x']=overlay_x

        seperator_line=Image(source=gray_seperator_line,
                    allow_stretch=True,
                    keep_ratio=False,
                    size_hint =(.98, .001),
                    pos_hint = {'x':.01, 'y':.13})


        overlay_menu.add_widget(overlay_layout)
        self.add_widget(bg_image)
        self.add_widget(back)
        self.add_widget(back_main)
        scroll_layout.add_widget(network)
        scroll_layout.add_widget(account)
        scroll_layout.add_widget(general_settings)
        scroll_layout.add_widget(advanced_settings)
        scroll_layout.add_widget(clean_mode)
        scroll_layout.add_widget(train)
        scroll_layout.add_widget(commission)
        scroll_layout.add_widget(about)
        scroll_layout.add_widget(pins)
        scroll_layout.add_widget(logs)
        pref_scroll.add_widget(scroll_layout)
        self.add_widget(pref_scroll)
        self.add_widget(seperator_line)

    def heat_overlay(self):
        overlay_menu=self.widgets['overlay_menu']
        overlay_menu.background_color=palette('dark_shade',.75)
        overlay_menu.title=''
        overlay_menu.separator_height=0
        overlay_menu.auto_dismiss=True
        self.widgets['overlay_layout'].clear_widgets()
        self.widgets['overlay_layout'].add_widget(self.widgets['overlay_x'])

        overlay_title=Label(text=current_language['heat_overlay'],
                        pos_hint = {'x':.0, 'y':.5},
                        markup=True)
        self.widgets['overlay_title']=overlay_title
        overlay_title.ref='heat_overlay'

        duration_1=RoundedButton(text=current_language['duration_1'],
                        size_hint =(.96, .125),
                        pos_hint = {'x':.02, 'y':.5},
                        background_normal='',
                        background_color=palette('primary',.85),
                        markup=True)
        self.widgets['duration_1']=duration_1
        duration_1.ref='duration_1'

        duration_2=RoundedButton(text=current_language['duration_2'],
                        size_hint =(.96, .125),
                        pos_hint = {'x':.02, 'y':.3},
                        background_normal='',
                        background_color=palette('primary',.85),
                        markup=True)
        self.widgets['duration_2']=duration_2
        duration_1.ref='duration_2'

        duration_3=RoundedButton(text=current_language['duration_3'],
                        size_hint =(.96, .125),
                        pos_hint = {'x':.02, 'y':.1},
                        background_normal='',
                        background_color=palette('primary',.85),
                        markup=True)
        self.widgets['duration_3']=duration_3
        duration_1.ref='duration_3'

        def duration_1_func(button):
            config=App.get_running_app().config_
            logic.heat_sensor_timer=300
            config.set('preferences','heat_timer','300')
            with open(preferences_path,'w') as configfile:
                config.write(configfile)
            self.widgets['overlay_menu'].dismiss()
        duration_1.bind(on_release=duration_1_func)

        def duration_2_func(button):
            config=App.get_running_app().config_
            logic.heat_sensor_timer=900
            config.set('preferences','heat_timer','900')
            with open(preferences_path,'w') as configfile:
                config.write(configfile)
            self.widgets['overlay_menu'].dismiss()
        duration_2.bind(on_release=duration_2_func)

        def duration_3_func(button):
            config=App.get_running_app().config_
            logic.heat_sensor_timer=1800
            config.set('preferences','heat_timer','1800')
            with open(preferences_path,'w') as configfile:
                config.write(configfile)
            self.widgets['overlay_menu'].dismiss()
        duration_3.bind(on_release=duration_3_func)

        self.widgets['overlay_layout'].add_widget(overlay_title)
        self.widgets['overlay_layout'].add_widget(duration_1)
        self.widgets['overlay_layout'].add_widget(duration_2)
        self.widgets['overlay_layout'].add_widget(duration_3)
        self.widgets['overlay_menu'].open()

    def maint_overlay(self):
        overlay_menu=self.widgets['overlay_menu']
        overlay_menu.background_color=palette('dark_shade',.75)
        overlay_menu.title=''
        overlay_menu.separator_height=0
        overlay_menu.auto_dismiss=True
        self.widgets['overlay_layout'].clear_widgets()
        self.widgets['overlay_layout'].add_widget(self.widgets['overlay_x'])

        warning_text=Label(
            text=current_language['maint_overlay_warning_text'],
            markup=True,
            size_hint =(1,.6),
            pos_hint = {'x':0, 'y':.4},)
        self.widgets['warning_text']=warning_text
        warning_text.ref='maint_overlay_warning_text'

        continue_button=RoundedButton(text=current_language['continue_button'],
                        size_hint =(.35, .25),
                        pos_hint = {'x':.05, 'y':.05},
                        background_normal='',
                        background_color=palette('primary',.85),
                        markup=True)
        self.widgets['continue_button']=continue_button
        continue_button.ref='continue_button'

        cancel_button=RoundedButton(text=current_language['cancel_button'],
                        size_hint =(.35, .25),
                        pos_hint = {'x':.6, 'y':.05},
                        background_normal='',
                        background_color=palette('primary',.85),
                        markup=True)
        self.widgets['cancel_button']=cancel_button
        cancel_button.ref='cancel_button'

        def continue_button_func(button):
            self.override_overlay()
        continue_button.bind(on_release=continue_button_func)

        def cancel_button_func(button):
            self.widgets['overlay_menu'].dismiss()
        cancel_button.bind(on_release=cancel_button_func)

        self.widgets['overlay_layout'].add_widget(warning_text)
        self.widgets['overlay_layout'].add_widget(continue_button)
        self.widgets['overlay_layout'].add_widget(cancel_button)
        self.widgets['overlay_menu'].open()

    def override_overlay(self):
        logic.fs.moli['maint_override']=1
        ls=App.get_running_app().context_screen.get_screen('main').widgets['lights']
        if ls.state=='down':
            ls.trigger_action()
        overlay_menu=self.widgets['overlay_menu']
        overlay_menu.title=''
        overlay_menu.separator_height=0
        overlay_menu.auto_dismiss=False
        self.widgets['overlay_layout'].clear_widgets()

        warning_text=Label(
            text=current_language['override_overlay_warning_text'],
            markup=True,
            size_hint =(1,.6),
            pos_hint = {'x':0, 'y':.4},)
        self.widgets['warning_text']=warning_text
        warning_text.ref='override_overlay_warning_text'

        disable_button=RoundedButton(text=current_language['disable_button'],
                        size_hint =(.9, .25),
                        pos_hint = {'x':.05, 'y':.05},
                        background_normal='',
                        background_color=palette('primary',.85),
                        markup=True)
        self.widgets['disable_button']=disable_button
        disable_button.ref='disable_button'

        light_button=RoundedToggleButton(text=current_language['lights'],
                        size_hint =(.2, .25),
                        pos_hint = {'x':.75, 'y':.05},
                        background_down='',
                        background_color=palette('primary',.85),
                        markup=True)
        self.widgets['light_button']=light_button
        light_button.ref='lights'

        disable_progress=CircularProgressBar()
        disable_progress._widget_size=200
        disable_progress._progress_colour=palette('primary',1)
        self.widgets['disable_progress']=disable_progress

        def light_button_func(button,*args):
            if logic.fs.moli['maint_override_light']==1:
                logic.fs.moli['maint_override_light']=0
            else:
                logic.fs.moli['maint_override_light']=1
        light_button.bind(state=light_button_func)

        def disable_button_func(button):
            logic.fs.moli['maint_override']=0
            logic.fs.moli['maint_override_light']=0
            self.widgets['overlay_menu'].dismiss()

        def progress_bar_update(dt,*args):
            self.widgets['disable_progress'].pos=self.widgets['disable_button'].last_touch.pos
            if not self.widgets['disable_progress'].parent:
                self.widgets['overlay_layout'].add_widget(self.widgets['disable_progress'])
            bar=App.get_running_app().context_screen.get_screen('preferences').widgets["disable_progress"]
            if bar.value >= 1000: # Checks to see if progress_bar.value has met 1000
                return False # Returning False schedule is canceled and won't repeat
            bar.value += 1000/3*dt#4.00 # Updates progress_bar's progress



        def create_clock(*args):
            Clock.schedule_once(disable_button_func, 3)
            self.ud['event'] = disable_button_func
            Clock.schedule_interval(progress_bar_update,.01)
            self.ud['event_bar'] = progress_bar_update

        def delete_clock(*args):
            bar=App.get_running_app().context_screen.get_screen('preferences').widgets["disable_progress"]
            if 'event' in self.ud:
                Clock.unschedule(self.ud['event'])
            if 'event_bar' in self.ud:
                self.widgets['overlay_layout'].remove_widget(disable_progress)
                Clock.unschedule(self.ud['event_bar'])
                bar.value=0

        disable_button.bind(
            on_press=create_clock,
            on_touch_up=delete_clock)

        self.widgets['overlay_layout'].add_widget(warning_text)
        self.widgets['overlay_layout'].add_widget(disable_button)
        self.widgets['overlay_layout'].add_widget(light_button)
        self.widgets['overlay_layout'].add_widget(disable_progress)

    def about_overlay(self):
        overlay_menu=self.widgets['overlay_menu']
        overlay_menu.title=''
        overlay_menu.separator_height=0
        overlay_menu.auto_dismiss=True
        self.widgets['overlay_layout'].clear_widgets()
        self.widgets['overlay_layout'].add_widget(self.widgets['overlay_x'])

        about_text=Label(
            text=current_language['about_overlay_text'],
            markup=True,
            size_hint =(1,.6),
            pos_hint = {'x':0, 'y':.4},)
        self.widgets['about_text']=about_text
        about_text.ref='about_overlay_text'

        version_info=Label(text=current_language['version_info_white'],
                markup=True,
                pos_hint = {'x':-.05, 'center_y':.6})
        version_info.ref='version_info'

        about_qr=Image(source=qr_link,
            allow_stretch=False,
            keep_ratio=True,
            size_hint =(.45,.45),
            pos_hint = {'x':.6, 'y':.58})

        qr_label=Label(text='[size=16][color=#ffffff]firesafeextinguisher.com[/color][/size]',
                markup=True,
                pos_hint = {'x':.33, 'center_y':.55})
        qr_label.ref='qr_label'

        about_back_button=RoundedButton(text=current_language['about_back'],
                        size_hint =(.9, .25),
                        pos_hint = {'x':.05, 'y':.05},
                        background_normal='',
                        background_color=palette('primary',.85),
                        markup=True)
        self.widgets['about_back_button']=about_back_button
        about_back_button.ref='about_back'

        def about_overlay_close(button):
            self.widgets['overlay_menu'].dismiss()
        about_back_button.bind(on_release=about_overlay_close)

        self.widgets['overlay_layout'].add_widget(about_text)
        self.widgets['overlay_layout'].add_widget(version_info)
        self.widgets['overlay_layout'].add_widget(about_qr)
        self.widgets['overlay_layout'].add_widget(qr_label)
        self.widgets['overlay_layout'].add_widget(about_back_button)
        self.widgets['overlay_menu'].open()

    def general_settings_overlay(self):
        overlay_menu=self.widgets['overlay_menu']
        overlay_menu.background_color=palette('dark_shade',.75)
        overlay_menu.title=''
        overlay_menu.separator_height=0
        overlay_menu.auto_dismiss=True
        self.widgets['overlay_layout'].clear_widgets()
        self.widgets['overlay_layout'].add_widget(self.widgets['overlay_x'])
        config=App.get_running_app().config_

        with overlay_menu.canvas.before:
           overlay_menu.msg_lines=Line(rounded_rectangle=(100, 100, 200, 200, 10, 10, 10, 10, 100),group='msg')

        def update_lines(*args):
            x=int(overlay_menu.width*.2)
            y=int(overlay_menu.height*.5)
            width=int(overlay_menu.width*.25)
            height=int(overlay_menu.height*.5)
            overlay_menu.msg_lines.rounded_rectangle=(x, y, width, height, 10, 10, 10, 10, 100)
        overlay_menu.bind(pos=update_lines, size=update_lines)

        # canvas is drawn to before widgets pos and size are set by parent.
        # update lines is bound to listen for changes to size and pos so it
        # can be updated accordingly.
        # however since the overlay is shared between different menus it does
        # not update its pos again after the drawing instructions are cleared,
        # this leads to the lines being drawn wrong again.
        # we call update_lines() while adding our message widgets to the overlay
        # to reposition the lines correctly before opening
        update_lines()

        def _swap_color(button,*args):
            if button.state=='down':
                button.bg_color=palette('primary',.85)
            if button.state=='normal':
                button.bg_color=palette('base',1)


        overlay_title=Label(text=current_language['general_settings_overlay'],
                        pos_hint = {'x':.0, 'y':.5},
                        markup=True)
        self.widgets['overlay_title']=overlay_title
        overlay_title.ref='general_settings_overlay'

        evoke_title=Label(text=current_language['evoke_title'],
                        pos_hint = {'center_x':.2, 'center_y':.87},
                        markup=True)
        self.widgets['evoke_title']=evoke_title
        evoke_title.ref='evoke_title'

        msg_evoke_on=RoundedToggleButton(text=current_language['msg_evoke_on'],
                        size_hint =(.2, .125),
                        pos_hint = {'center_x':.2, 'y':.65},
                        background_down='',
                        background_color=palette('base',.85),
                        markup=True,
                        group='evoke',
                        allow_no_selection=False)
        self.widgets['msg_evoke_on']=msg_evoke_on
        msg_evoke_on.ref='msg_evoke_on'
        msg_evoke_on.unbind(state=msg_evoke_on.color_swap)
        msg_evoke_on.bind(state=_swap_color)
        msg_evoke_on.bind(state=msg_evoke_on.color_swap)

        msg_evoke_off=RoundedToggleButton(text=current_language['msg_evoke_off'],
                        size_hint =(.2, .125),
                        pos_hint = {'center_x':.2, 'y':.45},
                        background_down='',
                        background_color=palette('base',.85),
                        markup=True,
                        group='evoke',
                        allow_no_selection=False)
        self.widgets['msg_evoke_off']=msg_evoke_off
        msg_evoke_off.ref='msg_evoke_off'
        msg_evoke_off.unbind(state=msg_evoke_off.color_swap)
        msg_evoke_off.bind(state=_swap_color)
        msg_evoke_off.bind(state=msg_evoke_off.color_swap)

        is_evoke=config.getboolean('preferences','evoke')
        if is_evoke:
            msg_evoke_on.state='down'
            _swap_color(msg_evoke_off)
        else:
            msg_evoke_off.state='down'
            _swap_color(msg_evoke_on)

        screensaver_timer_title=Label(text=current_language['screensaver_timer_title'],
                        pos_hint = {'center_x':.6, 'center_y':.9},
                        markup=True)
        self.widgets['screensaver_timer_title']=screensaver_timer_title
        screensaver_timer_title.ref='screensaver_timer_title'

        screensaver_timer_value=Label(
            text='[size=30][b][color=#ffffff]'+config.get('preferences','screensaver_timeout',fallback='10')+' Minutes',
            pos_hint = {'center_x':.6, 'center_y':.85},
            markup=True)
        self.widgets['screensaver_timer_value']=screensaver_timer_value

        screensaver_timer_setter=Slider(
            size_hint =(.4, .125),
            pos_hint = {'center_x':.6, 'y':.72},
            cursor_image=slider_handle_yellow,
            sensitivity='handle',
            min=1,
            max=30,
            step=1,
            value=config.getint('preferences','screensaver_timeout',fallback=10))
        self.widgets['screensaver_timer_setter']=screensaver_timer_setter

        heat_sensor_timer_title=Label(
            text=current_language['heat_sensor_timer_title'],
            pos_hint = {'center_x':.6, 'center_y':.58},
            markup=True)
        self.widgets['heat_sensor_timer_title']=heat_sensor_timer_title
        heat_sensor_timer_title.ref='heat_sensor_timer_title'

        heat_sensor_timer_value=Label(
            text='[size=30][b][color=#ffffff]'+str(int(config.getint('preferences','heat_timer',fallback=300))//60)+' Minutes',
            pos_hint = {'center_x':.6, 'center_y':.53},
            markup=True)
        self.widgets['heat_sensor_timer_value']=heat_sensor_timer_value

        heat_sensor_timer_setter=Slider(
            size_hint =(.4, .125),
            pos_hint = {'center_x':.6, 'y':.4},
            cursor_image=slider_handle_yellow,
            sensitivity='handle',
            min=2,
            max=30,
            step=1,
            value=int(config.getint('preferences','heat_timer',fallback=300))//60)
        self.widgets['heat_sensor_timer_setter']=heat_sensor_timer_setter

        def msg_evoke_on_func(button):
            config.set('preferences','evoke','True')
            with open(preferences_path,'w') as configfile:
                config.write(configfile)
        msg_evoke_on.bind(on_release=msg_evoke_on_func)

        def msg_evoke_off_func(button):
            config.set('preferences','evoke','False')
            with open(preferences_path,'w') as configfile:
                config.write(configfile)
        msg_evoke_off.bind(on_release=msg_evoke_off_func)

        def screensaver_timer_setter_display_func(slider,touch,*args):
            if touch.grab_current != slider:
                return
            screensaver_timer_value.text='[size=30][b][color=#ffffff]'+str(slider.value)+' Minutes'
        screensaver_timer_setter.bind(on_touch_move=screensaver_timer_setter_display_func)

        def screensaver_timer_setter_save_func(slider,touch,*args):
            if touch.grab_current != slider:
                return
            config.set('preferences','screensaver_timeout',str(slider.value))
            with open(preferences_path,'w') as configfile:
                config.write(configfile)
            ScreenSaver.timeout=slider.value*60
            ScreenSaver.service()
        screensaver_timer_setter.bind(on_touch_up=screensaver_timer_setter_save_func)

        def heat_sensor_timer_setter_display_func(slider,touch,*args):
            if touch.grab_current != slider:
                return
            heat_sensor_timer_value.text='[size=30][b][color=#ffffff]'+str(slider.value)+' Minutes'
        heat_sensor_timer_setter.bind(on_touch_move=heat_sensor_timer_setter_display_func)

        def heat_sensor_timer_setter_save_func(slider,touch,*args):
            if touch.grab_current != slider:
                return
            logic.heat_sensor_timer=slider.value*60
            config.set('preferences','heat_timer',str(slider.value*60))
            with open(preferences_path,'w') as configfile:
                config.write(configfile)
        heat_sensor_timer_setter.bind(on_touch_up=heat_sensor_timer_setter_save_func)

        def on_dismiss(self,*args):
            overlay_menu.canvas.before.remove_group("msg")

        self.widgets['overlay_layout'].add_widget(overlay_title)
        self.widgets['overlay_layout'].add_widget(evoke_title)
        self.widgets['overlay_layout'].add_widget(msg_evoke_on)
        self.widgets['overlay_layout'].add_widget(msg_evoke_off)
        self.widgets['overlay_layout'].add_widget(screensaver_timer_title)
        self.widgets['overlay_layout'].add_widget(screensaver_timer_value)
        self.widgets['overlay_layout'].add_widget(screensaver_timer_setter)
        self.widgets['overlay_layout'].add_widget(heat_sensor_timer_title)
        self.widgets['overlay_layout'].add_widget(heat_sensor_timer_value)
        self.widgets['overlay_layout'].add_widget(heat_sensor_timer_setter)
        overlay_menu.bind(on_dismiss=on_dismiss)
        overlay_menu.open()

    def advanced_settings_overlay(self):
        overlay_menu=self.widgets['overlay_menu']
        overlay_menu.background_color=palette('dark_shade',.75)
        overlay_menu.title=''
        overlay_menu.separator_height=0
        overlay_menu.auto_dismiss=True
        self.widgets['overlay_layout'].clear_widgets()
        self.widgets['overlay_layout'].add_widget(self.widgets['overlay_x'])
        config=App.get_running_app().config_

        # with overlay_menu.canvas.before:
        #    overlay_menu.msg_lines=Line(rounded_rectangle=(100, 100, 200, 200, 10, 10, 10, 10, 100),group='msg')

        # def update_lines(*args):
        #     x=int(overlay_menu.width*.2)
        #     y=int(overlay_menu.height*.5)
        #     width=int(overlay_menu.width*.25)
        #     height=int(overlay_menu.height*.5)
        #     overlay_menu.msg_lines.rounded_rectangle=(x, y, width, height, 10, 10, 10, 10, 100)
        # overlay_menu.bind(pos=update_lines, size=update_lines)

        # canvas is drawn to before widgets pos and size are set by parent.
        # update lines is bound to listen for changes to size and pos so it
        # can be updated accordingly.
        # however since the overlay is shared between different menus it does
        # not update its pos again after the drawing instructions are cleared,
        # this leads to the lines being drawn wrong again.
        # we call update_lines() while adding our message widgets to the overlay
        # to reposition the lines correctly before opening
        # update_lines()

        def _swap_color(button,*args):
            if button.state=='down':
                button.bg_color=palette('primary',.85)
            if button.state=='normal':
                button.bg_color=palette('base',1)


        overlay_title=Label(text=current_language['advanced_settings_overlay'],
                        pos_hint = {'x':.0, 'y':.5},
                        markup=True)
        self.widgets['overlay_title']=overlay_title
        overlay_title.ref='advanced_settings_overlay'


        input_filter_timer_title=Label(
            text=current_language['input_filter_timer_title'],
            pos_hint = {'center_x':.5, 'center_y':.88},
            markup=True)
        self.widgets['input_filter_timer_title']=input_filter_timer_title
        input_filter_timer_title.ref='input_filter_timer_title'

        input_filter_timer_value=Label(
            text='[size=30][b][color=#ffffff]'+config.get('preferences','input_filter_timeout',fallback='2'),
            pos_hint = {'center_x':.5, 'center_y':.83},
            markup=True)
        self.widgets['input_filter_timer_value']=input_filter_timer_value

        input_filter_timer_setter=Slider(
            size_hint =(.4, .125),
            pos_hint = {'center_x':.5, 'y':.7},
            cursor_image=slider_handle_yellow,
            sensitivity='handle',
            min=1,
            max=10,
            step=1,
            value=config.getint('preferences','input_filter_timeout',fallback=2))
        self.widgets['input_filter_timer_setter']=input_filter_timer_setter

        def input_filter_timer_setter_display_func(slider,touch,*args):
            if touch.grab_current != slider:
                return
            input_filter_timer_value.text='[size=30][b][color=#ffffff]'+str(slider.value)
        input_filter_timer_setter.bind(on_touch_move=input_filter_timer_setter_display_func)

        def input_filter_timer_setter_save_func(slider,touch,*args):
            if touch.grab_current != slider:
                return
            config.set('preferences','input_filter_timeout',str(slider.value))
            with open(preferences_path,'w') as configfile:
                config.write(configfile)
            logic.input_interference_filter=slider.value
            logger.debug(f'input interference filter set to: {slider.value}')
            logic.fs.heat_debounce_timer=slider.value
            logic.fs.micro_debounce_timer=slider.value
        input_filter_timer_setter.bind(on_touch_up=input_filter_timer_setter_save_func)


        schedule_mode_title=Label(
            text=current_language['schedule_mode_title'],
            pos_hint = {'center_x':.5, 'center_y':.6},
            markup=True)
        self.widgets['schedule_mode_title']=schedule_mode_title
        schedule_mode_title.ref='schedule_mode_title'

        schedule_mode_on=RoundedToggleButton(text=current_language['schedule_mode_on'],
                        size_hint =(.18, .125),
                        pos_hint = {'center_x':.625, 'center_y':.5},
                        background_down='',
                        background_color=palette('base',.85),
                        markup=True,
                        group='schedule',
                        allow_no_selection=False)
        self.widgets['schedule_mode_on']=schedule_mode_on
        schedule_mode_on.ref='schedule_mode_on'
        schedule_mode_on.unbind(state=schedule_mode_on.color_swap)
        schedule_mode_on.bind(state=_swap_color)
        schedule_mode_on.bind(state=schedule_mode_on.color_swap)

        schedule_mode_off=RoundedToggleButton(text=current_language['schedule_mode_off'],
                        size_hint =(.18, .125),
                        pos_hint = {'center_x':.375, 'center_y':.5},
                        background_down='',
                        background_color=palette('base',.85),
                        markup=True,
                        group='schedule',
                        allow_no_selection=False)
        self.widgets['schedule_mode_off']=schedule_mode_off
        schedule_mode_off.ref='schedule_mode_off'
        schedule_mode_off.unbind(state=schedule_mode_off.color_swap)
        schedule_mode_off.bind(state=_swap_color)
        schedule_mode_off.bind(state=schedule_mode_off.color_swap)

        is_limited=config.getboolean('config','limited',fallback=False)
        if is_limited:
            schedule_mode_on.state='down'
            _swap_color(schedule_mode_off)
        else:
            schedule_mode_off.state='down'
            _swap_color(schedule_mode_on)


        # def on_dismiss(self,*args):
        #     overlay_menu.canvas.before.remove_group("msg")

        self.widgets['overlay_layout'].add_widget(overlay_title)
        self.widgets['overlay_layout'].add_widget(input_filter_timer_title)
        self.widgets['overlay_layout'].add_widget(input_filter_timer_value)
        self.widgets['overlay_layout'].add_widget(input_filter_timer_setter)
        self.widgets['overlay_layout'].add_widget(schedule_mode_title)
        self.widgets['overlay_layout'].add_widget(schedule_mode_on)
        self.widgets['overlay_layout'].add_widget(schedule_mode_off)
        overlay_menu.open()

        def schedule_mode_on_func(button):
            App.get_running_app().limited=True
            config.set('config','limited','True')
            with open(preferences_path,'w') as configfile:
                config.write(configfile)
        schedule_mode_on.bind(on_release=schedule_mode_on_func)

        def schedule_mode_off_func(button):
            App.get_running_app().limited=False
            config.set('config','limited','False')
            with open(preferences_path,'w') as configfile:
                config.write(configfile)
        schedule_mode_off.bind(on_release=schedule_mode_off_func)
    def settings_back(self,button):
        self.parent.transition = SlideTransition(direction='down')
        self.manager.current='settings'
    def settings_back_main(self,button):
        self.parent.transition = SlideTransition(direction='left')
        self.manager.current='main'
    def advanced_settings_func(self,button):
        self.parent.transition = SlideTransition(direction='left')
        if App.get_running_app().admin_mode_start>time.time():
            self.advanced_settings_overlay()
        else: self.add_widget(PinLock(self.advanced_settings_overlay))
    def general_settings_func(self,button):
        self.general_settings_overlay()
    def train_func (self,button):
        self.parent.transition = SlideTransition(direction='left')
        self.manager.current='train'
    def about_func (self,button):
        self.parent.transition = SlideTransition(direction='right')
        self.about_overlay()
    def account_func (self,button):
        self.parent.transition = SlideTransition(direction='left')
        self.manager.current='account'
    def network_func (self,button):
        self.parent.transition = SlideTransition(direction='left')
        self.manager.current='network'
    def clean_mode_func(self,button):
        self.parent.transition = SlideTransition(direction='left')
        self.maint_overlay()
    def commission_func(self,button):
        self.parent.transition = SlideTransition(direction='left')
        self.manager.current='documents'
    def device_logs (self,button):
        self.parent.transition = SlideTransition(direction='left')
        self.manager.current='devices'
    def pins_func(self,button):
        self.parent.transition = SlideTransition(direction='left')
        self.manager.current='pin'
    def on_pre_enter(self,*args):
        self.widgets['pref_scroll'].scroll_y=1
    def on_enter(self):
        if self.duration_flag:
            self.duration_flag=0
            self.heat_overlay()
    def on_leave(self,*args):
        self.widgets['pref_scroll'].scroll_y=1

class PinScreen(Screen):
    def __init__(self, **kwargs):
        super(PinScreen,self).__init__(**kwargs)
        self.root=App.get_running_app()
        self.date_flag=0
        self.cols = 2
        self.widgets={}
        self.ud={}
        self.popups=[]
        self.pin=''
        bg_image = Image(source=background_image, allow_stretch=True, keep_ratio=False)

        back=RoundedButton(text=current_language['pin_back'],
                    size_hint =(.4, .1),
                    pos_hint = {'x':.06, 'y':.015},
                    background_down='',
                    background_color=palette('neutral',.85),
                    markup=True)
        self.widgets['back']=back
        back.ref='pin_back'
        back.bind(on_release=self.Pin_back)

        back_main=RoundedButton(text=current_language['pin_back_main'],
                        size_hint =(.4, .1),
                        pos_hint = {'x':.52, 'y':.015},
                        background_normal='',
                        background_color=palette('primary',.9),
                        markup=True)
        self.widgets['back_main']=back_main
        back_main.ref='pin_back_main'
        back_main.bind(on_release=self.Pin_back_main)

        num_pad=RelativeLayout(size_hint =(.9, .65),
            pos_hint = {'center_x':.6, 'center_y':.4})
        self.widgets['num_pad']=num_pad

        one=RoundedButton(text="[size=35][b][color=#000000] 1 [/color][/b][/size]",
            size_hint =(.15, .15),
            pos_hint = {'x':0, 'y':.85},
            background_down='',
            background_color=palette('neutral',.85),
            markup=True)
        self.widgets['one']=one
        one.bind(on_release=self.one_func)

        two=RoundedButton(text="[size=35][b][color=#000000] 2 [/color][/b][/size]",
            size_hint =(.15, .15),
            pos_hint = {'x':.2, 'y':.85},
            background_down='',
            background_color=palette('neutral',.85),
            markup=True)
        self.widgets['two']=two
        two.bind(on_release=self.two_func)

        three=RoundedButton(text="[size=35][b][color=#000000] 3 [/color][/b][/size]",
            size_hint =(.15, .15),
            pos_hint = {'x':.4, 'y':.85},
            background_down='',
            background_color=palette('neutral',.85),
            markup=True)
        self.widgets['three']=three
        three.bind(on_release=self.three_func)

        four=RoundedButton(text="[size=35][b][color=#000000] 4 [/color][/b][/size]",
            size_hint =(.15, .15),
            pos_hint = {'x':0, 'y':.65},
            background_down='',
            background_color=palette('neutral',.85),
            markup=True)
        self.widgets['four']=four
        four.bind(on_release=self.four_func)

        five=RoundedButton(text="[size=35][b][color=#000000] 5 [/color][/b][/size]",
            size_hint =(.15, .15),
            pos_hint = {'x':.2, 'y':.65},
            background_down='',
            background_color=palette('neutral',.85),
            markup=True)
        self.widgets['five']=five
        five.bind(on_release=self.five_func)

        six=RoundedButton(text="[size=35][b][color=#000000] 6 [/color][/b][/size]",
            size_hint =(.15, .15),
            pos_hint = {'x':.4, 'y':.65},
            background_down='',
            background_color=palette('neutral',.85),
            markup=True)
        self.widgets['six']=six
        six.bind(on_release=self.six_func)

        seven=RoundedButton(text="[size=35][b][color=#000000] 7 [/color][/b][/size]",
            size_hint =(.15, .15),
            pos_hint = {'x':0, 'y':.45},
            background_down='',
            background_color=palette('neutral',.85),
            markup=True)
        self.widgets['seven']=seven
        seven.bind(on_release=self.seven_func)

        eight=RoundedButton(text="[size=35][b][color=#000000] 8 [/color][/b][/size]",
            size_hint =(.15, .15),
            pos_hint = {'x':.2, 'y':.45},
            background_down='',
            background_color=palette('neutral',.85),
            markup=True)
        self.widgets['eight']=eight
        eight.bind(on_release=self.eight_func)

        nine=RoundedButton(text="[size=35][b][color=#000000] 9 [/color][/b][/size]",
            size_hint =(.15, .15),
            pos_hint = {'x':.4, 'y':.45},
            background_down='',
            background_color=palette('neutral',.85),
            markup=True)
        self.widgets['nine']=nine
        nine.bind(on_release=self.nine_func)

        zero=RoundedButton(text="[size=35][b][color=#000000] 0 [/color][/b][/size]",
            size_hint =(.15, .15),
            pos_hint = {'x':0, 'y':.25},
            background_down='',
            background_color=palette('neutral',.85),
            markup=True)
        self.widgets['zero']=zero
        zero.bind(on_release=self.zero_func)

        backspace=RoundedButton(text="[size=35][b][color=#000000] <- [/color][/b][/size]",
            size_hint =(.35, .15),
            pos_hint = {'x':.2, 'y':.25},
            background_down='',
            background_color=palette('highlight',.85),
            markup=True)
        self.widgets['backspace']=backspace
        backspace.bind(on_release=self.backspace_func)

        enter=RoundedButton(text="[size=35][b][color=#000000] -> [/color][/b][/size]",
            size_hint =(.15, .75),
            pos_hint = {'x':.6, 'y':.25},
            background_down='',
            background_color=palette('complement',.85),
            markup=True)
        self.widgets['enter']=enter
        enter.bind(on_release=self.enter_func)

        display=DisplayLabel(text=f'[size=25][color=#000000]{self.pin}[/color][/size]',
            size_hint =(.67, .10),
            pos_hint = {'x':.152, 'y':.77},
            valign='middle',
            halign='center',
            markup=True)
        self.widgets['display']=display

        reset_overlay=PinPop('system_reset')
        self.popups.append(reset_overlay)
        self.widgets['reset_overlay']=reset_overlay
        reset_overlay.ref='reset_overlay'
        reset_overlay.widgets['overlay_layout']=reset_overlay.overlay_layout

        reset_text=Label(
            text=current_language['reset_text'],
            markup=True,
            size_hint =(1,.6),
            pos_hint = {'x':0, 'y':.35},)
        self.widgets['reset_text']=reset_text
        reset_text.ref='reset_text'

        reset_confirm=RoundedButton(text=current_language['reset_confirm'],
                        size_hint =(.35, .25),
                        pos_hint = {'x':.05, 'y':.05},
                        background_down='',
                        background_color=palette('primary',.9),
                        markup=True)
        self.widgets['reset_confirm']=reset_confirm
        reset_confirm.ref='reset_confirm'

        reset_cancel=RoundedButton(text=current_language['reset_cancel'],
                        size_hint =(.35, .25),
                        pos_hint = {'x':.6, 'y':.05},
                        background_down='',
                        background_color=palette('primary',.9),
                        markup=True)
        self.widgets['reset_cancel']=reset_cancel
        reset_cancel.ref='reset_cancel'

        def reset_confirm_func(button):
            if os.name=='posix':
                os.system("sudo reboot")
        reset_confirm.bind(on_release=reset_confirm_func)

        def reset_cancel_func(button):
            self.widgets['reset_overlay'].dismiss()
        reset_cancel.bind(on_release=reset_cancel_func)

        date_overlay=PinPop('date')
        self.popups.append(date_overlay)
        self.widgets['date_overlay']=date_overlay
        date_overlay.ref='date_overlay'
        date_overlay.widgets['overlay_layout']=date_overlay.overlay_layout

        date_text=Label(
            text=current_language['date_text'],
            markup=True,
            size_hint =(1,.6),
            pos_hint = {'x':0, 'y':.35},)
        self.widgets['date_text']=date_text
        date_text.ref='date_text'

        date_confirm=RoundedButton(text=current_language['date_confirm'],
                        size_hint =(.35, .25),
                        pos_hint = {'x':.05, 'y':.05},
                        background_down='',
                        background_color=palette('primary',.9),
                        markup=True)
        self.widgets['date_confirm']=date_confirm
        date_confirm.ref='date_confirm'

        date_cancel=RoundedButton(text=current_language['date_cancel'],
                        size_hint =(.35, .25),
                        pos_hint = {'x':.6, 'y':.05},
                        background_down='',
                        background_color=palette('primary',.9),
                        markup=True)
        self.widgets['date_cancel']=date_cancel
        date_cancel.ref='date_cancel'

        def date_confirm_func(button):
            try:
                if not os.path.exists('logs/sys_report/report.jpg'):
                    raise FileNotFoundError
            except FileNotFoundError:
                logger.exception('Report Image File Missing')
                App.get_running_app().notifications.toast('[b][size=20]Report Image Error[/b][/size]\nAdditional error info logged','critical')
                self.widgets['date_overlay'].dismiss()
                return
            self.date_flag=1
            self.widgets['date_overlay'].dismiss()
            App.get_running_app().notifications.toast(f'[size=20]Date Format:\n\n[b]MMDDYYYY','error')
        date_confirm.bind(on_release=date_confirm_func)

        def date_cancel_func(button):
            self.widgets['date_overlay'].dismiss()
        date_cancel.bind(on_release=date_cancel_func)

        heat_override_overlay=PinPop('heat_override')
        self.popups.append(heat_override_overlay)
        self.widgets['heat_override_overlay']=heat_override_overlay
        heat_override_overlay.ref='heat_overlay'
        heat_override_overlay.widgets['overlay_layout']=heat_override_overlay.overlay_layout

        heat_override_text=Label(
            text=current_language['heat_override_text'],
            markup=True,
            size_hint =(1,.6),
            pos_hint = {'x':0, 'y':.35},)
        self.widgets['heat_override_text']=heat_override_text
        heat_override_text.ref='heat_override_text'

        heat_override_confirm=RoundedButton(text=current_language['heat_override_confirm'],
                        size_hint =(.35, .25),
                        pos_hint = {'x':.05, 'y':.05},
                        background_down='',
                        background_color=palette('primary',.9),
                        markup=True)
        self.widgets['heat_override_confirm']=heat_override_confirm
        heat_override_confirm.ref='heat_override_confirm'

        heat_override_cancel=RoundedButton(text=current_language['heat_override_cancel'],
                        size_hint =(.35, .25),
                        pos_hint = {'x':.6, 'y':.05},
                        background_down='',
                        background_color=palette('primary',.9),
                        markup=True)
        self.widgets['heat_override_cancel']=heat_override_cancel
        heat_override_cancel.ref='heat_override_cancel'

        def heat_override_confirm_func(button):
            logic.heat_sensor_timer=10
            config=self.root.config_
            config.set('preferences','heat_timer','10')
            with open(preferences_path,'w') as configfile:
                config.write(configfile)
            self.widgets['heat_override_overlay'].dismiss()
        heat_override_confirm.bind(on_release=heat_override_confirm_func)

        def heat_override_cancel_func(button):
            self.widgets['heat_override_overlay'].dismiss()
        heat_override_cancel.bind(on_release=heat_override_cancel_func)

        admin_overlay=PinPop('admin')
        self.popups.append(admin_overlay)
        self.widgets['admin_overlay']=admin_overlay
        admin_overlay.ref='admin_overlay'
        admin_overlay.widgets['overlay_layout']=admin_overlay.overlay_layout

        admin_text=Label(
            text=current_language['admin_text'],
            markup=True,
            size_hint =(1,.6),
            pos_hint = {'x':0, 'y':.35},)
        self.widgets['admin_text']=admin_text
        admin_text.ref='admin_text'

        admin_confirm=RoundedButton(text=current_language['admin_confirm'],
                        size_hint =(.35, .25),
                        pos_hint = {'x':.05, 'y':.05},
                        background_down='',
                        background_color=palette('primary',.9),
                        markup=True)
        self.widgets['admin_confirm']=admin_confirm
        admin_confirm.ref='admin_confirm'

        admin_cancel=RoundedButton(text=current_language['admin_cancel'],
                        size_hint =(.35, .25),
                        pos_hint = {'x':.6, 'y':.05},
                        background_down='',
                        background_color=palette('primary',.9),
                        markup=True)
        self.widgets['admin_cancel']=admin_cancel
        admin_cancel.ref='admin_cancel'

        def admin_confirm_func(button):
            app=App.get_running_app()
            admin_banner=app.notifications.banner('[i][size=20]Admin Mode Enabled','info')
            Clock.schedule_once(partial(app.notifications.remove_banner,admin_banner),900)
            app.admin_mode_start=time.time()+900#admin mode lasts 15 minutes
            self.widgets['admin_overlay'].dismiss()
        admin_confirm.bind(on_release=admin_confirm_func)

        def admin_cancel_func(button):
            self.widgets['admin_overlay'].dismiss()
        admin_cancel.bind(on_release=admin_cancel_func)

        report_pending_overlay=PinPop('report_pending')
        self.popups.append(report_pending_overlay)
        self.widgets['report_pending_overlay']=report_pending_overlay
        report_pending_overlay.ref='report_pending_overlay'
        report_pending_overlay.widgets['overlay_layout']=report_pending_overlay.overlay_layout

        report_pending_text=Label(
            text=current_language['report_pending_text'],
            markup=True,
            size_hint =(1,.6),
            pos_hint = {'x':0, 'y':.35},)
        self.widgets['report_pending_text']=report_pending_text
        report_pending_text.ref='report_pending_text'

        report_pending_confirm=RoundedButton(text=current_language['report_pending_confirm'],
                        size_hint =(.35, .25),
                        pos_hint = {'x':.05, 'y':.05},
                        background_down='',
                        background_color=palette('primary',.9),
                        markup=True)
        self.widgets['report_pending_confirm']=report_pending_confirm
        report_pending_confirm.ref='report_pending_confirm'

        report_pending_cancel=RoundedButton(text=current_language['report_pending_cancel'],
                        size_hint =(.35, .25),
                        pos_hint = {'x':.6, 'y':.05},
                        background_down='',
                        background_color=palette('primary',.9),
                        markup=True)
        self.widgets['report_pending_cancel']=report_pending_cancel
        report_pending_cancel.ref='report_pending_cancel'

        def report_pending_confirm_func(button):
            if App.get_running_app().report_pending==True:
                App.get_running_app().report_pending=False
            else:
                App.get_running_app().report_pending=True
            report_pending_setter_func()
            self.widgets['report_pending_overlay'].dismiss()
        report_pending_confirm.bind(on_release=report_pending_confirm_func)

        def report_pending_cancel_func(button):
            self.widgets['report_pending_overlay'].dismiss()
        report_pending_cancel.bind(on_release=report_pending_cancel_func)

        def report_pending_setter_func():
            config=App.get_running_app().config_
            config.set('config','report_pending',f'{App.get_running_app().report_pending}')
            with open(preferences_path,'w') as configfile:
                config.write(configfile)

        mount_overlay=PinPop('mount')
        self.popups.append(mount_overlay)
        self.widgets['mount_overlay']=mount_overlay
        mount_overlay.ref='mount_overlay'
        mount_overlay.widgets['overlay_layout']=mount_overlay.overlay_layout

        mount_text=Label(
            text=current_language['mount_text'],
            markup=True,
            size_hint =(1,.6),
            pos_hint = {'x':0, 'y':.35},)
        self.widgets['mount_text']=mount_text
        mount_text.ref='mount_text'

        mount_confirm=RoundedButton(text=current_language['mount_confirm'],
                        size_hint =(.35, .25),
                        pos_hint = {'x':.05, 'y':.05},
                        background_down='',
                        background_color=palette('primary',.9),
                        markup=True)
        self.widgets['mount_confirm']=mount_confirm
        mount_confirm.ref='mount_confirm'

        mount_cancel=RoundedButton(text=current_language['mount_cancel'],
                        size_hint =(.35, .25),
                        pos_hint = {'x':.6, 'y':.05},
                        background_down='',
                        background_color=palette('primary',.9),
                        markup=True)
        self.widgets['mount_cancel']=mount_cancel
        mount_cancel.ref='mount_cancel'

        def mount_confirm_func(button):
            self.widgets['mount_overlay'].dismiss()
            self.parent.transition = SlideTransition(direction='left')
            self.manager.current='mount'
        mount_confirm.bind(on_release=mount_confirm_func)

        def mount_cancel_func(button):
            self.widgets['mount_overlay'].dismiss()
        mount_cancel.bind(on_release=mount_cancel_func)

        device_reload_overlay=PinPop('device_reload')
        self.popups.append(device_reload_overlay)
        self.widgets['device_reload_overlay']=device_reload_overlay
        device_reload_overlay.ref='device_reload_overlay'
        device_reload_overlay.widgets['overlay_layout']=device_reload_overlay.overlay_layout

        device_reload_text=Label(
            text=current_language['device_reload_text'],
            markup=True,
            size_hint =(1,.6),
            pos_hint = {'x':0, 'y':.35},)
        self.widgets['device_reload_text']=device_reload_text
        device_reload_text.ref='device_reload_text'

        device_reload_confirm=RoundedButton(text=current_language['device_reload_confirm'],
                        size_hint =(.35, .25),
                        pos_hint = {'x':.05, 'y':.05},
                        background_down='',
                        background_color=palette('primary',.9),
                        markup=True)
        self.widgets['device_reload_confirm']=device_reload_confirm
        device_reload_confirm.ref='device_reload_confirm'

        device_reload_cancel=RoundedButton(text=current_language['device_reload_cancel'],
                        size_hint =(.35, .25),
                        pos_hint = {'x':.6, 'y':.05},
                        background_down='',
                        background_color=palette('primary',.9),
                        markup=True)
        self.widgets['device_reload_cancel']=device_reload_cancel
        device_reload_cancel.ref='device_reload_cancel'

        def device_reload_confirm_func(button):
            logic.devices=[]
            logic.get_devices()
            self.widgets['device_reload_overlay'].dismiss()
        device_reload_confirm.bind(on_release=device_reload_confirm_func)

        def device_reload_cancel_func(button):
            self.widgets['device_reload_overlay'].dismiss()
        device_reload_cancel.bind(on_release=device_reload_cancel_func)

        delete_devices_overlay=PinPop('delete_devices')
        self.popups.append(delete_devices_overlay)
        self.widgets['delete_devices_overlay']=delete_devices_overlay
        delete_devices_overlay.ref='delete_devices_overlay'
        delete_devices_overlay.widgets['overlay_layout']=delete_devices_overlay.overlay_layout

        delete_devices_text=Label(
            text=current_language['delete_devices_text'],
            markup=True,
            size_hint =(1,.6),
            pos_hint = {'x':0, 'y':.35},)
        self.widgets['delete_devices_text']=delete_devices_text
        delete_devices_text.ref='delete_devices_text'

        delete_devices_confirm=RoundedButton(text=current_language['delete_devices_confirm'],
                        size_hint =(.35, .25),
                        pos_hint = {'x':.05, 'y':.05},
                        background_down='',
                        background_color=palette('primary',.9),
                        markup=True)
        self.widgets['delete_devices_confirm']=delete_devices_confirm
        delete_devices_confirm.ref='delete_devices_confirm'
        delete_devices_confirm.bind(on_press=self.create_clock,on_touch_up=self.delete_clock)

        delete_devices_cancel=RoundedButton(text=current_language['delete_devices_cancel'],
                        size_hint =(.35, .25),
                        pos_hint = {'x':.6, 'y':.05},
                        background_down='',
                        background_color=palette('primary',.9),
                        markup=True)
        self.widgets['delete_devices_cancel']=delete_devices_cancel
        delete_devices_cancel.ref='delete_devices_cancel'

        def delete_devices_cancel_func(button):
            self.widgets['delete_devices_overlay'].dismiss()
        delete_devices_cancel.bind(on_release=delete_devices_cancel_func)

        batch_add_overlay=PinPop('batch_add')
        self.popups.append(batch_add_overlay)
        self.widgets['batch_add_overlay']=batch_add_overlay
        batch_add_overlay.ref='batch_add_overlay'
        batch_add_overlay.widgets['overlay_layout']=batch_add_overlay.overlay_layout

        batch_add_text=Label(
            text=current_language['batch_add_text'],
            markup=True,
            size_hint =(1,.6),
            pos_hint = {'x':0, 'y':.35},)
        self.widgets['batch_add_text']=batch_add_text
        batch_add_text.ref='batch_add_text'

        batch_add_confirm=RoundedButton(text=current_language['batch_add_confirm'],
                        size_hint =(.35, .25),
                        pos_hint = {'x':.05, 'y':.05},
                        background_down='',
                        background_color=palette('primary',.9),
                        markup=True)
        self.widgets['batch_add_confirm']=batch_add_confirm
        batch_add_confirm.ref='batch_add_confirm'

        batch_add_cancel=RoundedButton(text=current_language['batch_add_cancel'],
                        size_hint =(.35, .25),
                        pos_hint = {'x':.6, 'y':.05},
                        background_down='',
                        background_color=palette('primary',.9),
                        markup=True)
        self.widgets['batch_add_cancel']=batch_add_cancel
        batch_add_cancel.ref='batch_add_cancel'

        def batch_add_confirm_func(button):
            self.parent.transition = SlideTransition(direction='right')
            App.get_running_app().context_screen.current='devices'
            App.get_running_app().context_screen.get_screen('devices').widgets['batch_add_layout'].expand()
            self.widgets['batch_add_overlay'].dismiss()
        batch_add_confirm.bind(on_release=batch_add_confirm_func)

        def batch_add_cancel_func(button):
            self.widgets['batch_add_overlay'].dismiss()
        batch_add_cancel.bind(on_release=batch_add_cancel_func)

        delete_progress=CircularProgressBar()
        delete_progress._widget_size=200
        delete_progress._progress_colour=palette('highlight',1)
        self.widgets['delete_progress']=delete_progress

        report_state_overlay=PinPop('report_state')
        self.popups.append(report_state_overlay)
        self.widgets['report_state_overlay']=report_state_overlay
        report_state_overlay.ref='report_state_overlay'
        report_state_overlay.widgets['overlay_layout']=report_state_overlay.overlay_layout
        report_state_overlay.bind(on_pre_open=self.preset_state_spinner)

        report_state_text=Label(
            text=current_language['report_state_text'],
            markup=True,
            size_hint =(1,.6),
            pos_hint = {'x':0, 'y':.35},)
        self.widgets['report_state_text']=report_state_text
        report_state_text.ref='report_state_text'

        report_state_confirm=RoundedButton(text=current_language['report_state_confirm'],
                        size_hint =(.35, .25),
                        pos_hint = {'x':.05, 'y':.05},
                        background_down='',
                        background_color=palette('primary',.9),
                        markup=True)
        self.widgets['report_state_confirm']=report_state_confirm
        report_state_confirm.ref='report_state_confirm'

        report_state_cancel=RoundedButton(text=current_language['report_state_cancel'],
                        size_hint =(.35, .25),
                        pos_hint = {'x':.6, 'y':.05},
                        background_down='',
                        background_color=palette('primary',.9),
                        markup=True)
        self.widgets['report_state_cancel']=report_state_cancel
        report_state_cancel.ref='report_state_cancel'

        report_state_input=Spinner(
            disabled=False,
            text='KY',
            values=('KY','TN'),
            size_hint =(.4, .1),
            pos_hint = {'center_x':.5, 'center_y':.55})
        self.widgets['report_state_input']=report_state_input

        def report_state_confirm_func(*args):
            st=report_state_input.text
            config=App.get_running_app().config_
            config.set("config","report_state",st)
            with open(preferences_path,'w') as configfile:
                config.write(configfile)
            try:
                if App.get_running_app().context_screen.get_screen('report').imprint_state_labels():
                    App.get_running_app().notifications.toast(f'[size=20]Report state set:\n\n[b]{st}','info')
                else:
                    App.get_running_app().notifications.toast(f'[size=20]No Report Found','warning')
            except:
                logger.exception('Failed to set state')
                App.get_running_app().notifications.toast(f'[size=20]Failed to set state:\n\n[b]{st}','critical')
            self.widgets['report_state_overlay'].dismiss()
        report_state_confirm.bind(on_release=report_state_confirm_func)

        def report_state_cancel_func(*args):
            self.widgets['report_state_overlay'].dismiss()
        report_state_cancel.bind(on_release=report_state_cancel_func)

        bcm_board_trans_overlay=PinPop('bcm_board_trans')
        self.popups.append(bcm_board_trans_overlay)
        self.widgets['bcm_board_trans_overlay']=bcm_board_trans_overlay
        bcm_board_trans_overlay.ref='bcm_board_trans_overlay'
        bcm_board_trans_overlay.widgets['overlay_layout']=bcm_board_trans_overlay.overlay_layout

        bcm_board_trans_text=Label(
            text=current_language['bcm_board_trans_text'],
            markup=True,
            size_hint =(1,.6),
            pos_hint = {'x':0, 'y':.35},)
        self.widgets['bcm_board_trans_text']=bcm_board_trans_text
        bcm_board_trans_text.ref='bcm_board_trans_text'

        bcm_board_trans_confirm=RoundedButton(text=current_language['bcm_board_trans_confirm'],
                        size_hint =(.35, .25),
                        pos_hint = {'x':.05, 'y':.05},
                        background_down='',
                        background_color=palette('primary',.9),
                        markup=True)
        self.widgets['bcm_board_trans_confirm']=bcm_board_trans_confirm
        bcm_board_trans_confirm.ref='bcm_board_trans_confirm'

        bcm_board_trans_cancel=RoundedButton(text=current_language['bcm_board_trans_cancel'],
                        size_hint =(.35, .25),
                        pos_hint = {'x':.6, 'y':.05},
                        background_down='',
                        background_color=palette('primary',.9),
                        markup=True)
        self.widgets['bcm_board_trans_cancel']=bcm_board_trans_cancel
        bcm_board_trans_cancel.ref='bcm_board_trans_cancel'

        def bcm_board_trans_confirm_func(*args):
            for device in logic.devices:
                bcm_pin=device.pin
                board_pin=general.pin_translate(device.pin)
                if board_pin==0:
                    App.get_running_app().notifications.toast(f'[size=20]Invalid translation for\n{device.name}: Pin {bcm_pin}','critical')
                    logger.error(f'Invalid translation for {device.name}: Pin {bcm_pin}')
                    continue
                device.pin=board_pin
                logic.set_pin_mode(device)
                device.write()
                if bcm_pin in logic._available_pins:
                    logic.available_pins.append(bcm_pin)
                if board_pin in logic.available_pins:
                    logic.available_pins.remove(board_pin)
                logic.available_pins.sort()
                logic.pin_off(bcm_pin)
            self.widgets['bcm_board_trans_overlay'].dismiss()
        bcm_board_trans_confirm.bind(on_release=bcm_board_trans_confirm_func)

        def bcm_board_trans_cancel_func(*args):
            self.widgets['bcm_board_trans_overlay'].dismiss()
        bcm_board_trans_cancel.bind(on_release=bcm_board_trans_cancel_func)

        self.widgets['reset_overlay'].widgets['overlay_layout'].add_widget(reset_text)
        self.widgets['reset_overlay'].widgets['overlay_layout'].add_widget(reset_confirm)
        self.widgets['reset_overlay'].widgets['overlay_layout'].add_widget(reset_cancel)
        self.widgets['date_overlay'].widgets['overlay_layout'].add_widget(date_text)
        self.widgets['date_overlay'].widgets['overlay_layout'].add_widget(date_confirm)
        self.widgets['date_overlay'].widgets['overlay_layout'].add_widget(date_cancel)
        self.widgets['heat_override_overlay'].widgets['overlay_layout'].add_widget(heat_override_text)
        self.widgets['heat_override_overlay'].widgets['overlay_layout'].add_widget(heat_override_confirm)
        self.widgets['heat_override_overlay'].widgets['overlay_layout'].add_widget(heat_override_cancel)
        self.widgets['admin_overlay'].widgets['overlay_layout'].add_widget(admin_text)
        self.widgets['admin_overlay'].widgets['overlay_layout'].add_widget(admin_confirm)
        self.widgets['admin_overlay'].widgets['overlay_layout'].add_widget(admin_cancel)
        self.widgets['report_pending_overlay'].widgets['overlay_layout'].add_widget(report_pending_text)
        self.widgets['report_pending_overlay'].widgets['overlay_layout'].add_widget(report_pending_confirm)
        self.widgets['report_pending_overlay'].widgets['overlay_layout'].add_widget(report_pending_cancel)
        self.widgets['mount_overlay'].widgets['overlay_layout'].add_widget(mount_text)
        self.widgets['mount_overlay'].widgets['overlay_layout'].add_widget(mount_confirm)
        self.widgets['mount_overlay'].widgets['overlay_layout'].add_widget(mount_cancel)
        self.widgets['device_reload_overlay'].widgets['overlay_layout'].add_widget(device_reload_text)
        self.widgets['device_reload_overlay'].widgets['overlay_layout'].add_widget(device_reload_confirm)
        self.widgets['device_reload_overlay'].widgets['overlay_layout'].add_widget(device_reload_cancel)
        self.widgets['delete_devices_overlay'].widgets['overlay_layout'].add_widget(delete_devices_text)
        self.widgets['delete_devices_overlay'].widgets['overlay_layout'].add_widget(delete_devices_confirm)
        self.widgets['delete_devices_overlay'].widgets['overlay_layout'].add_widget(delete_devices_cancel)
        self.widgets['batch_add_overlay'].widgets['overlay_layout'].add_widget(batch_add_text)
        self.widgets['batch_add_overlay'].widgets['overlay_layout'].add_widget(batch_add_confirm)
        self.widgets['batch_add_overlay'].widgets['overlay_layout'].add_widget(batch_add_cancel)
        self.widgets['report_state_overlay'].widgets['overlay_layout'].add_widget(report_state_text)
        self.widgets['report_state_overlay'].widgets['overlay_layout'].add_widget(report_state_confirm)
        self.widgets['report_state_overlay'].widgets['overlay_layout'].add_widget(report_state_cancel)
        self.widgets['report_state_overlay'].widgets['overlay_layout'].add_widget(report_state_input)
        self.widgets['bcm_board_trans_overlay'].widgets['overlay_layout'].add_widget(bcm_board_trans_text)
        self.widgets['bcm_board_trans_overlay'].widgets['overlay_layout'].add_widget(bcm_board_trans_confirm)
        self.widgets['bcm_board_trans_overlay'].widgets['overlay_layout'].add_widget(bcm_board_trans_cancel)

        seperator_line=Image(source=gray_seperator_line,
                    allow_stretch=True,
                    keep_ratio=False,
                    size_hint =(.98, .001),
                    pos_hint = {'x':.01, 'y':.13})

        self.add_widget(bg_image)
        self.add_widget(back)
        self.add_widget(back_main)
        num_pad.add_widget(one)
        num_pad.add_widget(two)
        num_pad.add_widget(three)
        num_pad.add_widget(four)
        num_pad.add_widget(five)
        num_pad.add_widget(six)
        num_pad.add_widget(seven)
        num_pad.add_widget(eight)
        num_pad.add_widget(nine)
        num_pad.add_widget(zero)
        num_pad.add_widget(backspace)
        num_pad.add_widget(enter)
        self.add_widget(num_pad)
        self.add_widget(display)
        self.add_widget(seperator_line)

    def preset_state_spinner(self,*args):
        config=App.get_running_app().config_
        report_state=config.get("config","report_state",fallback='KY')
        self.widgets['report_state_input'].text=report_state

    def create_clock(self,*args):
        w=self.widgets
        delete_progress=CircularProgressBar()
        delete_progress._widget_size=200
        delete_progress._progress_colour=palette('highlight',1)
        self.widgets['delete_progress']=delete_progress
        scheduled_delete=partial(self.delete_devices_confirm_func)
        Clock.schedule_once(scheduled_delete, 2)
        self.ud['event'] = scheduled_delete
        w['delete_devices_overlay'].widgets['overlay_layout'].add_widget(w['delete_progress'])
        Clock.schedule_interval(self.progress_bar_update,.0001)
        self.ud['event_bar'] = self.progress_bar_update

    def delete_clock(self,*args):
        w=self.widgets
        if 'event' in self.ud:
            Clock.unschedule(self.ud['event'])
        if 'event_bar' in self.ud:
            Clock.unschedule(self.ud['event_bar'])
            w['delete_progress'].value=0
            w['delete_devices_overlay'].widgets['overlay_layout'].remove_widget(w['delete_progress'])

    def delete_devices_confirm_func(self,*args):
        del_func=App.get_running_app().context_screen.get_screen('devices').delete_device_confirm
        d=[i for i in logic.devices]
        for i in d:
            del_func(i)
        App.get_running_app().notifications.toast(f'[size=20]All Devices Deleted','info')
        self.widgets['delete_devices_overlay'].dismiss()

    def progress_bar_update(self,dt,*args):
        self.widgets['delete_progress'].pos=self.widgets['delete_devices_confirm'].last_touch.pos
        if not self.widgets['delete_progress'].parent:
            self.widgets['overlay_layout'].add_widget(self.widgets['delete_progress'])
        if self.widgets['delete_progress'].value >= 1000: # Checks to see if progress_bar.value has met 1000
            return False # Returning False schedule is canceled and won't repeat
        self.widgets['delete_progress'].value += 1000/2*dt # Updates progress_bar's progress

    def Pin_back(self,button):
        self.pin=''
        self.widgets['display'].update_text(self.pin)
        self.parent.transition = SlideTransition(direction='right')
        self.manager.current='preferences'
    def Pin_back_main(self,button):
        self.pin=''
        self.widgets['display'].update_text(self.pin)
        self.parent.transition = SlideTransition(direction='down')
        self.manager.current='main'
    def on_leave(self):
        self.pin=''
        self.date_flag=0
    def one_func(self,button):
        if len(self.pin)<11 and isinstance(button.last_touch,MouseMotionEvent):
            self.pin+='1'
        self.widgets['display'].update_text(self.pin)
    def two_func(self,button):
        if len(self.pin)<11 and isinstance(button.last_touch,MouseMotionEvent):   
            self.pin+='2'
        self.widgets['display'].update_text(self.pin)
    def three_func(self,button):
        if len(self.pin)<11 and isinstance(button.last_touch,MouseMotionEvent):
            self.pin+='3'
        self.widgets['display'].update_text(self.pin)
    def four_func(self,button):
        if len(self.pin)<11 and isinstance(button.last_touch,MouseMotionEvent):
            self.pin+='4'
        self.widgets['display'].update_text(self.pin)
    def five_func(self,button):
        if len(self.pin)<11 and isinstance(button.last_touch,MouseMotionEvent):
            self.pin+='5'
        self.widgets['display'].update_text(self.pin)
    def six_func(self,button):
        if len(self.pin)<11 and isinstance(button.last_touch,MouseMotionEvent):
            self.pin+='6'
        self.widgets['display'].update_text(self.pin)
    def seven_func(self,button):
        if len(self.pin)<11 and isinstance(button.last_touch,MouseMotionEvent):
            self.pin+='7'
        self.widgets['display'].update_text(self.pin)
    def eight_func(self,button):
        if len(self.pin)<11 and isinstance(button.last_touch,MouseMotionEvent):
            self.pin+='8'
        self.widgets['display'].update_text(self.pin)
    def nine_func(self,button):
        if len(self.pin)<11 and isinstance(button.last_touch,MouseMotionEvent):
            self.pin+='9'
        self.widgets['display'].update_text(self.pin)
    def zero_func(self,button):
        if len(self.pin)<11 and isinstance(button.last_touch,MouseMotionEvent):
            self.pin+='0'
        self.widgets['display'].update_text(self.pin)
    def backspace_func(self,button):
        if isinstance(button.last_touch,MouseMotionEvent):
            self.pin=self.pin[0:-1]
        self.widgets['display'].update_text(self.pin)
    def enter_func(self,button):
        if self.date_flag:
            try:
                if App.get_running_app().context_screen.get_screen('report').archive_report():
                    App.get_running_app().notifications.toast(f'[size=20]Current Report Archived','info')
                else:
                    App.get_running_app().notifications.toast(f'[size=20]No Report Found/Archived','warning')
                self.date_flag=0
                config=self.root.config_
                month=self.pin[0:2]
                day=self.pin[2:4]
                year=self.pin[4:8]
                config.set('documents','inspection_date',f'{month}-{day}-{year}')
                timestamp=datetime.now()
                timestamp=timestamp.replace(day=1,month=int(month),year=int(year))
                config.set('timestamps','System Inspection',f'{timestamp }')
                with open(preferences_path,'w') as configfile:
                    config.write(configfile)
                if App.get_running_app().context_screen.get_screen('report').create_current_report():
                    App.get_running_app().notifications.toast(f'[b][size=20]Inspection date set to\n    {month}-{day}-{year}')
                else:
                    App.get_running_app().notifications.toast(f'[size=20]No Report Found/Updated','warning')
            except:
                logger.exception('Setting Report Date Failed')
                App.get_running_app().notifications.toast('[b][size=20]Report Creation Error[/b][/size]\nAdditional error info logged','critical')
        elif hasattr(pindex.Pindex,f'p{self.pin}'):
            eval(f'pindex.Pindex.p{self.pin}(self)')
        if self.pin:
            logger.debug(f'Pin Entered: {self.pin}')
        self.pin=''
        self.widgets['display'].update_text(self.pin)

class DocumentScreen(Screen):
    def __init__(self, **kwargs):
        super(DocumentScreen,self).__init__(**kwargs)
        self.cols = 2
        self.widgets={}
        self.current_section=''
        bg_image = Image(source=background_image, allow_stretch=True, keep_ratio=False)
        self.dock_close_anim=Animation(pos_hint={'center_x':-.175},d=.5,t='out_back')
        self.dock_open_anim=Animation(pos_hint={'center_x':.175},d=.5,t='in_out_back')
        self._load_debug_thread=Thread()
        self._load_info_thread=Thread()
        self._load_error_thread=Thread()
        self.data_processed_event=threading.Event()
        self.stop_loading=threading.Event()

        screen_name=Label(
            text=current_language['document_screen_name'],
            markup=True,
            size_hint =(.4, .05),
            pos_hint = {'center_x':.15, 'center_y':.925},)
        self.widgets['screen_name']=screen_name
        screen_name.ref='document_screen_name'

        back=RoundedButton(text="[size=50][b][color=#000000]  Back [/color][/b][/size]",
                    size_hint =(.4, .1),
                    pos_hint = {'x':.06, 'y':.015},
                    background_down='',
                    background_color=palette('neutral',.85),
                    markup=True)
        self.widgets['back']=back
        back.ref='report_back'
        back.bind(on_release=self.Report_back)

        back_main=RoundedButton(text="[size=50][b][color=#000000]  Close Menu [/color][/b][/size]",
                        size_hint =(.4, .1),
                        pos_hint = {'x':.52, 'y':.015},
                        background_normal='',
                        background_color=palette('primary',.9),
                        markup=True)
        self.widgets['back_main']=back_main
        back_main.ref='report_back_main'
        back_main.bind(on_release=self.Report_back_main)

        seperator_line=Image(source=gray_seperator_line,
                    allow_stretch=True,
                    keep_ratio=False,
                    size_hint =(.98, .001),
                    pos_hint = {'x':.01, 'y':.13})

        dock=DenseRoundedColorLayout(
            bg_color=palette('secondary',.9),
            size_hint =(.45, .725),
            pos_hint = {'center_x':.175, 'center_y':.51})
        self.widgets['dock']=dock
        dock.bind(on_release=self.dock_handle_func)

        dock_handle=RoundedButton(
            size_hint =(.055,.425),
            pos_hint = {'center_x':.94, 'center_y':.5},
            background_down='',
            background_color=palette('light_tint',.9),
            markup=True)
        self.widgets['dock_handle']=dock_handle
        dock_handle.bind(on_release=self.dock_handle_func)

        dock_handle_lines=Image(
            source=menu_lines_vertical,
            allow_stretch=True,
            keep_ratio=False,
            size_hint =(.0325,.325),
            pos_hint = {'center_x':.94, 'center_y':.5})
        self.widgets['dock_handle_lines']=dock_handle_lines

        dock_reports=RoundedButton(
            text='[size=20][color=#ffffff][b]System Reports',
            size_hint =(.5,.15),
            pos_hint = {'center_x':.5, 'center_y':.85},
            background_down='',
            background_color=palette('dark_shade',1),
            markup=True)
        self.widgets['dock_reports']=dock_reports
        dock_reports.bind(state=self._swap_color)
        dock_reports.bind(on_release=self.dock_reports_func)
        dock_reports.bind(on_release=self.dock_handle_func)

        dock_maint=RoundedButton(
            text='[size=20][color=#ffffff][b]Manuals',
            size_hint =(.5,.15),
            pos_hint = {'center_x':.5, 'center_y':.65},
            background_down='',
            background_color=palette('dark_shade',1),
            markup=True)
        self.widgets['dock_maint']=dock_maint
        dock_maint.bind(state=self._swap_color)
        dock_maint.bind(on_release=self.dock_maint_func)
        dock_maint.bind(on_release=self.dock_handle_func)

        dock_install=RoundedButton(
            text='[size=20][color=#ffffff][b]Archives',
            size_hint =(.5,.15),
            pos_hint = {'center_x':.5, 'center_y':.45},
            background_down='',
            background_color=palette('dark_shade',1),
            markup=True)
        self.widgets['dock_install']=dock_install
        dock_install.bind(state=self._swap_color)
        dock_install.bind(on_release=self.dock_install_func)
        dock_install.bind(on_release=self.dock_handle_func)

        dock_logs=RoundedButton(
            text='[size=20][color=#ffffff][b]Runtime Logs',
            size_hint =(.5,.15),
            pos_hint = {'center_x':.5, 'center_y':.25},
            background_down='',
            background_color=palette('dark_shade',1),
            markup=True)
        self.widgets['dock_logs']=dock_logs
        dock_logs.bind(state=self._swap_color)
        dock_logs.bind(on_release=self.dock_logs_func)
        dock_logs.bind(on_release=self.dock_handle_func)

        container=FloatLayout(
            size_hint =(.9, .725),
            pos_hint = {'center_x':.525, 'center_y':.51})
        self.widgets['container']=container

        #####state report widgets#####

        report_image=Image(
            source=report_current,
            nocache=True)
        self.widgets['report_image']=report_image

        report_scroll_layout=RelativeLayout(
            size_hint_y=2.5,
            size_hint_x=.95)
        self.widgets['report_scroll_layout']=report_scroll_layout

        report_scroll=OutlineModalScroll(
            scroll_timeout=100000,
            bg_color=palette('dark_shade',0),
            bar_width=8,
            do_scroll_y=True,
            do_scroll_x=False,
            size_hint_y=1,
            size_hint_x=.95,
            pos_hint = {'center_x':.5, 'center_y':.5})
        report_scroll.bar_color=palette('primary',.75)
        report_scroll.bar_inactive_color=palette('primary',.55)
        self.widgets['report_scroll']=report_scroll

        report_selector_scroll=OutlineScroll(
            bg_color=palette('secondary',.75),
            bar_width=8,
            do_scroll_y=True,
            do_scroll_x=False,
            size_hint_y=1,
            size_hint_x=1,
            pos_hint = {'center_x':.5, 'center_y':.5})
        report_selector_scroll.bar_color=palette('primary',.75)
        report_selector_scroll.bar_inactive_color=palette('primary',.55)
        self.widgets['report_selector_scroll']=report_selector_scroll

        report_selector_layout=GridLayout(
            size_hint_y=None,
            size_hint_x=1,
            cols=3,
            padding=30,
            spacing=(10,10),
            pos_hint = {'center_x':.5, 'center_y':.5})
        self.widgets['report_selector_layout']=report_selector_layout
        report_selector_layout.bind(minimum_height=report_selector_layout.setter('height'))

        #####manual widgets#####

        manual_image=Image(
            source=report_current,
            nocache=True)
        self.widgets['manual_image']=manual_image

        manual_scroll_layout=RelativeLayout(
            size_hint_y=2.5,
            size_hint_x=.95)
        self.widgets['manual_scroll_layout']=manual_scroll_layout

        manual_scroll=OutlineModalScroll(
            bg_color=palette('dark_shade',0),
            bar_width=8,
            do_scroll_y=True,
            do_scroll_x=False,
            size_hint_y=.865,
            size_hint_x=.95,
            pos_hint = {'center_x':.5, 'center_y':.565})
        manual_scroll.bar_color=palette('primary',.75)
        manual_scroll.bar_inactive_color=palette('primary',.55)
        self.widgets['manual_scroll']=manual_scroll

        manual_selector_scroll=OutlineScroll(
            bg_color=palette('secondary',.75),
            bar_width=8,
            do_scroll_y=True,
            do_scroll_x=False,
            size_hint_y=1,
            size_hint_x=1,
            pos_hint = {'center_x':.5, 'center_y':.5})
        manual_selector_scroll.bar_color=palette('primary',.75)
        manual_selector_scroll.bar_inactive_color=palette('primary',.55)
        self.widgets['manual_selector_scroll']=manual_selector_scroll

        manual_selector_layout=GridLayout(
            size_hint_y=None,
            size_hint_x=1,
            cols=3,
            padding=30,
            spacing=(10,10),
            pos_hint = {'center_x':.5, 'center_y':.5})
        self.widgets['manual_selector_layout']=manual_selector_layout
        manual_selector_layout.bind(minimum_height=manual_selector_layout.setter('height'))

        #####archive widgets#####

        archive_image=Image(
            source=report_current,
            nocache=True)
        self.widgets['archive_image']=archive_image

        archive_scroll_layout=RelativeLayout(
            size_hint_y=2.5,
            size_hint_x=.95)
        self.widgets['archive_scroll_layout']=archive_scroll_layout

        archive_scroll=OutlineModalScroll(
            bg_color=palette('dark_shade',0),
            bar_width=8,
            do_scroll_y=True,
            do_scroll_x=False,
            size_hint_y=.865,
            size_hint_x=.95,
            pos_hint = {'center_x':.5, 'center_y':.565})
        archive_scroll.bar_color=palette('primary',.75)
        archive_scroll.bar_inactive_color=palette('primary',.55)
        self.widgets['archive_scroll']=archive_scroll

        archive_selector_scroll=OutlineScroll(
            bg_color=palette('secondary',.75),
            bar_width=8,
            do_scroll_y=True,
            do_scroll_x=False,
            size_hint_y=1,
            size_hint_x=1,
            pos_hint = {'center_x':.5, 'center_y':.5})
        archive_selector_scroll.bar_color=palette('primary',.75)
        archive_selector_scroll.bar_inactive_color=palette('primary',.55)
        self.widgets['archive_selector_scroll']=archive_selector_scroll

        archive_selector_layout=GridLayout(
            size_hint_y=None,
            size_hint_x=1,
            cols=3,
            padding=30,
            spacing=(10,10),
            pos_hint = {'center_x':.5, 'center_y':.5})
        self.widgets['archive_selector_layout']=archive_selector_layout
        archive_selector_layout.bind(minimum_height=archive_selector_layout.setter('height'))

        #####log files widgets#####

        debug_box=ExpandableRoundedColorLayout(
            size_hint =(.275, .45),
            pos_hint = {'center_x':.15, 'center_y':.5},
            expanded_size=(1,1),
            expanded_pos = {'center_x':.5, 'center_y':.5},
            bg_color=palette('light_tint',.9))
        self.widgets['debug_box']=debug_box
        debug_box.widgets={}
        debug_box.bind(state=self.bg_color)
        debug_box.bind(expanded=self.debug_box_populate)
        debug_box.bind(animating=partial(general.stripargs,debug_box.clear_widgets))

        debug_box_title=Label(
            text='[size=24][color=#000000][b]Debug Logs',
            markup=True,
            size_hint =(.4, .05),
            pos_hint = {'center_x':.5, 'center_y':.5},)
        self.widgets['debug_box_title']=debug_box_title

        debug_box_seperator=Image(
            source=black_seperator_line,
            allow_stretch=True,
            keep_ratio=False,
            size_hint =(.9, .005),
            pos_hint = {'x':.05, 'y':.85})
        self.widgets['debug_box_seperator']=debug_box_seperator

        debug_box_x=IconButton(
            source=overlay_x_icon_black,
            size_hint=(.1,.1),
            pos_hint={'x':.90,'y':.88})
        debug_box_x.bind(on_release=debug_box.shrink)
        self.widgets['debug_box_x']=debug_box_x

        debug_box_scroll=FileRecycleView(
            size_hint=(.9,.8485),
            pos_hint={'x':.05,'center_y':.425})
        self.widgets['debug_box_scroll']=debug_box_scroll

        info_box=ExpandableRoundedColorLayout(
            size_hint =(.275, .45),
            pos_hint = {'center_x':.475, 'center_y':.5},
            expanded_size=(1,1),
            expanded_pos = {'center_x':.5, 'center_y':.5},
            bg_color=palette('light_tint',.9))
        self.widgets['info_box']=info_box
        info_box.widgets={}
        info_box.bind(state=self.bg_color)
        info_box.bind(expanded=self.info_box_populate)
        info_box.bind(animating=partial(general.stripargs,info_box.clear_widgets))

        info_box_title=Label(
            text='[size=24][color=#000000][b]Info Logs',
            markup=True,
            size_hint =(.4, .05),
            pos_hint = {'center_x':.5, 'center_y':.5},)
        self.widgets['info_box_title']=info_box_title

        info_box_seperator=Image(
            source=black_seperator_line,
            allow_stretch=True,
            keep_ratio=False,
            size_hint =(.9, .005),
            pos_hint = {'x':.05, 'y':.85})
        self.widgets['info_box_seperator']=info_box_seperator

        info_box_x=IconButton(
            source=overlay_x_icon_black,
            size_hint=(.1,.1),
            pos_hint={'x':.90,'y':.88})
        info_box_x.bind(on_release=info_box.shrink)
        self.widgets['info_box_x']=info_box_x

        info_box_scroll=FileRecycleView(
            size_hint=(.9,.8485),
            pos_hint={'x':.05,'center_y':.425})
        self.widgets['info_box_scroll']=info_box_scroll

        error_box=ExpandableRoundedColorLayout(
            size_hint =(.275, .45),
            pos_hint = {'center_x':.8, 'center_y':.5},
            expanded_size=(1,1),
            expanded_pos = {'center_x':.5, 'center_y':.5},
            bg_color=palette('light_tint',.9))
        self.widgets['error_box']=error_box
        error_box.widgets={}
        error_box.bind(state=self.bg_color)
        error_box.bind(expanded=self.error_box_populate)
        error_box.bind(animating=partial(general.stripargs,error_box.clear_widgets))

        error_box_title=Label(
            text='[size=24][color=#000000][b]Error Logs',
            markup=True,
            size_hint =(.4, .05),
            pos_hint = {'center_x':.5, 'center_y':.5},)
        self.widgets['error_box_title']=error_box_title

        error_box_seperator=Image(
            source=black_seperator_line,
            allow_stretch=True,
            keep_ratio=False,
            size_hint =(.9, .005),
            pos_hint = {'x':.05, 'y':.85})
        self.widgets['error_box_seperator']=error_box_seperator

        error_box_x=IconButton(
            source=overlay_x_icon_black,
            size_hint=(.1,.1),
            pos_hint={'x':.90,'y':.88})
        error_box_x.bind(on_release=error_box.shrink)
        self.widgets['error_box_x']=error_box_x

        error_box_scroll=FileRecycleView(
            size_hint=(.9,.8485),
            pos_hint={'x':.05,'center_y':.425})
        self.widgets['error_box_scroll']=error_box_scroll

        report_scroll_layout.add_widget(report_image)
        report_scroll.add_widget(report_scroll_layout)
        report_selector_scroll.add_widget(report_selector_layout)

        manual_scroll_layout.add_widget(manual_image)
        manual_scroll.add_widget(manual_scroll_layout)
        manual_selector_scroll.add_widget(manual_selector_layout)

        archive_scroll_layout.add_widget(archive_image)
        archive_scroll.add_widget(archive_scroll_layout)
        archive_selector_scroll.add_widget(archive_selector_layout)

        dock.add_widget(dock_handle)
        dock.add_widget(dock_handle_lines)
        dock.add_widget(dock_reports)
        dock.add_widget(dock_maint)
        dock.add_widget(dock_install)
        dock.add_widget(dock_logs)

        debug_box.add_widget(debug_box_title)
        info_box.add_widget(info_box_title)
        error_box.add_widget(error_box_title)

        self.add_widget(bg_image)
        self.add_widget(screen_name)
        self.add_widget(seperator_line)
        self.add_widget(back)
        self.add_widget(back_main)
        self.add_widget(container)
        self.add_widget(dock)

    def dock_handle_func(self,*args):
        d=self.widgets['dock']
        if d.pos_hint['center_x']==.175:
            self.dock_close_anim.start(self.widgets['dock'])
        elif d.pos_hint['center_x']==-.175:
            self.dock_open_anim.start(self.widgets['dock'])

    def dock_reports_func(self,*args):
        if self.current_section=='reports':
            return
        _curr_report_found=False
        _old_reports_found=False
        self.current_section='reports'
        container_fade_out=Animation(opacity=0,d=.5)
        container_fade_in=Animation(opacity=1,d=.5)
        w=self.widgets
        container=w['container']
        w['report_selector_layout'].clear_widgets()

        if os.path.exists('logs/sys_report/report.jpg'):
            _curr_report_found=True
            curr_report=RoundedButton(
                    background_color=palette('light_tint',1),
                    size_hint=(1,None),
                    height=Window.height/7,
                    background_normal='',
                    text='[color=#000000][size=18]Current Report',
                    markup=True)
            curr_report.bind(on_release=lambda *args:setattr(w['report_image'],'source',report_current))
            curr_report.bind(on_release=lambda *args:w['report_image'].reload())
            curr_report.bind(on_release=lambda *args:self.add_widget(w['report_scroll']))
            w['report_selector_layout'].add_widget(curr_report)

        _report_paths = [f for f in glob.glob("logs/documents/system_reports/*.jpg")]
        _report_paths += [f for f in glob.glob("logs/documents/system_reports/*.png")]
        if len(_report_paths)>0:
            _old_reports_found=True
        for i in _report_paths:
            b=RoundedButton(
                background_color=palette('light_tint',1),
                size_hint=(1,None),
                height=Window.height/7,
                background_normal='',
                text='[color=#000000][size=18]'+pathlib.Path(i).stem,
                markup=True)
            b.bind(on_release=lambda _,i=i:setattr(w['report_image'],'source',i))
            b.bind(on_release=lambda *args:self.add_widget(w['report_scroll']))
            w['report_selector_layout'].add_widget(b)

        if not (_curr_report_found or _old_reports_found):
            empty_label=RoundedLabelColor(
                size_hint=(1,None),
                height=Window.height/7,
                bg_color=palette('light_tint',1),
                text='[color=#000000][size=28][b]System reports not found',
                markup=True)
            w['report_selector_layout'].add_widget(empty_label)

        def _swap_widgets(*args):
            container.clear_widgets()
            container.add_widget(w['report_selector_scroll'])
            container_fade_in.start(container)

        container_fade_out.start(container)
        container_fade_out.bind(on_complete=_swap_widgets)

    def dock_maint_func(self,*args):
        if self.current_section=='manuals':
            return
        _old_manuals_found=False
        self.current_section='manuals'
        container_fade_out=Animation(opacity=0,d=.5)
        container_fade_in=Animation(opacity=1,d=.5)
        w=self.widgets
        container=w['container']
        w['manual_selector_layout'].clear_widgets()

        _manual_paths = [f for f in glob.glob("logs/documents/manuals/*.jpg")]
        if len(_manual_paths)>0:
            _old_manuals_found=True
        for i in _manual_paths:
            b=RoundedButton(
                background_color=palette('light_tint',1),
                size_hint=(1,None),
                height=Window.height/7,
                background_normal='',
                text='[color=#000000][size=18]'+pathlib.Path(i).stem,
                markup=True)
            b.bind(on_release=lambda *args:setattr(w['manual_image'],'source',i))
            b.bind(on_release=lambda *args:self.add_widget(w['manual_scroll']))
            w['manual_selector_layout'].add_widget(b)

        if not _old_manuals_found:
            empty_label=RoundedLabelColor(
                size_hint=(1,None),
                height=Window.height/7,
                bg_color=palette('light_tint',1),
                text='[color=#000000][size=28][b]No manuals found',
                markup=True)
            w['manual_selector_layout'].add_widget(empty_label)

        def _swap_widgets(*args):
            container.clear_widgets()
            container.add_widget(w['manual_selector_scroll'])
            container_fade_in.start(container)

        container_fade_out.start(container)
        container_fade_out.bind(on_complete=_swap_widgets)

    def dock_install_func(self,*args):
        if self.current_section=='archives':
            return
        _old_archives_found=False
        self.current_section='archives'
        container_fade_out=Animation(opacity=0,d=.5)
        container_fade_in=Animation(opacity=1,d=.5)
        w=self.widgets
        container=w['container']
        w['archive_selector_layout'].clear_widgets()

        _archive_paths = [f for f in glob.glob("logs/documents/archives/*.jpg")]
        if len(_archive_paths)>0:
            _old_archives_found=True
        for i in _archive_paths:
            b=RoundedButton(
                background_color=palette('light_tint',1),
                size_hint=(1,None),
                height=Window.height/7,
                background_normal='',
                text='[color=#000000][size=18]'+pathlib.Path(i).stem,
                markup=True)
            b.bind(on_release=lambda *args:setattr(w['archive_image'],'source',i))
            b.bind(on_release=lambda *args:self.add_widget(w['archive_scroll']))
            w['archive_selector_layout'].add_widget(b)

        if not _old_archives_found:
            empty_label=RoundedLabelColor(
                size_hint=(1,None),
                height=Window.height/7,
                bg_color=palette('light_tint',1),
                text='[color=#000000][size=28][b]Archived documents not found',
                markup=True)
            w['archive_selector_layout'].add_widget(empty_label)

        def _swap_widgets(*args):
            container.clear_widgets()
            container.add_widget(w['archive_selector_scroll'])
            container_fade_in.start(container)

        container_fade_out.start(container)
        container_fade_out.bind(on_complete=_swap_widgets)

    def dock_logs_func(self,*args):
        if self.current_section=='logs':
            return
        self.current_section='logs'
        container_fade_out=Animation(opacity=0,d=.5)
        container_fade_in=Animation(opacity=1,d=.5)
        w=self.widgets
        container=w['container']
        log_boxes=[w['debug_box'],w['info_box'],w['error_box']]
        def _swap_widgets(*args):
            container.clear_widgets()
            for i in log_boxes:
                if i.expanded:i.shrink()
                container.add_widget(i)
            container_fade_in.start(container)
        container_fade_out.start(container)
        container_fade_out.bind(on_complete=_swap_widgets)


    def debug_box_populate(self,*args):
        w=self.widgets
        debug_box=w['debug_box']
        darken=Animation(rgba=palette('light_tint',1),d=.5)
        lighten=Animation(rgba=palette('light_tint',.9),d=.5)
        if debug_box.expanded:
            darken.start(debug_box.shape_color)
            debug_path='logs/log_files/debug'
            w['debug_box_scroll'].data=[]
            w['debug_box_scroll'].scroll_y=1

            if os.path.isdir(debug_path) and not self._load_debug_thread.is_alive():

                @mainthread
                def add_spinners():
                    debug_box.add_widget(PreLoader(rel_size=.3,ref='1',speed=500,color=palette('dark_shade',1)))
                    debug_box.add_widget(PreLoader(rel_size=.25,ref='2',speed=850,color=palette('dark_shade',1)))
                    debug_box.add_widget(PreLoader(rel_size=.2,ref='3',speed=600,color=palette('dark_shade',1)))
                    debug_box.add_widget(PreLoader(rel_size=.15,ref='4',speed=950,color=palette('dark_shade',1)))
                    debug_box.add_widget(PreLoader(rel_size=.1,ref='5',speed=700,color=palette('dark_shade',1)))
                    debug_box.add_widget(PreLoader(rel_size=.05,ref='6',speed=1050,color=palette('dark_shade',1)))

                @mainthread
                def remove_spinners():
                    for i in range(6):
                        if str(i+1) in debug_box.widgets:
                            debug_box.remove_widget(debug_box.widgets[str(i+1)])

                def adjust_scroll(_scroll_y,data_len,*args):
                    _scroll=w['debug_box_scroll']
                    if _scroll._touch:
                        #need to drop touch if manually scrolling
                        _scroll._touch=None
                        _scroll.do_scroll_y=False 
                    if 0 in (_scroll.scroll_y,data_len):
                        #at top of scroll, or no items
                        return

                    #stop current movement, because it doesnt
                    #know how to calulate velocity properly
                    #when adjusting scroll_y and moving
                    _scroll.effect_y.value=0
                    _scroll.effect_y.velocity=0

                    _val=(1.0-_scroll_y)*(data_len*250.0)
                    new_scroll_y=1.0-(_val/(len(_scroll.data)*250.0))

                    _scroll.scroll_y=new_scroll_y
                    #dont forget to reallow manual scrolling
                    _scroll.do_scroll_y=True

                @mainthread
                def _set_data(_data,last_chunk=False,*args):
                    _scroll=w['debug_box_scroll']
                    _scroll_y=_scroll.scroll_y
                    data_len=len(_scroll.data)
                    for i in _data:
                        _scroll.data.append(i)
                    if last_chunk:
                        self.data_processed_event.set()
                    remove_spinners()
                    Clock.schedule_once(partial(adjust_scroll,_scroll_y,data_len), -1)

                def data_chunker(_data:list,*args):
                    _process_interval=30
                    chnk_size=250
                    amt_chunks=-(len(_data)//-chnk_size)#ceiling division via negation
                    if amt_chunks>1:
                        chunk=_data[:chnk_size]
                        remaining_data=_data[chnk_size:]
                    else:
                        chunk=_data
                        remaining_data=None
                    def load_chunk(_chunk,*args):
                        if remaining_data:
                            _set_data(_chunk)
                            if self.stop_loading.wait(_process_interval):
                                self.data_processed_event.set()
                                return
                            data_chunker(remaining_data)
                        else:
                            _set_data(_chunk,last_chunk=True)
                            if self.stop_loading.wait(_process_interval):
                                self.data_processed_event.set()
                                return
                    load_chunk(chunk)

                def _load_data(*args):
                    file_list=os.listdir(debug_path)
                    add_spinners()
                    _data=[]
                    for file in file_list:
                        self.data_processed_event.clear()
                        for index,entry in enumerate(general.reverse_readline(os.path.join(debug_path,file))):
                            try:
                                entry=json.loads(entry)
                            except ValueError:
                                entry={'time':'',
                                        'text':'[i][size=26]Failed to load debug log',
                                        'file':'',
                                        'function':'',
                                        'line':''}
                            _time=f"[b]Time:[/b] {entry['time']}"
                            _text=f"[i][size=26]{entry['text']}[/size][/i]"
                            _file=f"[b]File:[/b] {entry['file']}"
                            _func=f"[b]Function:[/b] {entry['function']}"
                            _line=f"[b]Line:[/b] {entry['line']}"
                            entry_text=f"\n    [size=24][color=#000000]{_time}  \n\n    {_text}  \n\n    {general.pad_str(_file,40)}{_line} \n    {_func}  \n"
                            color=palette('dark_shade',.5) if index%2==0 else (0,0,0,.25)
                            _data.append({'text':entry_text,'color':color})
                        data_chunker(_data)
                        self.data_processed_event.wait()
                        if self.stop_loading:
                            self.stop_loading.clear()
                            return

                self._load_debug_thread=Thread(target=_load_data,daemon=True)
                self._load_debug_thread.start()

            w['debug_box_title'].pos_hint={'center_x':.5, 'center_y':.925}
            all_widgets=[
                w['debug_box_title'],
                w['debug_box_seperator'],
                w['debug_box_x'],
                w['debug_box_scroll']]
            for i in all_widgets:
                debug_box.add_widget(i)
        elif not debug_box.expanded:
            self.stop_loading.set()
            self.data_processed_event.set()
            lighten.start(debug_box.shape_color)
            w['debug_box_title'].pos_hint={'center_x':.5, 'center_y':.5}
            w['debug_box_scroll'].effect_y.velocity=0
            all_widgets=[
                w['debug_box_title']]
            for i in all_widgets:
                debug_box.add_widget(i)

    def info_box_populate(self,*args):
        w=self.widgets
        info_box=w['info_box']
        darken=Animation(rgba=palette('light_tint',1),d=.5)
        lighten=Animation(rgba=palette('light_tint',.9),d=.5)
        if info_box.expanded:
            darken.start(info_box.shape_color)
            info_path='logs/log_files/info'
            w['info_box_scroll'].data=[]
            w['info_box_scroll'].scroll_y=1

            if os.path.isdir(info_path) and not self._load_info_thread.is_alive():

                @mainthread
                def add_spinners():
                    info_box.add_widget(PreLoader(rel_size=.3,ref='1',speed=500,color=palette('dark_shade',1)))
                    info_box.add_widget(PreLoader(rel_size=.25,ref='2',speed=850,color=palette('dark_shade',1)))
                    info_box.add_widget(PreLoader(rel_size=.2,ref='3',speed=600,color=palette('dark_shade',1)))
                    info_box.add_widget(PreLoader(rel_size=.15,ref='4',speed=950,color=palette('dark_shade',1)))
                    info_box.add_widget(PreLoader(rel_size=.1,ref='5',speed=700,color=palette('dark_shade',1)))
                    info_box.add_widget(PreLoader(rel_size=.05,ref='6',speed=1050,color=palette('dark_shade',1)))

                @mainthread
                def remove_spinners():
                    for i in range(6):
                        if str(i+1) in info_box.widgets:
                            info_box.remove_widget(info_box.widgets[str(i+1)])

                def adjust_scroll(_scroll_y,data_len,*args):
                    _scroll=w['info_box_scroll']
                    if _scroll._touch:
                        #need to drop touch if manually scrolling
                        _scroll._touch=None
                        _scroll.do_scroll_y=False 
                    if 0 in (_scroll.scroll_y,data_len):
                        #at top of scroll, or no items
                        return

                    #stop current movement, because it doesnt
                    #know how to calulate velocity properly
                    #when adjusting scroll_y and moving
                    _scroll.effect_y.value=0
                    _scroll.effect_y.velocity=0

                    _val=(1.0-_scroll_y)*(data_len*250.0)
                    new_scroll_y=1.0-(_val/(len(_scroll.data)*250.0))

                    _scroll.scroll_y=new_scroll_y
                    #dont forget to reallow manual scrolling
                    _scroll.do_scroll_y=True

                @mainthread
                def _set_data(_data,last_chunk=False,*args):
                    _scroll=w['info_box_scroll']
                    _scroll_y=_scroll.scroll_y
                    data_len=len(_scroll.data)
                    for i in _data:
                        _scroll.data.append(i)
                    if last_chunk:
                        self.data_processed_event.set()
                    remove_spinners()
                    Clock.schedule_once(partial(adjust_scroll,_scroll_y,data_len), -1)

                def data_chunker(_data:list,*args):
                    _process_interval=30
                    chnk_size=250
                    amt_chunks=-(len(_data)//-chnk_size)#ceiling division via negation
                    if amt_chunks>1:
                        chunk=_data[:chnk_size]
                        remaining_data=_data[chnk_size:]
                    else:
                        chunk=_data
                        remaining_data=None
                    def load_chunk(_chunk,*args):
                        if remaining_data:
                            _set_data(_chunk)
                            if self.stop_loading.wait(_process_interval):
                                self.data_processed_event.set()
                                return
                            data_chunker(remaining_data)
                        else:
                            _set_data(_chunk,last_chunk=True)
                            if self.stop_loading.wait(_process_interval):
                                self.data_processed_event.set()
                                return
                    load_chunk(chunk)

                def _load_data(*args):
                    file_list=os.listdir(info_path)
                    add_spinners()
                    _data=[]
                    for file in file_list:
                        self.data_processed_event.clear()
                        for index,entry in enumerate(general.reverse_readline(os.path.join(info_path,file))):
                                try:
                                    entry=json.loads(entry)
                                except ValueError:
                                    entry={'time':'',
                                        'text':'[i][size=26]Failed to load info log',
                                        'file':'',
                                        'function':''}
                                _time=f"[b]Time:[/b] {entry['time']}"
                                _text=f"[i][size=26]{entry['text']}[/size][/i]"
                                _file=f"[b]File:[/b] {entry['file']}"
                                _func=f"[b]Function:[/b] {entry['function']}"
                                entry_text=f"\n    [size=24][color=#000000]{_time}  \n\n\n    {_text}  \n\n\n    {_file} \n"
                                color=palette('dark_shade',.5) if index%2==0 else (0,0,0,.25)
                                _data.append({'text':entry_text,'color':color})
                        data_chunker(_data)
                        self.data_processed_event.wait()
                        if self.stop_loading:
                            self.stop_loading.clear()
                            return

                self._load_info_thread=Thread(target=_load_data,daemon=True)
                self._load_info_thread.start()

            w['info_box_title'].pos_hint={'center_x':.5, 'center_y':.925}
            all_widgets=[
                w['info_box_title'],
                w['info_box_seperator'],
                w['info_box_x'],
                w['info_box_scroll']]
            for i in all_widgets:
                info_box.add_widget(i)
        elif not info_box.expanded:
            self.stop_loading.set()
            self.data_processed_event.set()
            lighten.start(info_box.shape_color)
            w['info_box_title'].pos_hint={'center_x':.5, 'center_y':.5}
            w['info_box_scroll'].effect_y.velocity=0
            all_widgets=[
                w['info_box_title']]
            for i in all_widgets:
                info_box.add_widget(i)

    def error_box_populate(self,*args):
        w=self.widgets
        error_box=w['error_box']
        darken=Animation(rgba=palette('light_tint',1),d=.5)
        lighten=Animation(rgba=palette('light_tint',.9),d=.5)
        if error_box.expanded:
            darken.start(error_box.shape_color)
            error_path='logs/log_files/errors'
            w['error_box_scroll'].data=[]
            w['error_box_scroll'].scroll_y=1

            if os.path.isdir(error_path) and not self._load_error_thread.is_alive():

                @mainthread
                def add_spinners():
                    error_box.add_widget(PreLoader(rel_size=.3,ref='1',speed=500,color=palette('dark_shade',1)))
                    error_box.add_widget(PreLoader(rel_size=.25,ref='2',speed=850,color=palette('dark_shade',1)))
                    error_box.add_widget(PreLoader(rel_size=.2,ref='3',speed=600,color=palette('dark_shade',1)))
                    error_box.add_widget(PreLoader(rel_size=.15,ref='4',speed=950,color=palette('dark_shade',1)))
                    error_box.add_widget(PreLoader(rel_size=.1,ref='5',speed=700,color=palette('dark_shade',1)))
                    error_box.add_widget(PreLoader(rel_size=.05,ref='6',speed=1050,color=palette('dark_shade',1)))

                @mainthread
                def remove_spinners():
                    for i in range(6):
                        if str(i+1) in error_box.widgets:
                            error_box.remove_widget(error_box.widgets[str(i+1)])

                def adjust_scroll(_scroll_y,data_len,*args):
                    _scroll=w['error_box_scroll']
                    if _scroll._touch:
                        #need to drop touch if manually scrolling
                        _scroll._touch=None
                        _scroll.do_scroll_y=False 
                    if 0 in (_scroll.scroll_y,data_len):
                        #at top of scroll, or no items
                        return

                    #stop current movement, because it doesnt
                    #know how to calulate velocity properly
                    #when adjusting scroll_y and moving
                    _scroll.effect_y.value=0
                    _scroll.effect_y.velocity=0

                    _val=(1.0-_scroll_y)*(data_len*250.0)
                    new_scroll_y=1.0-(_val/(len(_scroll.data)*250.0))

                    _scroll.scroll_y=new_scroll_y
                    #dont forget to reallow manual scrolling
                    _scroll.do_scroll_y=True

                @mainthread
                def _set_data(_data,last_chunk=False,*args):
                    _scroll=w['error_box_scroll']
                    _scroll_y=_scroll.scroll_y
                    data_len=len(_scroll.data)
                    for i in _data:
                        _scroll.data.append(i)
                    if last_chunk:
                        self.data_processed_event.set()
                    remove_spinners()
                    Clock.schedule_once(partial(adjust_scroll,_scroll_y,data_len), -1)

                def data_chunker(_data:list,*args):
                    _process_interval=30
                    chnk_size=250
                    amt_chunks=-(len(_data)//-chnk_size)#ceiling division via negation
                    if amt_chunks>1:
                        chunk=_data[:chnk_size]
                        remaining_data=_data[chnk_size:]
                    else:
                        chunk=_data
                        remaining_data=None
                    def load_chunk(_chunk,*args):
                        if remaining_data:
                            _set_data(_chunk)
                            if self.stop_loading.wait(_process_interval):
                                self.data_processed_event.set()
                                return
                            data_chunker(remaining_data)
                        else:
                            _set_data(_chunk,last_chunk=True)
                            if self.stop_loading.wait(_process_interval):
                                self.data_processed_event.set()
                                return
                    load_chunk(chunk)

                def _load_data(*args):
                    file_list=os.listdir(error_path)
                    add_spinners()
                    _data=[]
                    for file in file_list:
                        self.data_processed_event.clear()
                        for index,entry in enumerate(general.reverse_readline(os.path.join(error_path,file))):
                                try:
                                    entry=json.loads(entry)
                                except ValueError:
                                    entry={'time':'',
                                        'text':'[i][size=26]Failed to load error log',
                                        'file':'',
                                        'function':'',
                                        'line':'',
                                        'level':'',
                                        'exec_info':''}
                                _markup="\n    [size=20][color=#000000]"
                                _time=f"[b]Time:[/b] {entry['time']}"
                                _text=f"[i][size=26]{entry['text']}[/size][/i]"
                                _file=f"[b]File:[/b] {entry['file']}"
                                _func=f"[b]Function:[/b] {entry['function']}"
                                _line=f"[b]Line:[/b] {entry['line']}"
                                _level=f"[b]Level:[/b] {entry['level']}"
                                _exc=bool('exc_info' in entry)
                                entry_text=f"\n    [size=24][color=#000000]{_time}  \n\n    {_text}  \n\n    {general.pad_str(_file,49)}{_line} \n    {general.pad_str(_func,47)}{_level}  \n"
                                color=palette('dark_shade',.5) if index%2==0 else (0,0,0,.25)
                                _data.append({'text':entry_text,'color':color})
                                if _exc:
                                    _caught_exception='    '.join(entry['exc_info'].splitlines(True))
                                    t=_markup+str('  '.join(_caught_exception.splitlines(True)[-9:]))+'\n'
                                    _data.append({'text':t,'color':color})
                        data_chunker(_data)
                        self.data_processed_event.wait()
                        if self.stop_loading:
                            self.stop_loading.clear()
                            return

                self._load_error_thread=Thread(target=_load_data,daemon=True)
                self._load_error_thread.start()

            w['error_box_title'].pos_hint={'center_x':.5, 'center_y':.925}
            all_widgets=[
                w['error_box_title'],
                w['error_box_seperator'],
                w['error_box_x'],
                w['error_box_scroll']]
            for i in all_widgets:
                error_box.add_widget(i)
        elif not error_box.expanded:
            self.stop_loading.set()
            self.data_processed_event.set()
            lighten.start(error_box.shape_color)
            w['error_box_title'].pos_hint={'center_x':.5, 'center_y':.5}
            w['error_box_scroll'].effect_y.velocity=0
            all_widgets=[
                w['error_box_title']]
            for i in all_widgets:
                error_box.add_widget(i)

    def _swap_color(self,button,*args):
            if button.state=='down':
                button.shape_color.rgba=palette('primary',.15) #palette('primary',.15)
            if button.state=='normal':
                button.shape_color.rgba=palette('dark_shade',1)

    def bg_color(self,button,*args):
        if hasattr(button,'expanded'):
            if button.expanded:
                return
        if button.state=='normal':
            button.shape_color.rgba=palette('light_tint',.9)
        if button.state=='down':
            if button.shape_color.rgba==palette('light_tint',.9):
                button.shape_color.rgba=palette('light_tint',.8)

    def Report_back (self,button):
        self.parent.transition = SlideTransition(direction='right')
        self.manager.current='preferences'
    def Report_back_main (self,button):
        self.parent.transition = SlideTransition(direction='down')
        self.manager.current='main'

    def on_pre_enter(self,*args):
        w=self.widgets
        w['dock'].pos_hint={'center_x':.175, 'center_y':.51}
        w['container'].clear_widgets()
        self.current_section=''

class TroubleScreen(Screen):
    def __init__(self, **kwargs):
        super(TroubleScreen,self).__init__(**kwargs)
        self.cols = 2
        self.widgets={}
        bg_image = Image(source=background_image, allow_stretch=True, keep_ratio=False)

        back=RoundedButton(text=current_language['trouble_back'],
                    size_hint =(.4, .1),
                    pos_hint = {'x':.02, 'y':.015},
                    background_down='',
                    background_color=palette('neutral',.85),
                    markup=True)
        self.widgets['back']=back
        back.ref='trouble_back'
        back.bind(on_release=self.trouble_back)

        trouble_details=trouble_template('no_trouble')
        self.widgets['trouble_details']=trouble_details
        trouble_details.ref='no_trouble'

        trouble_layout=GridLayout(
            size_hint_y=None,
            size_hint_x=1,
            cols=1,
            padding=10,
            spacing=(1,5))
        self.widgets['trouble_layout']=trouble_layout
        trouble_layout.bind(minimum_height=trouble_layout.setter('height'))

        trouble_scroll=ScrollView(
            bar_width=8,
            scroll_type=['bars','content'],
            do_scroll_y=True,
            do_scroll_x=False,
            size_hint =(.9, .75),
            pos_hint = {'center_x':.5, 'y':.15})
        self.widgets['trouble_scroll']=trouble_scroll

        self.add_widget(bg_image)
        trouble_layout.add_widget(trouble_details)
        trouble_scroll.add_widget(trouble_layout)

        with self.canvas:
            self.outline_color=Color(*palette('neutral',.85))
            self.outline=Line(rectangle=(100, 100, 200, 200))

        def _update_rect(self, *args):
            ts=trouble_scroll
            x=int(ts.x)
            y=int(ts.y)
            width=int(ts.width)
            height=int(ts.height)
            self.outline.rectangle=(x, y, width, height)

        self._update_rect=_update_rect
        self.bind(size=self._update_rect, pos=self._update_rect)

        seperator_line=Image(source=gray_seperator_line,
                    allow_stretch=True,
                    keep_ratio=False,
                    size_hint =(.98, .001),
                    pos_hint = {'x':.01, 'y':.13})

        self.add_widget(trouble_scroll)
        self.add_widget(back)
        self.add_widget(seperator_line)

    def trouble_back (self,button):
        self.parent.transition = SlideTransition(direction='up')
        self.manager.current='main'

class MountScreen(Screen):
    def __init__(self, **kw):
        super(MountScreen,self).__init__(**kw)
        self.rename_text=''
        if os.name=='nt':
            self.internal_path=r'logs'
            self.external_path=r'logs'
        else:
            self.internal_path=r'/home/pi/Pi-ro-safe/logs'
            self.external_path=r'/media/pi'
        self.widgets={}
        bg_image = Image(source=background_image, allow_stretch=True, keep_ratio=False)

        back=RoundedButton(text=current_language['preferences_back'],
                        size_hint =(.4, .1),
                        pos_hint = {'x':.06, 'y':.015},
                        background_down='',
                        background_color=palette('neutral',.9),
                        markup=True)
        self.widgets['back']=back
        back.ref='preferences_back'
        back.bind(on_release=self.settings_back)

        back_main=RoundedButton(text=current_language['preferences_back_main'],
                        size_hint =(.4, .1),
                        pos_hint = {'x':.52, 'y':.015},
                        background_normal='',
                        background_color=palette('primary',.9),
                        markup=True)
        self.widgets['back_main']=back_main
        back_main.ref='preferences_back_main'
        back_main.bind(on_release=self.settings_back_main)

        file_selector_external=FileChooserIconView(
            dirselect=True,
            rootpath=self.external_path)
        self.widgets['file_selector_external']=file_selector_external

        file_layout_external=BoxLayoutColor(
            orientation='vertical',
            size_hint =(.4, .45),
            pos_hint = {'center_x':.75, 'y':.5})

        internal_label=Label(
            text=current_language['internal_label'],
            markup=True,
            size_hint =(.4, .05),
            pos_hint = {'center_x':.25, 'y':.95},)
        self.widgets['internal_label']=internal_label
        internal_label.ref='internal_label'

        file_selector_internal=FileChooserIconView(
            dirselect=True,
            rootpath=(self.internal_path))
        self.widgets['file_selector_internal']=file_selector_internal

        file_layout_internal=BoxLayoutColor(
            orientation='vertical',
            size_hint =(.4, .45),
            pos_hint = {'center_x':.25, 'y':.5})

        external_label=Label(
            text=current_language['external_label'],
            markup=True,
            size_hint =(.4, .05),
            pos_hint = {'center_x':.75, 'y':.95},)
        self.widgets['external_label']=external_label
        external_label.ref='external_label'

        instruction_label=LabelColor(
            text=current_language['instruction_label'],
            markup=True,
            size_hint =(.4, .35),
            pos_hint = {'center_x':.25, 'y':.14},)
        self.widgets['instruction_label']=instruction_label
        instruction_label.ref='instruction_label'

        import_button=RoundedButton(text=current_language['import_button'],
            size_hint =(.19, .1),
            pos_hint = {'center_x':.645, 'y':.39},
            background_down='',
            background_color=palette('neutral',.9),
            markup=True)
        self.widgets['import_button']=import_button
        import_button.ref='import_button'
        import_button.bind(on_release=self.import_button_func)

        export_button=RoundedButton(text=current_language['export_button'],
            size_hint =(.19, .1),
            pos_hint = {'center_x':.855, 'y':.39},
            background_down='',
            background_color=palette('neutral',.9),
            markup=True)
        self.widgets['export_button']=export_button
        export_button.ref='export_button'
        export_button.bind(on_release=self.export_button_func)

        rename_button=RoundedButton(text=current_language['rename_button'],
            size_hint =(.19, .1),
            pos_hint = {'center_x':.645, 'y':.265},
            background_down='',
            background_color=palette('neutral',.9),
            markup=True)
        self.widgets['rename_button']=rename_button
        rename_button.ref='rename_button'
        rename_button.bind(on_release=self.rename_button_func)

        del_button=RoundedButton(text=current_language['del_button'],
            size_hint =(.19, .1),
            pos_hint = {'center_x':.855, 'y':.265},
            background_down='',
            background_color=palette('neutral',.9),
            markup=True)
        self.widgets['del_button']=del_button
        del_button.ref='del_button'
        del_button.bind(on_release=self.del_button_func)

        refresh_button=RoundedButton(text=current_language['refresh_button'],
            size_hint =(.4, .1),
            pos_hint = {'center_x':.75, 'y':.14},
            background_down='',
            background_color=palette('neutral',.9),
            markup=True)
        self.widgets['refresh_button']=refresh_button
        refresh_button.ref='refresh_button'
        refresh_button.bind(on_release=self.refresh_button_func)

        overlay_menu=Popup(
            size_hint=(.8, .8),
            background = 'atlas://data/images/defaulttheme/bubble',
            title_color=[0, 0, 0, 1],
            title_size='38',
            title_align='center',
            separator_color=palette('highlight', .5))
        self.widgets['overlay_menu']=overlay_menu
        overlay_menu.ref='heat_overlay'

        overlay_layout=FloatLayout()
        self.widgets['overlay_layout']=overlay_layout

        seperator_line=Image(source=gray_seperator_line,
            allow_stretch=True,
            keep_ratio=False,
            size_hint =(.98, .001),
            pos_hint = {'x':.01, 'y':.13})

        file_layout_external.add_widget(file_selector_external)
        file_layout_internal.add_widget(file_selector_internal)
        overlay_menu.add_widget(overlay_layout)
        self.add_widget(bg_image)
        self.add_widget(internal_label)
        self.add_widget(external_label)
        self.add_widget(file_layout_external)
        self.add_widget(file_layout_internal)
        self.add_widget(back)
        self.add_widget(back_main)
        self.add_widget(seperator_line)
        self.add_widget(instruction_label)
        self.add_widget(import_button)
        self.add_widget(export_button)
        self.add_widget(rename_button)
        self.add_widget(del_button)
        self.add_widget(refresh_button)

    def import_overlay(self):
        w=self.widgets
        overlay_menu=w['overlay_menu']
        overlay_menu.background_color=palette('dark_shade',.85)
        overlay_menu.title=''
        overlay_menu.separator_height=0
        overlay_menu.auto_dismiss=True
        w['overlay_layout'].clear_widgets()
        fsi=w['file_selector_internal']
        fse=w['file_selector_external']
        internal_selection=fsi.selection[0] if fsi.selection else fsi.selection
        external_selection=fse.selection[0] if fse.selection else fse.selection
        #ensure that only one selection is made
        if external_selection:
            #internal selection can be cwd, so with external selection we have double selection
            double_selection=True
        else:
            #no external selection made
            double_selection=False

        if fsi.selection:
                #overwrite selection
                #strip path out of returned list (multiple selection possible, hence a list to contain them, although not used here)
                dst_path=fsi.selection[0]
        else:
            #can copy to cwd(current working directory)
            dst_path=fsi.path

        import_text=Label(
            text=current_language['import_text']+f'[size=26]{os.path.basename(external_selection)}({general.file_or_dir(external_selection)}) >> {os.path.basename(dst_path)}({general.file_or_dir(dst_path)})?[/size]' if double_selection else current_language['import_text_fail'],
            markup=True,
            size_hint =(1,.6),
            pos_hint = {'x':0, 'y':.4},)
        w['import_text']=import_text
        import_text.ref='import_text' if double_selection else 'import_text_fail'

        import_unique_text=Label(
            text='',
            markup=True,
            size_hint =(1,.6),
            pos_hint = {'center_x':.5, 'center_y':.5},)
        w['import_unique_text']=import_unique_text

        background_state='background_normal' if double_selection else 'background_down'
        continue_button=RoundedButton(text=current_language['continue_button'],
                        size_hint =(.35, .25),
                        pos_hint = {'x':.05, 'y':.05},
                        **{f'{background_state}':''},#accessing **kwargs dict at the desired key based on double_slection value
                        background_color=palette('primary',.85),
                        markup=True)
        w['continue_button']=continue_button
        continue_button.ref='continue_button'
        if double_selection:
            continue_button.disabled=False
        else:
            continue_button.disabled=True

        cancel_button=RoundedButton(text=current_language['cancel_button'],
                        size_hint =(.35, .25),
                        pos_hint = {'x':.6, 'y':.05},
                        background_normal='',
                        background_color=palette('primary',.85),
                        markup=True)
        w['cancel_button']=cancel_button
        cancel_button.ref='cancel_button'

        def continue_button_func(button):
            try:
                #strip path out of returned list (multiple selection possible, hence a list to contain them, although not used here)
                src=fse.selection[0]
            except IndexError:
                logger.exception('main.py MountScreen import_button_func(): src not selected')
                w['import_unique_text'].text="[size=20][color=#ffffff]You must make a selection from external storage to import[/color][/size]"
                return
            if fsi.selection:
                #overwrite selection
                #strip path out of returned list (multiple selection possible, hence a list to contain them, although not used here)
                dst=fsi.selection[0]
            else:
                #can copy to cwd(current working directory)
                dst=fsi.path

            if os.path.isdir(src):
                if os.path.isdir(dst):
                    dst=os.path.join(dst,os.path.basename(os.path.normpath(src)))
                else:
                    logger.error('main.py MountScreen import_button_func(): can not copy dir over file')
                    w['import_unique_text'].text="[size=20][color=#ffffff]Can not overwrite a file with a folder[/color][/size]"
                    return
            try:
                shutil.copytree(src, dst,dirs_exist_ok=True)
            except OSError as exc:
                if exc.errno in (errno.ENOTDIR, errno.EINVAL):
                    shutil.copy(src, dst)
                else: raise
            self.refresh_button_func()
            w['overlay_menu'].dismiss()
        continue_button.bind(on_release=continue_button_func)

        def cancel_button_func(button):
            self.refresh_button_func()
            w['overlay_menu'].dismiss()
        cancel_button.bind(on_release=cancel_button_func)

        w['overlay_layout'].add_widget(import_text)
        w['overlay_layout'].add_widget(import_unique_text)
        w['overlay_layout'].add_widget(continue_button)
        w['overlay_layout'].add_widget(cancel_button)
        w['overlay_menu'].open()

    def export_overlay(self):
        w=self.widgets
        overlay_menu=w['overlay_menu']
        overlay_menu.background_color=palette('dark_shade',.85)
        overlay_menu.title=''
        overlay_menu.separator_height=0
        overlay_menu.auto_dismiss=True
        w['overlay_layout'].clear_widgets()
        fsi=w['file_selector_internal']
        fse=w['file_selector_external']
        internal_selection=fsi.selection[0] if fsi.selection else fsi.selection
        external_selection=fse.selection[0] if fse.selection else fse.selection
        #ensure that only one selection is made
        if internal_selection:
            #external selection can be cwd, so with internal selection we have double selection
            double_selection=True
        else:
            #no internal selection made
            double_selection=False

        if fse.selection:
                #overwrite selection
                #strip path out of returned list (multiple selection possible, hence a list to contain them, although not used here)
                dst_path=fse.selection[0]
        else:
            #can copy to cwd(current working directory)
            dst_path=fse.path

        export_text=Label(
            text=current_language['export_text']+f'[size=26]{os.path.basename(internal_selection)}({general.file_or_dir(internal_selection)}) >> {os.path.basename(dst_path)}({general.file_or_dir(dst_path)})?[/size]' if double_selection else current_language['export_text_fail'],
            markup=True,
            size_hint =(1,.6),
            pos_hint = {'x':0, 'y':.4},)
        w['export_text']=export_text
        export_text.ref='export_text' if double_selection else 'export_text_fail'

        export_unique_text=Label(
            text='',
            markup=True,
            size_hint =(1,.6),
            pos_hint = {'center_x':.5, 'center_y':.5},)
        w['export_unique_text']=export_unique_text

        background_state='background_normal' if double_selection else 'background_down'
        continue_button=RoundedButton(text=current_language['continue_button'],
            size_hint =(.35, .25),
            pos_hint = {'x':.05, 'y':.05},
            **{f'{background_state}':''},#accessing **kwargs dict at the desired key based on double_slection value
            background_color=palette('primary',.85),
            markup=True)
        w['continue_button']=continue_button
        continue_button.ref='continue_button'
        if double_selection:
            continue_button.disabled=False
        else:
            continue_button.disabled=True

        cancel_button=RoundedButton(text=current_language['cancel_button'],
            size_hint =(.35, .25),
            pos_hint = {'x':.6, 'y':.05},
            background_normal='',
            background_color=palette('primary',.85),
            markup=True)
        w['cancel_button']=cancel_button
        cancel_button.ref='cancel_button'

        def continue_button_func(button):
            try:
                #strip path out of returned list (multiple selection possible, hence a list to contain them, although not used here)
                src=fsi.selection[0]
            except IndexError:
                logger.exception('main.py MountScreen export_button_func(): src not selected')
                w['export_unique_text'].text="[size=20][color=#ffffff]You must make a selection from internal storage to export[/color][/size]"
                return
            if fse.selection:
                #overwrite selection
                #strip path out of returned list (multiple selection possible, hence a list to contain them, although not used here)
                dst=fse.selection[0]
            else:
                #can copy to cwd(current working directory)
                dst=fse.path

            if os.path.isdir(src):
                if os.path.isdir(dst):
                    dst=os.path.join(dst,os.path.basename(os.path.normpath(src)))
                else:
                    logger.error('main.py MountScreen export_button_func(): can not copy dir over file')
                    w['export_unique_text'].text="[size=20][color=#ffffff]Can not overwrite a file with a folder[/color][/size]"
                    return
            try:
                shutil.copytree(src, dst,dirs_exist_ok=True)
            except OSError as exc:
                if exc.errno in (errno.ENOTDIR, errno.EINVAL):
                    shutil.copy(src, dst)
                else: raise
            self.refresh_button_func()
            w['overlay_menu'].dismiss()
        continue_button.bind(on_release=continue_button_func)

        def cancel_button_func(button):
            self.refresh_button_func()
            w['overlay_menu'].dismiss()
        cancel_button.bind(on_release=cancel_button_func)

        w['overlay_layout'].add_widget(export_text)
        w['overlay_layout'].add_widget(export_unique_text)
        w['overlay_layout'].add_widget(continue_button)
        w['overlay_layout'].add_widget(cancel_button)
        w['overlay_menu'].open()

    def del_overlay(self):
        w=self.widgets
        overlay_menu=w['overlay_menu']
        overlay_menu.background_color=palette('dark_shade',.85)
        overlay_menu.title=''
        overlay_menu.separator_height=0
        overlay_menu.auto_dismiss=True
        w['overlay_layout'].clear_widgets()
        fsi=w['file_selector_internal']
        fse=w['file_selector_external']
        internal_selection=fsi.selection[0] if fsi.selection else fsi.selection
        external_selection=fse.selection[0] if fse.selection else fse.selection
        #ensure that only one selection is made
        if bool(external_selection)^bool(internal_selection):
            single_selection=True
            selected_item_path=internal_selection if internal_selection else external_selection
            selected_item=os.path.basename(internal_selection) if internal_selection else os.path.basename(external_selection)
            view_port=fsi if fsi.selection else fse
            if selected_item_path == view_port.path or selected_item_path == self.internal_path or selected_item_path == self.external_path:
                #opening or closing a folder sets selection to cwd,
                #although that is a single selection it is undesirable to
                #delete the cwd so we treat it as unselected
                single_selection=False
        else:
            #selected multiple files or no selection made
            single_selection=False

        del_text=Label(
            text=current_language['del_text']+f'[size=26]{selected_item}?[/size]' if single_selection else current_language['del_text_fail'],
            markup=True,
            size_hint =(1,.6),
            pos_hint = {'x':0, 'y':.4},)
        w['del_text']=del_text
        del_text.ref='del_text' if single_selection else 'del_text_fail'

        background_state='background_normal' if single_selection else 'background_down'
        continue_button=RoundedButton(text=current_language['continue_button'],
                        size_hint =(.35, .25),
                        pos_hint = {'x':.05, 'y':.05},
                        **{f'{background_state}':''},#accessing **kwargs dict at the desired key based on single_slection value
                        background_color=palette('primary',.85),
                        markup=True)
        w['continue_button']=continue_button
        continue_button.ref='continue_button'
        if single_selection:
            continue_button.disabled=False
        else:
            continue_button.disabled=True

        cancel_button=RoundedButton(text=current_language['cancel_button'],
                        size_hint =(.35, .25),
                        pos_hint = {'x':.6, 'y':.05},
                        background_normal='',
                        background_color=palette('primary',.85),
                        markup=True)
        w['cancel_button']=cancel_button
        cancel_button.ref='cancel_button'

        def continue_button_func(button):
            if os.path.isdir(selected_item_path):
                shutil.rmtree(selected_item_path)
            else:
                os.remove(selected_item_path)
            self.refresh_button_func()
            w['overlay_menu'].dismiss()
        continue_button.bind(on_release=continue_button_func)

        def cancel_button_func(button):
            self.refresh_button_func()
            w['overlay_menu'].dismiss()
        cancel_button.bind(on_release=cancel_button_func)

        w['overlay_layout'].add_widget(del_text)
        w['overlay_layout'].add_widget(continue_button)
        w['overlay_layout'].add_widget(cancel_button)
        w['overlay_menu'].open()

    def rename_overlay(self):
        w=self.widgets
        overlay_menu=w['overlay_menu']
        overlay_menu.background_color=palette('dark_shade',.85)
        overlay_menu.title=''
        overlay_menu.separator_height=0
        overlay_menu.auto_dismiss=True
        w['overlay_layout'].clear_widgets()
        fsi=w['file_selector_internal']
        fse=w['file_selector_external']
        internal_selection=fsi.selection[0] if fsi.selection else fsi.selection
        external_selection=fse.selection[0] if fse.selection else fse.selection
        #ensure that only one selection is made
        if bool(external_selection)^bool(internal_selection):
            single_selection=True
            selected_item_path=internal_selection if internal_selection else external_selection
            selected_item=os.path.basename(internal_selection) if internal_selection else os.path.basename(external_selection)
            view_port=fsi if fsi.selection else fse
            if selected_item_path == view_port.path or selected_item_path == self.internal_path or selected_item_path == self.external_path:
                #opening or closing a folder sets selection to cwd,
                #although that is a single selection it is undesirable to
                #rename the cwd so we treat it as unselected
                single_selection=False
        else:
            #selected multiple files or no selection made
            single_selection=False

        rename_text=Label(
            text=current_language['rename_text']+f'[size=26]{selected_item}?[/size]' if single_selection else current_language['rename_text_fail'],
            markup=True,
            size_hint =(1,.6),
            pos_hint = {'x':0, 'y':.4},)
        w['rename_text']=rename_text
        rename_text.ref='rename_text' if single_selection else 'rename_text_fail'

        background_state='background_normal' if single_selection else 'background_down'
        continue_button=RoundedButton(text=current_language['continue_button'],
                        size_hint =(.35, .25),
                        pos_hint = {'x':.05, 'y':.05},
                        **{f'{background_state}':''},#accessing **kwargs dict at the desired key based on single_slection value
                        background_color=palette('primary',.85),
                        markup=True)
        w['continue_button']=continue_button
        continue_button.ref='continue_button'
        if single_selection:
            continue_button.disabled=False
        else:
            continue_button.disabled=True

        cancel_button=RoundedButton(text=current_language['cancel_button'],
                        size_hint =(.35, .25),
                        pos_hint = {'x':.6, 'y':.05},
                        background_normal='',
                        background_color=palette('primary',.85),
                        markup=True)
        w['cancel_button']=cancel_button
        cancel_button.ref='cancel_button'

        def continue_button_func(button):
            self.rename_input_overlay()
        continue_button.bind(on_release=continue_button_func)

        def cancel_button_func(button):
            self.refresh_button_func()
            w['overlay_menu'].dismiss()
        cancel_button.bind(on_release=cancel_button_func)

        w['overlay_layout'].add_widget(rename_text)
        w['overlay_layout'].add_widget(continue_button)
        w['overlay_layout'].add_widget(cancel_button)
        w['overlay_menu'].open()

    def rename_input_overlay(self):
        self.rename_text=''
        w=self.widgets
        overlay_menu=w['overlay_menu']
        overlay_menu.background_color=palette('dark_shade',.85)
        overlay_menu.title=''
        overlay_menu.separator_height=0
        overlay_menu.auto_dismiss=True
        w['overlay_layout'].clear_widgets()
        fsi=w['file_selector_internal']
        fse=w['file_selector_external']
        internal_selection=fsi.selection[0] if fsi.selection else fsi.selection
        external_selection=fse.selection[0] if fse.selection else fse.selection
        #ensure that only one selection is made
        if bool(external_selection)^bool(internal_selection):
            single_selection=True
            selected_item_path=internal_selection if internal_selection else external_selection
            selected_item=os.path.basename(internal_selection) if internal_selection else os.path.basename(external_selection)
            view_port=fsi if fsi.selection else fse
            if selected_item_path == view_port.path or selected_item_path == self.internal_path or selected_item_path == self.external_path:
                #opening or closing a folder sets selection to cwd,
                #although that is a single selection it is undesirable to
                #rename the cwd so we treat it as unselected
                single_selection=False
        else:
            #selected multiple files or no selection made
            single_selection=False

        rename_input_text=Label(
            text=current_language['rename_input_text']+f'[size=26]{selected_item}[/size]' if single_selection else current_language['rename_input_text_fail'],
            markup=True,
            size_hint =(1,.6),
            pos_hint = {'x':0, 'y':.65},)
        w['rename_input_text']=rename_input_text
        rename_input_text.ref='rename_input_text' if single_selection else 'rename_input_text_fail'

        rename_unique_text=Label(
            text=current_language['rename_unique_text'],
            markup=True,
            size_hint =(1,.6),
            pos_hint = {'center_x':.5, 'center_y':.5},)
        w['rename_unique_text']=rename_unique_text
        rename_unique_text.ref='rename_unique_text'

        get_name=TextInput(multiline=False,
                        focus=False,
                        hint_text="Enter new file/folder name",
                        font_size=26,
                        size_hint =(.5, .1),
                        pos_hint = {'center_x':.50, 'center_y':.65})
        w['get_name']=get_name
        get_name.bind(on_text_validate=partial(self.get_name_func))
        get_name.bind(text=partial(self.get_name_func))

        background_state='background_normal' if single_selection else 'background_down'
        save_button=RoundedButton(text=current_language['save_button'],
                        size_hint =(.35, .25),
                        pos_hint = {'x':.05, 'y':.05},
                        **{f'{background_state}':''},#accessing **kwargs dict at the desired key based on single_slection value
                        background_color=palette('primary',.85),
                        markup=True)
        w['save_button']=save_button
        save_button.ref='save_button'
        if single_selection:
            save_button.disabled=False
        else:
            save_button.disabled=True

        cancel_button=RoundedButton(text=current_language['cancel_button'],
                        size_hint =(.35, .25),
                        pos_hint = {'x':.6, 'y':.05},
                        background_normal='',
                        background_color=palette('primary',.85),
                        markup=True)
        w['cancel_button']=cancel_button
        cancel_button.ref='cancel_button'

        def save_button_func(path,button,*args):
            if self.rename_text:
                new_path=os.path.join(os.path.dirname(path),self.rename_text)
                try:
                    os.rename(path,new_path)
                    self.refresh_button_func()
                    w['overlay_menu'].dismiss()
                except FileExistsError:
                    if not w['rename_unique_text'].parent:
                        w['overlay_layout'].add_widget(w['rename_unique_text'])
                    w['get_name'].text=''
            else:
                if not w['rename_unique_text'].parent:
                        w['overlay_layout'].add_widget(w['rename_unique_text'])

        save_button.bind(on_release=partial(save_button_func,selected_item_path))

        def cancel_button_func(button):
            self.refresh_button_func()
            w['overlay_menu'].dismiss()
        cancel_button.bind(on_release=cancel_button_func)

        w['overlay_layout'].add_widget(rename_input_text)
        w['overlay_layout'].add_widget(get_name)
        w['overlay_layout'].add_widget(save_button)
        w['overlay_layout'].add_widget(cancel_button)

    def get_name_func(self,button,*args):
        self.rename_text=button.text

    def settings_back(self,button):
        self.parent.transition = SlideTransition(direction='right')
        self.manager.current='pin'
    def settings_back_main(self,button):
        self.parent.transition = SlideTransition(direction='down')
        self.manager.current='main'
    def import_button_func(self,button):
        self.import_overlay()
    def export_button_func(self,*args):
        self.export_overlay()
    def rename_button_func(self,*args):
        self.rename_overlay()
    def del_button_func(self,*args):
        self.del_overlay()
    def refresh_button_func(self,*args):
        self.widgets['file_selector_external']._update_files()
        self.widgets['file_selector_internal']._update_files()
        self.widgets['file_selector_external'].selection=[]
        self.widgets['file_selector_internal'].selection=[]

    def on_pre_enter(self, *args):
        self.refresh_button_func()
        self.widgets['file_selector_internal'].path=self.internal_path
        self.widgets['file_selector_external'].path=self.external_path
        return super().on_pre_enter(*args)

class AccountScreen(Screen):
    def __init__(self, **kwargs):
        super(AccountScreen,self).__init__(**kwargs)
        self.cols = 2
        self.widgets={}
        self.scheduled_funcs=[]
        bg_image = Image(source=background_image, allow_stretch=True, keep_ratio=False)
        self.unlocked=False
        self._link_code=''
        self.generate_link_timer=time.time()

        back=RoundedButton(
            text=current_language['settings_back'],
            size_hint =(.4, .1),
            pos_hint = {'x':.06, 'y':.015},
            background_down='',
            background_color=palette('neutral',.9),
            markup=True)
        self.widgets['back']=back
        back.ref='settings_back'
        back.bind(on_release=self.account_back)

        back_main=RoundedButton(
            text=current_language['preferences_back_main'],
            size_hint =(.4, .1),
            pos_hint = {'x':.52, 'y':.015},
            background_normal='',
            background_color=palette('primary',.9),
            markup=True)
        self.widgets['back_main']=back_main
        back_main.ref='preferences_back_main'
        back_main.bind(on_release=self.account_back_main)

        screen_name=Label(
            text=current_language['account_screen_name'],
            markup=True,
            size_hint =(.4, .05),
            pos_hint = {'center_x':.15, 'center_y':.925},)
        self.widgets['screen_name']=screen_name
        screen_name.ref='account_screen_name'

        information_box=RoundedColorLayoutButton(
            bg_color=palette('dark_shade',.85),
            size_hint =(.35, .25),
            pos_hint = {'center_x':.225, 'center_y':.75},)
        self.widgets['information_box']=information_box
        information_box.bind(on_release=self.account_prompt)

        information_title=Label(
            text=current_language['information_title'],
            markup=True,
            size_hint =(.4, .05),
            pos_hint = {'center_x':.5, 'center_y':.925},)
        self.widgets['information_title']=information_title
        information_title.ref='information_title'

        information_seperator=Image(
            source=gray_seperator_line,
            allow_stretch=True,
            keep_ratio=False,
            size_hint =(.9, .005),
            pos_hint = {'x':.05, 'y':.85})

        information_email=EmailInput(
            disabled=True,
            multiline=False,
            hint_text='Enter account email',
            size_hint =(.9, .2),
            pos_hint = {'x':.05, 'y':.5})
        information_email.bind(on_text_validate=self.email_validate)
        self.widgets['information_email']=information_email

        information_password=TextInput(
            disabled=True,
            multiline=False,
            password=True,
            hint_text='Enter password',
            size_hint =(.9, .2),
            pos_hint = {'x':.05, 'y':.20})
        information_password.bind(on_text_validate=self.password_validate)
        self.widgets['information_password']=information_password

        details_box=RoundedColorLayout(
            bg_color=palette('dark_shade',.85),
            size_hint =(.35, .4),
            pos_hint = {'center_x':.225, 'center_y':.4},)
        self.widgets['details_box']=details_box

        details_title=Label(
            text=current_language['details_title'],
            markup=True,
            size_hint =(.4, .05),
            pos_hint = {'center_x':.5, 'center_y':.925},)
        self.widgets['details_title']=details_title
        details_title.ref='details_title'

        details_seperator=Image(
            source=gray_seperator_line,
            allow_stretch=True,
            keep_ratio=False,
            size_hint =(.9, .005),
            pos_hint = {'x':.05, 'y':.85})

        details_body=MinimumBoundingLabel(
            text=current_language['details_body'],
            markup=True,
            halign='center',
            pos_hint = {'center_x':.5, 'center_y':.425},)
        self.widgets['details_body']=details_body
        details_body.ref='details_body'

        status_box=RoundedColorLayout(
            bg_color=palette('dark_shade',.85),
            size_hint =(.35, .675),
            pos_hint = {'center_x':.6, 'center_y':.5375},)
        self.widgets['status_box']=status_box

        status_title=Label(
            text=current_language['status_title'],
            markup=True,
            size_hint =(.4, .05),
            pos_hint = {'center_x':.5, 'center_y':.925},)
        self.widgets['status_title']=status_title
        status_title.ref='status_title'

        status_seperator=Image(
            source=gray_seperator_line,
            allow_stretch=True,
            keep_ratio=False,
            size_hint =(.9, .005),
            pos_hint = {'x':.05, 'y':.85})

        status_scroll=OutlineScroll(
            size_hint =(.9,.75),
            pos_hint = {'center_x':.5, 'center_y':.45},
            bg_color=palette('light_tint',.15),
            bar_width=8,
            bar_color=palette('primary',.9),
            bar_inactive_color=palette('primary',.35),
            do_scroll_y=True,
            do_scroll_x=False)

        status_scroll_layout = GridLayout(
            cols=1,
            spacing=10,
            size_hint_y=None,
            padding=5)

        # Make sure the height is such that there is something to scroll.
        status_scroll_layout.bind(minimum_height=status_scroll_layout.setter('height'))

        for i in range(20):#status_request:
            btn = RoundedButton(
                background_normal='',
                background_color=palette('secondary',1),
                text=str(i),
                size_hint_y=None,
                height=40)
            # btn.bind(on_release=partial(self.load_selected_msg,i))
            status_scroll_layout.add_widget(btn)


        side_bar_box=RoundedColorLayout(
            bg_color=palette('base',.85),
            size_hint =(.175, .675),
            pos_hint = {'center_x':.9, 'center_y':.5375},)
        self.widgets['side_bar_box']=side_bar_box

        side_bar_connect=ExpandableRoundedColorLayout(
            size_hint =(.9, .15),
            pos_hint = {'center_x':.5, 'center_y':.875},
            expanded_size=(5.143,1.185),
            expanded_pos = {'center_x':-1.785, 'center_y':.52},
            bg_color=palette('dark_shade',.9),
            locked=lambda x: self.add_widget(PinLock(lambda :(self.unlock(),x()))))
        self.widgets['side_bar_connect']=side_bar_connect
        side_bar_connect.widgets={}
        side_bar_connect.bind(state=self.bg_color)
        side_bar_connect.bind(expanded=self.side_bar_connect_populate)
        side_bar_connect.bind(animating=partial(general.stripargs,side_bar_connect.clear_widgets))

        side_bar_connect_title=Label(
            text=current_language['side_bar_connect_title'],
            markup=True,
            size_hint =(1, 1),
            pos_hint = {'center_x':.5, 'center_y':.5},)
        self.widgets['side_bar_connect_title']=side_bar_connect_title
        side_bar_connect_title.ref='side_bar_connect_title'

        side_bar_connect_seperator=Image(
            source=gray_seperator_line,
            allow_stretch=True,
            keep_ratio=False,
            size_hint =(.9, .005),
            pos_hint = {'x':.05, 'y':.85})
        self.widgets['side_bar_connect_seperator']=side_bar_connect_seperator

        side_bar_connect_login=AnalyticExpandable(
            size_hint =(.1, .075),
            pos_hint = {'center_x':.9, 'center_y':.75},
            expanded_size=(1,1),
            expanded_pos = {'center_x':.5, 'center_y':.5},
            bg_color=palette('dark_shade',0))
        self.widgets['side_bar_connect_login']=side_bar_connect_login
        side_bar_connect_login.widgets={}
        side_bar_connect_login.bind(expanded=self.side_bar_connect_login_populate)
        side_bar_connect_login.bind(animating=partial(general.stripargs,side_bar_connect_login.clear_widgets))

        side_bar_connect_login_title=MinimumBoundingLabel(
            text='[color=#ffffff][b][size=12]Already have an account?\n[u][size=16]Login',
            markup=True,
            size_hint =(1, 1),
            pos_hint = {'center_x':.5, 'center_y':.5},
            halign='center')
        self.widgets['side_bar_connect_login_title']=side_bar_connect_login_title

        side_bar_connect_login_seperator=Image(
            source=gray_seperator_line,
            allow_stretch=True,
            keep_ratio=False,
            size_hint =(.9, .005),
            pos_hint = {'x':.05, 'y':.85})
        self.widgets['side_bar_connect_login_seperator']=side_bar_connect_login_seperator

        side_bar_connect_login_back=RoundedButton(
            text='[color=#ffffff][b][size=12]Don\'t have an account yet?\n[u][size=16]Create Account',
            size_hint =(.1, .075),
            pos_hint = {'center_x':.1, 'center_y':.75},
            background_down='',
            background_color=palette('base',0),
            markup=True,
            halign='center')
        self.widgets['side_bar_connect_login_back']=side_bar_connect_login_back
        side_bar_connect_login_back.bind(on_release=self.side_bar_connect_login_expand_button_func)

        side_bar_connect_login_vertical_seperator=Image(
            source=gray_seperator_line_vertical,
            allow_stretch=True,
            keep_ratio=False,
            size_hint =(.0005, .3),
            pos_hint = {'center_x':.37, 'center_y':.60})
        self.widgets['side_bar_connect_login_vertical_seperator']=side_bar_connect_login_vertical_seperator

        side_bar_connect_login_email=MinimumBoundingLabel(
            text='[b][size=16]Email:',
            markup=True,
            size_hint=(None,None),
            pos_hint = {'right':.35, 'center_y':.7},)
        self.widgets['side_bar_connect_login_email']=side_bar_connect_login_email

        side_bar_connect_login_email_invalid_hint=MinimumBoundingLabel(
            text='[b][size=16][color=#aa0000]Email is not in a valid format.\nEnter valid email format',
            markup=True,
            size_hint=(None,None),
            pos_hint = {'center_x':.55, 'center_y':.63},
            halign='center')
        self.widgets['side_bar_connect_login_email_invalid_hint']=side_bar_connect_login_email_invalid_hint

        side_bar_connect_login_email_input=EmailInput(
            disabled=False,
            multiline=False,
            hint_text='Enter Account Email Address',
            size_hint =(.3, .05),
            pos_hint = {'x':.4, 'center_y':.7})
        self.widgets['side_bar_connect_login_email_input']=side_bar_connect_login_email_input
        side_bar_connect_login_email_input.bind(focus=self.side_bar_connect_login_email_input_clear)

        side_bar_connect_login_password=MinimumBoundingLabel(
            text='[b][size=16]Password:',
            markup=True,
            size_hint=(None,None),
            pos_hint = {'right':.35, 'center_y':.55},)
        self.widgets['side_bar_connect_login_password']=side_bar_connect_login_password

        side_bar_connect_login_password_input=TextInput(
            disabled=False,
            multiline=False,
            password=True,
            hint_text='Enter Account Password',
            size_hint =(.3, .05),
            pos_hint = {'x':.4, 'center_y':.55})
        self.widgets['side_bar_connect_login_password_input']=side_bar_connect_login_password_input
        side_bar_connect_login_password_input.bind(focus=self.side_bar_connect_login_password_input_clear)

        side_bar_connect_login_send=RoundedButton(
            text='[b][size=16]All Fields Required',
            size_hint =(.425, .075),
            pos_hint = {'center_x':.5, 'center_y':.3},
            background_normal='',
            background_color=palette('secondary',1),
            disabled=True,
            disabled_color=palette('light_tint',1),
            markup=True)
        self.widgets['side_bar_connect_login_send']=side_bar_connect_login_send
        side_bar_connect_login_send.bind(on_release=self.side_bar_connect_login_send_func)
        side_bar_connect_login_send.bind(disabled=self.side_bar_connect_login_send_disabled)

        side_bar_connect_login_expand_button=RoundedButton(
            size_hint =(.5, .075),
            pos_hint = {'center_x':.5, 'center_y':.075},
            background_down='',
            background_color=palette('light_tint',.9),
            markup=True)
        self.widgets['side_bar_connect_login_expand_button']=side_bar_connect_login_expand_button
        side_bar_connect_login_expand_button.bind(on_release=self.side_bar_connect_login_expand_button_func)

        side_bar_connect_login_expand_lines=Image(
            source=settings_icon,
            allow_stretch=True,
            keep_ratio=False,
            size_hint =(.4, .035),
            pos_hint = {'center_x':.5, 'center_y':.075})
        side_bar_connect_login_expand_lines.center=side_bar_connect_login_expand_button.center
        self.widgets['side_bar_connect_login_expand_lines']=side_bar_connect_login_expand_lines


        side_bar_connect_vertical_seperator=Image(
            source=gray_seperator_line_vertical,
            allow_stretch=True,
            keep_ratio=False,
            size_hint =(.0005, .3),
            pos_hint = {'center_x':.37, 'center_y':.60})
        self.widgets['side_bar_connect_vertical_seperator']=side_bar_connect_vertical_seperator

        side_bar_connect_email=MinimumBoundingLabel(
            text='[b][size=16]Email:',
            markup=True,
            size_hint=(None,None),
            pos_hint = {'right':.35, 'center_y':.7},)
        self.widgets['side_bar_connect_email']=side_bar_connect_email

        side_bar_connect_email_invalid_hint=MinimumBoundingLabel(
            text='[b][size=16][color=#aa0000]Email is not in a valid format.\nEnter valid email format',
            markup=True,
            size_hint=(None,None),
            pos_hint = {'center_x':.55, 'center_y':.63},
            halign='center')
        self.widgets['side_bar_connect_email_invalid_hint']=side_bar_connect_email_invalid_hint

        side_bar_connect_email_input=EmailInput(
            disabled=False,
            multiline=False,
            hint_text='Enter Email Address',
            size_hint =(.3, .05),
            pos_hint = {'x':.4, 'center_y':.7})
        self.widgets['side_bar_connect_email_input']=side_bar_connect_email_input
        side_bar_connect_email_input.bind(focus=self.side_bar_connect_email_input_clear)



        side_bar_connect_password=MinimumBoundingLabel(
            text='[b][size=16]Password:',
            markup=True,
            size_hint=(None,None),
            pos_hint = {'right':.35, 'center_y':.55},)
        self.widgets['side_bar_connect_password']=side_bar_connect_password

        side_bar_connect_password_input=TextInput(
            disabled=False,
            multiline=False,
            password=True,
            hint_text='Enter New Password',
            size_hint =(.3, .05),
            pos_hint = {'x':.4, 'center_y':.55})
        self.widgets['side_bar_connect_password_input']=side_bar_connect_password_input
        side_bar_connect_password_input.bind(focus=self.side_bar_connect_password_input_clear)

        side_bar_connect_send=RoundedButton(
            text='[b][size=16]All Fields Required',
            size_hint =(.425, .075),
            pos_hint = {'center_x':.5, 'center_y':.3},
            background_normal='',
            background_color=palette('secondary',1),
            disabled=True,
            disabled_color=palette('light_tint',1),
            markup=True)
        self.widgets['side_bar_connect_send']=side_bar_connect_send
        side_bar_connect_send.bind(on_release=self.side_bar_connect_send_func)
        side_bar_connect_send.bind(disabled=self.side_bar_connect_send_disabled)









        side_bar_connect_expand_button=RoundedButton(
            size_hint =(.5, .075),
            pos_hint = {'center_x':.5, 'center_y':.075},
            background_down='',
            background_color=palette('light_tint',.9),
            markup=True)
        self.widgets['side_bar_connect_expand_button']=side_bar_connect_expand_button
        side_bar_connect_expand_button.bind(on_release=self.side_bar_connect_expand_button_func)

        side_bar_connect_expand_lines=Image(
            source=settings_icon,
            allow_stretch=True,
            keep_ratio=False,
            size_hint =(.4, .035),
            pos_hint = {'center_x':.5, 'center_y':.075})
        side_bar_connect_expand_lines.center=side_bar_connect_expand_button.center
        self.widgets['side_bar_connect_expand_lines']=side_bar_connect_expand_lines

        side_bar_unlink=ExpandableRoundedColorLayout(
            size_hint =(.9, .15),
            pos_hint = {'center_x':.5, 'center_y':.6875},
            expanded_size=(5.143,1.185),
            expanded_pos = {'center_x':-1.785, 'center_y':.52},
            bg_color=palette('dark_shade',.9),
            locked=lambda x: self.add_widget(PinLock(lambda :(self.unlock(),x()))))
        self.widgets['side_bar_unlink']=side_bar_unlink
        side_bar_unlink.widgets={}
        side_bar_unlink.bind(state=self.bg_color)
        side_bar_unlink.bind(expanded=self.side_bar_unlink_populate)
        side_bar_unlink.bind(animating=partial(general.stripargs,side_bar_unlink.clear_widgets))

        side_bar_unlink_title=Label(
            text=current_language['side_bar_unlink_title'],
            markup=True,
            size_hint =(1, 1),
            pos_hint = {'center_x':.5, 'center_y':.5},)
        self.widgets['side_bar_unlink_title']=side_bar_unlink_title
        side_bar_unlink_title.ref='side_bar_unlink_title'

        side_bar_unlink_seperator=Image(
            source=gray_seperator_line,
            allow_stretch=True,
            keep_ratio=False,
            size_hint =(.9, .005),
            pos_hint = {'x':.05, 'y':.85})
        self.widgets['side_bar_unlink_seperator']=side_bar_unlink_seperator

        side_bar_unlink_expand_button=RoundedButton(
            size_hint =(.5, .075),
            pos_hint = {'center_x':.5, 'center_y':.075},
            background_down='',
            background_color=palette('light_tint',.9),
            markup=True)
        self.widgets['side_bar_unlink_expand_button']=side_bar_unlink_expand_button
        side_bar_unlink_expand_button.bind(on_release=self.side_bar_unlink_expand_button_func)

        side_bar_unlink_expand_lines=Image(
            source=settings_icon,
            allow_stretch=True,
            keep_ratio=False,
            size_hint =(.4, .035),
            pos_hint = {'center_x':.5, 'center_y':.075})
        side_bar_unlink_expand_lines.center=side_bar_unlink_expand_button.center
        self.widgets['side_bar_unlink_expand_lines']=side_bar_unlink_expand_lines

        side_bar_add=ExpandableRoundedColorLayout(
            size_hint =(.9, .15),
            pos_hint = {'center_x':.5, 'center_y':.5},
            expanded_size=(5.143,1.185),
            expanded_pos = {'center_x':-1.785, 'center_y':.52},
            bg_color=palette('dark_shade',.9),
            locked=lambda x: self.add_widget(PinLock(lambda :(self.unlock(),x()))))
        self.widgets['side_bar_add']=side_bar_add
        side_bar_add.widgets={}
        side_bar_add.bind(state=self.bg_color)
        side_bar_add.bind(expanded=self.side_bar_add_populate)
        side_bar_add.bind(animating=partial(general.stripargs,side_bar_add.clear_widgets))

        side_bar_add_title=Label(
            text=current_language['side_bar_add_title'],
            markup=True,
            size_hint =(1, 1),
            pos_hint = {'center_x':.5, 'center_y':.5},)
        self.widgets['side_bar_add_title']=side_bar_add_title
        side_bar_add_title.ref='side_bar_add_title'

        side_bar_add_seperator=Image(
            source=gray_seperator_line,
            allow_stretch=True,
            keep_ratio=False,
            size_hint =(.9, .005),
            pos_hint = {'x':.05, 'y':.85})
        self.widgets['side_bar_add_seperator']=side_bar_add_seperator

        side_bar_add_body=MinimumBoundingLabel(
            text=current_language['side_bar_add_body'],
            markup=True,
            pos_hint = {'center_x':.2, 'center_y':.5})
        self.widgets['side_bar_add_body']=side_bar_add_body
        side_bar_add_body.ref='side_bar_add_body'

        with side_bar_add_body.canvas.before:
            Color(*palette('dark_shade',1))
            side_bar_add_body.rect=Rectangle()

        # with side_bar_add_body.canvas.after:
        #    side_bar_add_body.status_lines=Line(rounded_rectangle=(100, 100, 200, 200, 10, 10, 10, 10, 100))

        def side_bar_add_body_update_lines(*args):
            offset=5
            x=int(side_bar_add_body.x)-offset
            y=int(side_bar_add_body.y)-offset
            width=int(side_bar_add_body.width*1)+offset*2
            height=int(side_bar_add_body.height*1)+offset*2
            # side_bar_add_body.status_lines.rounded_rectangle=(x, y, width, height, 10, 10, 10, 10, 100)
            side_bar_add_body.rect.pos=(x,y)
            side_bar_add_body.rect.size=(width,height)
        side_bar_add_body.bind(pos=side_bar_add_body_update_lines, size=side_bar_add_body_update_lines)

        side_bar_add_vertical_seperator=Image(
            source=gray_seperator_line_vertical,
            allow_stretch=True,
            keep_ratio=False,
            size_hint =(.0005, .4),
            pos_hint = {'center_x':.5, 'center_y':.55})
        self.widgets['side_bar_add_vertical_seperator']=side_bar_add_vertical_seperator

        side_bar_add_uuid=MinimumBoundingLabel(
            text='[b][size=16]UUID:',
            markup=True,
            size_hint=(None,None),
            pos_hint = {'right':.48, 'center_y':.675},)
        self.widgets['side_bar_add_uuid']=side_bar_add_uuid

        side_bar_add_uuid_display=MinimumBoundingLabel(
            text='',
            markup=True,
            halign='center',
            pos_hint = {'x':.55, 'center_y':.675})
        self.widgets['side_bar_add_uuid_display']=side_bar_add_uuid_display

        side_bar_add_link_code=MinimumBoundingLabel(
            text='[b][size=16]Link Code:',
            markup=True,
            size_hint=(None,None),
            pos_hint = {'right':.48, 'center_y':.425},)
        self.widgets['side_bar_add_link_code']=side_bar_add_link_code

        side_bar_add_link_code_display=MinimumBoundingLabel(
            text='',
            markup=True,
            pos_hint = {'x':.53, 'center_y':.425})
        self.widgets['side_bar_add_link_code_display']=side_bar_add_link_code_display

        side_bar_add_valid_box=RoundedColorLayout(
            bg_color=palette('complement',.75),
            size_hint=(.1, .115),
            pos_hint={'center_x':.5875, 'center_y':.3})
        self.widgets['side_bar_add_valid_box']=side_bar_add_valid_box

        side_bar_add_valid_text=MinimumBoundingLabel(
            text='[size=16][b][color=#000000]Valid',
            markup=True,
            pos_hint = {'center_x':.5, 'center_y':.8})
        self.widgets['side_bar_add_valid_text']=side_bar_add_valid_text

        side_bar_add_valid_time=MinimumBoundingLabel(
            text='[size=28][color=#000000]15:00',
            markup=True,
            pos_hint = {'center_x':.5, 'center_y':.35})
        self.widgets['side_bar_add_valid_time']=side_bar_add_valid_time

        side_bar_add_qr_missing=MinimumBoundingLabel(
            text='[size=16][color=#ffffff]No User ID Found.\nConfirm Your Account\nstatus and generate\na new link above.',
            markup=True,
            # size_hint =(1, 1),
            pos_hint = {'center_x':.8, 'center_y':.45},)
        self.widgets['side_bar_add_qr_missing']=side_bar_add_qr_missing
        # side_bar_add_qr_missing.ref='side_bar_add_qr_missing'

        side_bar_add_qr_frame=FloatLayout(
            size_hint =(None, .5),
            pos_hint = {'center_x':.8, 'center_y':.45})
        self.widgets['side_bar_add_qr_frame']=side_bar_add_qr_frame

        with side_bar_add_qr_frame.canvas.before:
            qrf=side_bar_add_qr_frame
            length=qrf.width*.3
            qrf.frame_color=Color(*palette('light_tint'))
            qrf.bl_line=Line(points=[qrf.x,qrf.y+length,qrf.x,qrf.y,qrf.x+length,qrf.y],width=2)
            qrf.tl_line=Line(points=[qrf.x,qrf.top-length,qrf.x,qrf.top,qrf.x+length,qrf.top],width=2)
            qrf.tr_line=Line(points=[qrf.right-length,qrf.top,qrf.right,qrf.top,qrf.right,qrf.top-length],width=2)
            qrf.br_line=Line(points=[qrf.right,qrf.y+length,qrf.right,qrf.y,qrf.right-length,qrf.y],width=2)

        def side_bar_add_qr_frame_align(self,*args):
            qrf=side_bar_add_qr_frame
            qrf.width=qrf.height
            qrf.bl_line.points=[qrf.x,qrf.y+length,qrf.x,qrf.y,qrf.x+length,qrf.y]
            qrf.tl_line.points=[qrf.x,qrf.top-length,qrf.x,qrf.top,qrf.x+length,qrf.top]
            qrf.tr_line.points=[qrf.right-length,qrf.top,qrf.right,qrf.top,qrf.right,qrf.top-length]
            qrf.br_line.points=[qrf.right,qrf.y+length,qrf.right,qrf.y,qrf.right-length,qrf.y]
        side_bar_add_qr_frame.bind(pos=side_bar_add_qr_frame_align,size=side_bar_add_qr_frame_align)

        side_bar_add_qr_image=Image(
            allow_stretch=True,
            keep_ratio=True,
            size_hint =(.95, .95),
            pos_hint = {'center_x':.5, 'center_y':.5})
        self.widgets['side_bar_add_qr_image']=side_bar_add_qr_image
        side_bar_add_qr_image.opacity=0

        side_bar_add_qr_generate=RoundedButton(
            text='[size=20][color=#000000]Generate Link',
            size_hint =(.15, .075),
            pos_hint = {'center_x':.8, 'y':.725},
            background_normal='',
            background_color=palette('accent',.85),
            markup=True)
        self.widgets['side_bar_add_qr_generate']=side_bar_add_qr_generate
        side_bar_add_qr_generate.bind(on_release=self.side_bar_add_qr_generate_func)

        side_bar_add_app_icon_layout=ExpandableRoundedColorLayout(
            size_hint =(.1, .1),
            pos_hint = {'center_x':.06, 'center_y':.125},
            expanded_size=(.75,.8),
            expanded_pos = {'center_x':.5, 'center_y':.5},
            bg_color=palette('light_tint',0),
            modal_dim=(0,0,0,.75))
        # side_bar_add_app_icon_layout.shrink_anim=Animation(size_hint=side_bar_add_app_icon_layout.original_size,d=.15,t='in_sine')
        # side_bar_add_app_icon_layout.return_anim=Animation(pos_hint=side_bar_add_app_icon_layout.original_pos,d=.15,t='in_sine')
        self.widgets['side_bar_add_app_icon_layout']=side_bar_add_app_icon_layout
        side_bar_add_app_icon_layout.widgets={}
        side_bar_add_app_icon_layout.bind(on_release=self.side_bar_add_app_icon_layout_func)
        side_bar_add_app_icon_layout.bind(expanded=self.side_bar_add_app_icon_layout_populate)
        side_bar_add_app_icon_layout.bind(animating=partial(general.stripargs,side_bar_add_app_icon_layout.clear_widgets))

        side_bar_add_app_icon_image=Image(
            source=app_icon_source,
            allow_stretch=False,
            keep_ratio=True,
            # size_hint=(1.5,1.5),
            pos_hint = {'center_x':.5, 'center_y':.5})
        self.widgets['side_bar_add_app_icon_image']=side_bar_add_app_icon_image

        side_bar_add_app_bubble_image=Image(
            source=square_bubble,
            allow_stretch=False,
            keep_ratio=True,
            size_hint=(1.5,1.5),
            pos_hint = {'center_x':1.5, 'center_y':.25})
        self.widgets['side_bar_add_app_bubble_image']=side_bar_add_app_bubble_image

        side_bar_add_app_title=Label(
            text='[size=24][color=#000000][b]Hood Control Admin',
            markup=True,
            size_hint =(.4, .05),
            pos_hint = {'center_x':.5, 'center_y':.925},)
        self.widgets['side_bar_add_app_title']=side_bar_add_app_title
        # side_bar_add_app_title.ref='side_bar_add_app_title'

        side_bar_add_app_seperator_line=Image(
            source=black_seperator_line,
            allow_stretch=True,
            keep_ratio=False,
            size_hint =(.98, .004),
            pos_hint = {'x':.01, 'y':.85})
        self.widgets['side_bar_add_app_seperator_line']=side_bar_add_app_seperator_line

        side_bar_add_app_mock_image=Image(
            source=hc_mockup,
            allow_stretch=False,
            keep_ratio=True,
            size_hint=(.7,.7),
            pos_hint = {'center_x':.225, 'y':.1})
        self.widgets['side_bar_add_app_mock_image']=side_bar_add_app_mock_image

        side_bar_add_app_body=MinimumBoundingLabel(
            text=current_language['side_bar_add_app_body'],
            markup=True,
            halign='center',
            pos_hint = {'center_x':.625, 'top':.75},)
        self.widgets['side_bar_add_app_body']=side_bar_add_app_body
        side_bar_add_app_body.ref='side_bar_add_app_body'

        side_bar_add_app_store_badges_image=Image(
            source=store_badges,
            allow_stretch=True,
            keep_ratio=True,
            size_hint=(.325,.325),
            pos_hint = {'center_x':.5, 'y':.1})
        self.widgets['side_bar_add_app_store_badges_image']=side_bar_add_app_store_badges_image

        side_bar_add_app_qr_image=Image(
            source=uid_qr,
            allow_stretch=True,
            keep_ratio=True,
            size_hint=(.325,.325),
            pos_hint = {'center_x':.775, 'y':.1})
        self.widgets['side_bar_add_app_qr_image']=side_bar_add_app_qr_image

        side_bar_add_expand_button=RoundedButton(
            size_hint =(.5, .075),
            pos_hint = {'center_x':.5, 'center_y':.075},
            background_down='',
            background_color=palette('light_tint',.9),
            markup=True)
        self.widgets['side_bar_add_expand_button']=side_bar_add_expand_button
        side_bar_add_expand_button.bind(on_release=self.side_bar_add_expand_button_func)

        side_bar_add_expand_lines=Image(
            source=settings_icon,
            allow_stretch=True,
            keep_ratio=False,
            size_hint =(.4, .035),
            pos_hint = {'center_x':.5, 'center_y':.075})
        side_bar_add_expand_lines.center=side_bar_add_expand_button.center
        self.widgets['side_bar_add_expand_lines']=side_bar_add_expand_lines

        side_bar_remove=ExpandableRoundedColorLayout(
            size_hint =(.9, .15),
            pos_hint = {'center_x':.5, 'center_y':.3125},
            expanded_size=(5.143,1.185),
            expanded_pos = {'center_x':-1.785, 'center_y':.52},
            bg_color=palette('dark_shade',.9),
            locked=lambda x: self.add_widget(PinLock(lambda :(self.unlock(),x()))))
        self.widgets['side_bar_remove']=side_bar_remove
        side_bar_remove.widgets={}
        side_bar_remove.bind(state=self.bg_color)
        side_bar_remove.bind(expanded=self.side_bar_remove_populate)
        side_bar_remove.bind(animating=partial(general.stripargs,side_bar_remove.clear_widgets))

        side_bar_remove_title=Label(
            text=current_language['side_bar_remove_title'],
            markup=True,
            size_hint =(1, 1),
            pos_hint = {'center_x':.5, 'center_y':.5},)
        self.widgets['side_bar_remove_title']=side_bar_remove_title
        side_bar_remove_title.ref='side_bar_remove_title'

        side_bar_remove_seperator=Image(
            source=gray_seperator_line,
            allow_stretch=True,
            keep_ratio=False,
            size_hint =(.9, .005),
            pos_hint = {'x':.05, 'y':.85})
        self.widgets['side_bar_remove_seperator']=side_bar_remove_seperator

        side_bar_remove_expand_button=RoundedButton(
            size_hint =(.5, .075),
            pos_hint = {'center_x':.5, 'center_y':.075},
            background_down='',
            background_color=palette('light_tint',.9),
            markup=True)
        self.widgets['side_bar_remove_expand_button']=side_bar_remove_expand_button
        side_bar_remove_expand_button.bind(on_release=self.side_bar_remove_expand_button_func)

        side_bar_remove_expand_lines=Image(
            source=settings_icon,
            allow_stretch=True,
            keep_ratio=False,
            size_hint =(.4, .035),
            pos_hint = {'center_x':.5, 'center_y':.075})
        side_bar_remove_expand_lines.center=side_bar_remove_expand_button.center
        self.widgets['side_bar_remove_expand_lines']=side_bar_remove_expand_lines

        side_bar_set_pin=RoundedButton(
            text=current_language['side_bar_set_pin'],
            size_hint =(.9, .15),
            pos_hint = {'center_x':.5, 'center_y':.125},
            background_normal='',
            background_color=palette('dark_shade',.9),
            markup=True)
        self.widgets['side_bar_set_pin']=side_bar_set_pin
        side_bar_set_pin.ref='side_bar_set_pin'
        side_bar_set_pin.bind(on_release=self.side_bar_set_pin_func)
        side_bar_set_pin.bind(state=self.bg_color)

        account_admin_hint=RoundedButton(
            text=f"[size=16][b][color=#ffffff]Enable Admin mode to edit fields[/size]",
            color=palette('dark_shade',1),
            size_hint=(.2,.05),
            pos_hint = {'center_x':.5, 'y':.14},
            markup=True,
            background_normal='',
            background_color=palette('dark_shade',.9))
        self.widgets['account_admin_hint']=account_admin_hint
        account_admin_hint.bind(on_touch_up=self.prompt_unlock)

        seperator_line=Image(
            source=gray_seperator_line,
            allow_stretch=True,
            keep_ratio=False,
            size_hint =(.98, .001),
            pos_hint = {'x':.01, 'y':.13})


        information_box.add_widget(information_title)
        information_box.add_widget(information_seperator)
        information_box.add_widget(information_email)
        information_box.add_widget(information_password)

        details_box.add_widget(details_title)
        details_box.add_widget(details_seperator)
        details_box.add_widget(details_body)

        status_box.add_widget(status_title)
        status_box.add_widget(status_seperator)
        status_box.add_widget(status_scroll)
        status_scroll.add_widget(status_scroll_layout)

        side_bar_connect_login.add_widget(side_bar_connect_login_title)

        side_bar_connect.add_widget(side_bar_connect_title)

        side_bar_unlink.add_widget(side_bar_unlink_title)

        side_bar_remove.add_widget(side_bar_remove_title)

        side_bar_add_app_icon_layout.add_widget(side_bar_add_app_icon_image)

        side_bar_add.add_widget(side_bar_add_title)
        side_bar_add_qr_frame.add_widget(side_bar_add_qr_image)
        side_bar_add_valid_box.add_widget(side_bar_add_valid_text)
        side_bar_add_valid_box.add_widget(side_bar_add_valid_time)

        side_bar_box.add_widget(side_bar_connect)
        side_bar_box.add_widget(side_bar_unlink)
        side_bar_box.add_widget(side_bar_add)
        side_bar_box.add_widget(side_bar_remove)
        side_bar_box.add_widget(side_bar_set_pin)

        self.add_widget(bg_image)
        self.add_widget(screen_name)
        self.add_widget(back)
        self.add_widget(back_main)
        self.add_widget(seperator_line)
        self.add_widget(information_box)
        self.add_widget(details_box)
        self.add_widget(status_box)
        self.add_widget(side_bar_box)

    def account_back (self,button):
        self.parent.transition = SlideTransition(direction='right')
        self.manager.current='preferences'
    def account_back_main (self,button):
        self.parent.transition = SlideTransition(direction='down')
        self.manager.current='main'
    def setup_connection(self,*args):
        self.auth_server()
    def remove_connection(self,*args):
        self.unlink_server()
    def email_validate(self,button,*args):
        config=App.get_running_app().config_
        config.set('account','email',f'{button.text}')
        with open(preferences_path,'w') as configfile:
            config.write(configfile)
    def password_validate(self,button,*args):
        config=App.get_running_app().config_
        config.set('account','password',f'{button.text}')
        with open(preferences_path,'w') as configfile:
            config.write(configfile)

    def side_bar_connect_populate(self,*args):
        self.clear_hints()
        sbc_parent=self.widgets['side_bar_box']
        darken=Animation(rgba=palette('dark_shade',1))
        lighten=Animation(rgba=palette('dark_shade',.85))
        side_bar_connect=self.widgets['side_bar_connect']
        side_bar_connect.clear_widgets()
        if side_bar_connect.expanded:
            self.remove_widget(sbc_parent)
            self.add_widget(sbc_parent)#needed to draw children on top
            darken.start(side_bar_connect.shape_color)
            w=self.widgets
            w['side_bar_connect_title'].pos_hint={'center_x':.5, 'center_y':.925}
            w['side_bar_connect_title'].size_hint=(.4, .05)
            w['side_bar_connect_email_input'].text=''
            w['side_bar_connect_password_input'].text=''
            all_widgets=[
                w['side_bar_connect_title'],
                w['side_bar_connect_seperator'],
                w['side_bar_connect_login'],
                w['side_bar_connect_vertical_seperator'],
                w['side_bar_connect_email'],
                w['side_bar_connect_email_input'],
                w['side_bar_connect_password'],
                w['side_bar_connect_password_input'],
                w['side_bar_connect_send'],
                w['side_bar_connect_expand_button'],
                w['side_bar_connect_expand_lines']]
            for i in all_widgets:
                side_bar_connect.add_widget(i)
        elif not side_bar_connect.expanded:
            lighten.start(side_bar_connect.shape_color)
            w=self.widgets
            w['side_bar_connect_title'].pos_hint={'center_x':.5, 'center_y':.5}
            w['side_bar_connect_title'].size_hint=(1,1)
            w['side_bar_connect_login'].shrink()
            all_widgets=[
                w['side_bar_connect_title']]
            for i in all_widgets:
                side_bar_connect.add_widget(i)
        self.connect_send_disable_func(False)

    def side_bar_connect_login_populate(self,*args):
        self.clear_hints()
        darken=Animation(rgba=palette('dark_shade',1),d=.25)
        lighten=Animation(rgba=palette('dark_shade',0))
        side_bar_connect_login=self.widgets['side_bar_connect_login']
        side_bar_connect_login.clear_widgets()
        if side_bar_connect_login.expanded:
            darken.start(side_bar_connect_login.shape_color)
            w=self.widgets
            w['side_bar_connect_login_title'].pos_hint={'center_x':.5, 'center_y':.925}
            w['side_bar_connect_login_title'].size_hint=(.4, .05)
            w['side_bar_connect_login_title'].text='[color=#ffffff][b][size=20]Account Login'
            w['side_bar_connect_login_email_input'].text=''
            w['side_bar_connect_login_password_input'].text=''
            w['side_bar_connect_email_input'].text=''
            w['side_bar_connect_password_input'].text=''
            all_widgets=[
                w['side_bar_connect_login_title'],
                w['side_bar_connect_login_seperator'],
                w['side_bar_connect_login_back'],
                w['side_bar_connect_login_vertical_seperator'],
                w['side_bar_connect_login_email'],
                w['side_bar_connect_login_email_input'],
                w['side_bar_connect_login_password'],
                w['side_bar_connect_login_password_input'],
                w['side_bar_connect_login_send'],
                w['side_bar_connect_login_expand_button'],
                w['side_bar_connect_login_expand_lines']]
            for i in all_widgets:
                side_bar_connect_login.add_widget(i)
        elif not side_bar_connect_login.expanded:
            lighten.start(side_bar_connect_login.shape_color)
            w=self.widgets
            w['side_bar_connect_login_title'].pos_hint={'center_x':.5, 'center_y':.5}
            w['side_bar_connect_login_title'].size_hint=(1,1)
            w['side_bar_connect_login_title'].text='[color=#ffffff][b][size=12]Already have an account?\n[u][size=16]Login'
            all_widgets=[
                w['side_bar_connect_login_title']]
            for i in all_widgets:
                side_bar_connect_login.add_widget(i)
        self.connect_login_send_disable_func(False)
        self.connect_send_disable_func(False)

    def side_bar_unlink_populate(self,*args):
        sbu_parent=self.widgets['side_bar_box']
        darken=Animation(rgba=palette('dark_shade',1))
        lighten=Animation(rgba=palette('dark_shade',.85))
        side_bar_unlink=self.widgets['side_bar_unlink']
        side_bar_unlink.clear_widgets()
        if side_bar_unlink.expanded:
            self.remove_widget(sbu_parent)
            self.add_widget(sbu_parent)#needed to draw children on top
            darken.start(side_bar_unlink.shape_color)
            w=self.widgets
            w['side_bar_unlink_title'].pos_hint={'center_x':.5, 'center_y':.925}
            w['side_bar_unlink_title'].size_hint=(.4, .05)
            all_widgets=[
                w['side_bar_unlink_title'],
                w['side_bar_unlink_seperator'],
                w['side_bar_unlink_expand_button'],
                w['side_bar_unlink_expand_lines']]
            for i in all_widgets:
                side_bar_unlink.add_widget(i)
        elif not side_bar_unlink.expanded:
            lighten.start(side_bar_unlink.shape_color)
            w=self.widgets
            w['side_bar_unlink_title'].pos_hint={'center_x':.5, 'center_y':.5}
            w['side_bar_unlink_title'].size_hint=(1,1)
            all_widgets=[
                w['side_bar_unlink_title']]
            for i in all_widgets:
                side_bar_unlink.add_widget(i)

    def side_bar_add_populate(self,*args):
        sbm_parent=self.widgets['side_bar_box']
        darken=Animation(rgba=palette('dark_shade',1))
        lighten=Animation(rgba=palette('dark_shade',.85))
        side_bar_add=self.widgets['side_bar_add']
        side_bar_add.clear_widgets()
        if side_bar_add.expanded:
            self.remove_widget(sbm_parent)
            self.add_widget(sbm_parent)#needed to draw children on top
            darken.start(side_bar_add.shape_color)
            w=self.widgets
            if os.path.exists(uid_qr):
                qr=w['side_bar_add_qr_image']
                qr.source=uid_qr
                qr.opacity=1
            else:w['side_bar_add_qr_image'].opacity=0
            w['side_bar_add_title'].pos_hint={'center_x':.5, 'center_y':.925}
            w['side_bar_add_title'].size_hint=(.4, .05)
            w['side_bar_add_title'].text=current_language['side_bar_add_title_expanded']
            if hasattr(w['side_bar_add_app_bubble_image'],'parent'):
                if w['side_bar_add_app_bubble_image'].parent==None:
                    w['side_bar_add_app_icon_layout'].add_widget(w['side_bar_add_app_bubble_image'])
            all_widgets=[
                w['side_bar_add_title'],
                w['side_bar_add_seperator'],
                w['side_bar_add_body'],
                w['side_bar_add_vertical_seperator'],
                w['side_bar_add_uuid'],
                w['side_bar_add_uuid_display'],
                w['side_bar_add_link_code'],
                w['side_bar_add_link_code_display'],
                w['side_bar_add_valid_box'],
                w['side_bar_add_qr_missing'],
                w['side_bar_add_qr_frame'],
                w['side_bar_add_qr_generate'],
                w['side_bar_add_app_icon_layout'],
                w['side_bar_add_expand_button'],
                w['side_bar_add_expand_lines']]
            for i in all_widgets:
                side_bar_add.add_widget(i)
            self.side_bar_add_qr_generate_func()
        elif not side_bar_add.expanded:
            lighten.start(side_bar_add.shape_color)
            w=self.widgets
            if w['side_bar_add_app_icon_layout'].expanded:
                w['side_bar_add_app_icon_layout'].shrink()
            w['side_bar_add_title'].pos_hint={'center_x':.5, 'center_y':.5}
            w['side_bar_add_title'].size_hint=(1,1)
            w['side_bar_add_title'].text=current_language['side_bar_add_title']
            all_widgets=[
                w['side_bar_add_title']]
            for i in all_widgets:
                side_bar_add.add_widget(i)

    def side_bar_add_app_icon_layout_populate(self,*args):
        sba_icon=self.widgets['side_bar_add_app_icon_layout']
        sba_parent=self.widgets['side_bar_add']
        darken=Animation(rgba=palette('light_tint',1))
        lighten=Animation(rgba=palette('light_tint',0),d=.75)
        side_bar_add_app_icon=self.widgets['side_bar_add_app_icon_layout']
        side_bar_add_app_icon.clear_widgets()
        if side_bar_add_app_icon.expanded:
            sba_parent.remove_widget(sba_icon)
            sba_parent.add_widget(sba_icon)#needed to draw children on top
            darken.start(side_bar_add_app_icon.shape_color)
            w=self.widgets
            all_widgets=[
                w['side_bar_add_app_title'],
                w['side_bar_add_app_seperator_line'],
                w['side_bar_add_app_mock_image'],
                w['side_bar_add_app_body'],
                w['side_bar_add_app_store_badges_image'],
                w['side_bar_add_app_qr_image']]
            for i in all_widgets:
                side_bar_add_app_icon.add_widget(i)
        elif not side_bar_add_app_icon.expanded:
            lighten.start(side_bar_add_app_icon.shape_color)
            w=self.widgets
            w['side_bar_add_app_icon_image'].opacity=0
            Animation(opacity=1,d=1.5).start(w['side_bar_add_app_icon_image'])
            all_widgets=[
                w['side_bar_add_app_icon_image']]
            for i in all_widgets:
                side_bar_add_app_icon.add_widget(i)

    def side_bar_remove_populate(self,*args):
        sbr_parent=self.widgets['side_bar_box']
        darken=Animation(rgba=palette('dark_shade',1))
        lighten=Animation(rgba=palette('dark_shade',.85))
        side_bar_remove=self.widgets['side_bar_remove']
        side_bar_remove.clear_widgets()
        if side_bar_remove.expanded:
            self.remove_widget(sbr_parent)
            self.add_widget(sbr_parent)#needed to draw children on top
            darken.start(side_bar_remove.shape_color)
            w=self.widgets
            w['side_bar_remove_title'].pos_hint={'center_x':.5, 'center_y':.925}
            w['side_bar_remove_title'].size_hint=(.4, .05)
            all_widgets=[
                w['side_bar_remove_title'],
                w['side_bar_remove_seperator'],
                w['side_bar_remove_expand_button'],
                w['side_bar_remove_expand_lines']]
            for i in all_widgets:
                side_bar_remove.add_widget(i)
        elif not side_bar_remove.expanded:
            lighten.start(side_bar_remove.shape_color)
            w=self.widgets
            w['side_bar_remove_title'].pos_hint={'center_x':.5, 'center_y':.5}
            w['side_bar_remove_title'].size_hint=(1,1)
            all_widgets=[
                w['side_bar_remove_title']]
            for i in all_widgets:
                side_bar_remove.add_widget(i)

    def side_bar_connect_login_expand_button_func(self,*args):
        sba=self.widgets['side_bar_connect_login']
        if sba.expanded:
            a=Animation(rgba=palette('dark_shade',0),d=.25)
            a.start(sba.shape_color)
            a.bind(on_complete=sba.shrink)
        if not sba.expanded:
            sba.expand()

    def side_bar_connect_expand_button_func(self,*args):
        sba=self.widgets['side_bar_connect']
        if sba.expanded:
            sba.shrink()
        if not sba.expanded:
            sba.expand()

    def side_bar_unlink_expand_button_func(self,*args):
        sba=self.widgets['side_bar_unlink']
        if sba.expanded:
            sba.shrink()
        if not sba.expanded:
            sba.expand()

    def side_bar_remove_expand_button_func(self,*args):
        sba=self.widgets['side_bar_remove']
        if sba.expanded:
            sba.shrink()
        if not sba.expanded:
            sba.expand()

    def side_bar_add_expand_button_func(self,*args):
        sba=self.widgets['side_bar_add']
        if sba.expanded:
            sba.shrink()
        if not sba.expanded:
            sba.expand()

    def side_bar_add_app_icon_layout_func(self,*args):
        sba=self.widgets['side_bar_add_app_icon_layout']
        def shrink(*args):
            if sba.expanded:
                sba.shrink()
        if sba.expanded:
            Clock.schedule_once(shrink,0)
        else:
            sba.shape_color.rgba=palette('light_tint',.2)

    def side_bar_add_qr_generate_func(self,*args):
        w=self.widgets
        if hasattr(server,'uid'):
            if server.uid:
                if self.generate_link_timer>time.time():
                    return
                self.uvt_event=Clock.schedule_interval(self.update_valid_time,.1)
                self.generate_link_timer=time.time()+15#900
                w['side_bar_add_qr_image'].source=uid_qr
                w['side_bar_add_qr_image'].opacity=1
                w['side_bar_add_valid_box'].opacity=1
                _quarterPoint = len(server.uid)//4
                _midPoint = len(server.uid)//2
                _endquarterPoint = int(len(server.uid)//1.3)
                _uuid=server.uid[:_quarterPoint]+'\n'+server.uid[_quarterPoint:_midPoint]+'\n'+server.uid[_midPoint:_endquarterPoint]+'\n'+server.uid[_endquarterPoint:]
                w['side_bar_add_uuid_display'].text=f'[size=16]{_uuid}'
                self._link_code='    '.join(random.choices(string.ascii_uppercase+string.digits+string.digits,k=6))
                w['side_bar_add_link_code_display'].text='[size=16]'+self._link_code
                stripped_link_code=self._link_code.replace(' ','')
                config=App.get_running_app().config_
                config.set('account','uuid',server.uid)
                config.set('account','link_code',stripped_link_code)
                with open(preferences_path,'w') as configfile:
                    config.write(configfile)
                qr_data=server.uid+stripped_link_code
                logger.debug(qr_data)
                self.generate_uid_qr(qr_data)
                w['side_bar_add_qr_image'].reload()
                return
        w['side_bar_add_qr_image'].opacity=0
        w['side_bar_add_valid_box'].opacity=0
        w['side_bar_add_uuid_display'].text=''
        w['side_bar_add_link_code_display'].text=''

    def side_bar_set_pin_func(self,*args):
        def set_pin(*args):
            pl=PinLock(set_pin=True,callback=confirm_pin)
            pl.widgets['title'].text='[size=20][color=#ffffff][b]Enter New Pin'
            self.add_widget(pl)

        def confirm_pin(**kwargs):
            if not 'alt_pin' in kwargs:
                App.get_running_app().notifications.toast('Error','warning')
                return
            pin=kwargs.pop('alt_pin')
            pl=PinLock(alt_pin=pin,callback=save_pin)
            pl.widgets['title'].text='[size=20][color=#ffffff][b]Confirm New Pin'
            self.add_widget(pl)

        def save_pin(pin,*args):
            root=App.get_running_app()
            config=root.config_
            config['account']['admin_pin']=pin
            with open(preferences_path,'w') as configfile:
                config.write(configfile)
            root.notifications.toast('[b][size=20]Pin Saved')

        self.add_widget(PinLock(set_pin))

    def side_bar_connect_login_email_input_clear(self,button,focused,*args):
        si=self.widgets['side_bar_connect_login_email_input']
        p=si.parent
        if p:
            p.remove_widget(si)
            p.add_widget(si)
        if focused:
            si.font_size=32
            si.pos_hint={'center_x':.5, 'center_y':.6}
            si.size_hint=(.8, .1)
        else:
            si.font_size=15
            si.pos_hint={'x':.4, 'center_y':.7}
            si.size_hint=(.3, .05)
        self.connect_login_send_disable_func(focused)

    def side_bar_connect_login_password_input_clear(self,button,focused,*args):
        pi=self.widgets['side_bar_connect_login_password_input']
        p=pi.parent
        if p:
            p.remove_widget(pi)
            p.add_widget(pi)
        if focused:
            pi.text=''
            pi.font_size=32
            pi.pos_hint={'center_x':.5, 'center_y':.6}
            pi.size_hint=(.8, .1)
        else:
            pi.font_size=15
            pi.pos_hint={'x':.4, 'center_y':.55}
            pi.size_hint=(.3, .05)
        self.connect_login_send_disable_func(focused)

    def side_bar_connect_email_input_clear(self,button,focused,*args):
        si=self.widgets['side_bar_connect_email_input']
        p=si.parent
        if p:
            p.remove_widget(si)
            p.add_widget(si)
        if focused:
            si.font_size=32
            si.pos_hint={'center_x':.5, 'center_y':.6}
            si.size_hint=(.8, .1)
        else:
            si.font_size=15
            si.pos_hint={'x':.4, 'center_y':.7}
            si.size_hint=(.3, .05)
        self.connect_send_disable_func(focused)

    def side_bar_connect_password_input_clear(self,button,focused,*args):
        pi=self.widgets['side_bar_connect_password_input']
        p=pi.parent
        if p:
            p.remove_widget(pi)
            p.add_widget(pi)
        if focused:
            pi.text=''
            pi.font_size=32
            pi.pos_hint={'center_x':.5, 'center_y':.6}
            pi.size_hint=(.8, .1)
        else:
            pi.font_size=15
            pi.pos_hint={'x':.4, 'center_y':.55}
            pi.size_hint=(.3, .05)
        self.connect_send_disable_func(focused)

    def bg_color(self,button,*args):
        if hasattr(button,'expanded'):
            if button.expanded:
                return
        if button.state=='normal':
            button.shape_color.rgba=palette('dark_shade',.9)
        if button.state=='down':
            button.shape_color.rgba=palette('primary',.15)

    def prompt_unlock(self,button,touch,*args):
        if not button.collide_point(*touch.pos):
            return
        if self.unlocked:
            return
        for widget in self.children:
            if isinstance(widget,PinLock):
                return
        self.add_widget(PinLock(self.unlock))

    def unlock(self,*args):
        self.unlocked=True
        self.check_admin_mode()

    def account_prompt(self,*args):
        if hasattr(self,'prompt_fade'):
            return
        if App.get_running_app().config_.get('account','email',fallback=False):
            return
        else:
            self.prompt_fade=True
            def clear_prompt_fade(*args):
                if hasattr(self,'prompt_fade'):
                    del self.prompt_fade
            b=self.widgets['side_bar_connect']
            p=b.parent
            pp=b.parent.parent
            p.remove_widget(b)
            p.add_widget(b)
            pp.remove_widget(p)
            pp.add_widget(p)
            with b.canvas.before:
                b.screen_fade=Color(*palette('dark_shade',0))
                Rectangle(size=Window.size)
            def modal(_touch):
                if not b.collide_point(*_touch.pos):
                    return True
                else:
                    super(ExpandableRoundedColorLayout,b).on_touch_down(_touch)
                    return True
            def not_modal(_touch):
                return super(ExpandableRoundedColorLayout,b).on_touch_down(_touch)
            setattr(b,'on_touch_down',modal)
            a=Animation(rgba=palette('dark_shade',.75),d=.35)
            a.start(b.screen_fade)
            def unfade(*args):
                a=Animation(rgba=palette('dark_shade',0),d=.25)
                a.start(b.screen_fade)
                a.bind(on_complete=clear_prompt_fade)
                setattr(b,'on_touch_down',not_modal)
            def schedule_unfade(*args):
                Clock.schedule_once(unfade,1.75)
            a.bind(on_complete=schedule_unfade)

    def check_admin_mode(self,*args):
        # App.get_running_app().admin_mode_start=time.time()+1000
        w=self.widgets
        if App.get_running_app().admin_mode_start>time.time() or self.unlocked:
            self.unlocked=True
            if w['account_admin_hint'].parent:
                self.remove_widget(w['account_admin_hint'])
            w['side_bar_connect'].unlock()
            w['side_bar_unlink'].unlock()
            w['side_bar_add'].unlock()
            w['side_bar_remove'].unlock()
        else:
            self.unlocked=False
            if not w['account_admin_hint'].parent:
                self.add_widget(w['account_admin_hint'])
            w['information_email'].disabled=True
            w['information_password'].disabled=True
            w['side_bar_connect'].lock()
            w['side_bar_unlink'].lock()
            w['side_bar_add'].lock()
            w['side_bar_remove'].lock()

        #check for presence of email
        if w['information_email'].text:
            w['side_bar_unlink'].disabled=False
            w['side_bar_add'].disabled=False
            w['side_bar_remove'].disabled=False
            w['side_bar_unlink'].shape_color.rgba=palette('dark_shade',.9)
            w['side_bar_add'].shape_color.rgba=palette('dark_shade',.9)
            w['side_bar_remove'].shape_color.rgba=palette('dark_shade',.9)
        else:
            w['side_bar_unlink'].disabled=True
            w['side_bar_add'].disabled=True
            w['side_bar_remove'].disabled=True
            w['side_bar_unlink'].shape_color.rgba=palette('secondary',.8)
            w['side_bar_add'].   shape_color.rgba=palette('secondary',.8)
            w['side_bar_remove'].shape_color.rgba=palette('secondary',.8)

    def generate_uid_qr(self,data,*args):
        qr=segno.make_qr(data)
        qr.save(
            uid_qr,
            'png',
            scale=5,
            border=1)

    def update_valid_time(self,*args):
        _dt=self.generate_link_timer-time.time()
        w=self.widgets
        box=w['side_bar_add_valid_box']
        valid_time=w['side_bar_add_valid_time']
        valid_text=w['side_bar_add_valid_text']
        gen=w['side_bar_add_qr_generate']
        if _dt>0:
            _time=str(timedelta(seconds=int(_dt)))[2:]
            box.shape_color.rgba=palette('complement',.75)
            valid_text.text='[size=16][b][color=#000000]Valid'
            valid_time.text=f'[size=28][color=#000000]{_time}'
            gen.disabled=True
            gen.shape_color.rgba=palette('accent',.5)
        else:
            self.uvt_event.cancel()
            box.shape_color.rgba=palette('highlight',.85)
            valid_text.text='[size=16][b][color=#000000]Expired'
            valid_time.text='[size=28][color=#000000]00:00'
            gen.disabled=False
            gen.shape_color.rgba=palette('accent',.85)
            config=App.get_running_app().config_
            config.set('account','link_code','')
            with open(preferences_path,'w') as configfile:
                config.write(configfile)

    def on_pre_enter(self, *args):
        w=self.widgets
        self.unlocked=False
        if App.get_running_app().config_.get('account','email',fallback=False):
            w['information_email'].text=App.get_running_app().config_['account']['email']
            w['information_password'].text=App.get_running_app().config_['account']['password']
            w['side_bar_connect_title'].text=current_language['side_bar_connect_title']
            w['side_bar_connect_title'].ref='side_bar_connect_title'
        else:
            w['side_bar_connect_title'].text=current_language['side_bar_create_title']
            w['side_bar_connect_title'].ref='side_bar_create_title'
        self.check_admin_mode()
        return super().on_pre_enter(*args)

    def auth_server(self,*args):
        self.clear_link_code()
        config=App.get_running_app().config_
        if not config.get('account','email',fallback=False):
            return
        if not config.get('account','password',fallback=False):
            return
        account_email=config['account']['email']
        account_password=config['account']['password']
        if not (account_email and account_password):
            return
        if hasattr(server,'user'):
            return
        server.device_requests=server._device_requests.copy()
        server.authUser(f'{account_email}', f'{account_password}')
        self._keep_ref(self.listen_to_server,.75)
        self._keep_ref(server.refresh_token,45*60)#45 minutes; token expires every hour.

    def auth_server_new_account(self,email,password,*args):
        self.clear_link_code()
        email=str(email)
        password=str(password)
        if not (email and password):
            return
        if hasattr(server,'user'):
            return
        server.device_requests=server._device_requests.copy()
        server.authUser(email, password)
        self._keep_ref(self.listen_to_server,.75)
        self._keep_ref(server.refresh_token,45*60)#45 minutes; token expires every hour.

    def listen_to_server(*args):
        if 1 not in server.device_requests.values():
            return

        main_screen=App.get_running_app().context_screen.get_screen('main')
        for i in server.device_requests.items():
            if not i[1]:
                continue
            if i[0] in main_screen.widgets:
                main_screen.widgets[i[0]].trigger_action()

        server.reset_reqs()

    def _keep_ref(self,func_to_sched,interval,*args):
        log=self.scheduled_funcs
        log.append(Clock.schedule_interval(func_to_sched,interval))

    def unlink_server(self,*args):
        if not hasattr(server,'user'):
            return
        for i in self.scheduled_funcs:
            i.cancel()
        self.scheduled_funcs=[]
        delattr(server,'user')

    def clear_link_code(self,*args):
        config=App.get_running_app().config_
        config.set('account','link_code','')
        with open(preferences_path,'w') as configfile:
            config.write(configfile)

    def side_bar_connect_login_send_disabled(self,button,disabled,*args):
        if  button.disabled:
            button.text='[b][size=16]All Fields Required'
        elif not button.disabled:
            button.text='[b][size=16]Connect Account'
        button.color_swap()

    def connect_login_send_disable_func(self,focused,*args):
        con_btn=self.widgets['side_bar_connect_login_send']
        si=self.widgets['side_bar_connect_login_email_input']
        pi=self.widgets['side_bar_connect_login_password_input']
        self.clear_hints()
        if (si.contains_valid_email and pi.text!=''):
            con_btn.disabled=False
            con_btn.bg_color=palette('accent',1)
            con_btn.color_swap()
        else:
            con_btn.disabled=True
            con_btn.bg_color=palette('secondary',1)
            con_btn.color_swap()
            if not focused and si.text!='' and not si.contains_valid_email:
                if hasattr(self,'login_email_hint_icon'):
                    return
                self.login_email_hint_icon=h=RoundedLabelColor(
                    text='[b][size=20]!',
                    markup=True,
                    bg_color=palette('highlight',.25),
                    size_hint =(.025, .05),
                    pos_hint = {'center_x':.725, 'center_y':.7})
                if hasattr(h,'parent'):
                    if h.parent:
                        return
                self.widgets['side_bar_connect_login'].add_widget(h)
                eih=self.widgets['side_bar_connect_login_email_invalid_hint']
                if hasattr(eih,'parent'):
                    if eih.parent:
                        return
                self.widgets['side_bar_connect_login'].add_widget(eih)

    def side_bar_connect_send_disabled(self,button,disabled,*args):
        if  button.disabled:
            button.text='[b][size=16]All Fields Required'
        elif not button.disabled:
            button.text='[b][size=16]Send Verification Email'
        button.color_swap()

    def connect_send_disable_func(self,focused,*args):
        con_btn=self.widgets['side_bar_connect_send']
        si=self.widgets['side_bar_connect_email_input']
        pi=self.widgets['side_bar_connect_password_input']
        self.clear_hints()
        if (si.contains_valid_email and pi.text!=''):
            con_btn.disabled=False
            con_btn.bg_color=palette('accent',1)
            con_btn.color_swap()
        else:
            con_btn.disabled=True
            con_btn.bg_color=palette('secondary',1)
            con_btn.color_swap()
            if not focused and si.text!='' and not si.contains_valid_email:
                if hasattr(self,'email_hint_icon'):
                    return
                self.email_hint_icon=h=RoundedLabelColor(
                    text='[b][size=20]!',
                    markup=True,
                    bg_color=palette('highlight',.25),
                    size_hint =(.025, .05),
                    pos_hint = {'center_x':.725, 'center_y':.7})
                if hasattr(h,'parent'):
                    if h.parent:
                        return
                self.widgets['side_bar_connect'].add_widget(h)
                eih=self.widgets['side_bar_connect_email_invalid_hint']
                if hasattr(eih,'parent'):
                    if eih.parent:
                        return
                self.widgets['side_bar_connect'].add_widget(eih)

    def clear_hints(self,*args):
        if hasattr(self,'email_hint_icon'):
            if hasattr(self.email_hint_icon, 'parent'):
                if self.email_hint_icon.parent:
                    self.email_hint_icon.parent.remove_widget(self.email_hint_icon)
            del self.email_hint_icon
        if hasattr(self,'login_email_hint_icon'):
            if hasattr(self.login_email_hint_icon, 'parent'):
                if self.login_email_hint_icon.parent:
                    self.login_email_hint_icon.parent.remove_widget(self.login_email_hint_icon)
            del self.login_email_hint_icon
        eih=self.widgets['side_bar_connect_email_invalid_hint']
        if hasattr(eih,'parent'):
            if eih.parent:
                eih.parent.remove_widget(eih)
        leih=self.widgets['side_bar_connect_login_email_invalid_hint']
        if hasattr(leih,'parent'):
            if leih.parent:
                leih.parent.remove_widget(leih)

    def side_bar_connect_login_send_func(self,*args):
        w=self.widgets
        email=w['side_bar_connect_login_email_input'].text
        password=w['side_bar_connect_login_password_input'].text
        response=server.authUser(email,password)
        # App.get_running_app().notifications.toast(response['message'])

    def side_bar_connect_send_func(self,*args):
        w=self.widgets
        email=w['side_bar_connect_email_input'].text
        password=w['side_bar_connect_password_input'].text
        self.auth_server_new_account(email,password)
        server.send_verification_email()

class NetworkScreen(Screen):
    def __init__(self, **kwargs):
        super(NetworkScreen,self).__init__(**kwargs)
        self.cols = 2
        self.widgets={}
        bg_image = Image(source=background_image, allow_stretch=True, keep_ratio=False)
        self._details_ssid=''
        self._scan=Thread()
        self._refresh_ap=Thread()
        self._ssid_details=Thread()
        self._known_networks=Thread()
        self._manual_connecting=Thread()
        self._known_connecting=Thread()
        self._known_removing=Thread()
        self._details_connecting=Thread()
        self._network_switching=Thread()
        self._auto_networks=Thread()
        self._priority_setting=Thread()
        self._disconnect_temp=Thread()
        self._disconnect_rmv=Thread()

        back=RoundedButton(
            text=current_language['settings_back'],
            size_hint =(.4, .1),
            pos_hint = {'x':.06, 'y':.015},
            background_down='',
            background_color=palette('neutral',.9),
            markup=True)
        self.widgets['back']=back
        back.ref='settings_back'
        back.bind(on_release=self.network_back)

        back_main=RoundedButton(
            text=current_language['preferences_back_main'],
            size_hint =(.4, .1),
            pos_hint = {'x':.52, 'y':.015},
            background_normal='',
            background_color=palette('primary',.9),
            markup=True)
        self.widgets['back_main']=back_main
        back_main.ref='preferences_back_main'
        back_main.bind(on_release=self.network_back_main)

        screen_name=Label(
            text=current_language['network_screen_name'],
            markup=True,
            size_hint =(.4, .05),
            pos_hint = {'center_x':.15, 'center_y':.925},)
        self.widgets['screen_name']=screen_name
        screen_name.ref='network_screen_name'

        information_box=ExpandableRoundedColorLayout(
            bg_color=palette('dark_shade',.85),
            size_hint =(.35, .25),
            pos_hint = {'center_x':.225, 'center_y':.75},
            expanded_size=(.9,.8),
            expanded_pos={'center_x':.5,'center_y':.55})
        self.widgets['information_box']=information_box
        information_box.bind(expanded=self.information_box_populate)
        information_box.bind(animating=partial(general.stripargs,information_box.clear_widgets))

        information_expand_button=RoundedButton(
            size_hint =(.5, .175),
            pos_hint = {'center_x':.5, 'center_y':.15},
            background_down='',
            background_color=palette('light_tint',.9),
            markup=True)
        self.widgets['information_expand_button']=information_expand_button
        information_expand_button.bind(on_release=self.information_expand_button_func)

        information_expand_lines=Image(
            source=settings_icon,
            allow_stretch=True,
            keep_ratio=False,
            size_hint =(.4, .075),
            pos_hint = {'center_x':.5, 'center_y':.15})
        information_expand_lines.center=information_expand_button.center
        self.widgets['information_expand_lines']=information_expand_lines

        information_title=Label(
            text=current_language['network_information_title'],
            markup=True,
            size_hint =(.4, .05),
            pos_hint = {'center_x':.5, 'center_y':.925},)
        self.widgets['information_title']=information_title
        information_title.ref='network_information_title'

        information_seperator=Image(
            source=gray_seperator_line,
            allow_stretch=True,
            keep_ratio=False,
            size_hint =(.9, .005),
            pos_hint = {'x':.05, 'y':.85})
        self.widgets['information_seperator']=information_seperator

        information_ssid=MinimumBoundingLabel(
            text='[b][size=16]SSID:',
            markup=True,
            size_hint =(.4, .05), 
            pos_hint = {'x':.2, 'center_y':.725},)
        self.widgets['information_ssid']=information_ssid

        information_status=MinimumBoundingLabel(
            text='[b][size=16]Status:',
            markup=True,
            size_hint =(.4, .05),
            pos_hint = {'x':.2, 'center_y':.55},)
        self.widgets['information_status']=information_status

        information_signal=MinimumBoundingLabel(
            text='[b][size=16]Signal:',
            markup=True,
            size_hint =(.4, .05),
            pos_hint = {'x':.2, 'center_y':.375},)
        self.widgets['information_signal']=information_signal

        details_box=ExpandableRoundedColorLayout(
            bg_color=palette('dark_shade',.85),
            size_hint =(.35, .4),
            pos_hint = {'center_x':.225, 'center_y':.4},
            expanded_size=(.9,.8),
            expanded_pos={'center_x':.5,'center_y':.55})
        details_box.widgets={}
        self.widgets['details_box']=details_box
        details_box.bind(expanded=self.details_box_populate)
        details_box.bind(animating=partial(general.stripargs,details_box.clear_widgets))

        details_expand_button=RoundedButton(
            size_hint =(.5, .125),
            pos_hint = {'center_x':.5, 'center_y':.15},
            background_down='',
            background_color=palette('light_tint',.9),
            markup=True)
        self.widgets['details_expand_button']=details_expand_button
        details_expand_button.bind(on_release=self.details_expand_button_func)

        details_expand_lines=Image(
            source=settings_icon,
            allow_stretch=True,
            keep_ratio=False,
            size_hint =(.4, .0525),
            pos_hint = {'center_x':.5, 'center_y':.15})
        details_expand_lines.center=details_expand_button.center
        self.widgets['details_expand_lines']=details_expand_lines

        details_title=Label(
            text=current_language['network_details_title'],
            markup=True,
            size_hint =(.4, .05),
            pos_hint = {'center_x':.5, 'center_y':.925},)
        self.widgets['details_title']=details_title
        details_title.ref='network_details_title'

        details_seperator=Image(
            source=gray_seperator_line,
            allow_stretch=True,
            keep_ratio=False,
            size_hint =(.9, .005),
            pos_hint = {'x':.05, 'y':.85})
        self.widgets['details_seperator']=details_seperator

        details_box_hint_text=Label(
            text=current_language['details_box_hint_text'],
            markup=True,
            size_hint =(.4, .05),
            pos_hint = {'center_x':.5, 'center_y':.5},)
        self.widgets['details_box_hint_text']=details_box_hint_text
        details_box_hint_text.ref='details_box_hint_text'

        details_ssid=MinimumBoundingLabel(
            text='[b][size=16]     SSID:',
            markup=True,
            size_hint=(None,None),
            pos_hint = {'x':.1, 'center_y':.8},)
        self.widgets['details_ssid']=details_ssid

        details_signal=MinimumBoundingLabel(
            text='[b][size=16]   Signal:',
            markup=True,
            size_hint=(None,None),
            pos_hint = {'x':.1, 'center_y':.75},)
        self.widgets['details_signal']=details_signal

        details_security=MinimumBoundingLabel(
            text='[b][size=16]Security:',
            markup=True,
            size_hint=(None,None),
            pos_hint = {'x':.1, 'center_y':.7},)
        self.widgets['details_security']=details_security

        details_connect_box=RoundedColorLayout(
            bg_color=palette('secondary',.85),
            size_hint =(.4, .6),
            pos_hint = {'center_x':.7, 'center_y':.5},)
        self.widgets['details_connect_box']=details_connect_box

        details_password_label=Label(
            text='[b][size=20]Connect',
            markup=True,
            size_hint=(.4, .05),
            pos_hint = {'center_x':.5, 'center_y':.925},)
        self.widgets['details_password_label']=details_password_label

        details_password_label_seperator=Image(
            source=gray_seperator_line,
            allow_stretch=True,
            keep_ratio=False,
            size_hint =(.9, .005),
            pos_hint = {'x':.05, 'y':.85})
        self.widgets['details_password_label_seperator']=details_password_label_seperator

        details_password_interior_box=LabelColor(
            size_hint =(.9,.75),
            pos_hint = {'center_x':.5, 'center_y':.45},
            bg_color=palette('light_tint',.15))
        self.widgets['details_password_interior_box']=details_password_interior_box

        details_ssid_known=RoundedLabelColor(
            bg_color=palette('accent',1),
            size_hint =(.5, .15),
            pos_hint = {'center_x':.5, 'center_y':.7},
            text='[b][size=16]Network is Known (Saved)',
            markup=True)
        details_ssid_known.opacity=0
        self.widgets['details_ssid_known']=details_ssid_known

        details_password=TextInput(
            disabled=False,
            multiline=False,
            password=True,
            hint_text='Enter Password',
            size_hint =(.8, .1),
            pos_hint = {'center_x':.5, 'center_y':.55})
        self.widgets['details_password']=details_password
        details_password.disabled=True
        details_password.bind(focus=self.details_password_clear_text)

        details_network_connect=RoundedButton(
            text='[b][size=16]Password Required',
            size_hint =(.6, .1),
            pos_hint = {'center_x':.5, 'center_y':.25},
            background_normal='',
            background_color=palette('secondary',1),
            disabled=True,
            disabled_color=palette('light_tint',1),
            markup=True)
        self.widgets['details_network_connect']=details_network_connect
        details_network_connect.bind(on_release=self.details_network_connect_func)
        details_network_connect.bind(disabled=self.details_network_connect_disabled)

        status_box=RoundedColorLayout(
            bg_color=palette('dark_shade',.85),
            size_hint =(.35, .675),
            pos_hint = {'center_x':.6, 'center_y':.5375},)
        status_box.widgets={}
        self.widgets['status_box']=status_box

        status_title=Label(
            text=current_language['network_status_title'],
            markup=True,
            size_hint =(.4, .05),
            pos_hint = {'center_x':.5, 'center_y':.925},)
        self.widgets['status_title']=status_title
        status_title.ref='network_status_title'

        status_seperator=Image(
            source=gray_seperator_line,
            allow_stretch=True,
            keep_ratio=False,
            size_hint =(.9, .005),
            pos_hint = {'x':.05, 'y':.85})

        status_scroll=OutlineScroll(
            size_hint =(.9,.75),
            pos_hint = {'center_x':.5, 'center_y':.45},
            bg_color=palette('light_tint',.15),
            bar_width=8,
            bar_color=palette('primary',.9),
            bar_inactive_color=palette('primary',.35),
            do_scroll_y=True,
            do_scroll_x=False)

        status_scroll_layout = GridLayout(
            cols=1,
            spacing=10,
            size_hint_y=None,
            padding=5)
        self.widgets['status_scroll_layout']=status_scroll_layout
        # Make sure the height is such that there is something to scroll.
        status_scroll_layout.bind(minimum_height=status_scroll_layout.setter('height'))

        side_bar_box=RoundedColorLayout(
            bg_color=palette('base',.85),
            size_hint =(.175, .675),
            pos_hint = {'center_x':.9, 'center_y':.5375},)
        self.widgets['side_bar_box']=side_bar_box

        side_bar_scan=RoundedButton(
            text=current_language['side_bar_scan'],
            size_hint =(.9, .15),
            pos_hint = {'center_x':.5, 'center_y':.875},
            background_normal='',
            background_color=palette('dark_shade',.85),
            markup=True)
        self.widgets['side_bar_scan']=side_bar_scan
        side_bar_scan.ref='side_bar_scan'
        side_bar_scan.bind(state=self.bg_color)
        side_bar_scan.bind(on_release=self.side_bar_scan_func)

        side_bar_manual=ExpandableRoundedColorLayout(
            size_hint =(.9, .15),
            pos_hint = {'center_x':.5, 'center_y':.6875},
            expanded_size=(5.143,1.185),
            expanded_pos = {'center_x':-1.785, 'center_y':.52},
            bg_color=palette('dark_shade',.85))
        side_bar_manual.widgets={}
        self.widgets['side_bar_manual']=side_bar_manual
        side_bar_manual.bind(state=self.bg_color)
        side_bar_manual.bind(expanded=self.side_bar_manual_populate)
        side_bar_manual.bind(animating=partial(general.stripargs,side_bar_manual.clear_widgets))

        side_bar_manual_title=Label(
            text=current_language['side_bar_manual_title'],
            markup=True,
            size_hint =(1, 1),
            pos_hint = {'center_x':.5, 'center_y':.5},)
        self.widgets['side_bar_manual_title']=side_bar_manual_title
        side_bar_manual_title.ref='side_bar_manual_title'

        side_bar_manual_seperator=Image(
            source=gray_seperator_line,
            allow_stretch=True,
            keep_ratio=False,
            size_hint =(.9, .005),
            pos_hint = {'x':.05, 'y':.85})
        self.widgets['side_bar_manual_seperator']=side_bar_manual_seperator

        side_bar_manual_expand_button=RoundedButton(
            size_hint =(.5, .075),
            pos_hint = {'center_x':.5, 'center_y':.075},
            background_down='',
            background_color=palette('light_tint',.9),
            markup=True)
        self.widgets['side_bar_manual_expand_button']=side_bar_manual_expand_button
        side_bar_manual_expand_button.bind(on_release=self.side_bar_manual_expand_button_func)

        side_bar_manual_expand_lines=Image(
            source=settings_icon,
            allow_stretch=True,
            keep_ratio=False,
            size_hint =(.4, .035),
            pos_hint = {'center_x':.5, 'center_y':.075})
        side_bar_manual_expand_lines.center=side_bar_manual_expand_button.center
        self.widgets['side_bar_manual_expand_lines']=side_bar_manual_expand_lines

        side_bar_manual_vertical_seperator=Image(
            source=gray_seperator_line_vertical,
            allow_stretch=True,
            keep_ratio=False,
            size_hint =(.0005, .4),
            pos_hint = {'center_x':.37, 'center_y':.55})
        self.widgets['side_bar_manual_vertical_seperator']=side_bar_manual_vertical_seperator

        side_bar_manual_ssid=MinimumBoundingLabel(
            text='[b][size=16]SSID:',
            markup=True,
            size_hint=(None,None),
            pos_hint = {'right':.35, 'center_y':.7},)
        self.widgets['side_bar_manual_ssid']=side_bar_manual_ssid

        side_bar_manual_ssid_input=TextInput(
            disabled=False,
            multiline=False,
            hint_text='Enter Network Name',
            size_hint =(.3, .05),
            pos_hint = {'x':.4, 'center_y':.7})
        self.widgets['side_bar_manual_ssid_input']=side_bar_manual_ssid_input
        side_bar_manual_ssid_input.bind(focus=self.side_bar_manual_ssid_input_clear)

        side_bar_manual_security=MinimumBoundingLabel(
            text='[b][size=16]Security:',
            markup=True,
            size_hint=(None,None),
            pos_hint = {'right':.35, 'center_y':.55},)
        self.widgets['side_bar_manual_security']=side_bar_manual_security

        side_bar_manual_security_input=MarkupSpinner(
            disabled=False,
            text='[size=16]Enter Security Type',
            markup=True,
            values=('[b][size=16]None','[b][size=16]WEP','[b][size=16]WPA','[b][size=16]WPA2/WPA3'),
            size_hint =(.3, .05),
            pos_hint = {'x':.4, 'center_y':.55})
        self.widgets['side_bar_manual_security_input']=side_bar_manual_security_input
        side_bar_manual_security_input.bind(text=self.security_input_func)

        side_bar_manual_password=MinimumBoundingLabel(
            text='[b][size=16]Password:',
            markup=True,
            size_hint=(None,None),
            pos_hint = {'right':.35, 'center_y':.4},)
        self.widgets['side_bar_manual_password']=side_bar_manual_password

        side_bar_manual_password_input=TextInput(
            disabled=False,
            multiline=False,
            password=True,
            hint_text='Enter Network Password',
            size_hint =(.3, .05),
            pos_hint = {'x':.4, 'center_y':.4})
        self.widgets['side_bar_manual_password_input']=side_bar_manual_password_input
        side_bar_manual_password_input.bind(focus=self.side_bar_manual_password_input_clear)

        side_bar_manual_connect=RoundedButton(
            text='[b][size=16]All Fields Required',
            size_hint =(.425, .075),
            pos_hint = {'center_x':.5, 'center_y':.25},
            background_normal='',
            background_color=palette('secondary',1),
            disabled=True,
            disabled_color=palette('light_tint',1),
            markup=True)
        self.widgets['side_bar_manual_connect']=side_bar_manual_connect
        side_bar_manual_connect.bind(on_release=self.side_bar_manual_connect_func)
        side_bar_manual_connect.bind(disabled=self.side_bar_manual_connect_disabled)

        side_bar_known=ExpandableRoundedColorLayout(
            size_hint =(.9, .15),
            pos_hint = {'center_x':.5, 'center_y':.5},
            expanded_size=(5.143,1.185),
            expanded_pos = {'center_x':-1.785, 'center_y':.52},
            bg_color=palette('dark_shade',.85),)
        side_bar_known.widgets={}
        self.widgets['side_bar_known']=side_bar_known
        side_bar_known.bind(state=self.bg_color)
        side_bar_known.bind(expanded=self.side_bar_known_populate)
        side_bar_known.bind(expanded=self.get_known_networks)
        side_bar_known.bind(animating=partial(general.stripargs,side_bar_known.clear_widgets))

        side_bar_known_title=Label(
            text=current_language['side_bar_known_title'],
            markup=True,
            size_hint =(1, 1),
            pos_hint = {'center_x':.5, 'center_y':.5},)
        self.widgets['side_bar_known_title']=side_bar_known_title
        side_bar_known_title.ref='side_bar_known_title'

        side_bar_known_seperator=Image(
            source=gray_seperator_line,
            allow_stretch=True,
            keep_ratio=False,
            size_hint =(.9, .005),
            pos_hint = {'x':.05, 'y':.85})
        self.widgets['side_bar_known_seperator']=side_bar_known_seperator

        side_bar_known_expand_button=RoundedButton(
            size_hint =(.5, .075),
            pos_hint = {'center_x':.5, 'center_y':.075},
            background_down='',
            background_color=palette('light_tint',.9),
            markup=True)
        self.widgets['side_bar_known_expand_button']=side_bar_known_expand_button
        side_bar_known_expand_button.bind(on_release=self.side_bar_known_expand_button_func)

        side_bar_known_expand_lines=Image(
            source=settings_icon,
            allow_stretch=True,
            keep_ratio=False,
            size_hint =(.4, .035),
            pos_hint = {'center_x':.5, 'center_y':.075})
        side_bar_known_expand_lines.center=side_bar_known_expand_button.center
        self.widgets['side_bar_known_expand_lines']=side_bar_known_expand_lines

        side_bar_known_instructions=LabelColor(
            bg_color=palette('dark_shade',1),
            text=current_language['side_bar_known_instructions'],
            markup=True,
            size_hint =(.35, .4),
            pos_hint = {'center_x':.25, 'center_y':.5},)
        self.widgets['side_bar_known_instructions']=side_bar_known_instructions
        side_bar_known_instructions.ref='side_bar_known_instructions'

        with side_bar_known_instructions.canvas.after:
           side_bar_known_instructions.status_lines=Line(rounded_rectangle=(100, 100, 200, 200, 10, 10, 10, 10, 100))

        def update_lines(*args):
            x=int(side_bar_known_instructions.x)
            y=int(side_bar_known_instructions.y)
            width=int(side_bar_known_instructions.width*1)
            height=int(side_bar_known_instructions.height*1)
            side_bar_known_instructions.status_lines.rounded_rectangle=(x, y, width, height, 10, 10, 10, 10, 100)
        side_bar_known_instructions.bind(pos=update_lines, size=update_lines)

        side_bar_known_status_box=RoundedColorLayout(
            bg_color=palette('secondary',.85),
            size_hint =(.4, .6),
            pos_hint = {'center_x':.7, 'center_y':.5},)
        side_bar_known_status_box.widgets={}
        self.widgets['side_bar_known_status_box']=side_bar_known_status_box

        side_bar_known_status_title=Label(
            text=current_language['side_bar_known_network_status_title'],
            markup=True,
            size_hint =(.4, .05),
            pos_hint = {'center_x':.5, 'center_y':.925},)
        self.widgets['side_bar_known_status_title']=side_bar_known_status_title
        side_bar_known_status_title.ref='side_bar_known_network_status_title'

        side_bar_known_status_seperator=Image(
            source=gray_seperator_line,
            allow_stretch=True,
            keep_ratio=False,
            size_hint =(.9, .005),
            pos_hint = {'x':.05, 'y':.85})
        self.widgets['side_bar_known_status_seperator']=side_bar_known_status_seperator

        side_bar_known_status_scroll=OutlineScroll(
            size_hint =(.9,.75),
            pos_hint = {'center_x':.5, 'center_y':.45},
            bg_color=palette('light_tint',.15),
            bar_width=8,
            bar_color=palette('primary',.9),
            bar_inactive_color=palette('primary',.35),
            do_scroll_y=True,
            do_scroll_x=False)
        self.widgets['side_bar_known_status_scroll']=side_bar_known_status_scroll

        side_bar_known_status_scroll_layout = GridLayout(
            cols=1,
            spacing=10,
            size_hint_y=None,
            padding=5)
        self.widgets['side_bar_known_status_scroll_layout']=side_bar_known_status_scroll_layout
        # Make sure the height is such that there is something to scroll.
        side_bar_known_status_scroll_layout.bind(minimum_height=side_bar_known_status_scroll_layout.setter('height'))

        side_bar_auto=ExpandableRoundedColorLayout(
            size_hint =(.9, .15),
            pos_hint = {'center_x':.5, 'center_y':.3125},
            expanded_size=(5.143,1.185),
            expanded_pos = {'center_x':-1.785, 'center_y':.52},
            bg_color=palette('dark_shade',.85))
        self.widgets['side_bar_auto']=side_bar_auto
        side_bar_auto.bind(state=self.bg_color)
        side_bar_auto.bind(expanded=self.side_bar_auto_populate)
        side_bar_auto.bind(expanded=self.get_auto_networks)
        side_bar_auto.bind(animating=partial(general.stripargs,side_bar_auto.clear_widgets))

        side_bar_auto_title=Label(
            text=current_language['side_bar_auto_title'],
            markup=True,
            size_hint =(1, 1),
            pos_hint = {'center_x':.5, 'center_y':.5},)
        self.widgets['side_bar_auto_title']=side_bar_auto_title
        side_bar_auto_title.ref='side_bar_auto_title'

        side_bar_auto_seperator=Image(
            source=gray_seperator_line,
            allow_stretch=True,
            keep_ratio=False,
            size_hint =(.9, .005),
            pos_hint = {'x':.05, 'y':.85})
        self.widgets['side_bar_auto_seperator']=side_bar_auto_seperator

        side_bar_auto_expand_button=RoundedButton(
            size_hint =(.5, .075),
            pos_hint = {'center_x':.5, 'center_y':.075},
            background_down='',
            background_color=palette('light_tint',.9),
            markup=True)
        self.widgets['side_bar_auto_expand_button']=side_bar_auto_expand_button
        side_bar_auto_expand_button.bind(on_release=self.side_bar_auto_expand_button_func)

        side_bar_auto_expand_lines=Image(
            source=settings_icon,
            allow_stretch=True,
            keep_ratio=False,
            size_hint =(.4, .035),
            pos_hint = {'center_x':.5, 'center_y':.075})
        side_bar_auto_expand_lines.center=side_bar_auto_expand_button.center
        self.widgets['side_bar_auto_expand_lines']=side_bar_auto_expand_lines

        side_bar_auto_instructions=LabelColor(
            bg_color=palette('dark_shade',1),
            text=current_language['side_bar_auto_instructions'],
            markup=True,
            size_hint =(.3, .4),
            pos_hint = {'center_x':.25, 'center_y':.5},)
        self.widgets['side_bar_auto_instructions']=side_bar_auto_instructions
        side_bar_auto_instructions.ref='side_bar_auto_instructions'

        with side_bar_auto_instructions.canvas.after:
           side_bar_auto_instructions.status_lines=Line(rounded_rectangle=(100, 100, 200, 200, 10, 10, 10, 10, 100))

        def update_lines(*args):
            x=int(side_bar_auto_instructions.x)
            y=int(side_bar_auto_instructions.y)
            width=int(side_bar_auto_instructions.width*1)
            height=int(side_bar_auto_instructions.height*1)
            side_bar_auto_instructions.status_lines.rounded_rectangle=(x, y, width, height, 10, 10, 10, 10, 100)
        side_bar_auto_instructions.bind(pos=update_lines, size=update_lines)

        side_bar_auto_status_box=RoundedColorLayout(
            bg_color=palette('secondary',.85),
            size_hint =(.4, .6),
            pos_hint = {'center_x':.7, 'center_y':.5},)
        side_bar_auto_status_box.widgets={}
        self.widgets['side_bar_auto_status_box']=side_bar_auto_status_box

        side_bar_auto_status_title=Label(
            text=current_language['side_bar_auto_network_status_title'],
            markup=True,
            size_hint =(.4, .05),
            pos_hint = {'center_x':.5, 'center_y':.925},)
        self.widgets['side_bar_auto_status_title']=side_bar_auto_status_title
        side_bar_auto_status_title.ref='side_bar_auto_network_status_title'

        side_bar_auto_status_seperator=Image(
            source=gray_seperator_line,
            allow_stretch=True,
            keep_ratio=False,
            size_hint =(.9, .005),
            pos_hint = {'x':.05, 'y':.85})
        self.widgets['side_bar_auto_status_seperator']=side_bar_auto_status_seperator

        side_bar_auto_status_scroll=OutlineAutoScroll(
            size_hint =(.9,.75),
            pos_hint = {'center_x':.5, 'center_y':.45},
            bg_color=palette('light_tint',.15),
            bar_width=8,
            bar_color=palette('primary',.9),
            bar_inactive_color=palette('primary',.35),
            do_scroll_y=True,
            do_scroll_x=False,
            effect_cls=ScrollEffect)
        self.widgets['side_bar_auto_status_scroll']=side_bar_auto_status_scroll

        side_bar_auto_status_scroll_layout = GridLayout(
            cols=1,
            spacing=10,
            size_hint_y=None,
            padding=5)
        self.widgets['side_bar_auto_status_scroll_layout']=side_bar_auto_status_scroll_layout
        # Make sure the height is such that there is something to scroll.
        side_bar_auto_status_scroll_layout.bind(minimum_height=side_bar_auto_status_scroll_layout.setter('height'))

        side_bar_disconnect=ExpandableRoundedColorLayout(
            size_hint =(.9, .15),
            pos_hint = {'center_x':.5, 'center_y':.125},
            expanded_size=(5.143,1.185),
            expanded_pos = {'center_x':-1.785, 'center_y':.52},
            bg_color=palette('dark_shade',.85))
        self.widgets['side_bar_disconnect']=side_bar_disconnect
        side_bar_disconnect.widgets={}
        side_bar_disconnect.bind(state=self.bg_color)
        side_bar_disconnect.bind(expanded=self.side_bar_disconnect_populate)
        side_bar_disconnect.bind(animating=partial(general.stripargs,side_bar_disconnect.clear_widgets))

        side_bar_disconnect_title=Label(
            text=current_language['side_bar_disconnect_title'],
            markup=True,
            size_hint =(1, 1),
            pos_hint = {'center_x':.5, 'center_y':.5},)
        self.widgets['side_bar_disconnect_title']=side_bar_disconnect_title
        side_bar_disconnect_title.ref='side_bar_disconnect_title'

        side_bar_disconnect_seperator=Image(
            source=gray_seperator_line,
            allow_stretch=True,
            keep_ratio=False,
            size_hint =(.9, .005),
            pos_hint = {'x':.05, 'y':.85})
        self.widgets['side_bar_disconnect_seperator']=side_bar_disconnect_seperator

        side_bar_disconnect_expand_button=RoundedButton(
            size_hint =(.5, .075),
            pos_hint = {'center_x':.5, 'center_y':.075},
            background_down='',
            background_color=palette('light_tint',.9),
            markup=True)
        self.widgets['side_bar_disconnect_expand_button']=side_bar_disconnect_expand_button
        side_bar_disconnect_expand_button.bind(on_release=self.side_bar_disconnect_expand_button_func)

        side_bar_disconnect_expand_lines=Image(
            source=settings_icon,
            allow_stretch=True,
            keep_ratio=False,
            size_hint =(.4, .035),
            pos_hint = {'center_x':.5, 'center_y':.075})
        side_bar_disconnect_expand_lines.center=side_bar_disconnect_expand_button.center
        self.widgets['side_bar_disconnect_expand_lines']=side_bar_disconnect_expand_lines

        side_bar_disconnect_vertical_seperator=Image(
            source=gray_seperator_line_vertical,
            allow_stretch=True,
            keep_ratio=False,
            size_hint =(.0005, .4),
            pos_hint = {'center_x':.37, 'center_y':.55})
        self.widgets['side_bar_disconnect_vertical_seperator']=side_bar_disconnect_vertical_seperator

        side_bar_disconnect_temp=MinimumBoundingLabel(
            text='[b][size=16]Disconnect Temporarily:',
            markup=True,
            size_hint=(None,None),
            pos_hint = {'right':.35, 'center_y':.7},)
        self.widgets['side_bar_disconnect_temp']=side_bar_disconnect_temp

        side_bar_disconnect_temp_btn=RoundedButton(
            text='[b][size=16]Disconnect: ',
            size_hint =(.3, .05),
            pos_hint = {'x':.4, 'center_y':.7},
            background_down='',
            background_color=palette('accent',1),
            markup=True)
        self.widgets['side_bar_disconnect_temp_btn']=side_bar_disconnect_temp_btn
        side_bar_disconnect_temp_btn.bind(on_release=self.side_bar_disconnect_temp_btn_func)

        side_bar_disconnect_rmv=MinimumBoundingLabel(
            text='[b][size=16]Disconnect and Forget:',
            markup=True,
            size_hint=(None,None),
            pos_hint = {'right':.35, 'center_y':.55},)
        self.widgets['side_bar_disconnect_rmv']=side_bar_disconnect_rmv

        side_bar_disconnect_rmv_btn=RoundedButton(
            text='[b][size=16]Forget: ',
            size_hint =(.3, .05),
            pos_hint = {'x':.4, 'center_y':.55},
            background_down='',
            background_color=palette('highlight',.9),
            markup=True)
        self.widgets['side_bar_disconnect_rmv_btn']=side_bar_disconnect_rmv_btn
        side_bar_disconnect_rmv_btn.bind(on_release=self.side_bar_disconnect_rmv_btn_func)

        side_bar_disconnect_status=MinimumBoundingLabel(
            text='[b][size=16]Wi-Fi:',
            markup=True,
            size_hint=(None,None),
            pos_hint = {'right':.35, 'center_y':.4},)
        self.widgets['side_bar_disconnect_status']=side_bar_disconnect_status

        side_bar_disconnect_status_btn_on=RoundedToggleButton(
            group='networking',
            text='[b][size=16]On',
            markup=True,
            size_hint =(.125, .05),
            pos_hint = {'center_x':.475, 'center_y':.4},
            background_down='',
            background_color=palette('accent',1),
            second_color=palette('secondary',.85),
            allow_no_selection=False)
        self.widgets['side_bar_disconnect_status_btn_on']=side_bar_disconnect_status_btn_on
        side_bar_disconnect_status_btn_on.bind(state=self.set_network_status_file)

        side_bar_disconnect_status_btn_off=RoundedToggleButton(
            group='networking',
            text='[b][size=16]Off',
            markup=True,
            size_hint =(.125, .05),
            pos_hint = {'center_x':.625, 'center_y':.4},
            background_down='',
            background_color=palette('accent',1),
            second_color=palette('secondary',.85),
            allow_no_selection=False)
        self.widgets['side_bar_disconnect_status_btn_off']=side_bar_disconnect_status_btn_off
        side_bar_disconnect_status_btn_off.bind(state=self.set_network_status_file)

        side_bar_disconnect_lines_overlay=FloatLayout()
        self.widgets['side_bar_disconnect_lines_overlay']=side_bar_disconnect_lines_overlay

        with side_bar_disconnect_lines_overlay.canvas.after:
           side_bar_disconnect.status_lines=Line(rounded_rectangle=(100, 100, 200, 200, 10, 10, 10, 10, 100))

        def update_lines(*args):
            x=int(side_bar_disconnect.width*.457)
            y=int(side_bar_disconnect.height*.54)
            width=int(side_bar_disconnect.width*.3)
            height=int(side_bar_disconnect.height*.1)
            side_bar_disconnect.status_lines.rounded_rectangle=(x, y, width, height, 10, 10, 10, 10, 100)
        side_bar_disconnect.bind(pos=update_lines, size=update_lines)

        account_admin_hint=MinimumBoundingLabel(text=f"[size=18][color=#ffffff]Enable Admin mode to edit fields[/size]",
                color=palette('dark_shade',1),
                pos_hint = {'center_x':.5, 'y':.14},
                markup=True)
        self.widgets['account_admin_hint']=account_admin_hint

        seperator_line=Image(
            source=gray_seperator_line,
            allow_stretch=True,
            keep_ratio=False,
            size_hint =(.98, .001),
            pos_hint = {'x':.01, 'y':.13})


        information_box.add_widget(information_title)
        information_box.add_widget(information_seperator)
        information_box.add_widget(information_ssid)
        information_box.add_widget(information_status)
        information_box.add_widget(information_signal)
        information_box.add_widget(information_expand_button)
        information_box.add_widget(information_expand_lines)

        details_box.add_widget(details_title)
        details_box.add_widget(details_seperator)
        details_box.add_widget(details_expand_button)
        details_box.add_widget(details_expand_lines)
        details_box.add_widget(details_box_hint_text)

        details_connect_box.add_widget(details_password_label)
        details_connect_box.add_widget(details_password_label_seperator)
        details_connect_box.add_widget(details_password_interior_box)
        details_connect_box.add_widget(details_ssid_known)
        details_connect_box.add_widget(details_password)
        details_connect_box.add_widget(details_network_connect)

        status_box.add_widget(status_title)
        status_box.add_widget(status_seperator)
        status_box.add_widget(status_scroll)
        status_scroll.add_widget(status_scroll_layout)

        side_bar_box.add_widget(side_bar_scan)
        side_bar_box.add_widget(side_bar_disconnect)
        side_bar_box.add_widget(side_bar_known)
        side_bar_box.add_widget(side_bar_auto)
        side_bar_box.add_widget(side_bar_manual)

        side_bar_known_status_box.add_widget(side_bar_known_status_title)
        side_bar_known_status_box.add_widget(side_bar_known_status_seperator)
        side_bar_known_status_box.add_widget(side_bar_known_status_scroll)
        side_bar_known_status_scroll.add_widget(side_bar_known_status_scroll_layout)

        side_bar_auto_status_box.add_widget(side_bar_auto_status_title)
        side_bar_auto_status_box.add_widget(side_bar_auto_status_seperator)
        side_bar_auto_status_box.add_widget(side_bar_auto_status_scroll)
        side_bar_auto_status_scroll.add_widget(side_bar_auto_status_scroll_layout)

        side_bar_manual.add_widget(side_bar_manual_title)
        side_bar_known.add_widget(side_bar_known_title)
        side_bar_auto.add_widget(side_bar_auto_title)
        side_bar_disconnect.add_widget(side_bar_disconnect_title)

        self.add_widget(bg_image)
        self.add_widget(screen_name)
        self.add_widget(back)
        self.add_widget(back_main)
        self.add_widget(seperator_line)
        # self.add_widget(account_admin_hint)
        self.add_widget(information_box)
        self.add_widget(details_box)
        self.add_widget(status_box)
        self.add_widget(side_bar_box)

    def set_network_status(self,status):
        if self._network_switching.is_alive():
            return
        def f(*args):
            if status:
                network.connect_wifi()
                self.refresh_ap_data()
                self.side_bar_scan_func()
            else:
                network.disconnect_wifi()
                self.refresh_ap_data()
                self.side_bar_scan_func()
        self._network_switching=Thread(target=f,daemon=True)
        self._network_switching.start()
    def set_network_status_file(self,btn,val):
        if val == 'normal':
            return
        config=App.get_running_app().config_
        w=self.widgets
        on=w['side_bar_disconnect_status_btn_on']
        off=w['side_bar_disconnect_status_btn_off']
        status=True if btn == on else False
        self.set_network_status(status)
        config.set('network','status',str(status))
        with open(preferences_path,'w') as configfile:
                config.write(configfile)

    def bg_color(self,button,*args):
        if hasattr(button,'expanded'):
            if button.expanded:
                return
        if button.state=='normal':
            button.shape_color.rgba=palette('dark_shade',.9)
        if button.state=='down':
            button.shape_color.rgba=palette('primary',.15)
    def network_back(self,button):
        self.parent.transition = SlideTransition(direction='right')
        self.manager.current='preferences'
    def network_back_main(self,button):
        self.parent.transition = SlideTransition(direction='down')
        self.manager.current='main'
    def side_bar_scan_func(self,*args):
        if self._scan.is_alive():
            return
        bounce=Animation(size_hint=(1, .2),d=.0,t='out_back')+Animation(size_hint=(.9, .15),d=.15,t='out_back')
        bounce.start(self.widgets['side_bar_scan'])

        @mainthread
        def add_spinners():
            sb=self.widgets['status_box']
            self.widgets['status_scroll_layout'].clear_widgets()
            sb.add_widget(PreLoader(rel_size=.5,ref='1',speed=500))
            sb.add_widget(PreLoader(rel_size=.45,ref='2',speed=550))
            sb.add_widget(PreLoader(rel_size=.4,ref='3',speed=600))
            sb.add_widget(PreLoader(rel_size=.35,ref='4',speed=650))
            sb.add_widget(PreLoader(rel_size=.3,ref='5',speed=700))
            sb.add_widget(PreLoader(rel_size=.25,ref='6',speed=750))

        @mainthread
        def remove_spinners():
            sb=self.widgets['status_box']
            for i in range(6):
                sb.remove_widget(sb.widgets[str(i+1)])

        @mainthread
        def add_button(ssid):
            current=False
            prefix=''
            suffix=''
            func=self.get_details
            if network.get_ssid()==ssid:
                current=True
                prefix='>  '
                suffix='  <'
                func=self.widgets['information_box'].expand
            c=palette('accent',.85) if current else palette('secondary',1)
            btn = RoundedButton(
                background_normal='',
                background_color=c,
                text='[b][size=16]'+prefix+str(ssid)+suffix,
                markup=True,
                size_hint_y=None,
                height=40)
            btn.bind(on_release=partial(func,ssid))
            self.widgets['status_scroll_layout'].add_widget(btn)

        def scanning():
            add_spinners()
            for i in network.get_available().splitlines():
                if i:
                    add_button(i)
            remove_spinners()

        self._scan=Thread(target=scanning,daemon=True)
        self._scan.start()
    def information_box_populate(self,*args):
        information_box=self.widgets['information_box']
        darken=Animation(rgba=palette('dark_shade',.95))
        lighten=Animation(rgba=palette('dark_shade',.85))
        information_box.clear_widgets()
        if information_box.expanded:
            darken.start(information_box.shape_color)
            w=self.widgets
            w['information_ssid'].pos_hint={'x':.1, 'center_y':.8}
            w['information_status'].pos_hint={'x':.1, 'center_y':.75}
            w['information_signal'].pos_hint={'x':.1, 'center_y':.7}
            w['information_expand_button'].pos_hint={'center_x':.5, 'center_y':.075}
            w['information_expand_lines'].pos_hint={'center_x':.5, 'center_y':.075}
            w['information_expand_button'].size_hint=(.5, .075)
            w['information_expand_lines'].size_hint=(.4, .035)
            all_widgets=[
                w['information_title'],
                w['information_seperator'],
                w['information_ssid'],
                w['information_status'],
                w['information_signal'],
                w['information_expand_button'],
                w['information_expand_lines']]
            for i in all_widgets:
                information_box.add_widget(i)
        elif not information_box.expanded:
            lighten.start(information_box.shape_color)
            w=self.widgets
            w['information_ssid'].pos_hint={'x':.2, 'center_y':.725}
            w['information_status'].pos_hint={'x':.2, 'center_y':.55}
            w['information_signal'].pos_hint={'x':.2, 'center_y':.375}
            w['information_expand_button'].pos_hint={'center_x':.5, 'center_y':.15}
            w['information_expand_lines'].pos_hint={'center_x':.5, 'center_y':.15}
            w['information_expand_button'].size_hint=(.5, .175)
            w['information_expand_lines'].size_hint=(.4, .075)
            all_widgets=[
                w['information_title'],
                w['information_seperator'],
                w['information_ssid'],
                w['information_status'],
                w['information_signal'],
                w['information_expand_button'],
                w['information_expand_lines']]
            for i in all_widgets:
                information_box.add_widget(i)
    def details_box_populate(self,*args):
        details_box=self.widgets['details_box']
        darken=Animation(rgba=palette('dark_shade',.95))
        lighten=Animation(rgba=palette('dark_shade',.85))
        if details_box.expanded:
            darken.start(details_box.shape_color)
            w=self.widgets
            w['details_expand_button'].pos_hint={'center_x':.5, 'center_y':.075}
            w['details_expand_lines'].pos_hint={'center_x':.5, 'center_y':.075}
            w['details_expand_button'].size_hint=(.5, .075)
            w['details_expand_lines'].size_hint=(.4, .035)
            all_widgets=[
                w['details_title'],
                w['details_seperator'],
                w['details_expand_button'],
                w['details_expand_lines'],
                w['details_ssid'],
                w['details_signal'],
                w['details_security'],
                w['details_connect_box']]
            for i in all_widgets:
                details_box.add_widget(i)
        elif not details_box.expanded:
            lighten.start(details_box.shape_color)
            w=self.widgets
            w['details_expand_button'].pos_hint={'center_x':.5, 'center_y':.15}
            w['details_expand_lines'].pos_hint={'center_x':.5, 'center_y':.15}
            w['details_expand_button'].size_hint=(.5, .125)
            w['details_expand_lines'].size_hint=(.4, .0525)
            w['details_ssid'].text='[b][size=16]        SSID:'
            w['details_signal'].text='[b][size=16]     Signal:'
            w['details_security'].text='[b][size=16]Security:'
            pw=w['details_password']
            pw.text=''
            pw.disabled=True
            w['details_network_connect'].disabled=True
            w['details_ssid_known'].opacity=0
            all_widgets=[
                w['details_title'],
                w['details_seperator'],
                w['details_expand_button'],
                w['details_expand_lines'],
                w['details_box_hint_text']]
            for i in all_widgets:
                details_box.add_widget(i)
    def side_bar_manual_populate(self,*args):
        sbm_parent=self.widgets['side_bar_box']
        darken=Animation(rgba=palette('dark_shade',.95))
        lighten=Animation(rgba=palette('dark_shade',.85))
        side_bar_manual=self.widgets['side_bar_manual']
        side_bar_manual.clear_widgets()
        if side_bar_manual.expanded:
            self.remove_widget(sbm_parent)
            self.add_widget(sbm_parent)#needed to draw children on top
            darken.start(side_bar_manual.shape_color)
            w=self.widgets
            w['side_bar_manual_title'].pos_hint={'center_x':.5, 'center_y':.925}
            w['side_bar_manual_title'].size_hint=(.4, .05)
            w['side_bar_manual_ssid_input'].text=''
            w['side_bar_manual_security_input'].text='[b][size=16]Enter Security Type'
            w['side_bar_manual_password_input'].text=''
            all_widgets=[
                w['side_bar_manual_title'],
                w['side_bar_manual_seperator'],
                w['side_bar_manual_expand_button'],
                w['side_bar_manual_expand_lines'],
                w['side_bar_manual_ssid'],
                w['side_bar_manual_ssid_input'],
                w['side_bar_manual_security'],
                w['side_bar_manual_security_input'],
                w['side_bar_manual_password'],
                w['side_bar_manual_password_input'],
                w['side_bar_manual_vertical_seperator'],
                w['side_bar_manual_connect']]
            for i in all_widgets:
                side_bar_manual.add_widget(i)
        elif not side_bar_manual.expanded:
            lighten.start(side_bar_manual.shape_color)
            w=self.widgets
            w['side_bar_manual_title'].pos_hint={'center_x':.5, 'center_y':.5}
            w['side_bar_manual_title'].size_hint=(1,1)
            all_widgets=[
                w['side_bar_manual_title']]
            for i in all_widgets:
                side_bar_manual.add_widget(i)
    def side_bar_known_populate(self,*args):
        sbn_parent=self.widgets['side_bar_box']
        darken=Animation(rgba=palette('dark_shade',.95))
        lighten=Animation(rgba=palette('dark_shade',.85))
        side_bar_known=self.widgets['side_bar_known']
        side_bar_known.clear_widgets()
        if side_bar_known.expanded:
            self.remove_widget(sbn_parent)
            self.add_widget(sbn_parent)#needed to draw children on top
            darken.start(side_bar_known.shape_color)
            w=self.widgets
            w['side_bar_known_title'].pos_hint={'center_x':.5, 'center_y':.925}
            w['side_bar_known_title'].size_hint=(.4, .05)
            all_widgets=[
                w['side_bar_known_title'],
                w['side_bar_known_seperator'],
                w['side_bar_known_expand_button'],
                w['side_bar_known_expand_lines'],
                w['side_bar_known_instructions'],
                w['side_bar_known_status_box']]
            for i in all_widgets:
                side_bar_known.add_widget(i)
        elif not side_bar_known.expanded:
            lighten.start(side_bar_known.shape_color)
            w=self.widgets
            w['side_bar_known_title'].pos_hint={'center_x':.5, 'center_y':.5}
            w['side_bar_known_title'].size_hint=(1,1)
            all_widgets=[
                w['side_bar_known_title']]
            for i in all_widgets:
                side_bar_known.add_widget(i)
    def side_bar_auto_populate(self,*args):
        sba_parent=self.widgets['side_bar_box']
        darken=Animation(rgba=palette('dark_shade',.95))
        lighten=Animation(rgba=palette('dark_shade',.85))
        side_bar_auto=self.widgets['side_bar_auto']
        side_bar_auto.clear_widgets()
        if side_bar_auto.expanded:
            self.remove_widget(sba_parent)
            self.add_widget(sba_parent)#needed to draw children on top
            darken.start(side_bar_auto.shape_color)
            w=self.widgets
            w['side_bar_auto_title'].pos_hint={'center_x':.5, 'center_y':.925}
            w['side_bar_auto_title'].size_hint=(.4, .05)
            all_widgets=[
                w['side_bar_auto_title'],
                w['side_bar_auto_seperator'],
                w['side_bar_auto_expand_button'],
                w['side_bar_auto_expand_lines'],
                w['side_bar_auto_instructions'],
                w['side_bar_auto_status_box']]
            for i in all_widgets:
                side_bar_auto.add_widget(i)
        elif not side_bar_auto.expanded:
            lighten.start(side_bar_auto.shape_color)
            w=self.widgets
            w['side_bar_auto_title'].pos_hint={'center_x':.5, 'center_y':.5}
            w['side_bar_auto_title'].size_hint=(1,1)
            all_widgets=[
                w['side_bar_auto_title']]
            for i in all_widgets:
                side_bar_auto.add_widget(i)
    def side_bar_disconnect_populate(self,*args):
        config=App.get_running_app().config_
        if not config.has_option('network','status'):
                config.add_section('network')
                config.set('network','status','True')
        status=App.get_running_app().config_.getboolean('network','status')
        sbd_parent=self.widgets['side_bar_box']
        darken=Animation(rgba=palette('dark_shade',.95))
        lighten=Animation(rgba=palette('dark_shade',.85))
        side_bar_disconnect=self.widgets['side_bar_disconnect']
        side_bar_disconnect.clear_widgets()
        if side_bar_disconnect.expanded:
            self.remove_widget(sbd_parent)
            self.add_widget(sbd_parent)#needed to draw children on top
            darken.start(side_bar_disconnect.shape_color)
            w=self.widgets
            if status:
                w['side_bar_disconnect_status_btn_on'].state='down'
                w['side_bar_disconnect_status_btn_off'].state='normal'
            else:
                w['side_bar_disconnect_status_btn_on'].state='normal'
                w['side_bar_disconnect_status_btn_off'].state='down'
            w['side_bar_disconnect_title'].pos_hint={'center_x':.5, 'center_y':.925}
            w['side_bar_disconnect_title'].size_hint=(.4, .05)
            w['side_bar_disconnect_temp_btn'].text=f'[b][size=16]Disconnect: [size=20][u]{network.get_ssid()}'
            w['side_bar_disconnect_rmv_btn'].text=f'[b][size=16]Forget: [size=20][u]{network.get_ssid()}'
            all_widgets=[
                w['side_bar_disconnect_title'],
                w['side_bar_disconnect_seperator'],
                w['side_bar_disconnect_expand_button'],
                w['side_bar_disconnect_expand_lines'],
                w['side_bar_disconnect_temp'],
                w['side_bar_disconnect_temp_btn'],
                w['side_bar_disconnect_rmv'],
                w['side_bar_disconnect_rmv_btn'],
                w['side_bar_disconnect_status'],
                w['side_bar_disconnect_status_btn_on'],
                w['side_bar_disconnect_status_btn_off'],
                w['side_bar_disconnect_vertical_seperator'],
                w['side_bar_disconnect_lines_overlay']]
            for i in all_widgets:
                side_bar_disconnect.add_widget(i)
        elif not side_bar_disconnect.expanded:
            lighten.start(side_bar_disconnect.shape_color)
            w=self.widgets
            w['side_bar_disconnect_title'].pos_hint={'center_x':.5, 'center_y':.5}
            w['side_bar_disconnect_title'].size_hint=(1,1)
            all_widgets=[
                w['side_bar_disconnect_title']]
            for i in all_widgets:
                side_bar_disconnect.add_widget(i)
    def information_expand_button_func(self,*args):
        ib=self.widgets['information_box']
        if ib.expanded:
            ib.shrink()
        if not ib.expanded:
            ib.expand()
    def details_expand_button_func(self,*args):
        db=self.widgets['details_box']
        if db.expanded:
            db.shrink()
        if not db.expanded:
            db.expand()
    def side_bar_manual_expand_button_func(self,*args):
        sbm=self.widgets['side_bar_manual']
        if sbm.expanded:
            sbm.shrink()
        if not sbm.expanded:
            sbm.expand()
    def side_bar_known_expand_button_func(self,*args):
        sbn=self.widgets['side_bar_known']
        if sbn.expanded:
            sbn.shrink()
        if not sbn.expanded:
            sbn.expand()
    def side_bar_auto_expand_button_func(self,*args):
        sba=self.widgets['side_bar_auto']
        if sba.expanded:
            sba.shrink()
        if not sba.expanded:
            sba.expand()
    def side_bar_disconnect_expand_button_func(self,*args):
        sbd=self.widgets['side_bar_disconnect']
        if sbd.expanded:
            sbd.shrink()
        if not sbd.expanded:
            sbd.expand()

    def side_bar_disconnect_temp_btn_func(self,*args):
        if self._disconnect_temp.is_alive():
            return

        @mainthread
        def add_spinners():
            db=self.widgets['side_bar_disconnect']
            db.add_widget(PreLoader(rel_size=.3,ref='1',speed=500))
            db.add_widget(PreLoader(rel_size=.25,ref='2',speed=850))
            db.add_widget(PreLoader(rel_size=.2,ref='3',speed=600))
            db.add_widget(PreLoader(rel_size=.15,ref='4',speed=950))
            db.add_widget(PreLoader(rel_size=.1,ref='5',speed=700))
            db.add_widget(PreLoader(rel_size=.05,ref='6',speed=1050))

        @mainthread
        def remove_spinners():
            db=self.widgets['side_bar_disconnect']
            for i in range(6):
                if str(i+1) in db.widgets:
                    db.remove_widget(db.widgets[str(i+1)])

        @mainthread
        def  _refresh_btn_text():
            w=self.widgets
            tmp=w['side_bar_disconnect_temp_btn']
            tmp.text='[b][size=16]Disconnect: '

        def _disconnect():
            db=self.widgets['side_bar_disconnect']
            add_spinners()
            if network.get_ssid():
                network.disconnect_ssid(network.get_ssid())
                _refresh_btn_text()
            remove_spinners()
            self.refresh_ap_data()
            self.side_bar_scan_func()

        self._disconnect_temp=Thread(target=_disconnect,daemon=True)
        self._disconnect_temp.start()

    def side_bar_disconnect_rmv_btn_func(self,*args):
        if self._disconnect_rmv.is_alive():
            return

        @mainthread
        def add_spinners():
            db=self.widgets['side_bar_disconnect']
            db.add_widget(PreLoader(rel_size=.3,ref='1',speed=500))
            db.add_widget(PreLoader(rel_size=.25,ref='2',speed=850))
            db.add_widget(PreLoader(rel_size=.2,ref='3',speed=600))
            db.add_widget(PreLoader(rel_size=.15,ref='4',speed=950))
            db.add_widget(PreLoader(rel_size=.1,ref='5',speed=700))
            db.add_widget(PreLoader(rel_size=.05,ref='6',speed=1050))

        @mainthread
        def remove_spinners():
            db=self.widgets['side_bar_disconnect']
            for i in range(6):
                if str(i+1) in db.widgets:
                    db.remove_widget(db.widgets[str(i+1)])

        @mainthread
        def  _refresh_btn_text():
            w=self.widgets
            tmp=w['side_bar_disconnect_temp_btn']
            tmp.text='[b][size=16]Disconnect: '
            rmv=w['side_bar_disconnect_rmv_btn']
            rmv.text='[b][size=16]Forget: '

        def _forget():
            db=self.widgets['side_bar_disconnect']
            add_spinners()
            if network.get_ssid():
                network.remove_profile(network.get_ssid())
                _refresh_btn_text()
            remove_spinners()
            self.refresh_ap_data()
            self.side_bar_scan_func()

        self._disconnect_rmv=Thread(target=_forget,daemon=True)
        self._disconnect_rmv.start()

    def details_network_connect_func(self,*args):
        if self._details_connecting.is_alive():
            return

        @mainthread
        def add_spinners():
            db=self.widgets['details_box']
            db.add_widget(PreLoader(rel_size=.3,ref='1',speed=500))
            db.add_widget(PreLoader(rel_size=.25,ref='2',speed=850))
            db.add_widget(PreLoader(rel_size=.2,ref='3',speed=600))
            db.add_widget(PreLoader(rel_size=.15,ref='4',speed=950))
            db.add_widget(PreLoader(rel_size=.1,ref='5',speed=700))
            db.add_widget(PreLoader(rel_size=.05,ref='6',speed=1050))

        @mainthread
        def remove_spinners():
            db=self.widgets['details_box']
            for i in range(6):
                if str(i+1) in db.widgets:
                    db.remove_widget(db.widgets[str(i+1)])

        @mainthread
        def set_toast_msg(text,level):
            App.get_running_app().notifications.toast(text,level)

        def _connect():
            db=self.widgets['details_box']
            pw=self.widgets['details_password'].text
            ssid=self._details_ssid
            add_spinners()
            if ssid in network.get_known().splitlines():
                success=network.connect_to_saved(ssid)
            else:success=network.connect_to(ssid,pw)
            remove_spinners()
            self.refresh_ap_data()
            self.side_bar_scan_func()
            if success:
                set_toast_msg('[b][size=20]Connection Successful','info')
                db.shrink()
                self.widgets['details_password'].text=''
            else:
                set_toast_msg('[b][size=20]Connection Failed','error')
                if not ssid in network.get_known().splitlines():
                    self.widgets['details_password'].text=''

        self._known_connecting=Thread(target=_connect,daemon=True)
        self._known_connecting.start()

    def side_bar_manual_connect_func(self,*args):
        if self._manual_connecting.is_alive():
            return

        @mainthread
        def add_spinners():
            sbm=self.widgets['side_bar_manual']
            sbm.add_widget(PreLoader(rel_size=.3,ref='1',speed=500))
            sbm.add_widget(PreLoader(rel_size=.25,ref='2',speed=850))
            sbm.add_widget(PreLoader(rel_size=.2,ref='3',speed=600))
            sbm.add_widget(PreLoader(rel_size=.15,ref='4',speed=950))
            sbm.add_widget(PreLoader(rel_size=.1,ref='5',speed=700))
            sbm.add_widget(PreLoader(rel_size=.05,ref='6',speed=1050))

        @mainthread
        def remove_spinners():
            sbm=self.widgets['side_bar_manual']
            for i in range(6):
                if str(i+1) in sbm.widgets:
                    sbm.remove_widget(sbm.widgets[str(i+1)])

        @mainthread
        def set_toast_msg(text,level):
            App.get_running_app().notifications.toast(text,level)

        def _connect():
            sbm=self.widgets['side_bar_manual']
            add_spinners()
            success=network.connect_to(self.widgets['side_bar_manual_ssid_input'].text,self.widgets['side_bar_manual_password_input'].text)
            remove_spinners()
            self.refresh_ap_data()
            self.side_bar_scan_func()
            if success:
                set_toast_msg('[b][size=20]Connection Successful','info')
                sbm.shrink()
            else:
                set_toast_msg('[b][size=20]Connection Failed','error')
                w=self.widgets
                w['side_bar_manual_ssid_input'].text=''
                w['side_bar_manual_security_input'].text='[b][size=16]Enter Security Type'
                w['side_bar_manual_password_input'].text=''

        self._manual_connecting=Thread(target=_connect,daemon=True)
        self._manual_connecting.start()

    def get_details(self,ssid,*args):
        self.details_expand_button_func()
        if self._ssid_details.is_alive():
            return

        @mainthread
        def add_spinners():
            db=self.widgets['details_box']
            db.add_widget(PreLoader(rel_pos=(.2,.75),rel_size=.075,ref='1',speed=500))
            db.add_widget(PreLoader(rel_pos=(.2,.75),rel_size=.0625,ref='2',speed=850))
            db.add_widget(PreLoader(rel_pos=(.2,.75),rel_size=.05,ref='3',speed=600))
            db.add_widget(PreLoader(rel_pos=(.2,.75),rel_size=.0375,ref='4',speed=950))
            db.add_widget(PreLoader(rel_pos=(.2,.75),rel_size=.025,ref='5',speed=700))
            db.add_widget(PreLoader(rel_pos=(.2,.75),rel_size=.0125,ref='6',speed=1050))

        @mainthread
        def remove_spinners():
            db=self.widgets['details_box']
            for i in range(6):
                if str(i+1) in db.widgets:
                    db.remove_widget(db.widgets[str(i+1)])

        @mainthread
        def clear_details():
            self.widgets['details_ssid'].text='[b][size=16]      SSID:'
            self.widgets['details_signal'].text='[b][size=16]   Signal:'
            self.widgets['details_security'].text='[b][size=16]Security:'

        @mainthread
        def set_details(ssid,signal,security):
            self.widgets['details_ssid'].text='[b][size=16]'+ssid
            self.widgets['details_signal'].text='[b][size=16]'+signal
            self.widgets['details_security'].text='[b][size=16]'+security

        @mainthread
        def set_pw_hidden():
            pw=self.widgets['details_password']
            pw.text='**********'
            pw.disabled=True
            self.widgets['details_network_connect'].disabled=False
            self.widgets['details_ssid_known'].opacity=1

        @mainthread
        def set_pw_blank():
            pw=self.widgets['details_password']
            pw.text=''
            pw.disabled=False
            self.widgets['details_network_connect'].disabled=False
            self.widgets['details_ssid_known'].opacity=0

        def _details(ssid,*args):
            self._details_ssid=ssid
            clear_details()
            add_spinners()
            if ssid in network.get_known().splitlines() and not ssid=='':
                set_pw_hidden()
            else:
                set_pw_blank()
            entry_len=30
            ssid=f'      SSID: {ssid}'
            signal=f'   Signal: {network.get_signal()}/100'
            security=f'Security: {network.get_security()}'
            while len(ssid)<entry_len:
                ssid=ssid[:11]+' '+ssid[11:]
            if len(ssid)>entry_len:
                ssid=ssid[:28]+'...'
            while len(signal)<entry_len:
                signal=signal[:11]+' '+signal[11:]
            while len(security)<entry_len:
                security=security[:10]+' '+security[10:]

            set_details(ssid,signal,security)
            remove_spinners()
        self._ssid_details=Thread(target=_details,daemon=True,args=(ssid,))
        self._ssid_details.start()

    def known_connect_func(self,profile,*args):
        if self._known_connecting.is_alive():
            return

        @mainthread
        def add_spinners():
            sbk=self.widgets['side_bar_known']
            sbk.add_widget(PreLoader(rel_size=.3,ref='1',speed=500))
            sbk.add_widget(PreLoader(rel_size=.25,ref='2',speed=850))
            sbk.add_widget(PreLoader(rel_size=.2,ref='3',speed=600))
            sbk.add_widget(PreLoader(rel_size=.15,ref='4',speed=950))
            sbk.add_widget(PreLoader(rel_size=.1,ref='5',speed=700))
            sbk.add_widget(PreLoader(rel_size=.05,ref='6',speed=1050))

        @mainthread
        def remove_spinners():
            sbk=self.widgets['side_bar_known']
            for i in range(6):
                if str(i+1) in sbk.widgets:
                    sbk.remove_widget(sbk.widgets[str(i+1)])

        @mainthread
        def set_toast_msg(text,level):
            App.get_running_app().notifications.toast(text,level)

        def _connect(profile):
            sbk=self.widgets['side_bar_known']
            if 'menu_bubble' in self.widgets:
                self.remove_widget(self.widgets['menu_bubble'])
            add_spinners()
            success=network.connect_to_saved(profile)
            remove_spinners()
            self.refresh_ap_data()
            self.side_bar_scan_func()
            if success:
                set_toast_msg('[b][size=20]Connection Successful','info')
                sbk.shrink()
            else:
                set_toast_msg('[b][size=20]Connection Failed','warning')

        self._known_connecting=Thread(target=_connect,daemon=True,args=(profile,))
        self._known_connecting.start()

    def remove_known_profile_func(self,profile,*args):
        if self._known_removing.is_alive():
            return

        @mainthread
        def add_spinners():
            sbk=self.widgets['side_bar_known']
            sbk.add_widget(PreLoader(rel_size=.3,ref='1',speed=500))
            sbk.add_widget(PreLoader(rel_size=.25,ref='2',speed=850))
            sbk.add_widget(PreLoader(rel_size=.2,ref='3',speed=600))
            sbk.add_widget(PreLoader(rel_size=.15,ref='4',speed=950))
            sbk.add_widget(PreLoader(rel_size=.1,ref='5',speed=700))
            sbk.add_widget(PreLoader(rel_size=.05,ref='6',speed=1050))

        @mainthread
        def remove_spinners():
            sbk=self.widgets['side_bar_known']
            for i in range(6):
                if str(i+1) in sbk.widgets:
                    sbk.remove_widget(sbk.widgets[str(i+1)])

        @mainthread
        def set_toast_msg(text,level):
            App.get_running_app().notifications.toast(text,level)

        def _remove(profile):
            sbk=self.widgets['side_bar_known']
            if 'menu_bubble' in self.widgets:
                self.remove_widget(self.widgets['menu_bubble'])
            add_spinners()
            success=network.remove_profile(profile)
            if success:
                set_toast_msg(f'[b][size=20]Removed Connection:\n        {profile}','info')
                self.refresh_ap_data()
                self.side_bar_scan_func()
                self.get_known_networks()
            else:
                set_toast_msg(f'[b][size=20]Failed to remove connection:\n            {profile}','warning')
            remove_spinners()

        self._known_removing=Thread(target=_remove,daemon=True,args=(profile,))
        self._known_removing.start()

    def swap_to_details(self,profile,btn,*args):
        btn.parent.parent.clear()  #gets the ScrollBubbleMenu to clear
        self.side_bar_known_expand_button_func()
        if network.get_ssid()==profile:
            self.widgets['information_box'].expand()
        else:self.get_details(profile)

    def get_known_networks(self,*args):
        if self._known_networks.is_alive():
            return

        def add_bubble(profile,button):
            scroll=self.widgets['side_bar_known_status_scroll']
            cnct=BubbleButton(markup=True,text='[b][size=18]Connect',size_hint_y=.3,background_color=palette('accent',1))
            cnct.bind(on_release=partial(self.known_connect_func,profile))
            rmv=BubbleButton(markup=True,text='[b][size=18]Forget',size_hint_y=.2,background_color=palette('highlight',1))
            rmv.bind(on_release=partial(self.remove_known_profile_func,profile))
            dtl=BubbleButton(markup=True,text='[b][size=18]Details',size_hint_y=.2)
            dtl.bind(on_release=partial(self.swap_to_details,profile))

            b=ScrollMenuBubble(
                button,
                scroll,
                orientation='vertical',
                spacing=[0,100],
                arrow_pos='right_mid',
                size_hint =(.5,7.5),
                pos_hint = {'right':0, 'center_y':.5},
                background_image=opaque_bubble,
                background_color=palette('secondary',1))

            b.add_widget(cnct)
            b.add_widget(rmv)
            b.add_widget(dtl)
            self.add_widget(b)

        @mainthread
        def add_button(profile):
            btn = RoundedButton(
                    background_normal='',
                    background_color=palette('secondary',1),
                    text='[b][size=16]'+str(profile),
                    markup=True,
                    size_hint_y=None,
                    height=40)
            btn.bind(on_release=partial(add_bubble,profile))
            self.widgets['side_bar_known_status_scroll_layout'].add_widget(btn)

        @mainthread
        def _clear_widgets(self):
            self.widgets['side_bar_known_status_scroll_layout'].clear_widgets()

        def _known():
            _clear_widgets(self)
            for i in network.get_known().splitlines():
                add_button(i)
        self._known_networks=Thread(target=_known,daemon=True)
        self._known_networks.start()

    def get_auto_networks(self,*args):
        if self._auto_networks.is_alive():
            return

        @mainthread
        def add_button(profile,index):
            layout=self.widgets['side_bar_auto_status_scroll_layout']
            btn = DraggableRoundedLabelColor(
                index=index,
                bg_color=palette('secondary',1),
                text=f'[b][size=16]{str(profile)}',
                markup=True,
                size_hint_y=None,
                height=40,
                func=partial(self._set_priority,profile))
            layout.add_widget(btn,len(layout.children))

        @mainthread
        def _clear_children():
            self.widgets['side_bar_auto_status_scroll_layout'].clear_widgets()

        def _auto():
            _clear_children()
            for index,profile in enumerate(reversed(network.get_profiles_by_priority().splitlines())):
                if os.name=='posix':
                    profile = profile.split(':',1)[1]
                add_button(profile,index)
        self._auto_networks=Thread(target=_auto,daemon=True,)
        self._auto_networks.start()

    def _set_priority(self,profile,*args):
        print('werk')
        return
        if self._priority_setting.is_alive():
            return
        priority=0
        def f(*args):
            network.set_profile_priority(profile,priority)
        self._priority_setting=Thread(target=f,daemon=True)
        self._priority_setting.start()

    def check_admin_mode(self,*args):
        if App.get_running_app().admin_mode_start>time.time():
            pass

    def refresh_ap_data(self,*args):
        if self._scan.is_alive():
            return

        @mainthread
        def set_labels(ssid,status,signal):
            self.widgets['information_ssid'].text='[b][size=16]'+ssid
            self.widgets['information_status'].text='[b][size=16]'+status
            self.widgets['information_signal'].text='[b][size=16]'+signal

        def refreshing():
            entry_len=30
            ssid=f'   SSID: {network.get_ssid()}'
            status=f'Status: {network.get_status()}'
            if network.is_connected():
                signal=f'Signal: {network.get_signal()}/100'
            else:signal=f'Signal: {network.get_signal()}'
            while len(ssid)<entry_len:
                ssid=ssid[:8]+' '+ssid[8:]
            if len(ssid)>entry_len:
                ssid=ssid[:28]+'...'
            while len(status)<entry_len:
                status=status[:8]+' '+status[8:]
            while len(signal)<entry_len:
                signal=signal[:8]+' '+signal[8:]

            set_labels(ssid,status,signal)

        self._refresh_ap=Thread(target=refreshing,daemon=True)
        self._refresh_ap.start()

    def details_network_connect_disabled(self,button,disabled,*args):
        if  button.disabled:
            button.background_down='None'
            button.background_normal=''
            button.text='[b][size=16]Password Required'
        elif not button.disabled:
            button.background_down=''
            button.background_normal='None'
            button.text='[b][size=16]Connect to Network'
        button.color_swap()

    def side_bar_manual_connect_disabled(self,button,disabled,*args):
        if  button.disabled:
            button.text='[b][size=16]All Fields Required'
        elif not button.disabled:
            button.text='[b][size=16]Connect to Network'
        button.color_swap()

    def details_password_clear_text(self,button,focused,*args):
        pi=self.widgets['details_password']
        p=pi.parent
        if p: p.remove_widget(pi)
        if focused:
            self.widgets['details_box'].add_widget(pi)
            self.widgets['details_password'].text=''
            pi.font_size=32
            pi.pos_hint={'center_x':.5, 'center_y':.6}
            pi.size_hint=(.8, .1)
        else:
            self.widgets['details_connect_box'].add_widget(pi)
            pi.font_size=15
            pi.pos_hint={'center_x':.5, 'center_y':.5}
            pi.size_hint=(.8, .1)

    def manual_connect_disable_func(self,*args):
        con_btn=self.widgets['side_bar_manual_connect']
        si=self.widgets['side_bar_manual_ssid_input']
        security_input=self.widgets['side_bar_manual_security_input']
        pi=self.widgets['side_bar_manual_password_input']
        if (si.text!='' and security_input.text!='[b][size=16]Enter Security Type' and pi.text!=''):
            con_btn.disabled=False
            con_btn.bg_color=palette('accent',1)
            con_btn.color_swap()
        else:
            con_btn.disabled=True
            con_btn.bg_color=palette('secondary',1)
            con_btn.color_swap()

    def side_bar_manual_password_input_clear(self,button,focused,*args):
        pi=self.widgets['side_bar_manual_password_input']
        p=pi.parent
        if p:
            p.remove_widget(pi)
            p.add_widget(pi)
        if focused:
            pi.text=''
            pi.font_size=32
            pi.pos_hint={'center_x':.5, 'center_y':.6}
            pi.size_hint=(.8, .1)
        else:
            pi.font_size=15
            pi.pos_hint={'x':.4, 'center_y':.4}
            pi.size_hint=(.3, .05)
        self.manual_connect_disable_func()

    def security_input_func(self,button,*args):
        self.manual_connect_disable_func()

    def side_bar_manual_ssid_input_clear(self,button,focused,*args):
        si=self.widgets['side_bar_manual_ssid_input']
        p=si.parent
        if p:
            p.remove_widget(si)
            p.add_widget(si)
        if focused:
            si.text=''
            si.font_size=32
            si.pos_hint={'center_x':.5, 'center_y':.6}
            si.size_hint=(.8, .1)
        else:
            si.font_size=15
            si.pos_hint={'x':.4, 'center_y':.7}
            si.size_hint=(.3, .05)
        self.manual_connect_disable_func()

    def on_pre_enter(self, *args):
        # self.check_admin_mode()
        self.refresh_event=Clock.schedule_interval(self.refresh_ap_data,5)
        Clock.schedule_once(self.refresh_ap_data)
        Clock.schedule_once(self.side_bar_scan_func)
        return super().on_pre_enter(*args)

    def on_leave(self, *args):
        self.refresh_event.cancel()
        self.widgets['information_box'].shrink()
        self.widgets['details_box'].shrink()
        return super().on_leave(*args)

class AnalyticScreen(Screen):
    def __init__(self, **kwargs):
        super(AnalyticScreen,self).__init__(**kwargs)
        self.cols = 2
        self.widgets={}
        self.scheduled_funcs=[]
        bg_image = Image(source=background_image, allow_stretch=True, keep_ratio=False)
        white_filter=Image(source=white_gradient, allow_stretch=True, keep_ratio=False)
        white_filter.opacity=.825

        back=RoundedButton(
            text="[size=50][b][color=#cccccc]  Back [/color][/b][/size]",
            size_hint =(.4, .1),
            pos_hint = {'x':.06, 'y':.015},
            background_down='',
            background_color=palette('dark_shade',1),
            markup=True)
        self.widgets['back']=back
        # back.ref='settings_back'
        back.bind(on_release=self.account_back)

        back_main=RoundedButton(
            text=current_language['preferences_back_main'],
            size_hint =(.4, .1),
            pos_hint = {'x':.52, 'y':.015},
            background_normal='',
            background_color=palette('primary',.9),
            markup=True)
        self.widgets['back_main']=back_main
        back_main.ref='preferences_back_main'
        back_main.bind(on_release=self.account_back_main)

        screen_name=Label(
            text=current_language['analytic_screen_name'],
            markup=True,
            size_hint =(.4, .05),
            pos_hint = {'center_x':.15, 'center_y':.925},)
        self.widgets['screen_name']=screen_name
        screen_name.ref='analytic_screen_name'

        details_box=RoundedColorLayout(
            bg_color=palette('dark_shade',.85),
            size_hint =(.775, .675),
            pos_hint = {'x':.025, 'center_y':.52},)
        self.widgets['details_box']=details_box

        details_title=Label(
            text="[size=28][color=#ffffff][b]Details",
            markup=True,
            size_hint =(.5, .05),
            pos_hint = {'center_x':.5, 'center_y':.925},)
        self.widgets['details_title']=details_title
        details_title.ref='details_title'

        details_hint=ExpandableRoundedColorLayout(
            size_hint =(.05, .1),
            pos_hint = {'x':.05, 'y':.875},
            expanded_size=(.98,.98),
            expanded_pos={'x':.01,'y':.01},
            bg_color=palette('light_tint',.8))
        details_hint.widgets={}
        self.widgets['details_hint']=details_hint
        details_hint.bind(state=self.bg_color_white)
        details_hint.bind(expanded=self.details_hint_populate)
        details_hint.bind(animating=partial(general.stripargs,details_hint.clear_widgets))

        details_hint_title=Label(
            text="[size=38][color=#000000][b]?",
            markup=True,
            size_hint =(1, 1),
            pos_hint = {'center_x':.5, 'center_y':.5},)
        self.widgets['details_hint_title']=details_hint_title
        # details_hint_title.ref='details_hint_title'

        details_hint_seperator=Image(
            source=black_seperator_line,
            allow_stretch=True,
            keep_ratio=False,
            size_hint =(.9, .005),
            pos_hint = {'x':.05, 'y':.85})
        self.widgets['details_hint_seperator']=details_hint_seperator

        details_scroll=OutlineScroll(
            size_hint =(.96,.8),
            pos_hint = {'center_x':.5, 'center_y':.425},
            bg_color=palette('light_tint',.15),
            bar_width=8,
            bar_color=palette('primary',.9),
            bar_inactive_color=palette('primary',.35),
            do_scroll_y=True,
            do_scroll_x=False)

        details_scroll_layout = FloatLayout(size_hint=(1,2))
        self.widgets['details_scroll_layout']=details_scroll_layout

        details_atmosphere_box=RoundedColorLayout(##################################
            size_hint =(.99, .3),
            pos_hint = {'center_x':.5, 'top':.99},
            bg_color=palette('dark_shade',.75))
        self.widgets['details_atmosphere_box']=details_atmosphere_box

        details_atmosphere_title=Label(
            text=f"[size=24][color=#ffffff][u]{' '*50}Atmosphere{' '*50}",
            markup=True,
            size_hint=(1,.05),
            pos_hint={'center_x':.5,'top':.925})
        self.widgets['details_atmosphere_title']=details_atmosphere_title

        building_balance=AnalyticExpandable(
            size_hint =(.25, .75),
            pos_hint = {'x':.125, 'y':.05},
            expanded_size=(1,1),
            expanded_pos={'x':0,'y':0},
            bg_color=palette('light_tint',.8))
        building_balance.widgets={}
        self.widgets['building_balance']=building_balance
        building_balance.bind(state=self.bg_color_white)
        building_balance.bind(expanded=self.building_balance_populate)
        building_balance.bind(animating=partial(general.stripargs,building_balance.clear_widgets))


        building_balance_title=Label(
            text="[size=20][color=#000000][b]Air Balance",
            markup=True,
            size_hint=(1,.1),
            pos_hint={'center_x':.5,'top':.95},)
        self.widgets['building_balance_title']=building_balance_title
        # building_balance_title.ref='building_balance_title'

        building_balance_gauge=CircularProgressBar(
            pos_hint={'x':.5,'y':.4})
        building_balance_gauge._widget_size=125
        building_balance_gauge._progress_colour=(0, 0, 0,1)
        self.widgets['building_balance_gauge']=building_balance_gauge

        building_balance_back=RoundedButton(
            text="[size=18][color=#ffffff][b]Close",
            size_hint =(.15, .2),
            pos_hint = {'x':.825, 'y':.025},
            background_down='',
            background_color=palette('dark_shade',.9),
            markup=True)
        self.widgets['building_balance_back']=building_balance_back
        # back.ref='settings_back'
        building_balance_back.bind(on_release=self.building_balance_back_func)




        details_hint_back=RoundedButton(
            text="[size=18][color=#ffffff][b]Close",
            size_hint =(.15, .1),
            pos_hint = {'center_x':.5, 'y':.025},
            background_down='',
            background_color=palette('dark_shade',.9),
            markup=True)
        self.widgets['details_hint_back']=details_hint_back
        # back.ref='settings_back'
        details_hint_back.bind(on_release=self.details_hint_back_func)

        details_custom=ExpandableRoundedColorLayout(
            size_hint =(.15, .1),
            pos_hint = {'x':.8, 'y':.875},
            expanded_size=(.98,.98),
            expanded_pos={'x':.01,'y':.01},
            bg_color=palette('light_tint',.8))
        details_custom.widgets={}
        self.widgets['details_custom']=details_custom
        details_custom.bind(state=self.bg_color_white)
        details_custom.bind(expanded=self.details_custom_populate)
        details_custom.bind(animating=partial(general.stripargs,details_custom.clear_widgets))

        details_custom_title=Label(
            text="[size=18][color=#000000][b]Customize\n   Details",
            markup=True,
            size_hint =(1, 1),
            pos_hint = {'center_x':.5, 'center_y':.5},)
        self.widgets['details_custom_title']=details_custom_title
        # details_custom_title.ref='details_custom_title'

        details_custom_cancel=RoundedButton(
            text="[size=18][color=#ffffff][b]Cancel",
            size_hint =(.15, .1),
            pos_hint = {'x':.65, 'y':.025},
            background_down='',
            background_color=palette('dark_shade',.9),
            markup=True)
        self.widgets['details_custom_cancel']=details_custom_cancel
        # back.ref='settings_back'
        details_custom_cancel.bind(on_release=self.details_custom_cancel_func)

        details_custom_generate=RoundedButton(
            text="[size=18][color=#ffffff][b]Generate Report",
            size_hint =(.15, .1),
            pos_hint = {'x':.825, 'y':.025},
            background_down='',
            background_color=palette('dark_shade',.9),
            markup=True)
        self.widgets['details_custom_generate']=details_custom_generate
        # back.ref='settings_back'
        details_custom_generate.bind(on_release=self.details_custom_generate_func)

        details_seperator=Image(
            source=gray_seperator_line,
            allow_stretch=True,
            keep_ratio=False,
            size_hint =(.9, .005),
            pos_hint = {'x':.05, 'y':.85})

        side_bar_box=RoundedColorLayout(
            bg_color=palette('secondary',.85),
            size_hint =(.15, .675),
            pos_hint = {'x':.825, 'center_y':.52},)
        self.widgets['side_bar_box']=side_bar_box

        side_bar_building=RoundedToggleButton(
            text="[size=20][color=#ffffff][b]Building",
            size_hint =(.9, .15),
            pos_hint = {'center_x':.5, 'center_y':.875},
            background_normal='',
            background_color=palette('primary',.25),
            markup=True,
            group='side',
            allow_no_selection=False,
            state='down')
        self.widgets['side_bar_building']=side_bar_building
        side_bar_building.bind(state=self.bg_color)
        # side_bar_connect.ref='side_bar_connect'
        side_bar_building.bind(on_release=self.load_building)

        side_bar_equipment=RoundedToggleButton(
            text="[size=20][color=#ffffff][b]Equipment",
            size_hint =(.9, .15),
            pos_hint = {'center_x':.5, 'center_y':.6875},
            background_normal='',
            background_color=palette('dark_shade',.9),
            markup=True,
            group='side',
            allow_no_selection=False)
        self.widgets['side_bar_equipment']=side_bar_equipment
        side_bar_equipment.bind(state=self.bg_color)
        # side_bar_unlink.ref='side_bar_unlink'
        # side_bar_unlink.bind(on_release=self.remove_connection)

        side_bar_remote=RoundedToggleButton(
            text="[size=20][color=#ffffff][b]Remote-Access",
            size_hint =(.9, .15),
            pos_hint = {'center_x':.5, 'center_y':.5},
            background_normal='',
            background_color=palette('dark_shade',.9),
            markup=True,
            group='side',
            allow_no_selection=False)
        self.widgets['side_bar_remote']=side_bar_remote
        side_bar_remote.bind(state=self.bg_color)
        # side_bar_add.ref='side_bar_add'
        # side_bar_add.bind(on_release=self.side_bar_add)

        side_bar_fault=RoundedToggleButton(
            text="[size=20][color=#ffffff][b]Faults",
            size_hint =(.9, .15),
            pos_hint = {'center_x':.5, 'center_y':.3125},
            background_normal='',
            background_color=palette('dark_shade',.9),
            markup=True,
            group='side',
            allow_no_selection=False)
        self.widgets['side_bar_fault']=side_bar_fault
        side_bar_fault.bind(state=self.bg_color)
        # side_bar_remove.ref='side_bar_remove'
        # side_bar_remove.bind(on_release=self.side_bar_remove)

        side_bar_refresh=RoundedToggleButton(
            text="[size=20][color=#ffffff][b]Reports",
            size_hint =(.9, .15),
            pos_hint = {'center_x':.5, 'center_y':.125},
            background_normal='',
            background_color=palette('dark_shade',.9),
            markup=True,
            group='side',
            allow_no_selection=False)
        self.widgets['side_bar_refresh']=side_bar_refresh
        side_bar_refresh.bind(state=self.bg_color)
        # side_bar_refresh.ref='side_bar_refresh'
        # side_bar_refresh.bind(on_release=self.side_bar_refresh)


        account_admin_hint=MinimumBoundingLabel(text=f"[size=18][color=#ffffff]Enable Admin mode to edit fields[/size]",
                color=palette('dark_shade',1),
                pos_hint = {'center_x':.5, 'y':.2},
                markup=True)
        self.widgets['account_admin_hint']=account_admin_hint

        seperator_line=Image(
            source=black_seperator_line,
            allow_stretch=True,
            keep_ratio=False,
            size_hint =(.98, .001),
            pos_hint = {'x':.01, 'y':.13})

        details_hint.add_widget(details_hint_title)

        details_custom.add_widget(details_custom_title)

        details_scroll.add_widget(details_scroll_layout)

        details_atmosphere_box.add_widget(details_atmosphere_title)
        details_atmosphere_box.add_widget(building_balance)

        building_balance.add_widget(building_balance_title)
        building_balance.add_widget(building_balance_gauge)

        details_box.add_widget(details_title)
        details_box.add_widget(details_hint)
        details_box.add_widget(details_custom)
        details_box.add_widget(details_seperator)
        details_box.add_widget(details_scroll)

        side_bar_box.add_widget(side_bar_building)
        side_bar_box.add_widget(side_bar_equipment)
        side_bar_box.add_widget(side_bar_remote)
        side_bar_box.add_widget(side_bar_fault)
        side_bar_box.add_widget(side_bar_refresh)

        self.add_widget(bg_image)
        self.add_widget(white_filter)
        self.add_widget(screen_name)
        self.add_widget(back)
        self.add_widget(back_main)
        self.add_widget(seperator_line)
        self.add_widget(details_box)
        self.add_widget(side_bar_box)

    def load_building(self,*args):
        w=self.widgets
        layout=w['details_scroll_layout']
        w['details_title'].text="[size=28][color=#ffffff][b]Building Details"
        layout.clear_widgets()
        all_widgets=[
            w['details_atmosphere_box']
        ]
        for i in all_widgets:
            layout.add_widget(i)
        Clock.schedule_interval(self.get_balance,0)


    def building_balance_populate(self,*args):
        balance=self.widgets['building_balance']
        darken=Animation(rgba=palette('light_tint',1))
        lighten=Animation(rgba=palette('light_tint',.8))
        balance.clear_widgets()
        if balance.expanded:
            darken.start(balance.shape_color)
            w=self.widgets
            all_widgets=[
                w['building_balance_back']
                ]
            for i in all_widgets:
                balance.add_widget(i)
        elif not balance.expanded:
            lighten.start(balance.shape_color)
            w=self.widgets
            w['building_balance_gauge'].value+=1
            all_widgets=[
                w['building_balance_title'],
                w['building_balance_gauge']]
            for i in all_widgets:
                balance.add_widget(i)

    def details_custom_populate(self,*args):
        details_custom=self.widgets['details_custom']
        darken=Animation(rgba=palette('light_tint',1))
        lighten=Animation(rgba=palette('light_tint',.8))
        details_custom.clear_widgets()
        if details_custom.expanded:
            darken.start(details_custom.shape_color)
            w=self.widgets
            all_widgets=[
                w['details_custom_cancel'],
                w['details_custom_generate']]
            for i in all_widgets:
                details_custom.add_widget(i)
        elif not details_custom.expanded:
            lighten.start(details_custom.shape_color)
            w=self.widgets
            all_widgets=[
                w['details_custom_title']]
            for i in all_widgets:
                details_custom.add_widget(i)

    def details_hint_populate(self,*args):
        details_hint=self.widgets['details_hint']
        darken=Animation(rgba=palette('light_tint',1))
        lighten=Animation(rgba=palette('light_tint',.8))
        details_hint.clear_widgets()
        if details_hint.expanded:
            darken.start(details_hint.shape_color)
            w=self.widgets
            w['details_hint_title'].pos_hint={'center_x':.5, 'center_y':.925}
            w['details_hint_title'].size_hint=(.4, .05)
            w['details_hint_title'].text="[size=20][color=#000000][b]Guide to Analytics"
            all_widgets=[
                w['details_hint_title'],
                w['details_hint_seperator'],
                w['details_hint_back']]
            for i in all_widgets:
                details_hint.add_widget(i)
        elif not details_hint.expanded:
            lighten.start(details_hint.shape_color)
            w=self.widgets
            w['details_hint_title'].pos_hint={'center_x':.5, 'center_y':.5}
            w['details_hint_title'].size_hint=(1,1)
            w['details_hint_title'].text="[size=38][color=#000000][b]?"
            all_widgets=[
                w['details_hint_title']]
            for i in all_widgets:
                details_hint.add_widget(i)

    def details_custom_expand_button_func(self,*args):
        sbd=self.widgets['details_custom']
        if sbd.expanded:
            sbd.shrink()
        if not sbd.expanded:
            sbd.expand()

    def details_hint_expand_button_func(self,*args):
        sbd=self.widgets['details_hint']
        if sbd.expanded:
            sbd.shrink()
        if not sbd.expanded:
            sbd.expand()

    def building_balance_expand_button_func(self,*args):
        sbd=self.widgets['building_balance']
        if sbd.expanded:
            sbd.shrink()
        if not sbd.expanded:
            sbd.expand()

    def bg_color(self,button,*args):
        if hasattr(button,'expanded'):
            if button.expanded:
                return
        if button.state=='normal':
            button.shape_color.rgba=palette('dark_shade',.9)
        if button.state=='down':
            button.shape_color.rgba=palette('primary',.25)

    def bg_color_white(self,button,*args):
        if hasattr(button,'expanded'):
            if button.expanded:
                return
        if button.state=='normal':
            button.shape_color.rgba=palette('light_tint',.8)
        if button.state=='down':
            button.shape_color.rgba=palette('light_tint',.5)

    def  get_balance(self,*args):
        if os.name=='nt':
            self.widgets['building_balance_gauge'].value+=1
            if self.widgets['building_balance_gauge'].value>1000:
                self.widgets['building_balance_gauge'].value=0
            return
        if _manometer.D1==None:
            return
        self.widgets['building_balance_gauge'].value=(_manometer.D1/16777216)*1000

    def building_balance_back_func(self,*args):
        self.building_balance_expand_button_func()
    def details_hint_back_func(self,*args):
        self.details_hint_expand_button_func()
    def details_custom_cancel_func(self,*args):
        self.details_custom_expand_button_func()
    def details_custom_generate_func(self,*args):
        self.details_custom_expand_button_func()
    def account_back (self,button):
        self.parent.transition = SlideTransition(direction='up')
        self.manager.current='settings'
    def account_back_main (self,button):
        self.parent.transition = SlideTransition(direction='left')
        self.manager.current='main'

    def on_pre_enter(self,*args):
        self.load_building()
        return super().on_pre_enter(*args)

    def on_leave(self, *args):
        self.widgets['details_custom'].shrink()
        self.widgets['details_hint'].shrink()
        self.widgets['building_balance'].shrink()
        return super().on_leave(*args)

def listen(app_object,*args):
    root=App.get_running_app()
    notifications=App.get_running_app().notifications
    event_log=logic.fs.milo
    pass_flag=False
    if len(app_object.children)== 2:
        widgets=app_object.children[1].widgets
    elif len(app_object.children)== 1:
        widgets=app_object.children[0].widgets
    else:
        pass_flag=True
    if pass_flag:
        pass
    else:
        main_screen=app_object.get_screen('main')
    #exhaust
        if event_log['exhaust']==1:
            if main_screen.widgets['fans'].state=='down':
                main_screen.widgets['fans'].text=current_language['fans']
        elif event_log['exhaust']==0:
            if main_screen.widgets['fans'].state=='down':
                main_screen.widgets['fans'].text=current_language['fans']
    #mau
        if event_log['mau']==1:
            pass
    #lights
        if event_log['lights']==1:
            pass
    #heat sensor
        if 'heat_sensor' in logic.fs.aux_state:#if event_log['heat_sensor']==1:
            if main_screen.widgets['fans'].state=='normal':
                main_screen.widgets['fans'].text = current_language['fans_heat']
        else:
            if main_screen.widgets['fans'].state=='normal':
                main_screen.widgets['fans'].text=current_language['fans']
    #dry contact
        if event_log['dry_contact']==1:
            pass
    #micro switch
        if event_log['micro_switch']==1:
            if app_object.current!='alert':
                if not hasattr(root,'system_banner'):
                    root.system_banner=notifications.banner('[i][size=20]Fire System Actuated','critical',100)
            elif app_object.current=='alert':
                if hasattr(root,'system_banner'):
                    notifications.remove_banner(root.system_banner)
                    del root.system_banner
            if App.get_running_app().service_pin_entered:
                pass
            elif app_object.current!='alert':
                ScreenSaver.pause()
                app_object.transition = SlideTransition(direction='left')
                app_object.current='alert'
                app_object.get_screen('preferences').widgets['overlay_menu'].dismiss()
                app_object.get_screen('devices').widgets['overlay_menu'].dismiss()
                app_object.get_screen('settings').widgets['overlay_menu'].dismiss()
                for i in app_object.get_screen('pin').popups:
                    try:
                        i.dismiss()
                    except KeyError:
                        logger.exception("main.listen()#micro switch: pop.dismiss() error")

            logic.fs.moli['maint_override']=0
        elif event_log['micro_switch']==0:
            App.get_running_app().service_pin_entered=False
            if hasattr(root,'system_banner'):
                notifications.remove_banner(target=root.system_banner)
                del root.system_banner
            if app_object.current=='alert':
                ScreenSaver.resume()
                app_object.transition = SlideTransition(direction='right')
                app_object.current='main'
    #troubles
        trouble_log=event_log['troubles']
        troubles_screen=app_object.get_screen('trouble')
        trouble_display=troubles_screen.widgets['trouble_layout']

        if 1 in {i[0]:i[1] for i in trouble_log.items() if i[0] != 'short_duration'}.values():#if any troubles detected; short duration no longer trouble
            main_screen.widgets['trouble_button'].source=trouble_icon
            main_screen.widgets['trouble_button'].color=palette('light_tint',1)
            if 'trouble_details' in troubles_screen.widgets:
                trouble_display.remove_widget(troubles_screen.widgets['trouble_details'])
                del troubles_screen.widgets['trouble_details']
        else:#if no troubles detected
            if main_screen.widgets['trouble_button'].source==trouble_icon:
                main_screen.widgets['trouble_button'].source=trouble_icon_dull
                main_screen.widgets['trouble_button'].color=palette('light_tint',.15)
            if 'trouble_details' not in troubles_screen.widgets:
                trouble_details=trouble_template('no_trouble')
                troubles_screen.widgets['trouble_details']=trouble_details
                trouble_display.add_widget(trouble_details)
    #heat trouble
        if trouble_log['heat_override']==1:
            if app_object.current!='alert':
                main_screen.widgets['fans'].text =current_language['fans_heat']
                if 'heat_trouble' not in troubles_screen.widgets:
                    root.heat_trouble_banner=notifications.banner('[i][size=20]Unsafe temperatures detected while fan switch off. Fan override activated.','warning')
                    heat_trouble=trouble_template('heat_trouble_title',
                    'heat_trouble_body',
                    link_text='heat_trouble_link',ref_tag='fans')
                    heat_trouble.ref='heat_trouble'

                    def fan_switch(*args):
                        App.get_running_app().notifications.toast('[b][size=20]Fans Activated')
                        app_object.get_screen('main').widgets['fans'].trigger_action()

                    heat_trouble.bind(on_release=fan_switch)
                    heat_trouble.bind(on_ref_press=fan_switch)
                    troubles_screen.widgets['heat_trouble']=heat_trouble
                    troubles_screen.widgets['heat_trouble'].bind(texture_size=lambda instance, value: setattr(instance, 'height', value[1]))
                    trouble_display.add_widget(heat_trouble)
        elif trouble_log['heat_override']==0:
            if 'heat_trouble' in troubles_screen.widgets:
                if hasattr(root,'heat_trouble_banner'):
                    notifications.remove_banner(root.heat_trouble_banner)
                    delattr(root,'heat_trouble_banner')
                trouble_display.remove_widget(troubles_screen.widgets['heat_trouble'])
                del troubles_screen.widgets['heat_trouble']
    #short duration trouble
                #banner only trouble
        if trouble_log['short_duration']==1:
            if app_object.current!='alert':
                if not hasattr(root,'short_duration_trouble_banner'):
                    root.short_duration_trouble_banner=notifications.banner('[i][size=20]Heat sensor override duration set to test mode')
        elif trouble_log['short_duration']==0:
            if hasattr(root,'short_duration_trouble_banner'):
                notifications.remove_banner(root.short_duration_trouble_banner)
                delattr(root,'short_duration_trouble_banner')

    #gas valve trip trouble
        if trouble_log['gv_trip']==1:
            if app_object.current!='alert':
                if 'gasvalve_trouble' not in troubles_screen.widgets:
                    gasvalve_trouble=trouble_template('gasvalve_trouble_title',
                    'gasvalve_trouble_body',
                    link_text='gasvalve_trouble_link',ref_tag='gasvalve_trouble')
                    gasvalve_trouble.ref='gasvalve_trouble'

                    gasvalve_trouble.bind(on_release=logic.gv_reset_all)
                    gasvalve_trouble.bind(on_ref_press=logic.gv_reset_all)
                    troubles_screen.widgets['gasvalve_trouble']=gasvalve_trouble
                    troubles_screen.widgets['gasvalve_trouble'].bind(texture_size=lambda instance, value: setattr(instance, 'height', value[1]))
                    trouble_display.add_widget(gasvalve_trouble)
        elif trouble_log['gv_trip']==0:
            if 'gasvalve_trouble' in troubles_screen.widgets:
                trouble_display.remove_widget(troubles_screen.widgets['gasvalve_trouble'])
                del troubles_screen.widgets['gasvalve_trouble']

    #micro switch released
        if trouble_log['actuation']==1:
            if 'actuation_trouble' not in troubles_screen.widgets:
                actuation_trouble=trouble_template('actuation_trouble_title',
                'actuation_trouble_body',
                link_text='actuation_trouble_link',ref_tag='actuation_trouble')
                actuation_trouble.ref='actuation_trouble'

                def actuation_trouble_func(*args):
                    App.get_running_app().service_pin_entered=False


                actuation_trouble.bind(on_release=actuation_trouble_func)
                actuation_trouble.bind(on_ref_press=actuation_trouble_func)
                troubles_screen.widgets['actuation_trouble']=actuation_trouble
                troubles_screen.widgets['actuation_trouble'].bind(texture_size=lambda instance, value: setattr(instance, 'height', value[1]))
                trouble_display.add_widget(actuation_trouble)
        elif trouble_log['actuation']==0:
            if 'actuation_trouble' in troubles_screen.widgets:
                trouble_display.remove_widget(troubles_screen.widgets['actuation_trouble'])
                del troubles_screen.widgets['actuation_trouble']

    #device load errors
        if trouble_log['load_errors']==1:
            if 'load_errors' not in troubles_screen.widgets:
                load_errors=trouble_template('load_errors_trouble_title',
                'load_errors_trouble_body',
                link_text='load_errors_trouble_link',ref_tag='load_errors_trouble')
                load_errors.ref='load_errors'

                def load_errors_func(*args):
                    app_object.transition = SlideTransition(direction='up')
                    app_object.current='devices'

                load_errors.bind(on_release=load_errors_func)
                load_errors.bind(on_ref_press=load_errors_func)
                troubles_screen.widgets['load_errors']=load_errors
                troubles_screen.widgets['load_errors'].bind(texture_size=lambda instance, value: setattr(instance, 'height', value[1]))
                trouble_display.add_widget(load_errors)
        elif trouble_log['actuation']==0:
            if 'load_errors' in troubles_screen.widgets:
                trouble_display.remove_widget(troubles_screen.widgets['load_errors'])
                del troubles_screen.widgets['load_errors']

def listen_to_UpdateService(*args):
    toast=App.get_running_app().notifications.toast
    screen_manager=App.get_running_app().context_screen
    cg=screen_manager.get_screen('main')
    msg_icon=cg.widgets['msg_icon']
    if UpdateService.update_prompt:
        if 'Update' not in [i.name for i in messages.active_messages]:
            messages.activate('update',(UpdateService.update_system,
                                        partial(messages.deactivate,'update'),
                                        cg.widgets['messenger_button'].schedule_refresh))
            messages.refresh_active_messages()
    if UpdateService.reboot_prompt:
        if 'Restart' not in [i.name for i in messages.active_messages]:
            messages.activate('reboot',(UpdateService.reboot,
                                        partial(messages.deactivate,'reboot'),
                                        cg.widgets['messenger_button'].schedule_refresh))
            messages.refresh_active_messages()
            toast('[b][size=20]Update Successful','info')
    if UpdateService.usb_update_found and not UpdateService.reboot_prompt:
        if 'Update Media' not in [i.name for i in messages.active_messages]:
            messages.activate('usb_update',(UpdateService.usb_update,
                                        partial(messages.deactivate,'usb_update'),
                                        cg.widgets['messenger_button'].schedule_refresh))
            messages.refresh_active_messages()
            toast('[b][size=20]Update Media Found','info')
    else:
        if 'Update Media' in [i.name for i in messages.active_messages]:
            messages.deactivate('usb_update')
            messages.refresh_active_messages()


class Hood_Control(App):
    def build(self):
        self.service_pin_entered=False
        self.admin_mode_start=time.time()
        self.report_pending=False#overwritten in settings_setter() from config file
        self.config_ = configparser.ConfigParser()
        self.config_.read(preferences_path)
        settings_setter(self.config_)
        self.limited=self.config_.getboolean("config","limited",fallback=False)
        Clock.schedule_once(partial(language_setter,config=self.config_))
        self.context_screen=ScreenManager()
        self.context_screen.add_widget(ControlGrid(name='main'))
        self.context_screen.add_widget(ActuationScreen(name='alert'))
        self.context_screen.add_widget(SettingsScreen(name='settings'))
        self.context_screen.add_widget(ReportScreen(name='report'))
        self.context_screen.add_widget(DevicesScreen(name='devices'))
        self.context_screen.add_widget(TrainScreen(name='train'))
        self.context_screen.add_widget(PreferenceScreen(name='preferences'))
        self.context_screen.add_widget(PinScreen(name='pin'))
        self.context_screen.add_widget(DocumentScreen(name='documents'))
        self.context_screen.add_widget(TroubleScreen(name='trouble'))
        self.context_screen.add_widget(MountScreen(name='mount'))
        self.context_screen.add_widget(AccountScreen(name='account'))
        self.context_screen.add_widget(NetworkScreen(name='network'))
        self.context_screen.add_widget(AnalyticScreen(name='analytics'))
        listener_event=Clock.schedule_interval(partial(listen, self.context_screen),.75)
        Clock.schedule_interval(listen_to_UpdateService,.75)
        device_update_event=Clock.schedule_interval(partial(logic.update_devices),.75)
        device_save_event=Clock.schedule_interval(partial(logic.save_devices),600)
        Clock.schedule_interval(self.context_screen.get_screen('main').widgets['clock_label'].update, 1)
        Clock.schedule_once(messages.refresh_active_messages)
        Clock.schedule_interval(messages.refresh_active_messages,10)
        # Clock.schedule_once(self.context_screen.get_screen('account').auth_server)
        # Clock.schedule_interval(UpdateService.update,10)
        Clock.schedule_interval(UpdateService.usb_probe,10)
        Window.bind(on_request_close=self.exit_check)
        Window.bind(children=self.keep_notifications_on_top)
        self.notifications=Notifications(pos_hint={'x':.75,'y':.135},size_hint=(.25,.8))
        Clock.schedule_once(partial(Window.add_widget,self.notifications))
        Clock.schedule_interval(self.notifications.update,.1)
        Clock.schedule_interval(logic_supervisor,10)
        ScreenSaver.start(timeout=(self.config_.getint('preferences','screensaver_timeout',fallback=10)*60))
        return self.context_screen

    def keep_notifications_on_top(self,window,children,*args):
        if children[0] == self.notifications:
            return
        if self.notifications.parent == None:
            return
        def _reorder(*args):
            self.notifications.parent.remove_widget(self.notifications)
            self.notifications.parent=None
            Window.add_widget(self.notifications)
        Clock.schedule_once(_reorder,0)

    def exit_check(*args,**kwargs):
        logger.info('main.py Hood_control.exit_check(): on_request_close')
        # return True  # block app's exit
        return False  # let the app close

def settings_setter(config):
    heat_duration=config['preferences']['heat_timer']
    if heat_duration == '300':
        logic.heat_sensor_timer=300
    elif heat_duration == '900':
        logic.heat_sensor_timer=900
    elif heat_duration == '1800':
        logic.heat_sensor_timer=1800

    report_status=config.getboolean('config','report_pending')
    App.get_running_app().report_pending=report_status

def language_setter(*args,config=None):
    def widget_walker(widget,current_language):
        if isinstance(widget,trouble_template):
            widget.translate(current_language)
            return
        if hasattr(widget,'children'):
            for i in widget.children:
                widget_walker(i,current_language)
        if hasattr(widget,'text') and hasattr(widget,'ref'):
            if widget.text!='':
                try:
                    widget.text=current_language[str(widget.ref)]
                except KeyError:
                    logger.exception(f'main.py lanuguage_setter():  {widget} has no entry in selected lanuage dict')
    if config:
        global current_language
        lang_pref=config['preferences']['language']
        current_language=eval(f'lang_dict.{lang_pref}')
    for i in App.get_running_app().root.screens:
        widget_walker(i,current_language)

logic_control = Thread(target=logic.logic,daemon=True)
logic_control.start()

def logic_supervisor(*args):
    global logic_control
    if logic_control.is_alive():
        return
    logger.error('main.py logic_supervisor(): logic thread stopped working')
    logger.info('main.py logic_supervisor(): logic thread restart attempted')
    logic_control = Thread(target=logic.logic,daemon=True)
    logic_control.start()

try:
    Hood_Control().run()
except KeyboardInterrupt:
    logger.exception('Keyboard Inturrupt')
except:
    traceback.print_exc()
    logger.exception('Hood_Control stopped running')
finally:
    logic.save_devices()
    logger.debug("devices saved")
    logic.clean_exit()
    logger.debug("pins set as inputs")
    server.clean_exit()
    logger.debug("streams closed")
    quit()
