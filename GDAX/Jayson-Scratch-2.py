
import httplib
import urllib
import hashlib
import hmac
import time
import requests
import json
from utils import *
from shutil import move


# Use these for testing or Replace with your own API key data
# BTC_API_KEY = "4UJ8ZHCW-LIR3CGIJ-Y2GZAQ92-6CQ7W6IB-1WTYSZ98"
# BTC_API_SECRET = "409431dc77f94b5046ff49343a3d24c852fe2b6bbc701162dda002fe03e30e2d"

config = read_config()

# *******************************************************************************************************
# ********************************* DEFINE FUNCTIONS *********************************************
# *******************************************************************************************************

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
        exit(2)
    return return_number


def generate_matrix(start, end, percentage, tpair):
    # Generates the peg Marix, the corresponding Matrix_Trade_State and Matrix_Order_Id.
    current = start
    matrix = []
    while current <= end:
        matrix.append(current)
        current *= percentage
        current = round_tpair_price(current, tpair)

    trade_state = [0 for _ in matrix]
    order_id_list = [0 for _ in matrix]


    return matrix, trade_state, order_id_list


def btce_signed_request(method, params):
    """Makes a signed request to the BTC-e API with the given method and parameters."""

    params["method"] = method
    params["nonce"] = int(round(time.time() - 1398621111, 1) * 10)

    h = hmac.new(str(config["BTCE_API_SECRET"]), digestmod=hashlib.sha512)
    h.update(urllib.urlencode(params))

    trade_headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Key": config["BTCE_API_KEY"],
        "Sign": h.hexdigest(),
    }

    response = requests.post(
        "https://wex.nz/tapi", headers=trade_headers, data=params)

    print '[%s] %s %s' % (method, response.status_code, response.reason)
    return response


def marketdepth(tpair, limit=150):
    """Returns a tuple containing (asks, bids)."""

    resp = requests.get(
        "https://wex.nz/api/3/depth/" + tpair, params={"limit": limit})
    if resp.status_code == 200:
        data = resp.json()
        data = data.get(tpair)
        return data.get("asks"), data.get("bids")
    else:
        return None, None


def trade(tpair, rate, ttype, amount):
    """Adds a trade order to the exchange.  Returns a tuple with the values (success, order id)."""

    print "Trading tpair " + str(tpair) + " amount is " + str(
        amount) + " and type is " + str(ttype) + " rate is " + str(rate)
    resp = btce_signed_request("Trade", {
        "pair": tpair,
        "rate": rate,
        "type": ttype,
        "amount": amount,
    })

    if resp.status_code == 200:
        data = resp.json()
        success = data.get("success") == 1
        order_id = data.get("return", {}).get("order_id")
        return success, order_id
    else:
        print "Trade function did not return 200 - Error! \n"
        return False, None


def cancelorder(order_id):
    """Returns True if the order was canceled successfully, False otherwise."""

    resp = btce_signed_request("CancelOrder", {"order_id": order_id})
    if resp.status_code == 200:
        data = resp.json()
        return data.get("success") == 1
    else:
        return False


def activeorders(tpair=None):
    """Returns an array of the user's active orders.  Optional tpair parameter specifies the trading pair."""

    params = {}
    if tpair is not None:
        params["pair"] = tpair

    resp = btce_signed_request("ActiveOrders", params)
    if resp.status_code == 200:
        data = resp.json()
        data = data.get("return")
        if data is None:
            return None
            print("no orders suckers!")


        tuplelist = []
        keylist = data.keys()

        for key in keylist:
            tuple = [data[key]['rate'], data[key]['type'], int(key)]
            #print str(tuple) + "\n"
            tuplelist.append(tuple)

                # tuplelistrate[num].append(data[key]['rate'])

        j = lambda x: x[0]

        tuplelist.sort(key=j, reverse=False)
        return tuplelist
    else:
        return None


        # the data is returned as a dictionary, so we convert it to an array for convenience
#        orders = []
#        for order_id, order_data in data.iteritems():
#            order_data[
#                "order_id"] = order_id  # add the order_id to the returned order data
#            orders.append(order_data)
#        return orders
#    else:
#        return None


def tradehistory(tpair=None):
    """Returns an array of the user's trades.  Optional tpair parameter specifies the trading pair."""

    params = {}
    if tpair is not None:
        params["pair"] = tpair

    resp = btce_signed_request("TradeHistory", params)

    if resp.status_code == 200:
        data = resp.json()
        data = data.get("return")
        if data is None:
            return None

        tuplelist2 = []
        keylist2 = data.keys()

        for key in keylist2:
            tuple = [data[key]['timestamp'],  data[key]['type'], data[key]['amount'], data[key]['rate'],
                    data[key]['is_your_order'], int(key)]
            # print str(tuple) + "\n"
            tuplelist2.append(tuple)

            # tuplelistrate[num].append(data[key]['rate'])

        j = lambda x: x[0]

        tuplelist2.sort(key=j, reverse=False)
        return tuplelist2

    else:
        return None


def tradehistoryT(tpair=None):
    """Returns an array of the user's trades.  Optional tpair parameter specifies the trading pair."""

    params = {}
    if tpair is not None:
        params["pair"] = tpair

    resp = btce_signed_request("TradeHistory", params)

    if resp.status_code == 200:
        data = resp.json()
        data = data.get("return")
        if data is None:
            return None

        tuplelist2 = []
        keylist2 = data.keys()

        for key in keylist2:
            tuple = [data[key]['timestamp'],  data[key]['type'], data[key]['amount'], data[key]['rate'],
                    data[key]['is_your_order'], int(key)]
            # print str(tuple) + "\n"
            tuplelist2.append(tuple)

            # tuplelistrate[num].append(data[key]['rate'])

        j = lambda x: x[0]

        tuplelist2.sort(key=j, reverse=True)
        return tuplelist2

    else:
        return


'''
        # the data is returned as a dictionary, so we convert it to an array for convenience
        trades = []
        for trade_id, trade_data in data.iteritems():
            trade_data[
                "trade_id"] = trade_id  # add the trade_id to the returned trade data
            trades.append(trade_data)
        return trades
    else:
        return None
'''



matrix_established = 0
matrix_preestablished = 0
matrix_bottom = -1
matrix_top = -1
matrix = []
matrix_trade_state = []
matrix_order_id = []
current_tpair_mprice = -1

# Open a debug file for debug data
debugfile = open("/Users/woodybrando/PycharmProjects/EdenMatrixTrading/debug_log.txt", 'w+')

# Open the log file to append
logfile = open(str(config["matrix_log_fname"]), 'a+')

# Check to see if we are reading in an already created Matrix from Matrix file or if making a new one
# If a Matrix.txt with valid data exists, then we already have a Matrix on the market.
# If not, we need to generate a matrix at current market price, and invest in our moonbasket and initial inv
# and put in all the matrix buys & sells on the market
error_to_catch = getattr(__builtins__,'FileNotFoundError', IOError)
try:
    # Does the matrix.txt file exist with valid data
    mfile = open(str(config["matrix_fname"]),'r')

except error_to_catch:
    debugfile.write(str(config["matrix_fname"]) + " does not exist")

 # See if file exists by trying to open for reading, if so then close it and open a read/write file
else:
    mfile_lines = mfile.readlines()
    if len(mfile_lines) < 5:
        # Not really a valid Matrix file. Close teh read handle, and open a writing handle to make Matrix file
        mfile.close()
        mfile = open(str(config["matrix_fname"]), 'w')
        matrix_established = 0
    else :
        debugfile.write("Using PreEstablished Matrix\n")

        # Code to read Matrix File
        linenum = 0
        for mfile_line in mfile_lines:
            #debugfile.write("MFILE Line: " + str(mfile_line) + "\n")

            mfile_line.rstrip()
            debugfile.write("MFILE Line: " + str(mfile_line) + "\n")

            if mfile_line.find("[") != -1:
                mfile_line_parsed = mfile_line.split(",")
                mfile_line_index = int(mfile_line_parsed[0].strip('[]'))
                #debugfile.write("Index:" + str(mfile_line_index) + "\n")

                matrix.append(round_tpair_price(float(mfile_line_parsed[1].strip('[]')),config["tpair"]))
                #debugfile.write("Peg:" + str(matrix[mfile_line_index]) + "\n")

                matrix_trade_state.append(int(mfile_line_parsed[2].strip('[]')))
                #debugfile.write("Trade_state:" + str(matrix_trade_state[mfile_line_index]) + "\n")

                matrix_order_id.append(int(mfile_line_parsed[3].strip('[]\n')))
                #debugfile.write("Order Id:" + str(matrix_order_id[mfile_line_index]) + "\n")


            elif linenum == 0:
                if mfile_line.find("MARKET_PRICE") != -1:
                    # Needs to be fixed
                    last_tpair_mprice = round_tpair_price(float(mfile_line.split("=")[1]), config["tpair"])
                else:
                    debugfile.write("Error reading Matrix File\n")
                    exit(2)
            elif linenum == 1:
                debugfile.write("We have linenum is 1")

                if mfile_line.find("TRADE_VOLUME") != -1:
                    trade_volume = round_tpair_volume(float(mfile_line.split("=")[1]), config["tpair"])
                else:
                    debugfile.write("Error reading Matrix File\n")
                    exit(3)
            elif linenum == 2:
                if mfile_line.find("MOON_BASKET_PRICE") != -1:
                    moon_basket_peg = round_tpair_price(float(mfile_line.split("=")[1]), config["tpair"])
                else:
                    debugfile.write("Error reading Matrix File\n")
                    exit(4)

            linenum += 1
            matrix_established = 1
            matrix_preestablished = 1
# End of code to read in Matrix.txt file

'''

PreviousActiveOrders = open(str(config["matrix_fname"]),'r')

matrixJayson = []

for lined in PreviousActiveOrders:
    matrixJayson.append(lined)
    print(lined)

#for order in activeorders():
#    print(order)

activeordersplus = activeorders()

new = []

for typeline in activeorders():
    #print(typeline)
    if typeline[1] == str('buy'):
        typeline.append(1)
    elif typeline[1] == str('sell'):
        typeline.append(2)
    assert isinstance(typeline, object)
    new.append(typeline)
    print(typeline)

#print('hello')


for line in new:

    print(line)

#print('helllo2')

matrixJayson = zip(matrix, matrix_trade_state, matrix_order_id)

#for line in matrixJayson:
#    print(line)

print('hello3')

#for price in new:
#    print(price[0])

#for item in matrixJayson:

#    print(item)

'''

#for x,y in zip(matrixJayson, new):
#    if x[0] != y[0]:
#        print(x)

lasttradeid = []
lasttradeid = open("./lasttradeid", 'r')

for line in lasttradeid:
    print(line)
    lastTradeMem = line





th = tradehistory()


thT = tradehistoryT()

for item in th:
    latesttrade = []
    #print(item[0])
    latesttrade = item[0]

print("latest trade is =")

print(latesttrade)
type(latesttrade)


print("previous trade is =")

print(lastTradeMem)
type(lastTradeMem)

newtradeshistory = []

if int(latesttrade) == int(lastTradeMem):
    print("we have a match! so go back to sleep, no new trades yet... remember... patience... is... a... v...i...r...t...u...........e")

else:
    print("lordy o' lordy! We've had a trade!")
    for item in thT:
        if int(item[0]) != int(latesttrade):
            newtradeshistory.append(item)
            print(newtradeshistory)



'''
if lastTradeMem == tradehistory():
    print("not time to trade yet, patience is a virtue...")
    exit(9)


else:
    for line in tradehistory():
        print(line)
        if lasttradeMem != line:
            print('time to trade')


exit(10)

'''