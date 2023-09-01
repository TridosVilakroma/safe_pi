from kivy.uix.label import Label
from kivy.graphics import Rectangle, Color, Line, Bezier

class Banner(Label):
    def __init__(self,level,value, **kwargs):
        kwargs['markup']=True
        super(Banner,self).__init__(**kwargs)
        #Notifications(pos_hint={'x':.75,'y':.135},size_hint=(.25,.8)
        self.size_hint =(4.1,.1)
        self.pos_hint = {'x':-3.05,'y':1.25}#'x':-3.05,'y':.975
        self.value=value
        self.remove_flag=False
        self.level=level
        theme={
            'info':{
                'color':(50/255, 200/255, 50/255,.4),
                'time':3.5},
            'warning':{
                'color':(245/250, 216/250, 41/250,.4),
                'time':4.5},
            'error':{
                'color':(218/255, 127/255, 36/255,.4),
                'time':5},
            'critical':{
                'color':(218/255, 36/255, 36/255,.4),
                'time':6}}
        self.theme=theme[level]

        with self.canvas.before:
                self.colour = Color(0,0,0,.5)
                self.rect = Rectangle(size=self.size, pos=self.pos)
                Color(*self.theme['color'])
                self.outline = Line(rectangle=(100, 100, 200, 200))
        self.bind(size=self._update_rect, pos=self._update_rect)

        def update_lines(self,*args):
            x=int(self.x)
            y=int(self.y)
            width=int(self.width)
            height=int(self.height)
            self.outline.rectangle=(x, y, width, height)
        self.bind(pos=update_lines, size=update_lines)

    def _update_rect(self, instance, *args):
        self.rect.pos = instance.pos
        self.rect.size = instance.size

