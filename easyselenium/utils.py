import sys
import logging

from random import choice
from datetime import datetime


def get_timestamp():
    timetuple = datetime.now().timetuple()
    timestamp = "%d%02d%02d%02d%02d%02d" % timetuple[:6]
    return timestamp


def get_random_value(_list, *val_to_skip):
    _tmp = list(_list)
    for skipped in val_to_skip:
        _tmp.remove(skipped)
    value = choice(_tmp)
    return value


class Logger(object):
    def __init__(self, log_to_console=True, file_path=None):
        self.__logger = logging.getLogger('easyselenium.browser')
        self.__logger.setLevel(logging.DEBUG)
        
        if log_to_console:
            handler = logging.StreamHandler(sys.stdout)
            self.__logger.addHandler(handler)
        
        if file_path:
            handler = logging.FileHandler(file_path, encoding='utf8')
            self.__logger.addHandler(handler)
    
    def info(self, msg, *args, **kwargs):
        self.__logger.info(msg, *args, **kwargs)
