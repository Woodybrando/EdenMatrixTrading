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

import time
import utils
from utils import die
from exchange_btce import *

STATE_BUY_ORDER = 1
STATE_SELL_ORDER = 2
STATE_NONE = 0
STATE_BOUGHT = -1
STATE_SOLD = -2

# ***********************************************************************************************************
# Read the config and current state
# ***********************************************************************************************************

config = utils.read_config()
state = utils.State()

# ***********************************************************************************************************
# Open the log file
# ***********************************************************************************************************

log = open(config["log_file"], 'w')

# ***********************************************************************************************************
# Select the exchange we want to use
# ***********************************************************************************************************

exchange = None
if config["exchange_choice"] == "btc-e.com":
    exchange = BtceExchange(config["BTCE_API_KEY"], config["BTCE_API_SECRET"], config["btce_trade_fee"])
else:
    die("We don't have software created for markets other than btc-e yet. Stay tuned!")


if state.initialized is False:
    # ***********************************************************************************************************
    # Generate the matrix
    # ***********************************************************************************************************
    current_tpair_mprice = exchange.marketprice(config["tpair"])

    # Generate the matrix of pegs (and the corresponding trading state matrix)
    matrix_bottom = config["matrix_bottom_ratio"] * current_tpair_mprice
    matrix_bottom = utils.round_tpair_price(matrix_bottom, config["tpair"])
    matrix_top = config["matrix_top_ratio"] * current_tpair_mprice
    matrix_top = utils.round_tpair_price(matrix_top, config["tpair"])

    # "Matrix" will hold the pegs
    state.matrix = utils.generate_matrix(matrix_bottom, matrix_top, config["matrix_spread_percent"], config["tpair"])

    # WHAT AMOUNT OF FIAT ($, EURO, YUAN, YEN) ARE YOU OKAY WITH GIVING UP FOREVER
    # TO LEARN FROM THIS EXPERIENCE? What is initial investment amount?

    # EDEN STORE VALUE: (USER INITIAL INVESTMENT)
    initial_investment = config["initial_investment"]
    initial_setup_fee = initial_investment * exchange.trade_fee
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
    # moon_basket_current_market_buy_amount# VANNYCAT AND JAYSON NOT USD!
    moon_basket_current_market_buy_amount = initial_investment * config["moon_basket_factor"]

    # Set the price of the Moonbasket Sell to one peg above the matrix
    moon_basket_peg = utils.round_tpair_price((matrix_top * config["matrix_spread_percent"]), config["tpair"])


    # Uncomment this out when the printout looks good
    # EDEN: (current_tpair_mprice)/(moon_basket_current_market_buy_amount) = (moonbasket_coins_count) 20
    moonbasket_coins_count = moon_basket_current_market_buy_amount / current_tpair_mprice
    moonbasket_coins_count = utils.round_tpair_volume(moonbasket_coins_count, config["tpair"])

    # EDEN: BUY (moonbasket_coins_count) @ (current_tpair_mprice)
    # EDEN: AND CONFIRM TRANSACTION
    trade_success, order_id = exchange.trade(config["tpair"], 99999999, "buy", moonbasket_coins_count) # this is how you buy @ market price on btc-e
    log.write("Purchased moonbucket %s coins at price %s\n" % (moonbasket_coins_count, current_tpair_mprice))

    # EDEN: SET MOONBASKET GOAL SELLS (moonbasket_coins_count @ one peg above matrix top)
    # EDEN CREATE SELL moonbasket_coins_count @ moon_basket_peg
    trade_success, order_id = exchange.trade(config["tpair"], moon_basket_peg, "sell", moonbasket_coins_count)
    log.write("Moonbasket Sell Order established %s coins to sell at price %s\n" % (moonbasket_coins_count, moon_basket_peg))



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
    above_market_coin_count = utils.round_tpair_volume(above_market_buy / current_tpair_mprice, config["tpair"])
    number_of_pegs = len(matrix)

    # NOTE : WE ARE WORKING WITH A STATIC TRADE VOLUME HERE. IF THAT CHANGES LOOK FOR ALL INSTANCES OF TRADE_VOLUME IN
    # CODE AND ADJUST ACCORDINGLY
    starting_tpair_coins = matrix_investment / current_tpair_mprice
    trade_volume = starting_tpair_coins / number_of_pegs
    trade_volume = utils.round_tpair_volume(trade_volume, config["tpair"])

    # trade_success, order_id = trade(config["tpair"], current_tpair_mprice, "buy", above_market_coin_count)
    log.write("Initial investment: Purchased %s coins at price %s\n" % (above_market_coin_count, current_tpair_mprice))
    log.write("Trade volume is %s at each peg" % trade_volume)


    # For each peg ask is this peg less than the market price we paid by an amount > the spread of 1.9% (rounded up)
    # if so then place a buy at our static volume and
    # store the value 1 in our matrix_trade_state
    # if peg value is greater than market price we paid by 1.9%
    # set a sell at our static volume till one below our top peg and
    # store the value 2 in our matrix_peg_state
    # also for peg <= spread below market
    # set matrix_trade_state associated to that peg index to 0
    # also store each trade id in matrix_trade_id in index equal to peg index #

    for i, peg in enumerate(state.matrix):
        if peg < current_tpair_mprice:
            # if the peg is at least `matrix_spread_percent` below the current market price, set a buy order
            if (peg * config["matrix_spread_percent"]) < current_tpair_mprice:
                trade_success, order_id = exchange.trade(config["tpair"], peg, "buy", trade_volume)
                if not trade_success:
                    die("Error setting buy order (tpair: %s, peg: %s, volume: %s)" % (config["tpair"], peg, trade_volume))

                state.trade_state[peg] = {
                    'order_id': order_id,
                    'state': STATE_BUY_ORDER,
                    'volume': trade_volume,
                }
                state.save()
                log.write("%s[%s][%s][%s]\n" % (trade_volume, peg, STATE_BUY_ORDER, order_id))

            # if the peg is too close, do not set a buy order
            else:
                state.trade_state[peg] = {
                    'order_id': None,
                    'state': STATE_NONE,
                    'volume': 0,
                }
                state.save()
                log.write("%s[%s][%s][%s]\n" % (trade_volume, peg, STATE_NONE, None))

        elif peg == current_tpair_mprice:
            state.trade_state[peg] = {
                'order_id': None,
                'state': STATE_NONE,
                'volume': 0,
            }
            state.save()
            log.write("%s[%s][%s][%s]\n" % (trade_volume, peg, STATE_NONE, None))

        else:
            # if the peg is at least `matrix_spread_percent` above the current market price, set a sell order
            if (peg - (peg * config["matrix_spread_percent"])) <= current_tpair_mprice:
                trade_success, order_id = exchange.trade(config["tpair"], peg, "sell", trade_volume)
                if not trade_success:
                    die("Error setting sell order (tpair: %s, peg: %s, volume: %s)" % (config["tpair"], peg, trade_volume))

                state.trade_state[peg] = {
                    'order_id': order_id,
                    'state': STATE_SELL_ORDER,
                    'volume': trade_volume,
                }
                state.save()
                log.write("%s[%s][%s][%s]\n" % (trade_volume, peg, STATE_BUY_ORDER, order_id))
            else:
                state.trade_state[peg] = {
                    'order_id': None,
                    'state': STATE_NONE,
                    'volume': 0,
                }
                state.save()
                log.write("%s[%s][%s][%s]\n" % (trade_volume, peg, STATE_NONE, None))

    state.initialized = True
    state.last_tpair_mprice = current_tpair_mprice
    state.save()

# ------------------------------------------------------------------------------------------------------
# EDEN HAS INITIAL MATRIX ESTABLISHED!
# WAIT 30 SECOND INTERVALS TO QUERY MARKET AND UPDATE AT THOSE INTERVALS
# SEE LOGIC LOOP TO UNDERSTAND UPDATES
#------------------------------------------------------------------------------------------------------


"""
state.trade_state = {
    peg: {
        order_id: '12345'
        state: STATE_WHATEVER,
        volume: 123,
    }
}
"""

def detect_completed_orders(active_orders):
    completed_buys = []
    completed_sells = []

    for peg, order in state.trade_state.iteritems():
        if order['state'] == STATE_NONE:
            continue

        if active_orders.get(order['order_id']) is None:
            if order['state'] == STATE_BUY_ORDER:
                completed_buys.append((peg, order['volume']))
            elif order['state'] == STATE_SELL_ORDER:
                completed_sells.append((peg, order['volume']))

            order['state'] = STATE_NONE
            order['order_id'] = None

    state.save()
    return completed_buys, completed_sells


def main_loop():
    while True:
        active_orders = exchange.activeorders(config["tpair"])
        if active_orders is None:
            die("active_orders is None") # @@TODO?

        # detect any filled orders and update trade_state with STATE_NONE for those pegs
        completed_buys, completed_sells = detect_completed_orders(trade_history)

        current_tpair_mprice = exchange.marketprice(config["tpair"])
        if current_tpair_mprice > state.last_tpair_mprice:
            # if it dipped down and we made buys, but the price is now higher, sell those buys at market price
            total_buy_volume = 0
            for x in completed_buys:
                _, vol = x
                total_buy_volume += vol

            if total_buy_volume > 0:
                trade_success, _ = exchange.trade(config["tpair"], 0.1, "sell", total_buy_volume) # sell for 0.1 is btc-e's suggested way of selling at market price

        elif current_tpair_mprice < last_tpair_mprice:
            # if it jumped up and we made sells, but the price is now lower, buy those sells at market price
            total_sell_volume = 0
            for x in completed_sells:
                _, vol = x
                total_sell_volume += vol

            if total_sell_volume > 0:
                trade_success, _ = exchange.trade(config["tpair"], 99999999, "buy", total_sell_volume) # buy for extremely high price is btc-e's suggested way of buying at market price

        # for any STATE_NONE pegs in the matrix, re-set our orders
        new_orders = []
        for peg, order in trade_state.iteritems():
            if order['state'] == STATE_NONE:
                if peg < current_tpair_mprice:
                    trade_success, order_id = exchange.trade(config["tpair"], peg, "buy", trade_volume)
                    new_orders.append((peg, order_id, STATE_BUY_ORDER, trade_volume))

                elif peg > current_tpair_mprice:
                    trade_success, order_id = exchange.trade(config["tpair"], peg, "sell", trade_volume)
                    new_orders.append((peg, order_id, STATE_SELL_ORDER, trade_volume))

        # update trade_state with our new orders
        for new_order in new_orders:
            peg, order_id, state, trade_volume = new_order
            trade_state[peg] = {
                'order_id': order_id,
                'state': state,
                'volume': trade_volume,
            }
        state.save()

        last_tpair_mprice = current_tpair_mprice
        time.sleep(30)


"""
active orders json response:
{
    "success":1,
    "return":{
        "343152":{
            "pair":"btc_usd",
            "type":"sell",
            "amount":12.345,
            "rate":485
        },
        ...
    }
}

trade history json response:
{
    "success":1,
    "return":{
        "166830":{
            "pair":"btc_usd",
            "type":"sell",
            "amount":1,
            "rate":450,
            "order_id":343148,
            "is_your_order":1,
            "timestamp":1342445793
        }
    }
}
"""



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