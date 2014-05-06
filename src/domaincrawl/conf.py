from ConfigParser import ConfigParser
from ConfigParser import Error
from collections import namedtuple, OrderedDict
from sys import stderr
from multiprocessing import cpu_count
from ast import literal_eval

DEFAULT_CONF = dict(connect_timeout = 4, response_timeout = 5,
                    max_page_charlen = 100000,max_redirects = 1,
                    max_parser_workers=cpu_count(), user_agent = "Python-urllib/2.6",
                    logger_name="root")
def get_default():
    return namedtuple_from_dict(DEFAULT_CONF)

def from_file(file_name):
    conf = ConfigParser(defaults=DEFAULT_CONF)
    try:
        conf.read(file_name)
    except Error:
        stderr.write("Error reading config file. Please ensure that the file exists, has correct permissions,"
                     "and is a valid python config file")
        stderr.flush()
        raise
    conf_dict = conf.defaults()
    typed_config_list = []
    # The ugly try-catch is required due to a quirk in literal_eval of plain strings
    for k,v in conf_dict.items():
        try:
            typed_val = literal_eval(v)
        except ValueError:
            typed_val = "'" + v + "'"
        typed_config_list.append((k,typed_val))
    merged_dict = OrderedDict(dict(DEFAULT_CONF.items() + typed_config_list))
    return namedtuple_from_dict(merged_dict)

def namedtuple_from_dict(conf_dict):
    Conf = namedtuple("Conf",conf_dict.keys())
    config_named_tuple = Conf._make(conf_dict.values())
    return config_named_tuple
