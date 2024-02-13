from pathlib import Path
import os,logging

logger=logging.getLogger('logger')

default_config='''
[preferences]
heat_timer = 300
language = english
evoke = True

[documents]
inspection_date = 

[config]
report_pending = False

[timestamps]
system inspection = 

[account]
email = 
password = 
uuid = 
link_code = 

[network]
status = True
'''

logs_tree = {
    "logs":{
        "configurations": {
            "hood_control.ini": default_config,
            "pushed_messages.json": "{}"
            },
        "devices": {
            "device_list.json": "{}"
        },
        "documents":{
            "system_reports":{},
            "manuals":{},
            "archives":{}
        },
        "log_files":{
            "debug":{},
            "errors":{},
            "info":{}
        },
        "sys_report":{}}
}

def create_dir_tree(root, tree):
    """
    Create directory tree recursively from a dictionary representation using pathlib.

    Args:
    - root: Root directory to start creating the tree (as a Path object).
    - tree: Dictionary representing the directory tree structure.
    """
    for key, value in tree.items():
        path = root / key
        if isinstance(value, dict):
            path.mkdir(exist_ok=True)
            create_dir_tree(path, value)
        else:
            if path.exists():
                continue
            with open(path, 'w') as f:
                logger.debug(f'creating file: {path.name}')
                f.write(value)

def build_logs_tree(*args):
    create_dir_tree(Path(os.getcwd()),logs_tree)

if __name__=='__main__':
    # Specify the root directory
    root_directory = Path(os.getcwd())

    # Create the directory tree
    create_dir_tree(root_directory, logs_tree)