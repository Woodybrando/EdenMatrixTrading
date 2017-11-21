
import json
import math

def read_config():
    config = {}
    with open('./Bryn_wex_ltc_usd/config_wex_ltc_usd.json') as f:
        config = json.load(f)
    for k, v in config.iteritems():
        print '%s: %s' % (k, v)
    return config

def round_tpair_price(number, tpair):
    return_number = 0
    if tpair == "nmc_usd":
        return_number = round(number, 2)
    elif tpair == "ltc_usd":
        return_number = round(number, 3)
    elif tpair == "ppc_usd":
        return_number = round(number, 3)
    elif tpair == "eth_btc":
        return_number = round(number, 5)
    elif tpair == "btc_usd":
        return_number = round(number, 6)
    else:
        print "ERROR!! Haven't defined round price function for tpair " + tpair
        exit(1)
    return return_number


def round_tpair_volume(number, tpair):
    return_number = 0
    if tpair == "nmc_usd":
        return_number = round(number, 4)
    elif tpair == "ppc_usd":
        return_number = round(number, 3)
    elif tpair == "ltc_usd":
        return_number = round(number, 4)
    elif tpair == "eth_btc":
        return_number = round(number, 4)

    # Could do more than 5 digits for BTC but let's keep at 4 for keeping it simple
    elif tpair == "btc_usd":
        return_number = round(number, 4)
    else:
        print "ERROR!! Haven't defined round volume function for tpair " + tpair
        exit(1)
    return return_number

def round_down_tpair_volume(number, tpair):
    return_number = 0
    if tpair == "nmc_usd":
        return_number = math.floor(10000*round(number, 4))/10000
    elif tpair == "ppc_usd":
        return_number = math.floor(1000*round(number, 3))/1000
    elif tpair == "ltc_usd":
        return_number = math.floor(10000*round(number, 4))/10000
    elif tpair == "eth_btc":
        return_number = math.floor(10000*round(number, 4))/10000

    # Could do more than 5 digits for BTC but let's keep at 4 for keeping it simple
    elif tpair == "btc_usd":
        return_number = math.floor(10000*round(number, 4))/10000
    else:
        print "ERROR!! Haven't defined round down volume function for tpair " + tpair
        exit(1)
    return return_number

def get_kill_order_price(tpair):
    kill_price = 0
    if tpair == "nmc_usd":
        kill_price = ".001"
    elif tpair == "ppc_usd":
        kill_price = ".01"
    else:
        print "ERROR, Haven't defined Kill Order Price for tpair " + str(tpair) + "\n"
        exit(1)
    return kill_price

# Return not the very next peg, but the peg even one higher than that.
def get_full_peg_higher(peg, matrix):
    above_peg = 0
    for index, price in enumerate(matrix):
        if above_peg == 1:
            if index == len(matrix) -1:
                return -1
            else:
                return matrix[index+1]
        elif price > peg:
            above_peg = 1
    return -1

def get_full_peg_lower(peg, matrix):
    above_peg = 0
    two_lower_peg = -1
    for index, price in enumerate(matrix):
        if above_peg == 1:
            return two_lower_peg
        elif price >= peg:
            above_peg = 1
        else:
            if index != 0:
                two_lower_peg = matrix[index-1]

    return two_lower_peg


# Replace a line in a file.
# For instance used to update Matrix File as we update orders.
def replace_line(file_name, line_num, text):
    lines = open(file_name, 'r').readlines()
    lines[line_num] = text
    out = open(file_name, 'w')
    out.writelines(lines)
    out.close()