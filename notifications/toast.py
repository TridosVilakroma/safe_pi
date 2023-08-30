from kivy.uix.label import Label
from kivy.graphics import Rectangle, Color, Line, Bezier

class Toast(Label):
    def __init__(self,level, **kwargs):
        kwargs['markup']=True
        super(Toast,self).__init__(**kwargs)
        self.size_hint =(1, .2)
        self.pos_hint = {'x':1, 'y':0}
        self.life_time=0
        self.level=level
        theme={
            'info':{
                'color':(0,1,0,1),
                'time':3.5},
            'warning':{
                'color':(1,1,0,1),
                'time':4.5},
            'error':{
                'color':(1,.5,0,1),
                'time':5},
            'critical':{
                'color':(1,0,0,1),
                'time':6}}
        self.theme=theme[level]

        with self.canvas.before:
                self.colour = Color(0,0,0,.7)
                self.rect = Rectangle(size=self.size, pos=self.pos)
                Color(.5,.5,.5,.5)
                self.outline = Line(rectangle=(100, 100, 200, 200))
                Color(*self.theme['color'])
                self.theme_line = Line(points=(100, 100,200,200),width=2.5,cap='none')
        self.bind(size=self._update_rect, pos=self._update_rect)

        def update_lines(self,*args):
            x=int(self.x)
            y=int(self.y)
            width=int(self.width)
            height=int(self.height)
            self.outline.rectangle=(x, y, width, height)
            x+=2
            self.theme_line.points=(x, y,x,y+height)
        self.bind(pos=update_lines, size=update_lines)

    def _update_rect(self, instance, *args):
        self.rect.pos = instance.pos
        self.rect.size = instance.size

    