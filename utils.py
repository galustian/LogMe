import os
import json

def read_log(year=None):
    # if new year, create new log-file
    if not os.path.isfile('logs/log-{}.json'.format(year)):
        update_log({}, year=year)
        return {}

    with open('logs/log-{}.json'.format(year)) as f:
        log = json.load(f)
    
    return log

def read_log_only(year=None):
    with open('logs/log-{}.json'.format(year)) as f:
        log = json.load(f)
    
    return log