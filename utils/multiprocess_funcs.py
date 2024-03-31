import os,json
from utils import general
from kivy.clock import mainthread

@mainthread
def _load_debug_data(debug_path,data_target,*args):
                    for file in os.listdir(debug_path):
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
                            color=(0,0,0,.5) if index%2==0 else (0,0,0,.25)
                            data_target.append({'text':entry_text,'color':color})