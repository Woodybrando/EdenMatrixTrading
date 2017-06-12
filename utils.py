
import json

def read_config():
    config = {}
    with open('./config.json') as f:
        config = json.load(f)
    for k, v in config.iteritems():
        print '%s: %s' % (k, v)
    return config


class State:
    def __init__(self):
        data = {}
        try:
            with open('./current-state.json') as f:
                data = json.load(f)
        except:
            pass

        self.matrix = data.get('matrix', None)
        self.initialized = data.get('initialized', False)
        self.trade_state = data.get('trade_state', None)
        self.last_tpair_mprice = data.get('last_tpair_mprice', None)
        self.save()

    def save(self):
        print 'Saving state'
        data = {
            'matrix': self.matrix,
            'initialized': self.initialized,
            'trade_state': self.trade_state,
            'last_tpair_mprice': self.last_tpair_mprice,
        }
        with open('./current-state.json', 'w') as f:
            f.write(json.dumps(data))


def round_tpair_price(number, tpair):
    return_number = 0
    if tpair == "nmc_usd":
        return_number = round(number, 2)
    elif tpair == "ltc_usd":
        return_number = round(number, 2)
    elif tpair == "eth_btc":
        return_number = round(number, 5)
    else:
        print "ERROR!! Haven't defined round price function for tpair " + tpair
        exit(1)
    return return_number


def round_tpair_volume(number, tpair):
    return_number = 0
    if tpair == "nmc_usd":
        return_number = round(number, 4)
    elif tpair == "ltc_usd":
        return_number = round(number, 4)
    elif tpair == "eth_btc":
        return_number = round(number, 4)
    else:
        print "ERROR!! Haven't defined round volume function for tpair " + tpair
        exit(1)
    return return_number


def generate_matrix(start, end, percentage, tpair):
    """Generates the peg Marix, the corresponding Matrix_Trade_State and Matrix_Order_Id."""
    """ @@TODO: generate matrix from the center outwards? """
    current = start
    matrix = []
    while current <= end:
        matrix.append(current)
        current *= percentage
        current = round_tpair_price(current, tpair)

    return matrix


def die(reason):
    print reason
    exit(1)