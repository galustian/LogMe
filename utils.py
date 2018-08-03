import os
import json


def abs_path(file):
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), file)


def update_log(log, year=None):
    with open(abs_path('logs/log-{}.json'.format(year)), 'w') as f:
        json.dump(log, f)


def read_log(year=None):
    # if new year, create new log-file
    if not os.path.isfile(abs_path('logs/log-{}.json'.format(year))):
        update_log({}, year=year)
        return {}

    with open(abs_path('logs/log-{}.json'.format(year))) as f:
        log = json.load(f)
    
    return log


def read_log_only(year=None):
    with open(abs_path('logs/log-{}.json'.format(year))) as f:
        log = json.load(f)
    
    return log