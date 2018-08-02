import os
import subprocess
import json
import time

def get_active_window_names():
    abs_filepath = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'get_window.sh')
    win_id = subprocess.getoutput(abs_filepath).strip()
    if len(win_id.split()) != 2:
        return ['other']
    
    names = win_id.split(', ')
    for i in range(len(names)):
        names[i] = names[i].strip('"')
    
    return names

def get_application_name(window_names):
    with open('app_names.json') as f:
        name_dict = json.load(f)
    
    app_name = ""

    for name in window_names:
        try:
            app_name = name_dict[name.lower()]
            break
        except KeyError:
            app_name = "Other"

    return app_name

def active_app_name():
    window_names = get_active_window_names()
    return get_application_name(window_names)

if __name__ == '__main__':
    while True:
        print(active_app_name())
        time.sleep(1)

