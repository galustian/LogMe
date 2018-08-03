import os
import subprocess
import json
import time
from datetime import datetime
from utils import read_log, update_log

# how often should the log file be overwritten (every MEMORY_SECONDS seconds)
MEMORY_SECONDS = 10
LOG_INTERVAL = 1


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
            app_name = "other"

    return app_name


def active_app_name():
    window_names = get_active_window_names()
    return get_application_name(window_names)


def log_active_app_per_second():
    now = datetime.now()
    
    log = read_log(year=now.year)
    seconds_in_memory_count = 0

    while True:
        # Format: Day-Month-Year
        date_str = "{}-{}-{}".format(now.day, now.month, now.year)
        
        app_name = active_app_name()

        if date_str in log:
            if app_name in log[date_str]:
                log[date_str][app_name] += LOG_INTERVAL
            else:
                log[date_str][app_name] = LOG_INTERVAL
        else:
            log[date_str] = {}
            log[date_str][app_name] = LOG_INTERVAL
        
        # after LOG_INTERVAL seconds overwrite log file
        if seconds_in_memory_count >= MEMORY_SECONDS:
            update_log(log, year=now.year)
            now = datetime.now()
            log = read_log(year=now.year)

            seconds_in_memory_count = 0
        else:
            seconds_in_memory_count += LOG_INTERVAL

        time.sleep(LOG_INTERVAL)


if __name__ == '__main__':
    log_active_app_per_second()
