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
from utils import *

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
        exit(1)
    return return_number


def generate_matrix(start, end, percentage, tpair):
    """Generates the peg Marix, the corresponding Matrix_Trade_State and Matrix_Order_Id."""
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

        # the data is returned as a dictionary, so we convert it to an array for convenience
        orders = []
        for order_id, order_data in data.iteritems():
            order_data[
                "order_id"] = order_id  # add the order_id to the returned order data
            orders.append(order_data)
        return orders
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
# Get Current Market Price
# ***********************************************************************************************************

if config["exchange_choice"] == "wex.nz":
    depth = marketdepth(config["tpair"], 5)
    if depth is None:
        print "Error connecting to wex.nz"
        exit(1)

    # Debug make sure these asks look appropriate
    current_tpair_mprice = depth[0][4][0]

else:
    print "We don't have software created for markets other than wex.nz yet. Stay tuned!"
    current_tpair_mprice = 0
    #exit 1

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


# EDEN open file to record initial purchases and Matrix information
file = open("/Users/woodybrando/Documents/Eden-Project/GitHub/Scratch/NMC_USD_Matrix", 'w')


# WHAT AMOUNT OF FIAT ($, EURO, YUAN, YEN) ARE YOU OKAY WITH GIVING UP FOREVER
# TO LEARN FROM THIS EXPERIENCE? What is initial investment amount?

# EDEN STORE VALUE: (USER INITIAL INVESTMENT)

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


# Uncomment this out when the printout looks good
# More debug
# EDEN: (current_tpair_mprice)/(moon_basket_current_market_buy_amount) = (moonbasket_coins_count) 20
moonbasket_coins_count = moon_basket_current_market_buy_amount / current_tpair_mprice
moonbasket_coins_count = round_tpair_volume(moonbasket_coins_count, config["tpair"])

# EDEN: BUY (moonbasket_coins_count) @ (current_tpair_mprice)
# EDEN: AND CONFIRM TRANSACTION
#trade_success, order_id = trade(config["tpair"], current_tpair_mprice, "buy", moonbasket_coins_count)
file.write("Purchased moonbucket " + str(moonbasket_coins_count) + " coins at price " +
           str(current_tpair_mprice) + "\n")

# EDEN: SET MOONBASKET GOAL SELLS (moonbasket_coins_count @ one peg above matrix top)
# EDEN CREATE SELL moonbasket_coins_count @ moon_basket_peg
#trade_success, order_id = trade(config["tpair"], moon_basket_peg, "sell", moonbasket_coins_count)
file.write("Moonbasket Sell Order established " + str(moonbasket_coins_count) + "coins to sell at price "
           + str(moon_basket_peg) + '\n')



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
file.write("Initial investment: Purchased " + str(above_market_coin_count) + " coins at price "
           + str(current_tpair_mprice) + '\n')
file.write("Trade volume is " + str(trade_volume) + "at each peg")



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
# ----------------> Set order_id to 0 if debugging
order_id = 0

for peg in matrix:
    if peg < current_tpair_mprice:
        if (peg * config["matrix_spread_percent"]) < current_tpair_mprice:
            #trade_success, order_id = trade(config["tpair"], peg, "buy", trade_volume)
            matrix_trade_state[list_counter] = 1
            matrix_order_id[list_counter] = order_id
            file.write(str(trade_volume) + "[" + str(peg) + "][" + str(matrix_trade_state[list_counter]) + "]"
                       + "][" + str(matrix_order_id[list_counter]) + "]\n")
        else:
            matrix_trade_state[list_counter] = 0
            matrix_order_id[list_counter] = 0
            file.write(str(trade_volume) + "[" + str(peg) + "][" + str(matrix_trade_state[list_counter]) + "]"
                       + "][" + str(matrix_order_id[list_counter]) + "]\n")
    elif peg == current_tpair_mprice:
        matrix_trade_state[list_counter] = 0
        matrix_order_id[list_counter] = 0
        file.write(str(trade_volume) + "[" + str(peg) + "][" + str(matrix_trade_state[list_counter]) + "]"
                   + "][" + str(matrix_order_id[list_counter]) + "]\n")

    else:
        if (peg - (peg * config["matrix_spread_percent"])) <= current_tpair_mprice:
            #trade_success, order_id = trade(config["tpair"], peg, "sell", trade_volume)
            matrix_trade_state[list_counter] = 2
            matrix_order_id[list_counter] = order_id
            file.write(str(trade_volume) + "[" + str(peg) + "][" + str(matrix_trade_state[list_counter]) + "]"
                       + "][" + str(matrix_order_id[list_counter]) + "]\n")
        else:
            matrix_trade_state[list_counter] = 0
            matrix_order_id[list_counter] = 0
            file.write(str(trade_volume) + "[" + str(peg) + "][" + str(matrix_trade_state[list_counter]) + "]"
                       + "][" + str(matrix_order_id[list_counter]) + "]\n")

    list_counter += 1

# ------------------------------------------------------------------------------------------------------
# EDEN HAS INITIAL MATRIX ESTABLISHED!
# WAIT 30 SECOND INTERVALS TO QUERY MARKET AND UPDATE AT THOSE INTERVALS
# SEE LOGIC LOOP TO UNDERSTAND UPDATES
#------------------------------------------------------------------------------------------------------
# ----> PUT IN LOOP ---> LOOP ---> PUT IN LOOP --> PUT IN LOOP --> PUT IN LOOP --> PUT IN LOOP
success = 1
while (success == 1):
    time.sleep(2)

# Check what the last Order_id was. This was be used as the starting point to look at most recent activity.
    last_order_id = order_id

# Get the new current market price
    last_tpair_mprice = current_tpair_mprice
    depth = marketdepth(config["tpair"], 5)
    if depth is None:
        print "Error connecting to btc-e.com"
        exit(1)

# Debug make sure these asks look appropriate
    current_tpair_mprice = depth[0][4][0]

#------------------------------------------------------------------------------------------------------
# EDEN LOGIC LOOP
#-----------------------------------------------------------------------------------------------------
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
    matrix_has_active_order = [0 for _ in matrix]
#'''
    if a_orders == None:
        file.write("No active Orders\n")
    else:
    # GET THE MATRIX_TRADE_STATES ARRAY UPDATED TO INDICATE
    # 1=HAS BUY ORDER
    # 2=HAS SELL ORDER
    # -1=BOUGHT
    # -2= SOLD
        for order in a_orders:
            file.write("Active Order: " + str(order["amount"]) + "[" + str(order["rate"]) + "]["
                   + str(order["type"]) + "]\n")
            matrix_peg_index = matrix.index(order["rate"]) if order["rate"] in matrix else None
            if matrix_peg_index == None:
                file.write("Active Order outside of Matrix at peg " + str(order["rate"]) + "\n")
            else:
            # LOOPING THROUGH EVERY ACTIVE ORDER, INDICATE YES
            # THERE IS AN ACTIVE ORDER IN THE MATRIX_HAS_ACTIVE_ORDER ARRAY
                matrix_has_active_order[matrix_peg_index] = 1
            # ----------> DEBUG -------------------------------------------------------------------
            # IF LOGIC IS WRITE THESE ERRORS WON'T HAPPEN. REMOVE WHEN CODE TESTED SUFFICIENTLY
            # ------------------------------------------------------------------------------------
                if matrix_trade_state[matrix_peg_index] == 1 & (str(order["type"]) != str("buy")):
                    print "Error trade state of peg " + str(matrix[matrix_peg_index]) + " is not buy \n"
                if matrix_trade_state[matrix_peg_index] == 2 & (str(order["type"]) != str("sell")):
                    print "Error trade state of peg " + str(matrix[matrix_peg_index]) + " is not sell \n"


# FOR ALL PEGS WITH matrix_has_active_order == 0, FILL IN WHETHER THEY WERE BOUGHT OR SOLD
# BY CHANGING matrix_trade_state TO BE -1 (bought) OR -2 (sold)
    for i in matrix_has_active_order:
        if matrix_has_active_order[i] == 0:
            if matrix_trade_state[i] == 1:
                matrix_trade_state[i] = -1
            elif matrix_trade_state[i] == 2:
                matrix_trade_state[i] = -2
            else:
                print "Error in the case of Have Active Order at " + str(matrix[i]) + " but trade state is " + str(matrix_trade_state[i]) + "\n"


# HERE IS THE REAL LOGIC NOW THAT WE HAVE ALL OUR ACTIVE ORDERS ARRAYS UPDATED TO INDICATE BUYS AND SELLS ....

# FOR A HIGH MARKET............
    if current_tpair_mprice > last_tpair_mprice:

    # CHECK IF IT DIPPED DOWN TO DO BUYS ALSO IN THIS TIME INTERVAL OR IF ONLY DID SELLS
    # IF DID DIP, SELL ALL THOSE BUYS AT CURRENT MARKET, THEN PUT THEM IN AS BUY PEGS AGAIN
        for index, price in enumerate(matrix):
            if matrix_trade_state[index] == -1:
                trade_success, order_id = trade(config["tpair"], current_tpair_mprice, "sell", trade_volume)
                trade_success, order_id = trade(config["tpair"], price, "buy", trade_volume)
                matrix_trade_state[index] = 1
                matrix_order_id[index] = order_id

    # THEN REPLACE ALL SELLS WITH BUYS IN ONE SPOT LOWER
    # -------------> NEED TO ADD CODE TO CHECK THAT THE LOWER SPOT IS OPEN WHICH IT SHOULD BE  ------------
    # ------------> ALSO CODE TO MAKE SURE NO THROWING EXCEPTIONS OF -1 INDEX OR GOING OUT OF MATRIX ------------------
        for index, price in enumerate(matrix):
            if matrix_trade_state[index] == -2:
                trade_success, order_id = trade(config["tpair"], matrix[index-1], "buy", trade_volume)
                matrix_trade_state[index-1] = 1
                matrix_order_id[index-1] = order_id

# FOR A LOW MARKET...............
    else:
    # CHECK IF IT POPPED UP TO ALSO DO SELLS IN THIS TIME INTERVAL OR IF ONLY DID BUYS
    # IF DID POP, BUY THAT MANY AT CURRENT MARKET, THEN PUT THEM IN AS SELL PEGS AGAIN
        for index, price in enumerate(matrix):
            if matrix_trade_state[index] == -2:
                trade_success, order_id = trade(config["tpair"], current_tpair_mprice, "buy", trade_volume)
                trade_success, order_id = trade(config["tpair"], price, "sell", trade_volume)
                matrix_trade_state[index] = 2
                matrix_order_id[index] = order_id

    # THEN REPLACE ALL BUYS WITH SELLS ONE SPOT HIGHER
    # -------------> NEED TO ADD CODE TO CHECK THAT THE HIGHER SPOT IS OPEN WHICH IT SHOULD BE  ------------
    # ------------> ALSO CODE TO MAKE SURE NO THROWING EXCEPTIONS OF -1 INDEX OR GOIGN OUT OF MATRIX -------------------
        for index, price in enumerate(matrix):
            if matrix_trade_state[index] == -1:
                trade_success, order_id = trade(config["tpair"], matrix[index+1], "sell", trade_volume)
                matrix_trade_state[index+1] = 2
                matrix_order_id[index+1] = order_id

    success = 1
#'''
'''
recent_trades = tradehistory(config["tpair"])
tradenum = 0
for trade in recent_trades:

    print "This is " + str(tradenum)
    tradenum += 1
    # ******** Jayson and Vanny - find out how to get at the data in the tradehistory and react accordingly ****
'''

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