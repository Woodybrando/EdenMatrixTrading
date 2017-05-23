
import json

def read_config():
    config = {}
    with open('./config.json') as f:
        config = json.load(f)
    for k, v in config.iteritems():
        print '%s: %s' % (k, v)
    return config