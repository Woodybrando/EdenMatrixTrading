#!/usr/bin/env python
'''
    Copyright (c) 2017 by Jayson Rahmlow <jayson.rahmlow@gmail.com>
      and Vanessa Rahmlow <vannyrahmlow@gmail.com>

    This file is part of EdenMatrixTrading.

    EdenMatrixTrading is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    EdenMatrixTrading is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with EdenMatrixTrading.  If not, see <http://www.gnu.org/licenses/>.
'''

import httplib
import urllib
import hashlib
import hmac
import time
import requests
import json
import numpy as np
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


        tuplelist = []
        keylist = data.keys()

        for key in keylist:
            tuple = (data[key]['rate'], data[key]['type'], int(key))
            #print str(tuple) + "\n"
            tuplelist.append(tuple)

                # tuplelistrate[num].append(data[key]['rate'])

        j = lambda x: x[0]

        tuplelist.sort(key=j, reverse=False)
        return tuplelist
    else:
        return None



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

        # the data is returned as a dictionary, so we convert it to an array for convenience
        trades = []
        for trade_id, trade_data in data.iteritems():
            trade_data[
                "trade_id"] = trade_id  # add the trade_id to the returned trade data
            trades.append(trade_data)
        return trades
    else:
        return None

def find_matrix_gap_idx(current_price, matrixlist):
    # type: (object, object) -> object

    gap_idx = (np.abs(np.asarray(matrixlist) - current_price)).argmin()
    if gap_idx <= 0:
        debugfile.write("Error determining Matrix Gap")
        exit(1)
    if gap_idx > (len(matrixlist)-1):
        debugfile.write("Error determining Matrix Gap")
        exit(1)
    else:
        return gap_idx

def write_matrix_file(mfile):

    # Always get up to date Market Price
    depth = marketdepth(config["tpair"], 5)
    if depth is None:
        debugfile.write("Error connecting to wex.nz\n")
        mprice = 0
    else:
        mprice = depth[0][4][0]

    mfile.write("MARKET_PRICE=" + str(mprice) + "\n")
    mfile.write("MOON_BASKET_PRICE=" + str(moon_basket_peg) + "\n")
    mfile.write("TRADE_VOLUME=" + str(trade_volume) + "\n")
    mfile.write("MATRIX=" + "\n")

    for index, peg in enumerate(matrix):
            mfile.write("[" + str(index) + "],[" + str(peg) + "],["
            + str(matrix_trade_state[index])
           + "],[" + str(matrix_order_id[index]) + "]\n")


def write_matrix_CSV(mCSV):

    for index, peg in enumerate(matrix_CSV):
        mCSV.write(str(trade_volume) + ", " + str(peg) + ", "
            + str(matrix_trade_state[index])
           + ", " + str(matrix_order_id[index]) + "\n")


def exit_program(rc, mfile):
    mfile.close()
    tempfilename = str(config["matrix_dir"]) + "/matrixtemp.txt"
    try:
        tempfile = open(tempfilename, 'w')
    except error_to_catch:
        debugfile.write("Error opening Temp Matrix file " + str(tempfilename))
    else:
        write_matrix_file(tempfile)
        move(str(config["matrix_fname"]), str(config["matrix_fname"]) + "_backup")
        move(tempfilename, str(config["matrix_fname"]))
        tempfile.close()
    exit(rc)



# *******************************************************************************************************
# ********************************* END OF DEFINE FUNCTIONS *********************************************
# *******************************************************************************************************

# CONFIGURATIONS DEFINED IN CONFIG FILE, FOR EXAMPLE
# WHAT MARKET WOULD YOU LIKE TO TRADE IN: BTC-E, GDAX, POLONIEX
# PRESS HERE TO LEARN MORE ABOUT EACH EXCHANGE
# exchange_choice = "btc-e.com"

# WHAT CURRENCY PAIR WOULD YOU LIKE TO TRADE IN
# USER PAIR Example: LTC/USD
# tpair = "ltc_usd" or "nmc_btc"

# BTC-E MARKET FEE
# btce_trade_fee = .002

# ***********************************************************************************************************
# SECTION A - INITIALIZATIONS
# ***********************************************************************************************************
matrix_established = 0
matrix_preestablished = 0
matrix_bottom = -1
matrix_top = -1
matrix = []
matrix_trade_state = []
matrix_prev_trade_state = []
matrix_order_id = []
current_tpair_mprice = -1
matrix_CSV = []
trade_success = 1
order_id = 999

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

 # Read the Matrix File
else:
    mfile_lines = mfile.readlines()
    if len(mfile_lines) < 5:
        # Not really a valid Matrix file. Close the read handle, and open a writing handle to make Matrix file
        mfile.close()
        mfile = open(str(config["matrix_fname"]), 'w')
        mCSV = open(str(config["matrix_CSV"]), 'w')
        matrix_established = 0
    else :
        debugfile.write("Using PreEstablished Matrix\n")

        # Code to read Matrix File
        # Can't use exit_rc function in this block because mfile is 'r' not 'w'
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
                    exit(1)
            elif linenum == 1:
                if mfile_line.find("MOON_BASKET_PRICE") != -1:
                    moon_basket_peg = round_tpair_price(float(mfile_line.split("=")[1]), config["tpair"])
                else:
                    debugfile.write("Error reading Matrix File\n")
                    exit(1)
            elif linenum == 2:
                if mfile_line.find("TRADE_VOLUME") != -1:
                    trade_volume = round_tpair_volume(float(mfile_line.split("=")[1]), config["tpair"])
                else:
                    debugfile.write("Error reading Matrix File\n")
                    exit(1)

            linenum += 1
            matrix_established = 1
            matrix_preestablished = 1

            # Close the Read Handle, Open up a Write Handle
            mfile.close()
            mCSV.close()

            mfile = open(str(config["matrix_fname"]), 'w')
            mCSV = open(str(config["matrix_CSV"]), 'w')

# End of code to read in Matrix.txt file


if matrix_established == 0:

    # ***********************************************************************************************************
    # Get Current Market Price
    # ***********************************************************************************************************

    if config["exchange_choice"] == "wex.nz":
        depth = marketdepth(config["tpair"], 5)
        if depth is None:
            print "Error connecting to wex.nz"
            exit(1)

        # Debug make sure these asks look appropriate
        current_tpair_mprice = depth[0][4][0]

        # Open the Matrix.txt file
        error_to_catch = getattr(__builtins__, 'FileNotFoundError', IOError)
        try:
            # Does the matrix.txt file exist with valid data
            mfile = open(str(config["matrix_fname"]), 'w')

        except error_to_catch:
            debugfile.write(str(config["matrix_fname"]) + " can not be opened")
            exit(1)

        # Write the market price to Matrix File and Log file
        logfile.write("Market price = " + str(current_tpair_mprice) + "\n")

    else:
        debugfile.write("We don't have software created for markets other than wex.nz yet. Stay tuned!\n")
        current_tpair_mprice = 0
        exit(1)

    # Generate the matrix of pegs (and the corresponding trading state matrix)
    # ------------------------------------------------ WORK TO BE DONE HERE -----------------------------------------
    # For the moment the bottom and top are defined with hard limits but this will change to be related to the current
    # market price, so the matrix_bottom and matrix_top will be taken out of config file then and calculated here
    # ------------------------------------------------ WORK TO BE DONE HERE -----------------------------------------
    matrix_bottom = config["matrix_bottom_ratio"] * current_tpair_mprice
    matrix_bottom = round_tpair_price(matrix_bottom, config["tpair"])
    matrix_top = config["matrix_top_ratio"] * current_tpair_mprice
    matrix_top = round_tpair_price(matrix_top, config["tpair"])


    # "Matrix" will hold the pegs
    # "Matrix_Trade_State" will hold the order states (0=no order, too near market 1="buy" 2="sell"
    # "Matrix_Order_Id" will hold the OrderId associated with each peg
    matrix, matrix_trade_state, matrix_order_id = generate_matrix(matrix_bottom, matrix_top,
                                                              config["matrix_spread_percent"], config["tpair"])


    # WHAT AMOUNT OF FIAT ($, EURO, YUAN, YEN) ARE YOU OKAY WITH GIVING UP FOREVER
    # TO LEARN FROM THIS EXPERIENCE? What is initial investment amount?

    # EDEN STORE VALUE: (USER INITIAL INVESTMENT)
    # EDEN open file to record initial purchases and Matrix information
    logfile = open(str(config["matrix_log_fname"]), 'w')

    initial_investment = config["initial_investment"]
    initial_setup_fee = initial_investment * config["btce_trade_fee"]
    initial_investment -= initial_setup_fee

    # EDEN: DISPLAY: "WE WILL CALL THIS YOUR INITIAL INVESTMENT"


    # ***********************************************************************************************************
    # EDEN ASK: WHAT PERCENT OF INVESTMENT TO BE PUT IN MOON BASKET/MATRIX - .1, .3, .5?
    # ***********************************************************************************************************

    # Moon basket is a long term hold goal (say you want to pay off a credit card, or a car loan, how @ what price would it take)
    # moon_basket_factor
    # example: MOONBASKET FACTOR = .3
    # this is what could be a user defined
    # moon_basket_factor = .3

    # EDEN CALC: (initial_investment)*(moon_basket_factor) = (moon_basket_current_market_buy_amount) = 300

    moon_basket_current_market_buy_amount = initial_investment * config["moon_basket_factor"]

    # Set the price of the Moonbasket Sell to one peg above the matrix
    moon_basket_peg = round_tpair_price((matrix_top * config["matrix_spread_percent"]), config["tpair"])



    # your matrix won, now what do you want to do with your money

    # EDEN: (current_tpair_mprice)/(moon_basket_current_market_buy_amount) = (moonbasket_coins_count) 20
    moonbasket_coins_count = moon_basket_current_market_buy_amount / current_tpair_mprice
    moonbasket_coins_count = round_tpair_volume(moonbasket_coins_count, config["tpair"])

    # EDEN: BUY (moonbasket_coins_count) @ (current_tpair_mprice)
    # EDEN: AND CONFIRM TRANSACTION
    #trade_success, order_id = trade(config["tpair"], current_tpair_mprice, "buy", moonbasket_coins_count)
    if trade_success != 1:
        debugfile.write("Error Purchasing Moonbasket Coins (" + str(moonbasket_coins_count) + ")")
        exit(1)
    logfile.write("Moonbasket Volume = " + str(moonbasket_coins_count) + "\n")
    logfile.write("Moonbasket Bought Price = " + str(current_tpair_mprice) + "\n")


    # EDEN: SET MOONBASKET GOAL SELLS (moonbasket_coins_count @ one peg above matrix top)
    # EDEN CREATE SELL moonbasket_coins_count @ moon_basket_peg
    #trade_success, order_id = trade(config["tpair"], moon_basket_peg, "sell", moonbasket_coins_count)
    if trade_success != 1:
        debugfile.write("Error Creating Moonbasket Sale Order, Coins(" + str(moonbasket_coins_count) +
                        ") Price(" + str(moon_basket_peg) + ")")
        exit(1)
    logfile.write("Moonbasket Sell Price = " + str(moon_basket_peg) + '\n')


    #############################################################################################################
    # Buy Initial Matrix Investment
    ############################################################################################################
    # EDEN: WHAT RATIO OF MATRIX WOULD YOU LIKE TO CHOOSE 60/40 65/35?
    # EDEN: EXPLANATION OF BENEFIT OR MARKET CONDITIONS EACH APPROPIATE FOR
    matrix_investment = initial_investment - moon_basket_current_market_buy_amount

    # this is where we take our remaining $700 (non moon basket) investment and split it in to 2
    # $350 would go into a current market buy, those coins would be spread into a peg spread from 1 peg above market to 2 * current market
    # $350 would go into buys @ below market peg spreads down to .5 of current market.
    # this gives our buys more volume to protect against a falling market price
    # this gives our sells less volume but more of a spread and great value for selling off new coins
    below_market_buy = matrix_investment * .5
    above_market_buy = matrix_investment * .5
    above_market_coin_count = round_tpair_volume(above_market_buy / current_tpair_mprice, config["tpair"])
    number_of_pegs = len(matrix)

    # NOTE : WE ARE WORKING WITH A STATIC TRADE VOLUME HERE. IF THAT CHANGES LOOK FOR ALL INSTANCES OF TRADE_VOLUME IN
    # CODE AND ADJUST ACCORDINGLY
    starting_tpair_coins = matrix_investment / current_tpair_mprice
    trade_volume = starting_tpair_coins / number_of_pegs
    trade_volume = round_tpair_volume(trade_volume, config["tpair"])

    #trade_success, order_id = trade(config["tpair"], current_tpair_mprice, "buy", above_market_coin_count)
    if trade_success != 1:
        debugfile.write("Error Purchasing Matrix Investment Coins(" + str(above_market_coin_count) + ") Price(" +
                str(current_tpair_mprice) + ")\n" )
        exit(1)
    logfile.write("Matrix Coins Purchased = " + str(above_market_coin_count) + "\n")
    logfile.write("Matrix Coins Price Purchased = " + str(current_tpair_mprice) + '\n')
    logfile.write("Matrix Trade Volume = " + str(trade_volume) + "\n")

    # VANNY debugging Oct 4

    # ***********************************************************************************************************
    # SECTION B - ACTUALLY PRODUCE OUR MATRIX AND WRITE IT TO MFILE - UNLESS IT WAS ALREADY READ IN FROM AN MFILE
    # ***********************************************************************************************************

    # For each peg ask is this peg less than the market price we paid by an amount > the spread of 1.9% (rounded up)
    # if so then place a buy at our static volume and
    # store the value 1 in our matrix_trade_state
    # if peg value is greater than market price we paid by 1.9%
    # set a sell at our static volume till one below our top peg and
    # store the value 2 in our matrix_peg_state
    # also for peg <= spread below market
    # set matrix_trade_state associated to that peg index to 0
    # also store each trade id in matrix_trade_id in index equal to peg index #
    list_counter = 0

    for peg in matrix:
        if peg < current_tpair_mprice:
            if (peg * config["matrix_spread_percent"]) < current_tpair_mprice:
                #trade_success, order_id = trade(config["tpair"], peg, "buy", trade_volume)
                if trade_success != 1:
                    debugfile.write("Error Matrix Order Type:Buy Volume:" + str(trade_volume) + " Price:" + str(peg))
                    exit(1)
                matrix_trade_state[list_counter] = 1
                matrix_order_id[list_counter] = order_id
            else:
                matrix_trade_state[list_counter] = 0
                matrix_order_id[list_counter] = 0

        elif peg == current_tpair_mprice:
            matrix_trade_state[list_counter] = 0
            matrix_order_id[list_counter] = 0

        else:
            if (peg - (peg * config["matrix_spread_percent"])) <= current_tpair_mprice:
                #trade_success, order_id = trade(config["tpair"], peg, "sell", trade_volume)
                if trade_success != 1:
                    debugfile.write("Error Matrix Order Type:Sell Volume:" + str(trade_volume) + " Price:" + str(peg))
                    exit(1)
                matrix_trade_state[list_counter] = 2
                matrix_order_id[list_counter] = order_id

            else:
                matrix_trade_state[list_counter] = 0
                matrix_order_id[list_counter] = 0

        list_counter += 1
        matrix_established = 1
    # End of Loop to create matrix


    matrix_CSV = matrix
    print(matrix_CSV)


    write_matrix_file(mfile)
    write_matrix_CSV(mCSV)

# End of code to purchase moonbasket, initial invest, and to establish the matrix on WEX

# ***********************************************************************************************************
# SECTION C - EDEN LOGIC - LOOP THROUGH ACTIVE ORDERS AND UPDATE
# ***********************************************************************************************************

# ------------------------------------------------------------------------------------------------------
# EDEN HAS INITIAL MATRIX ESTABLISHED!
# WAIT 30 SECOND INTERVALS TO QUERY MARKET AND UPDATE AT THOSE INTERVALS
# SEE LOGIC LOOP TO UNDERSTAND UPDATES
#------------------------------------------------------------------------------------------------------

# This will be done in loop but put here
'''

# ----> PUT IN LOOP ---> LOOP ---> PUT IN LOOP --> PUT IN LOOP --> PUT IN LOOP --> PUT IN LOOP
success = 1
matrix_file_update_needed = 0

# This turns off the Program to update orders!! Debug Success=0, Run Mode success = 1
success = 1
first_pass = 1
while (success == 1):
    time.sleep(2)
    matrix_update_needed = 0
    matrix_prev_trade_state = []

    # Reset variables that track Trade States
    # Move last trade state reality into matrix_prev_trade_state
    for pos, state in enumerate(matrix_trade_state):
        assert isinstance(state, object)
        matrix_prev_trade_state.append(state)
        matrix_trade_state[pos] = 0

    soldup_indexes = []

    # First time run through - if there was already a matrix established in a file read in
    # then the last_tpair_mprice is given there. Then after the first update, we will keep up with
    # more current tprices
    if matrix_preestablished != 1:
        last_tpair_mprice = current_tpair_mprice
        matrix_preestablished = 0

    # Get the new current market price
    depth = marketdepth(config["tpair"], 5)
    if depth is None:
        print "Error connecting to wex.nz"
        exit(1)

    # Debug make sure these asks look appropriate
    current_tpair_mprice = depth[0][4][0]
    debugfile.write("Current Market : " + str(current_tpair_mprice) + "\n")

    #------------------------------------------------------------------------------------------------------
    # EDEN LOGIC LOOP
    #-----------------------------------------------------------------------------------------------------
    # ***********************************************************************************************************
    # SECTION C1 : GET THE MATRIX_TRADE_STATES ARRAY UPDATED TO INDICATE BOUGHTS AND SOLDS
    # ***********************************************************************************************************
    
    # Now get activeOrders
    # 1) IF current_tpair_mprice > last_tpair_mprice
    # WERE THERE BUYS (in other words, market dipped low before going higher)?
    # 1A) YES : then do a) sell off all those buys at new higher market val price, and refill those buy pegs right back in
    #            and do b) for all sells, fill in buy pegs at one peg below
    # 1B) NO: then just b) for all sells, fill in buy pegs at one peg below
    # 2) IF current_tpair_mprice < last_tpair_mprice
    # WERE THERE SELLS? (in other words market went high before going low)
    # 2A) YES : then do a) purchase low with all the coins sold and replace those sell pegs
    #            and do b) for all buys, fill in sell pegs at one price higher

    a_orders = activeorders(config["tpair"])
#    matrix_has_active_order = [0 for _ in matrix]
    matrix_gap_idx = find_matrix_gap_idx(current_tpair_mprice, matrix)


    if a_orders == None:
        debugfile.write("No active Orders\n")
        success = 0
    else:
        # UPDATE MATRIX_TRADE_STATE
        # 1=HAS BUY ORDER
        # 2=HAS SELL ORDER
        # -1=BOUGHT
        # -2= SOLD
        for order in a_orders:
            # logfile.write("Active Order: " + str(order["amount"]) + "[" + str(order["rate"]) + "]["
            #       + str(order["type"]) + "]\n")

            rounded_rate = round_tpair_price(order[0], config["tpair"])

            #debugfile.write("Rounded rate for order [" + str(rounded_rate) +"]\n")
            # debug vanny take this out
            #matrix_update_needed = 0
            #success = 0
            # ********************************

            # Ignore the moon_basket_peg
            if rounded_rate == moon_basket_peg:
                break
            else:
                try:
                    matrix_peg_index = matrix.index(rounded_rate)
                except:
                    debugfile.write("Unable to correlate active order with price " + str(rounded_rate) + "to matrix entry\n")
                    exit_program(1, mfile)

                # LOOPING THROUGH EVERY ACTIVE ORDER, INDICATE IF THERE IS A BUY OR SELL THERE
                if (str(order[1]) == str("buy")):
                    matrix_trade_state[matrix_peg_index] = 1
                elif (str(order[1]) == str("sell")):
                    matrix_trade_state[matrix_peg_index] = 2
                else:
                    debugfile.write("Unknown trade state in Active order State:" + str(order["type"]))
                    exit_program(1, mfile)
        # ***********************************************************************************************************
        # SECTION C3 : UPDATE THE MARKET WITH NEW BUYS AND SELLS ACCORDING TO PEGS THAT POPPED
        # ***********************************************************************************************************
        # FOR A HIGH MARKET............
        if current_tpair_mprice > last_tpair_mprice:

            # We want the gap index to be below market in this situation
#            if matrix[matrix_gap_idx] > current_tpair_mprice:
#                matrix_gap_idx -= 1

            # CHECK IF IT DIPPED DOWN TO DO BUYS ALSO IN THIS TIME INTERVAL OR IF ONLY DID SELLS
            # IF DID DIP, SELL ALL THOSE BUYS AT CURRENT MARKET, THEN PUT THEM IN AS BUY PEGS AGAIN
            # This code handles ALL buys

            # -------------------------------------------------------------------------------
            # --- START If you manually fix the Matrix File before running we don't need to do this
            # -------------------------------------------------------------------------------
            # Count how many units were bought down below old market price
            # This will also fill in the old gap if the gap was below market
            #  * * * COINS BOUGHT REALLY LOW * * *
            need_to_sell_trade_volume = 0
            for index, price in enumerate(matrix):
                if (price < last_tpair_mprice):
                    if matrix_trade_state[index] == 0 and index != matrix_gap_idx:
                        need_to_sell_trade_volume += trade_volume
                        need_to_sell_price = price

            # Also count to see if any units were sold even higher than new market price
            # * * * COINS SOLD REALLY HIGH * * *
            need_to_buy_trade_volume = 0
            for index, price in enumerate(matrix):
                if (price > current_tpair_mprice):
                    if matrix_trade_state[index] == 0 and index != matrix_gap_idx:
                        need_to_buy_trade_volume += trade_volume
                        need_to_buy_price = price

            # Only buy/sell the difference of these two
            if need_to_buy_trade_volume > need_to_sell_trade_volume:
                need_to_buy_trade_volume = need_to_buy_trade_volume - need_to_sell_trade_volume
            elif need_to_sell_trade_volume > need_to_buy_trade_volume:
                need_to_sell_trade_volume = need_to_sell_trade_volume - need_to_buy_trade_volume
            else:
                need_to_sell_trade_volume = 0
                need_to_buy_trade_volume = 0


            # If more coins were bought down below OLD market price, then sell these extras,
            # Debug : 0.1 is supposed ot sell at best price close to market.
            if need_to_sell_trade_volume > 0:
                trade_success, order_id = trade(config["tpair"], need_to_sell_price, "sell", need_to_sell_trade_volume)  # will sell at market
                if trade_success != 1:
                    debugfile.write(
                        "Error Retrace Order Type:Sell Volume:" + str(need_to_sell_trade_volume) + " Price:Market\n")
                    matrix_trade_state[index] = 99
                    matrix_order_id[index] = 99
                    exit_program(1, mfile)
                # Check if the Sell at Market actually happened

            # If more coins were bought high above current new higher market price, then buy these extras,
            # they end up going back in as sells after we finish the main logic for the higher market case
            # Debug : 0.1 is supposed ot sell at best price close to market.
            elif need_to_buy_trade_volume > 0:
                trade_success, order_id = trade(config["tpair"], need_to_buy_price, "buy", need_to_buy_trade_volume)  # will sell at market
                if trade_success != 1:
                    debugfile.write(
                        "Error Retrace Order Type:Buy Volume:" + str(need_to_buy_trade_volume) + " Price:Market\n")
                    matrix_trade_state[index] = 99
                    matrix_order_id[index] = 99
                    exit_program(1, mfile)
                    # Check if the Buy at Market actually happened

            # -----------------------------------------------------------------------------------
            # END  If you manually fix the Matrix File before running we don't need to do this
            # ----------------------------------------------------------------------------------

            # FILL in ALL OPENS (BOUGHTS) WITH SAME BUYS THAT WERE BELOW LAST MARKET PRICE
            # * * * COINS BOUGHT REALLY LOW, FILL THEM BACK IN AS IS * * *
            for index, price in enumerate(matrix):
                if matrix_trade_state[index] == 0:
                    if price < last_tpair_mprice:
                        trade_success, order_id = trade(config["tpair"], matrix[index], "buy", trade_volume)
                        if trade_success != 1:
                            debugfile.write(
                                "Error Retrace Order Type:Buy Volume:" + str(trade_volume) + " Price:" + str(
                                    matrix[index]))
                            matrix_trade_state[index] = -99
                            matrix_order_id[index] = -99
                            exit_program(1, mfile)

                        matrix_trade_state[index] = 1
                        matrix_order_id[index] = order_id

            # * * * USUAL CASE - SOLD HIGHER, SO BUY ONE LOWER * * *
            # FILL ALL REST OF OPENS (SOLDS) WITH BUYS UP TO ONE SPOT LOWER THAN MARKET (AKA AT THE GAP)
            # DONT HAVE TO CHECK FOR GAP BECAUSE THIS WILL NATURALLY PUT A GAP IN RIGHT BELOW CURRENT MARKET
            for index, price in enumerate(matrix):
                if matrix_trade_state[index] == 0:
                    # This is your typical case! Sold higher, Buy one Lower!
                    if price <= current_tpair_mprice:
                        if index == 0:
                            debugfile.write("Error Sold at Lowest Matrix Point, Cant reset buy at price: " + str(price))
                            exit_program(1, mfile)
                        else:
                            trade_success, order_id = trade(config["tpair"], matrix[index-1], "buy", trade_volume)
                            if trade_success != 1:
                                debugfile.write(
                                    "Error Retrace Order Type:Buy Volume:" + str(trade_volume) + " Price:" + str(
                                        matrix[index-1]))
                                matrix_trade_state[index-1] = -99
                                matrix_order_id[index-1] = -99
                                exit_program(1, mfile)

                            matrix_trade_state[index-1] = 1
                            matrix_order_id[index-1] = order_id

                    # * * * COINS SOLD AT REALLY HIGH, MARKET BACK DOWN, JUST PUT BACK IN * * *
                    # Then in the case where the market went higher up too before it came back to down to this price
                    # This can be checked by seeing if there are open slots above current market
                    # Then we put them back in as sells (we already have enough coins bought to do this)
                    else:
                        trade_success, order_id = trade(config["tpair"], price, "sell", trade_volume)
                        if trade_success != 1:
                            debugfile.write(
                                "Error Retrace Order Type:Sell Volume:" + str(trade_volume) + " Price:" + str(
                                    price))
                            matrix_trade_state[index] = 99
                            matrix_order_id[index] = 99
                            exit_program(1, mfile)

                        matrix_trade_state[index] = 2
                        matrix_order_id[index] = order_id


        # VANNY HERE IS WHERE WE START WORKING AGAIN
        # FOR A LOW MARKET...............
        else:

            # We want the gap index to be above market in this situation
#            if current_tpair_mprice > matrix[matrix_gap_idx]:
#                matrix_gap_idx += 1

            # -------------------------------------------------------------------------------
            # --- START If you manually fix the Matrix File before running we don't need to do this
            # -------------------------------------------------------------------------------
            # Count to see if any units were bought even lower than new market price
            # * * * COINS BOUGHT REALLY LOW * * *
            need_to_sell_trade_volume = 0
            for index, price in enumerate(matrix):
                if (price > current_tpair_mprice):
                    if matrix_trade_state[index] == 0 and index != matrix_gap_idx:
                        need_to_sell_trade_volume += trade_volume
                        need_to_sell_price = price

            # Count how many units were sold even above the old market price
            # * * * COINS SOLD REALLY HIGH * * *
            need_to_buy_trade_volume = 0
            for index, price in enumerate(matrix):
                if (price > last_tpair_mprice):
                    if matrix_trade_state[index] == 0 and index != matrix_gap_idx:
                        need_to_buy_trade_volume += trade_volume
                        need_to_buy_price = price

            # Only buy/sell the difference of these two
            if need_to_buy_trade_volume > need_to_sell_trade_volume:
                need_to_buy_trade_volume = need_to_buy_trade_volume - need_to_sell_trade_volume
            elif need_to_sell_trade_volume > need_to_buy_trade_volume:
                need_to_sell_trade_volume = need_to_sell_trade_volume - need_to_buy_trade_volume
            else:
                need_to_sell_trade_volume = 0
                need_to_buy_trade_volume = 0


            # If more coins were sold up above OLD market price, then buy this amount extra,
            # they end up going back in as sells naturally in the code
            # Debug : 0.1 is supposed ot buy at best price close to market.
            if need_to_buy_trade_volume > 0:
                trade_success, order_id = trade(config["tpair"], need_to_buy_price, "buy", need_to_buy_trade_volume)  # will sell at market
                if trade_success != 1:
                    debugfile.write(
                        "Error Retrace Order Type:Buy Volume:" + str(need_to_buy_trade_volume) + " Price:Market\n")
                    matrix_trade_state[index] = -99
                    matrix_order_id[index] = -99
                    exit_program(1, mfile)

            # If more coins were bought high above current new higher market price, then buy these extras,
            # they end up going back in as sells after we finish the main logic for the higher market case
            # Debug : 0.1 is supposed ot sell at best price close to market.
            elif need_to_sell_trade_volume > 0:
                trade_success, order_id = trade(config["tpair"], need_to_sell_price, "sell", need_to_sell_trade_volume)  # will sell at market
                if trade_success != 1:
                    debugfile.write(
                        "Error Retrace Order Type:Sell Volume:" + str(need_to_sell_trade_volume) + " Price:Market \n")
                    matrix_trade_state[index] = 99
                    matrix_order_id[index] = 99
                    exit_program(1, mfile)

            # -----------------------------------------------------------------------------------
            # END  If you manually fix the Matrix File before running we don't need to do this
            # ----------------------------------------------------------------------------------

            # COINS SOLD REALLY HIGH, PUT BACK IN AS THEY WERE, MARKET BACK DOWN FROM THERE
            for index, price in enumerate(matrix):
                if price > last_tpair_mprice:
                    if matrix_trade_state[index] == 0:
                        trade_success, order_id = trade(config["tpair"], price, "sell", trade_volume)
                        if trade_success != 1:
                            debugfile.write(
                                "Error Retrace Order Type:Sell Volume:" + str(trade_volume) + " Price:" + str(
                                        price))
                            matrix_trade_state[index] = 99
                            matrix_order_id[index] = 99
                            exit_program(1, mfile)

                        matrix_trade_state[index] = 2
                        matrix_order_id[index] = order_id

                # THEN REPLACE ALL BUYS WITH SELLS ONE SPOT HIGHER
                for index, price in enumerate(matrix):
                    if matrix_trade_state[index] == 0:
                        # Here is our typical case. Bought a little lower, let's sell one higher!
                        if price >= current_tpair_mprice:
                                if (index + 1) > (len(matrix)-1):
                                    debugfile.write("Error, Trying to Sell outside of our Matrix above Price:" + str(matrix[index]))
                                    exit_program(1, mfile)
                                else:
                                    trade_success, order_id = trade(config["tpair"], matrix[index+1], "sell", trade_volume)
                                    if trade_success != 1:
                                        debugfile.write(
                                            "Error Retrace Order Type:Sell Volume:" + str(trade_volume) + " Price:" + str(
                                                matrix[index+1]))
                                        matrix_trade_state[index+1] = 99
                                        matrix_order_id[index+1] = 99
                                        exit_program(1,mfile)

                                    matrix_order_id[index+1] = order_id
                                    soldup_indexes.append(index+1)

                        # If they were buys lower Then current price, go ahead and
                        # sell at market and put back in as buys as the same prices
                        else:
                            trade_success, order_id = trade(config["tpair"], matrix[index], "buy", trade_volume)
                            if trade_success != 1:
                                debugfile.write(
                                    "Error Retrace Order Type:Sell Volume:" + str(trade_volume) + " Price:" + str(
                                        matrix[index]))
                                exit_program(1, mfile)

                            matrix_trade_state[index] = 1
                            matrix_order_id[index] = order_id

                # We couldn't reset the trade_state pegs to Sells above in order to not break looping on the
                # next peg, so we do it here in this extra littel loop (otherwise we could loop backwards through
                #the Sell code in the low market then we wouldn't need to do this separately)
                for idxval in soldup_indexes:
                    matrix_trade_state[idxval] = 2


    last_tpair_mprice = current_tpair_mprice

# End of Action Bot Loop acting on active orders


# Housekeeping
logfile.close()
debugfile.close()

# Rewrite Matrix File and Exit Program
exit_program(0, mfile)



# Next to do
# A daily coin free coin counter
# Since investors are so Value based when looking at performance
# we need a new coin counter to track how much new coin we've made today
# so for NMC today I've made 6 new NMC
# Original buy got me say 100, now I have 106 for the same initial investment
# So say the overall value has gone down from $200 to $180
# The investor should appreciate that they only initially got 100
# NMC for their initial investment
# They can now sell 6 coins without affecting their
# initial investment

# Another to do
# A GUI, lets you quit program manually and will call exit_program so closes up with housecleaning
# instead of a kill

'''