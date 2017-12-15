#!/usr/bin/env python
'''
    Copyright (c) 2017 by Jayson Rahmlow <jayson.rahmlow@gmail.com>
      and Vanessa Rahmlow <vanessarahmlow@gmail.com>

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
from datetime import datetime
import requests
import json
import numpy as np
from utils import *
import shutil
import copy


# *******************************************************************************************************
# ********************************* DEFINE FUNCTIONS *********************************************
# *******************************************************************************************************

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

#    h = hmac.new(str(config["BTCE_API_SECRET"]), digestmod=hashlib.sha512)
    h = hmac.new(secret, digestmod=hashlib.sha512)
    h.update(urllib.urlencode(params))

    trade_headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Key": key,
        "Sign": h.hexdigest(),
    }

    response = requests.post(
        "https://wex.nz/tapi", headers=trade_headers, data=params)

    print '[%s] %s %s' % (method, response.status_code, response.reason)
    return response


def marketdepth(tpair, limit=150):
    """Returns a tuple containing (asks, bids)."""

    try:
        resp = requests.get(
            "https://wex.nz/api/3/depth/" + tpair, params={"limit": limit})
    except requests.exceptions.ConnectionError:
        return None

    if resp.status_code == 200:
        data = resp.json()
        data = data.get(tpair)
        return data.get("asks"), data.get("bids")
    else:
        return None


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
        debugfile.write(str(ttype) + " order " + str(amount) + str(tpair) + " at price " + str(rate) + "Time: " + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + "\n")
        recent_trades = True
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

    number_of_tries = 0
    params = {}
    if tpair is not None:
        params["pair"] = tpair
    while number_of_tries < 5:
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
            if number_of_tries < 5:
                number_of_tries += 1
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

def find_matrix_gap_idx_and_peg(current_price, matrixlist):
    # type: (object, object) -> object

    gap_idx = (np.abs(np.asarray(matrixlist) - current_price)).argmin()
    if gap_idx <= 0:
        debugfile.write("Error determining Matrix Gap")
        exit(1)
    if gap_idx > (len(matrixlist)-1):
        debugfile.write("Error determining Matrix Gap")
        exit(1)
    else:
        return gap_idx, matrixlist[gap_idx]

def write_matrix_file(mfile):
    # type: (object) -> object

    # Always get up to date Market Price
    depth = marketdepth(config["tpair"])
    if depth is None:
        debugfile.write("Error connecting to wex.nz to check market price.\n")
        mprice = last_tpair_mprice
    else:
        mprice = depth[0][1][0]

    mfile.write("INITIAL_MARKET_PRICE=" + str(initial_tpair_mprice) + "\n")
    mfile.write("MARKET_PRICE=" + str(mprice) + "\n")
    mfile.write("MOON_BASKET_PRICE=" + str(moon_basket_peg) + "\n")
    mfile.write("TRADE_VOLUME=" + str(trade_volume) + "\n")
    mfile.write("MATRIX=" + "\n")

    for index, peg in enumerate(matrix):
            mfile.write("[" + str(index) + "],[" + str(peg) + "],["
            + str(matrix_trade_state[index])
           + "],[" + str(matrix_order_id[index]) + "]\n")



def exit_program(rc):

    backup_matrix_file()

    try:
        matrix_file_handle = open(config['matrix_fname'], 'w')
    except error_to_catch:
        debugfile.write("Error opening Matrix file " + str(config['matrix_fname']))
    else:
        write_matrix_file(matrix_file_handle)
        mfile.close()

    exit(rc)


def backup_matrix_file():
    error_to_catch = getattr(__builtins__, 'FileNotFoundError', IOError)
    try:
        # Does the matrix.txt file exist?
        mfile = open(str(config["matrix_fname"]), 'r')

    except error_to_catch:
        debugfile.write("Error opening Matrix file " + str(config['matrix_fname']))
    else:
        mfile.close()

    new_fname = str(config["matrix_dir"]) + "/Matrix_" + str(config['tpair']) +"_backup.txt"
    shutil.copy(config['matrix_fname'], new_fname)


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


# ***********************************************************************************************************
# SECTION A - INITIALIZATIONS
# ***********************************************************************************************************
matrix_established = 0
matrix_preestablished = 0
matrix_bottom = -1
matrix_top = -1
matrix = []
matrix_trade_state = []
matrix_order_id = []
initial_tpair_mprice = -1
current_tpair_mprice = -1
last_tpair_mprice = -1
moon_basket_peg = -1
trade_volume = -1
key = ""
secret = ""
last_matrix_gap_idx = -1
recent_trades = False
perform_retrace_trade_orders = 1
config_filename = ""
# Vanny - change when you run on new market
config_filename = "/Users/vannycat/PycharmProjects/EdenMatrixTrading/Bryn_wex_dsh_ltc/config_wex_dsh_ltc.json"

####################################################################################
### GUI STUFF HERE
### Make a gui for all this
# Request and read config
if config_filename == "":
    config_filename = input("Provide Config File to indicate your Market & Exchange Currency, and financial investment preferences :\n")
print "Confirming config file: " + str(config_filename) + "\n"
config = read_config(config_filename)

# Open a debug file for debug data
temp_debug_filename = str(config["matrix_dir"]) + "/debug_" + str(config["trade_style"]) + "_" + str(config["tpair"]) + ".txt"
debugfile = open(temp_debug_filename, 'w+')


#print "Do you want to run in Trade mode (conduct all trades) or generate Data Only mode? (Generate Matrix & Data)"
D = 1
T = 2
Q = 3
d = D
t = T
q = Q
dont_trade_input = input("T or D :")
if dont_trade_input == T:
    dont_trade = 0
    debugfile.write("Trade Mode is On. Conducting all trades to respond to market. \n")
elif dont_trade_input == D:
    debugfile.write("Data Generation Mode is On. No trades will auto run.\nCreating Matrix File if one doesn't exist and printing trades that will respond to Market. \n")
    dont_trade = 1
elif dont_trade_input == Q:
    print "Quitting program."
    exit(0)
else:
    print "Unrecognized response. Exiting program\n"
    exit(14)


# Read in financial info to log in
info_filename = input("Please provide account info filename:")
info_file = open(info_filename, 'r')

linenum = 0
info_file_lines = info_file.readlines()
for info_file_line in info_file_lines:
    if linenum == 0:
        key = info_file_line.strip()
    elif linenum == 1:
        secret = info_file_lines[1].strip()
    else:
        print "Ignoring this line: info_file_line \n"
    linenum += 1
info_file.close()

############ END OF GUI STUFF


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
    if len(mfile_lines) < 6:
        # Not really a valid Matrix file. Close the read handle, and open a writing handle to make Matrix file
        mfile.close()
        backup_matrix_file()
        mfile = open(str(config["matrix_fname"]), 'w')
        matrix_established = 0
    else :
        debugfile.write("Using PreEstablished Matrix\n")
        # Backup Matrix File
        backup_matrix_file()

        # Code to read Matrix File
        # Can't use exit_rc function in this block because mfile is 'r' not 'w'
        linenum = 0
        for mfile_line in mfile_lines:
            #debugfile.write("MFILE Line: " + str(mfile_line) + "\n")

            mfile_line.rstrip()
            debugfile.write(str(mfile_line))

            if mfile_line.find("[") != -1:
                mfile_line_parsed = mfile_line.split(",")
                mfile_line_index = int(mfile_line_parsed[0].strip('[]'))
                #debugfile.write("Index:" + str(mfile_line_index) + "\n")

                matrix.append(round_tpair_price(float(mfile_line_parsed[1].strip('[]')),config["tpair"]))
                #debugfile.write("Peg:" + str(matrix[mfile_line_index]) + "\n")

                # Note the Matrix Gap Index with a 3
                if int(mfile_line_parsed[2].strip('[]')) == 3:
                    if last_matrix_gap_idx != -1:
                        debugfile.write("Error. More than one Matrix Gap Index in Matrix File.\n")
                        exit_program(1)
                    last_matrix_gap_idx = int(mfile_line_parsed[0].strip('[]'))

                matrix_trade_state.append(int(mfile_line_parsed[2].strip('[]')))
                #debugfile.write("Trade_state:" + str(matrix_trade_state[mfile_line_index]) + "\n")

                matrix_order_id.append(int(mfile_line_parsed[3].strip('[]\n')))
                #debugfile.write("Order Id:" + str(matrix_order_id[mfile_line_index]) + "\n")

            elif linenum == 0:
                if mfile_line.find("INITIAL_MARKET_PRICE") != -1:
                    # Needs to be fixed
                    initial_tpair_mprice = round_tpair_price(float(mfile_line.split("=")[1]), config["tpair"])
                else:
                    debugfile.write("Error reading Matrix File\n")
                    exit(1)
            elif linenum == 1:
                if mfile_line.find("MARKET_PRICE") != -1:
                    # Needs to be fixed
                    last_tpair_mprice = round_tpair_price(float(mfile_line.split("=")[1]), config["tpair"])
#                    debugfile.write("PREVIOUS MARKET PRICE = " + last_tpair_mprice + "\n")
                else:
                    debugfile.write("Error reading Matrix File\n")
                    exit(1)
            elif linenum == 2:
                if mfile_line.find("MOON_BASKET_PRICE") != -1:
                    moon_basket_peg = round_tpair_price(float(mfile_line.split("=")[1]), config["tpair"])
                else:
                    debugfile.write("Error reading Matrix File\n")
                    exit(1)
            elif linenum == 3:
                if mfile_line.find("TRADE_VOLUME") != -1:
                    trade_volume = round_tpair_volume(float(mfile_line.split("=")[1]), config["tpair"])
                else:
                    debugfile.write("Error reading Matrix File\n")
                    exit(1)

            linenum += 1
            matrix_established = 1

        # Close the Read Handle
        mfile.close()

        # Assign this variable to be the current tpair price - this is for the first time run through the trade loop
        last_tfile_mprice = initial_tpair_mprice
# End of code to read in Matrix.txt file


if matrix_established == 0:

    Y = 1
    N = 2
    y = Y
    n = N
    if (dont_trade == 0):
        print "No matrix established. Eden will generate matrix file and establish positions in the market. Do you want to Proceed?"
        user_input = input("Y or N:")
        if user_input == N or user_input == n:
            print "Program Quitting"
            exit(10)
        elif user_input == Y or user_input == y:
            print "Proceeding... \n"
        else:
            print "Invalid response. Program Quitting"
            exit(11)

    else:
        print "No matrix established. Program is in Dont Trade Mode. Eden will generate matrix file only."

    # ***********************************************************************************************************
    # Get Current Market Price
    # ***********************************************************************************************************

    if config["tpair_set_market_start_price"] != "" and float(config["tpair_set_market_start_price"]) > 0:
        current_tpair_mprice = float(config["tpair_set_market_start_price"])
        initial_tpair_mprice = float(config["tpair_set_market_start_price"])

    elif config["exchange_choice"] == "wex.nz":
        depth = marketdepth(config["tpair"])
        if depth is None:
            print "Error connecting to wex.nz"
            exit(1)

        # Debug make sure these asks look appropriate
        current_tpair_mprice = depth[0][1][0]
        initial_tpair_mprice = depth[0][1][0]

    # Debug vanny - just assign market prices for now.
    # Need to query market and put this in
    elif config["exchange_choice"] == "gdax.com":
        #current_tpair_mprice = .00930
        #initial_tpair_mprice = .00930
        print "Please set current tpair price manually in software or in config file."
        exit(1)
    else:
        debugfile.write("We don't have software created for markets other than wex.nz and gdax.com yet. Stay tuned!\n")
        exit(1)

    # Open the Matrix.txt file
    error_to_catch = getattr(__builtins__, 'FileNotFoundError', IOError)
    try:
        # Does the matrix.txt file exist with valid data
        mfile = open(str(config["matrix_fname"]), 'w')

    except error_to_catch:
        debugfile.write(str(config["matrix_fname"]) + " can not be opened")
        exit(1)

    # Generate the matrix of pegs (and the corresponding trading state matrix)
    # ------------------------------------------------ WORK TO BE DONE HERE -----------------------------------------
    # For the moment the bottom and top are defined with hard limits but this will change to be related to the current
    # market price, so the matrix_bottom and matrix_top will be taken out of config file then and calculated here
    # ------------------------------------------------ WORK TO BE DONE HERE -----------------------------------------
    matrix_bottom = config["matrix_bottom_ratio"] * initial_tpair_mprice
    matrix_bottom = round_tpair_price(matrix_bottom, config["tpair"])
    matrix_top = config["matrix_top_ratio"] * initial_tpair_mprice
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
    initial_investment = config["initial_investment"]
    initial_setup_fee = initial_investment * config["wex_trade_fee"]
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
    moon_basket_trade_fee = moon_basket_current_market_buy_amount * config["wex_trade_fee"]

    # Set the price of the Moonbasket Sell to one peg above the matrix
    moon_basket_peg = round_tpair_price((matrix_top * config["matrix_spread_percent"]), config["tpair"])



    # your matrix won, now what do you want to do with your money

    # EDEN: (initial_tpair_mprice)/(moon_basket_current_market_buy_amount) = (moonbasket_coins_count) 20
    moonbasket_coins_count = moon_basket_current_market_buy_amount / initial_tpair_mprice
    moonbasket_coins_count = round_tpair_volume(moonbasket_coins_count, config["tpair"])

    # if not in data only mode, see if we should do init investment and/or do retraces?
    if dont_trade == 0:
        # Query User Do they want to Perform the Initial investment purchase & set up matrix?
        # Do they just want to turn on Retrace Engine?
        # Or both?
        I = 1
        R = 2
        B = 3
        i = I
        r = R
        b = B

        print "Matrix values are known. Preparing to Trade. Do you want to set up Initial Matrix (I), Initiate Matrix Retrace Trading (R), or" \
              "do Both (B) ?\n"
        type_of_trades_to_set_input = input("I or R or B :")
        if type_of_trades_to_set_input == I:
            perform_initial_trade_orders = 1
            perform_retrace_trade_orders = 0
            debugfile.write("Purchasing Moonbasket and Initial Investments and setting Moonbasket Sell and setting Matrix Trade Orders in Market. No retrace strategy running. \n")
        elif type_of_trades_to_set_input == R:
            perform_retrace_trade_orders = 1
            perform_initial_trade_orders = 0
            debugfile.write(" Turning on Eden engine to perform active trade retraces. \n")
        elif dont_trade_input == B:
            perform_retrace_trade_orders = 1
            perform_initial_trade_orders = 1
        else:
            print "Unrecognized response. Exiting program\n"
            exit(14)

    # EDEN: BUY (moonbasket_coins_count) @ (initial_tpair_mprice)
    # EDEN: AND CONFIRM TRANSACTION
    # Vanny 121417
    if dont_trade != 1:
        # trade_success, order_id = trade(config["tpair"], initial_tpair_mprice, "buy", moonbasket_coins_count)
        #if trade_success != 1:
        #    debugfile.write("Error Purchasing Moonbasket Coins (" + str(moonbasket_coins_count) + ")")
        #    exit(1)
        debugfile.write("Moonbasket Volume = " + str(moonbasket_coins_count) + "\n")
        debugfile.write("Moonbasket Bought Price = " + str(initial_tpair_mprice) + "\n")

    # Subtract the trade Fee paid on teh Moonbasket Purchase
    moonbasket_coins_count = (moon_basket_current_market_buy_amount - moon_basket_trade_fee) / initial_tpair_mprice
    moonbasket_coins_count = round_down_tpair_volume(moonbasket_coins_count, config["tpair"])
    debugfile.write("Moonbasket Coin Count: " + str(moonbasket_coins_count) + "\n")



    # EDEN: SET MOONBASKET GOAL SELLS (moonbasket_coins_count @ one peg above matrix top)
    # EDEN CREATE SELL moonbasket_coins_count @ moon_basket_peg
    # Vanny 121417
    if dont_trade != 1:
        #trade_success, order_id = trade(config["tpair"], moon_basket_peg, "sell", moonbasket_coins_count)
        #if trade_success != 1:
        #    debugfile.write("Error Creating Moonbasket Sale Order, Coins(" + str(moonbasket_coins_count) +
        #                    ") Price(" + str(moon_basket_peg) + ")")
        #    exit(1)
        debugfile.write("Moonbasket Sell Price = " + str(moon_basket_peg) + '\n')


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
    above_market_coin_count = round_tpair_volume(above_market_buy / initial_tpair_mprice, config["tpair"])
    number_of_pegs = len(matrix)

    debugfile.write("Above Market Coins Count (to sell): " + str(above_market_coin_count) + "\n")


    # NOTE : WE ARE WORKING WITH A STATIC TRADE VOLUME HERE. IF THAT CHANGES LOOK FOR ALL INSTANCES OF TRADE_VOLUME IN
    # CODE AND ADJUST ACCORDINGLY
    starting_tpair_coins = matrix_investment / initial_tpair_mprice
    trade_volume = starting_tpair_coins / number_of_pegs
    trade_volume = round_down_tpair_volume(trade_volume, config["tpair"])

    # Vanny 121417
    if (dont_trade != 1):
        #trade_success, order_id = trade(config["tpair"], initial_tpair_mprice, "buy", above_market_coin_count)
        #if trade_success != 1:
        #    debugfile.write("Error Purchasing Matrix Investment Coins(" + str(above_market_coin_count) + ") Price(" +
        #            str(initial_tpair_mprice) + ")\n" )
        #    exit(1)
        debugfile.write("Matrix Coins Purchased = " + str(above_market_coin_count) + "\n")
        debugfile.write("Matrix Coins Price Purchased = " + str(initial_tpair_mprice) + '\n')
        debugfile.write("Matrix Trade Volume = " + str(trade_volume) + "\n")

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
    order_id = 99

    last_matrix_gap_idx, gap_peg = find_matrix_gap_idx_and_peg(initial_tpair_mprice, matrix)
    for peg in matrix:
        if peg == gap_peg:
            matrix_trade_state[list_counter] = 3
            matrix_order_id[list_counter] = 0

        elif peg < initial_tpair_mprice:
            if (dont_trade != 1):
                trade_success, order_id = trade(config["tpair"], peg, "buy", trade_volume)
                if trade_success != 1:
                    debugfile.write("Error Matrix Order Type:Buy Volume:" + str(trade_volume) + " Price:" + str(peg))
                    exit(1)
            matrix_trade_state[list_counter] = 1
            matrix_order_id[list_counter] = order_id

        elif peg > initial_tpair_mprice:
            if (dont_trade != 1):
                trade_success, order_id = trade(config["tpair"], peg, "sell", trade_volume)
                if trade_success != 1:
                    debugfile.write("Error Matrix Order Type:Sell Volume:" + str(trade_volume) + " Price:" + str(peg))
                    exit(1)
            matrix_trade_state[list_counter] = 2
            matrix_order_id[list_counter] = order_id

        else:
            debugfile("Peg at price " + str(peg) + " can't be assigned a trade_state.\n")
            exit(1)

        list_counter += 1
        matrix_established = 1
    # End of Loop to create matrix

    write_matrix_file(mfile)
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


# ----> PUT IN LOOP ---> LOOP ---> PUT IN LOOP --> PUT IN LOOP --> PUT IN LOOP --> PUT IN LOOP
success = 1
matrix_file_update_needed = 0
soldup_indexes = []
rebuy_low_pegs = []
resell_high_pegs = []
last_matrix_trade_state = []
depth_call_failed = 0

# This turns off the Program to update orders!! Debug Success=0, Run Mode success = 1
if (dont_trade == 1 or perform_retrace_trade_orders == 0):
    success = 0
else:
    success = 1

while (success == 1):

    number_of_active_orders = 0

    # Get the new current market price
    depth = marketdepth(config["tpair"])
    if depth is None:
        while (depth_call_failed < 10 and depth is None):
            debugfile.write("Error connecting to wex.nz. Retrying... \n")
            time.sleep(10)
            depth = marketdepth(config["tpair"])
            depth_call_failed += 1
        if depth is None:
            debugfile.write("Exited program. Unable to connect to wex.nz to check market price. \n")
            exit(1)
    current_tpair_mprice = depth[0][1][0]
    # debugfile.write("Current Market : " + str(current_tpair_mprice) + "\n")

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

    if recent_trades:
        time.sleep(20)
        recent_trades = False
    a_orders = activeorders(config["tpair"])
    if a_orders == None:
        number_of_active_orders = 0
    else:
        number_of_active_orders = len(a_orders)

#    matrix_has_active_order = [0 for _ in matrix]
    matrix_gap_idx, gap_peg = find_matrix_gap_idx_and_peg(current_tpair_mprice, matrix)

    del soldup_indexes[:]
    del rebuy_low_pegs[:]
    del resell_high_pegs[:]
    del last_matrix_trade_state[:]

    if a_orders == None:
        debugfile.write("No active Orders\n")
        success = 0
    elif number_of_active_orders == len(matrix):
        # If there are active orders in all Matrix Slots except gap, plus one Moonbasket, we are good...
        success = 1
    elif number_of_active_orders > len(matrix) + 1:
        debugfile.write("Matrix Bot Killed by Kill Price Buy (" + str(order[0]) + ")\n")
        exit_program(2)
    else:
        # Copy the matrix trade state list(or do we actually need it?)
        #  and refresh matrix_trade_state to be all empty until updated by active orders.
        # saved_matrix_trade_state = list(matrix_trade_state)
        last_matrix_trade_state = copy.deepcopy(matrix_trade_state)
        del matrix_trade_state[:]
        matrix_trade_state = []
        for _ in matrix:
            matrix_trade_state.append(0)

        debugfile.write(str(number_of_active_orders) +" Active Orders less then matrix length. Processing completed orders....\n")

        # UPDATE MATRIX_TRADE_STATE
        # 1=HAS BUY ORDER
        # 2=HAS SELL ORDER
        # 0= SOLD OR GAP
        for order in a_orders:

            # See if we turned off the program by putting a 0.001 buy in the market
            # This is our "Kill Switch" to stop the program running from the market
            if (order[0] == get_kill_order_price(config['tpair'])):
                debugfile.write("Matrix Bot Killed by Kill Price Buy (" + str(order[0]) + ")\n")
                matrix_trade_state = last_matrix_trade_state
                exit_program(2)

            rounded_rate = round_tpair_price(order[0], config["tpair"])

            # ********************************

            # Ignore the moon_basket_peg
            if rounded_rate == moon_basket_peg:
                break
            else:
                try:
                    matrix_peg_index = matrix.index(rounded_rate)
                except:
                    matrix_trade_state = last_matrix_trade_state
                    debugfile.write("Unable to correlate active order with price " + str(rounded_rate) + "to matrix entry\n")
                    exit_program(1)

                # LOOPING THROUGH EVERY ACTIVE ORDER, INDICATE IF THERE IS A BUY OR SELL THERE
                if (str(order[1]) == str("buy")):
                    matrix_trade_state[matrix_peg_index] = 1
                elif (str(order[1]) == str("sell")):
                    matrix_trade_state[matrix_peg_index] = 2
                else:
                    debugfile.write("Unknown trade state in Active order State:" + str(order["type"]))
                    exit_program(1)

        # ***********************************************************************************************************
        # SECTION C3 : UPDATE THE MARKET WITH NEW BUYS AND SELLS ACCORDING TO PEGS THAT POPPED
        # ***********************************************************************************************************
        # FOR A HIGH MARKET............
        if current_tpair_mprice > last_tpair_mprice:

            debugfile.write("High market, Current: " + str(current_tpair_mprice) + " Last: " + str(last_tpair_mprice) + "\n")

            # We want the gap index to be below market in this situation
            if matrix[matrix_gap_idx] > current_tpair_mprice:
                matrix_gap_idx -= 1

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
            need_to_sell_price = 0
            lower_buys_threshold = get_full_peg_lower(last_tpair_mprice, matrix)
            if lower_buys_threshold != -1:
                for index, price in enumerate(matrix):
                    if price <= lower_buys_threshold:
                        if matrix_trade_state[index] == 0 and last_matrix_trade_state[index] != 3:
                            if last_matrix_trade_state[index] != 1:
                                debugfile.write("Program error. Market up. Coin bought(?) lower than last tpair price - Buy price " + str(price) +
                                            " Last tpair price " + str(last_tpair_mprice))
                                exit_program(1)

                            #if matrix_trade_state[index] == 0 and index != matrix_gap_idx and index != last_matrix_gap_idx:
                            need_to_sell_trade_volume += trade_volume
                            need_to_sell_price = price # sell at market, this will be below market which will sell at market

                            # This is a peg we will replace in the code: FILL in ALL BOUGHTS WITH SAME BUYS THAT WERE BELOW LAST MARKET PRICE
                            rebuy_low_pegs.append(price)

            # Also count to see if any units were sold even higher than new market price by one whole peg or more
            # * * * COINS SOLD REALLY HIGH * * *
            need_to_buy_trade_volume = 0
            need_to_buy_price = 0
            higher_sells_threshold = get_full_peg_higher(current_tpair_mprice, matrix)
            if higher_sells_threshold != -1:
                for index, price in enumerate(matrix):
#                if (price > current_tpair_mprice and index != 0 and matrix[index-1] >= current_tpair_mprice):
                    if price >= higher_sells_threshold :
                        if matrix_trade_state[index] == 0 and last_matrix_trade_state[index] != 3:
                            if last_matrix_trade_state[index] != 2:
                                debugfile.write("Program error. Market up. Coin sold(?) higher than current tpair price - Sell price " + str(price) +
                                                " Current tpair price " + str(current_tpair_mprice))
                            need_to_buy_trade_volume += trade_volume
                            if need_to_buy_price == 0:
                                need_to_buy_price = price # buy at market this will be above market which will buy at market

                            # This is a peg we will replace in the code: For all empty spots way up above even current market price
                            resell_high_pegs.append(price)

            # Only buy/sell the difference of these two
            if need_to_buy_trade_volume > need_to_sell_trade_volume:
                need_to_buy_trade_volume = need_to_buy_trade_volume - need_to_sell_trade_volume
                need_to_sell_trade_volume = 0
            elif need_to_sell_trade_volume > need_to_buy_trade_volume:
                need_to_sell_trade_volume = need_to_sell_trade_volume - need_to_buy_trade_volume
                need_to_buy_trade_volume = 0
            else:
                need_to_sell_trade_volume = 0
                need_to_buy_trade_volume = 0


            # If more coins were bought down below OLD market price, then sell these extras,
            # Debug : 0.1 is supposed ot sell at best price close to market.
            if need_to_sell_trade_volume > 0:
                # DEBUG VANNY
                debugfile.write("FIRST case need to sell trade volume to refill in LOWS...")

                trade_success, order_id = trade(config["tpair"], need_to_sell_price, "sell", need_to_sell_trade_volume)  # will sell at market
                debugfile.write("Selling " + str(need_to_sell_trade_volume) + "extra coin at market... sell order price:" +
                                str(need_to_sell_price) + " to replenish coins bought very low.\n")
                print "Selling " + str(need_to_sell_trade_volume) + "extra coin at market... sell order price:" + str(need_to_sell_price) + " to replenish coins bought very low.\n"
                if trade_success != 1:
                    debugfile.write(
                        "Error Retrace Order Type:Sell Volume:" + str(need_to_sell_trade_volume) + " Price:Market\n")
                    matrix_trade_state[index] = 99
                    matrix_order_id[index] = 99
                    exit_program(1)
                # Check if the Sell at Market actually happened

            # If more coins were bought high above current new higher market price, then buy these extras,
            # they end up going back in as sells after we finish the main logic for the higher market case
            # Debug : 0.1 is supposed ot sell at best price close to market.
            elif need_to_buy_trade_volume > 0:
                trade_success, order_id = trade(config["tpair"], need_to_buy_price, "buy", need_to_buy_trade_volume)  # will sell at market
                debugfile.write("Buying " + str(need_to_buy_trade_volume) + " extra coin at market... buy order price: " +
                                str(need_to_buy_price) + "to replenish coins sold very high.\n")
                print "Buying " + str(need_to_buy_trade_volume) + " extra coin at market... buy order price: " + str(need_to_buy_price) + "to replenish coins sold very high.\n"
                if trade_success != 1:
                    debugfile.write(
                        "Error Retrace Order Type:Buy Volume:" + str(need_to_buy_trade_volume) + " Price:Market\n")
                    matrix_trade_state[index] = 99
                    matrix_order_id[index] = 99
                    exit_program(1)
                    # Check if the Buy at Market actually happened

            # -----------------------------------------------------------------------------------
            # END  If you manually fix the Matrix File before running we don't need to do this
            # ----------------------------------------------------------------------------------

            # FILL in ALL OPENS (BOUGHTS) WITH SAME BUYS THAT WERE BELOW LAST MARKET PRICE
            # * * * COINS BOUGHT REALLY LOW, FILL THEM BACK IN AS IS * * *
            for buy_peg in rebuy_low_pegs:
                buy_index = matrix.index(buy_peg)
                trade_success, order_id = trade(config["tpair"], buy_peg, "buy", trade_volume)
                if trade_success != 1:
                    debugfile.write(
                        "Error Retrace Order Very Low Coin Bought, Trying to refill as is.... Type:Buy Volume:" + str(
                            trade_volume) + " Price:" + str(buy_peg))
                    matrix_trade_state[buy_index] = -99
                    matrix_order_id[buy_index] = -99
                    exit_program(1)

                debugfile.write("Case One rebuys in high market. Repurchased coin at price " + str(buy_peg) + "\n")
                print "Case One rebuys in high market. Repurchased coin at price " + str(buy_peg) + "\n"
                matrix_trade_state[buy_index] = 1
                matrix_order_id[buy_index] = order_id

            # For all empty spots way up above even current market price
            for sell_peg in resell_high_pegs:
                sell_index = matrix.index(sell_peg)
                trade_success, order_id = trade(config["tpair"], sell_peg, "sell", trade_volume)
                if trade_success != 1:
                    debugfile.write(
                        "Error Retrace Order Very High Coin sold, Trying to refill as is.... Type:Sell Volume:" + str(
                            trade_volume) + " Price:" + str(sell_peg))
                    matrix_trade_state[sell_index] = 99
                    matrix_order_id[sell_index] = 99
                    exit_program(1)

                debugfile.write("Case One resells in high market. Resold coin at price " + str(sell_peg) + "\n")
                print "Case One resells in high market. Resold coin at price " + str(sell_peg) + "\n"

                matrix_trade_state[sell_index] = 2
                matrix_order_id[sell_index] = order_id


            # * * * USUAL CASE - SOLD HIGHER, SO BUY ONE LOWER * * *
            # FILL ALL REST OF OPENS (SOLDS) WITH BUYS UP TO ONE SPOT LOWER THAN MARKET (AKA AT THE GAP)
            # DONT HAVE TO CHECK FOR GAP BECAUSE THIS WILL NATURALLY PUT A GAP IN RIGHT BELOW CURRENT MARKET
            # This is your typical case! Sold higher, Buy one Lower!
            # price <= current_tpair_mprice:
            for index, price in enumerate(matrix):

                if matrix_trade_state[index] == 0:

                    if (index + 1) > (len(matrix)-1):
                        debugfile.write("Error, Trying to Sell outside of our Matrix above Price:" + str(price))
                        exit_program(1)

                    if matrix_trade_state[index+1] == 0:
                        trade_success, order_id = trade(config["tpair"], price, "buy", trade_volume)
                        if trade_success != 1:
                            debugfile.write(
                                "Error Retrace Order Type:Buy Volume:" + str(trade_volume) + " Price:" + str(
                                    price))
                            matrix_trade_state[index] = -99
                            matrix_order_id[index] = -99
                            exit_program(1)

                        matrix_trade_state[index] = 1
                        matrix_order_id[index] = order_id


        # FOR A LOW MARKET...............
        elif current_tpair_mprice < last_tpair_mprice:

            debugfile.write("Low market, Current: " + str(current_tpair_mprice) + " Last: " + str(last_tpair_mprice) + "\n")


            # We want the gap index to be above market in this situation
            if current_tpair_mprice > matrix[matrix_gap_idx]:
                matrix_gap_idx += 1

            # -------------------------------------------------------------------------------
            # --- START If you manually fix the Matrix File before running we don't need to do this
            # -------------------------------------------------------------------------------
            # Count to see if any units were bought even lower (by one whole peg) than new market price
            # * * * COINS BOUGHT REALLY LOW * * *
            need_to_sell_trade_volume = 0
            need_to_sell_price = 0
            lower_buys_threshold = get_full_peg_lower(current_tpair_mprice, matrix)
            if lower_buys_threshold != -1:
                for index, price in enumerate(matrix):
#                    if (price < current_tpair_mprice and index != last_matrix_gap_idx
#                        and index < len(matrix) -1 and matrix[index+1] <= current_tpair_mprice):
                    if price < lower_buys_threshold:
                        if matrix_trade_state[index] == 0 and last_matrix_trade_state[index] != 3:
                            if last_matrix_trade_state[index] != 1:
                                debugfile.write("Program error. Market down. Coin bought(?) lower than current tpair price - Buy price " + str(price) +
                                                " Current tpair price " + str(current_tpair_mprice))
                                exit_program(1)

                            need_to_sell_trade_volume += trade_volume
                            need_to_sell_price = price

                            # This is a peg we will rebuy in the : "If they were buys lower by one whole peg
                            # or more ......" code below
                            rebuy_low_pegs.append(price)

            # Count how many units were sold even above the old market price
            # * * * COINS SOLD REALLY HIGH * * *
            need_to_buy_trade_volume = 0
            need_to_buy_price = 0
            higher_sells_threshold = get_full_peg_higher(last_tpair_mprice, matrix)
            if higher_sells_threshold != -1:
                for index, price in enumerate(matrix):
                    if price > last_tpair_mprice:
#                        if matrix_trade_state[index] == 0 and index != matrix_gap_idx and index != last_matrix_gap_idx:
                        if matrix_trade_state[index] == 0 and last_matrix_trade_state[index] != 3:
                            if last_matrix_trade_state[index] != 2:
                                debugfile.write("Program error. Market down. Coin sold(?) higher than last tpair price - Sell price " + str(price) +
                                                " Last tpair price " + str(last_tpair_mprice))
                                exit_program(1)

                            need_to_buy_trade_volume += trade_volume
                            if need_to_buy_price == 0:
                                need_to_buy_price = price

                            # These are coins we will resell down below in the "COINS SOLD REALLY HIGH, PUT..." code
                            resell_high_pegs.append(price)

            # Only buy/sell the difference of these two
            if need_to_buy_trade_volume > need_to_sell_trade_volume:
                need_to_buy_trade_volume = need_to_buy_trade_volume - need_to_sell_trade_volume
                need_to_sell_trade_volume = 0
            elif need_to_sell_trade_volume > need_to_buy_trade_volume:
                need_to_sell_trade_volume = need_to_sell_trade_volume - need_to_buy_trade_volume
                need_to_buy_trade_volume = 0
            else:
                need_to_sell_trade_volume = 0
                need_to_buy_trade_volume = 0


            # If more coins were sold up above OLD market price, then buy this amount extra,
            # they end up going back in as sells naturally in the code
            # Debug : 0.1 is supposed ot buy at best price close to market.
            if need_to_buy_trade_volume > 0:
                trade_success, order_id = trade(config["tpair"], need_to_buy_price, "buy", need_to_buy_trade_volume)  # will sell at market
                debugfile.write(
                    "Buying " + str(need_to_buy_trade_volume) + "extra coin at market... sell order price:" +
                    str(need_to_buy_price) + " to replenish coins sold very high. Current tpair price " + str(current_tpair_mprice) + "\n")
                print "Buying " + str(need_to_buy_trade_volume) + "extra coin at market... sell order price:" + str(need_to_buy_price) + " to replenish coins sold very high. Current tpair price " + str(
                        current_tpair_mprice) + "\n"
                if trade_success != 1:
                    debugfile.write(
                        "Error Retrace Order Type:Buy Volume:" + str(need_to_buy_trade_volume) + " Price:Market\n")
                    matrix_trade_state[index] = -99
                    matrix_order_id[index] = -99
                    exit_program(1)

            # If more coins were bought high above current new higher market price, then buy these extras,
            # they end up going back in as sells after we finish the main logic for the higher market case
            # Debug : 0.1 is supposed ot sell at best price close to market.
            elif need_to_sell_trade_volume > 0:
                debugfile.write("SECOND case need to sell trade volume to refill in LOWS...")

                trade_success, order_id = trade(config["tpair"], need_to_sell_price, "sell", need_to_sell_trade_volume)  # will sell at market
                debugfile.write(
                    "Selling " + str(need_to_sell_trade_volume) + "extra coin at market... sell order price:" +
                    str(need_to_sell_price) + " to replenish coins bought very low. Current tpair price " + str(current_tpair_mprice) + "\n")
                print "Selling " + str(need_to_sell_trade_volume) + "extra coin at market... sell order price:" + str(need_to_sell_price) + " to replenish coins bought very low. Current tpair price " + str(
                        current_tpair_mprice) + "\n"
                if trade_success != 1:
                    debugfile.write(
                        "Error Retrace Order Type:Sell Volume:" + str(need_to_sell_trade_volume) + " Price:Market \n")
                    matrix_trade_state[index] = 99
                    matrix_order_id[index] = 99
                    exit_program(1)

            # -----------------------------------------------------------------------------------
            # END  If you manually fix the Matrix File before running we don't need to do this
            # ----------------------------------------------------------------------------------

            # COINS SOLD REALLY HIGH, PUT BACK IN AS THEY WERE, MARKET BACK DOWN FROM THERE
            for sell_peg in resell_high_pegs:
                sell_index = matrix.index(sell_peg)
                trade_success, order_id = trade(config["tpair"], sell_peg, "sell", trade_volume)
                if trade_success != 1:
                    debugfile.write(
                        "Error Retrace Order Very High Coin sold, Trying to refill as is.... Type:Sell Volume:" + str(
                            trade_volume) + " Price:" + str(sell_peg) + " Current tpair price " + str(current_tpair_mprice) + "\n")
                    matrix_trade_state[sell_index] = 99
                    matrix_order_id[sell_index] = 99
                    exit_program(1)

                matrix_trade_state[sell_index] = 2
                matrix_order_id[sell_index] = order_id


            # If they were buys lower by one whole peg or more below the current price, go ahead and
            # put back in as buys as the same prices
            for buy_peg in rebuy_low_pegs:
                buy_index = matrix.index(buy_peg)
                trade_success, order_id = trade(config["tpair"], buy_peg, "buy", trade_volume)
                if trade_success != 1:
                    debugfile.write(
                        "Error Retrace Order Very Low Coin Bought, Trying to refill as is.... Type:Buy Volume:" + str(
                            trade_volume) + " Price:" + str(buy_peg) + " Current tpair price " + str(current_tpair_mprice) + "\n")
                    matrix_trade_state[buy_index] = -99
                    matrix_order_id[buy_index] = -99
                    exit_program(1)

                matrix_trade_state[buy_index] = 1
                matrix_order_id[buy_index] = order_id

            # THEN REPLACE ALL BUYS WITH SELLS ONE SPOT HIGHER
            # Here is our typical case. Bought a little lower, let's sell one higher!
            for index, price in enumerate(matrix):

                if matrix_trade_state[index] == 0:
                    if index == 0:
                        debugfile.write("Error, Trying to Sell Below Lowest Index in Matrix:" + str(matrix[index]))
                        exit_program(1)

                    elif matrix_trade_state[index-1] == 0:
                        trade_success, order_id = trade(config["tpair"], matrix[index], "sell", trade_volume)
                        if trade_success != 1:
                            debugfile.write(
                                "Error Retrace Order Type:Sell Volume:" + str(trade_volume) + " Price:" + str(
                                    matrix[index]))
                            matrix_trade_state[index] = 99
                            matrix_order_id[index] = 99
                            exit_program(1)

                        matrix_order_id[index] = order_id
                        soldup_indexes.append(index)


            # We couldn't reset the trade_state pegs to Sells above in order to not break looping on the
            # next peg, so we do it here in this extra littel loop (otherwise we could loop backwards through
            #the Sell code in the low market then we wouldn't need to do this separately)
            for idxval in soldup_indexes:
                matrix_trade_state[idxval] = 2

        else:

            # Only need to handle the cases of buys really low and sells really high
            # and the cases of one up or one down

            # Count to see if any units were bought even lower (by one whole peg) than new market price
            # * * * COINS BOUGHT REALLY LOW * * *
            need_to_sell_trade_volume = 0
            need_to_sell_price = 0
            lower_buys_threshold = get_full_peg_lower(current_tpair_mprice, matrix)
            if lower_buys_threshold != -1:
                for index, price in enumerate(matrix):
                    #                    if (price < current_tpair_mprice and index != last_matrix_gap_idx
                    #                        and index < len(matrix) -1 and matrix[index+1] <= current_tpair_mprice):
                    if price < lower_buys_threshold:
                        if matrix_trade_state[index] == 0 and last_matrix_trade_state[index] != 3:
                            if last_matrix_trade_state[index] != 1:
                                debugfile.write(
                                    "Program error. Market equal. Coin bought(?) lower than current tpair price - Buy price " + str(
                                        price) +
                                    " Current tpair price " + str(current_tpair_mprice))
                                exit_program(1)

                            need_to_sell_trade_volume += trade_volume
                            need_to_sell_price = price

                            # This is a peg we will rebuy in the : "If they were buys lower by one whole peg
                            # or more ......" code below
                            rebuy_low_pegs.append(price)

            # Count how many units were sold even above the old market price
            # * * * COINS SOLD REALLY HIGH * * *
            need_to_buy_trade_volume = 0
            need_to_buy_price = 0
            higher_sells_threshold = get_full_peg_higher(current_tpair_mprice, matrix)
            if higher_sells_threshold != -1:
                for index, price in enumerate(matrix):
                    if price > current_tpair_mprice:
                        #                        if matrix_trade_state[index] == 0 and index != matrix_gap_idx and index != last_matrix_gap_idx:
                        if matrix_trade_state[index] == 0 and last_matrix_trade_state[index] != 3:
                            if last_matrix_trade_state[index] != 2:
                                debugfile.write(
                                    "Program error. Market equal. Coin sold(?) higher than current tpair price - Sell price " + str(
                                        price) +
                                    " Current tpair price " + str(current_tpair_mprice))
                                exit_program(1)

                            need_to_buy_trade_volume += trade_volume
                            if need_to_buy_price == 0:
                                need_to_buy_price = price

                            # These are coins we will resell down below in the "COINS SOLD REALLY HIGH, PUT..." code
                            resell_high_pegs.append(price)

            # Only buy/sell the difference of these two
            if need_to_buy_trade_volume > need_to_sell_trade_volume:
                need_to_buy_trade_volume = need_to_buy_trade_volume - need_to_sell_trade_volume
                need_to_sell_trade_volume = 0
            elif need_to_sell_trade_volume > need_to_buy_trade_volume:
                need_to_sell_trade_volume = need_to_sell_trade_volume - need_to_buy_trade_volume
                need_to_buy_trade_volume = 0
            else:
                need_to_sell_trade_volume = 0
                need_to_buy_trade_volume = 0

            # If more coins were sold up above OLD market price, then buy this amount extra,
            # they end up going back in as sells naturally in the code
            # Debug : 0.1 is supposed ot buy at best price close to market.
            if need_to_buy_trade_volume > 0:
                trade_success, order_id = trade(config["tpair"], need_to_buy_price, "buy",
                                                need_to_buy_trade_volume)  # will sell at market
                debugfile.write(
                    "Buying " + str(need_to_buy_trade_volume) + "extra coin at market... sell order price:" +
                    str(need_to_buy_price) + " to replenish coins sold very high. Current tpair price " + str(
                        current_tpair_mprice) + "\n")
                print "Buying " + str(need_to_buy_trade_volume) + "extra coin at market... sell order price:" + str(
                    need_to_buy_price) + " to replenish coins sold very high. Current tpair price " + str(
                    current_tpair_mprice) + "\n"
                if trade_success != 1:
                    debugfile.write(
                        "Error Retrace Order Type:Buy Volume:" + str(need_to_buy_trade_volume) + " Price:Market\n")
                    matrix_trade_state[index] = -99
                    matrix_order_id[index] = -99
                    exit_program(1)

            # If more coins were bought high above current new higher market price, then buy these extras,
            # they end up going back in as sells after we finish the main logic for the higher market case
            # Debug : 0.1 is supposed ot sell at best price close to market.
            elif need_to_sell_trade_volume > 0:
                debugfile.write("SECOND case need to sell trade volume to refill in LOWS...")

                trade_success, order_id = trade(config["tpair"], need_to_sell_price, "sell",
                                                need_to_sell_trade_volume)  # will sell at market
                debugfile.write(
                    "Selling " + str(need_to_sell_trade_volume) + "extra coin at market... sell order price:" +
                    str(need_to_sell_price) + " to replenish coins bought very low. Current tpair price " + str(
                        current_tpair_mprice) + "\n")
                print "Selling " + str(need_to_sell_trade_volume) + "extra coin at market... sell order price:" + str(
                    need_to_sell_price) + " to replenish coins bought very low. Current tpair price " + str(
                    current_tpair_mprice) + "\n"
                if trade_success != 1:
                    debugfile.write(
                        "Error Retrace Order Type:Sell Volume:" + str(need_to_sell_trade_volume) + " Price:Market \n")
                    matrix_trade_state[index] = 99
                    matrix_order_id[index] = 99
                    exit_program(1)

            # -----------------------------------------------------------------------------------
            # END  If you manually fix the Matrix File before running we don't need to do this
            # ----------------------------------------------------------------------------------

            # COINS SOLD REALLY HIGH, PUT BACK IN AS THEY WERE, MARKET BACK DOWN FROM THERE
            for sell_peg in resell_high_pegs:
                sell_index = matrix.index(sell_peg)
                trade_success, order_id = trade(config["tpair"], sell_peg, "sell", trade_volume)
                if trade_success != 1:
                    debugfile.write(
                        "Error Retrace Order Very High Coin sold, Trying to refill as is.... Type:Sell Volume:" + str(
                            trade_volume) + " Price:" + str(sell_peg) + " Current tpair price " + str(
                            current_tpair_mprice) + "\n")
                    matrix_trade_state[sell_index] = 99
                    matrix_order_id[sell_index] = 99
                    exit_program(1)

                matrix_trade_state[sell_index] = 2
                matrix_order_id[sell_index] = order_id

            # If they were buys lower by one whole peg or more below the current price, go ahead and
            # put back in as buys as the same prices
            for buy_peg in rebuy_low_pegs:
                buy_index = matrix.index(buy_peg)
                trade_success, order_id = trade(config["tpair"], buy_peg, "buy", trade_volume)
                if trade_success != 1:
                    debugfile.write(
                        "Error Retrace Order Very Low Coin Bought, Trying to refill as is.... Type:Buy Volume:" + str(
                            trade_volume) + " Price:" + str(buy_peg) + " Current tpair price " + str(
                            current_tpair_mprice) + "\n")
                    matrix_trade_state[buy_index] = -99
                    matrix_order_id[buy_index] = -99
                    exit_program(1)

                matrix_trade_state[buy_index] = 1
                matrix_order_id[buy_index] = order_id

            # Refill one above or one below if necessary
            buy_happened = False
            sell_happened = False
            bought_index = -1
            sold_index = -1
            for index, price in enumerate(matrix):

                if matrix_trade_state[index] == 0:
                    if index == 0:
                        debugfile.write("Error, Trying to Sell Below Lowest Index in Matrix:" + str(matrix[index]))
                        exit_program(1)
                    if last_matrix_trade_state[index] == 1:
                        if buy_happened:
                            debugfile.write("Market Equal. Error multiple buys detected near market. \n")
                            exit_program(1)
                        buy_happened = True
                        bought_index = index
                    elif last_matrix_trade_state[index] == 2:
                        if sell_happened:
                            debugfile.write("Market Equal. Error multiple sells detected near market. \n")
                            exit_program(1)
                        sell_happened = True
                        sold_index = index

            if buy_happened and sell_happened:
                debugfile.write("Market Equal. Error determining which pegs to refill. Both buy and sell pegs indicated \n")
                exit_program(1)

            elif buy_happened:
                if matrix_trade_state[bought_index+1] != 0:
                    debugfile.write("Market Equal. Error, buy happened at " + str(matrix[bought_index]) + " but peg at price " + str(matrix[bought_index + 1]) + "is not open for a new sell order\n")
                    exit_program(1)
                else:
                    trade_success, order_id = trade(config["tpair"], matrix[bought_index + 1], "sell", trade_volume)
                    if trade_success != 1:
                        debugfile.write(
                            "Error Retrace Order Type:Sell Volume:" + str(trade_volume) + " Price:" + str(
                                matrix[bought_index+1]))
                        matrix_trade_state[bought_index+1] = 99
                        matrix_order_id[bought_index + 1] = 99
                        exit_program(1)

                    matrix_order_id[bought_index + 1] = order_id
                    matrix_trade_state[bought_index + 1] = 2

            elif sell_happened:
                if matrix_trade_state[sold_index - 1] != 0:
                    debugfile.write("Market Equal. Error, sell happened at " + str(matrix[sold_index]) + " but peg at price " + str(matrix[sold_index - 1]) + "is not open for a new buy order\n")
                    exit_program(1)
                else:
                    trade_success, order_id = trade(config["tpair"], matrix[sold_index - 1], "buy", trade_volume)
                    if trade_success != 1:
                        debugfile.write(
                            "Error Retrace Order Type:Buy Volume:" + str(trade_volume) + " Price:" + str(
                                matrix[sold_index - 1]))
                        matrix_trade_state[sold_index - 1] = 99
                        matrix_order_id[sold_index - 1] = 99
                        exit_program(1)

                    matrix_order_id[sold_index - 1] = order_id
                    matrix_trade_state[sold_index - 1] = 2


        # Put in the gap!!
        for index, state in enumerate(matrix_trade_state):
            if state == 0:
                matrix_trade_state[index] = 3

        # Check to make sure we don't have more than one open slot in Matrix
        found_gap_state = 0
        for index, state in enumerate(matrix_trade_state):
            if state == 3:
                if found_gap_state == 1:
                    debugfile.write("More than one gap detected in Matrix.")
                    exit_program(1)
                found_gap_state = 1


#    last_matrix_gap_idx = matrix_gap_idx
    last_tpair_mprice = current_tpair_mprice
    depth_call_failed = 0
    time.sleep(4)

# End of Action Bot Loop acting on active orders


# Housekeeping
debugfile.close()

# Rewrite Matrix File and Exit Program
exit_program(0)



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