import os
import sys
import subprocess
import json
import time
from datetime import datetime
from utils import read_log, update_log, abs_path

# how often should the log file be overwritten (every MEMORY_SECONDS seconds)
MEMORY_SECONDS = 10
LOG_INTERVAL = 1


def get_active_window_names():
    abs_filepath = abs_path('get_window.sh')
    win_id = subprocess.getoutput(abs_filepath).strip()
    if len(win_id.split()) != 2:
        return ['other']
    
    names = win_id.split(', ')
    for i in range(len(names)):
        names[i] = names[i].strip('"')
    
    return names


def get_application_name(window_names):
    with open(abs_path('app_names.json')) as f:
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


# Create daemon process to run in the background
pid = os.fork()

if pid < 0:
    sys.exit(1)
if pid > 0:
    print("Daemon PID: ", pid)
    sys.exit(0)

os.setsid()
if os.getsid(0) < 0:
    sys.exit(1)

os.chdir('/')
os.umask(0)

sys.stdin.close()
sys.stdout.close()
sys.stderr.close()
os.close(0)
os.close(1)
os.close(2)

log_active_app_per_second()
