__author__ = 'mquinlan'

import sys
import csv
import QSTK.qstkutil.qsdateutil as du
import datetime as dt
import QSTK.qstkutil.DataAccess as da
import collections
from decimal import *
import json


class MarketSimulator:
    def run(self, initial_cash_amount, orders_file, output_file):
        symbols = self.extract_symbols(orders_file)
        print 'Symbols %s ' % symbols

        orders_by_date = self.collate_orders_per_day(orders_file)
        print 'Orders per day %s ' % orders_by_date

        all_trade_dates = orders_by_date.keys()
        date_start = all_trade_dates[0]
        date_end = all_trade_dates[len(all_trade_dates) - 1]

        print 'Trade start date: %s ' % date_start
        print 'Trade end date: %s ' % date_end

        # close is adjusted close according to First Figure subheading of http://wiki.quantsoftware.org/index.php?title=QSTK_Tutorial_1
        ls_keys = ['close']
        d_data, trading_days = self.download_data_from_yahoo(date_start, date_end, symbols, ls_keys)
        print 'Downloaded Yahoo data: %s ' % d_data

        owned_shares = self.owned_shares_per_day(trading_days, orders_by_date)
        # cash_balances_per_day = self.calculate_cash_balances_per_day(trading_days, initial_cash_amount, owned_shares, d_data['close'])
        # equity_balances_per_day = self.calculate_equity_balances_per_day(trading_days, owned_shares, d_data['close'])
        #
        # daily_portfolio_balance = self.calculate_portfolio_balance(cash_balances_per_day, equity_balances_per_day)
        #
        # self.output_balances(daily_portfolio_balance, output_file)

    def owned_shares_per_day(self, trading_days, orders_by_date):
        #Dictionary of dictionaries keyed by date. Second dimension dictionary is running total of stock and shares for that day
        share_allocation_by_date = {}
        for i in range(len(trading_days)):
            trading_day = trading_days[i]


    def download_data_from_yahoo(self, date_start, date_end, symbols, ls_keys):
        # Yahoo data date_end is exclusive, need to add a day to get the data we want
        date_end_extension = date_end + dt.timedelta(days=1)
        ldt_timestamps = du.getNYSEdays(date_start, date_end_extension, dt.timedelta(hours=16))

        symbols.add('SPY')
        dataobj = da.DataAccess('Yahoo')

        print "Downloading data from Yahoo"
        ldf_data = dataobj.get_data(ldt_timestamps, symbols, ls_keys)
        d_data = dict(zip(ls_keys, ldf_data))

        for s_key in ls_keys:
            d_data[s_key] = d_data[s_key].fillna(method='ffill')
            d_data[s_key] = d_data[s_key].fillna(method='bfill')
            d_data[s_key] = d_data[s_key].fillna(1.0)

        return d_data, ldt_timestamps

    def extract_symbols(self, orders_file):
        symbols = set()

        with open(orders_file, 'rb') as csvfile:
            orders_reader = csv.reader(csvfile, delimiter=',')
            for order in orders_reader:
                symbols.add(order[3])
                # order_date = time.strptime(order[0].concat(' ').concat(order[1]).concat(' ').concat(order[2]), '%Y %m %d')
        return symbols

    def collate_orders_per_day(self, orders_file):
        orders_by_date = {}

        with open(orders_file, 'rb') as csvfile:
            orders_reader = csv.reader(csvfile, delimiter=',')
            for order in orders_reader:
                order_entry = []
                order_entry.append(order[3]) # ticker
                order_entry.append(order[4]) # Buy/Sell
                order_entry.append(order[5]) # Number shares

                date_of_order = dt.datetime(int(order[0]), int(order[1]), int(order[2]), 0, 0, 0, 0)
                current_orders = orders_by_date.get(date_of_order)
                if current_orders is None:
                    list_of_orders = []
                    list_of_orders.append(order_entry)
                    orders_by_date[date_of_order] = list_of_orders
                else:
                    current_orders.append(order_entry)

        return collections.OrderedDict(sorted(orders_by_date.items()))

    # def calculate_portfolio_balance(self, trading_days, initial_cash_amount, orders_by_date, closing_prices):
    #
    #     # Go through each day, check if there's an order, if there is, execute it.
    #     # End of day balance = cash + n(ticker closing price * shares)
    #     running_total = Decimal(initial_cash_amount)
    #     share_allocation = {}
    #     getcontext().prec = 2
    #     daily_balances = collections.OrderedDict()
    #
    #     #We have to adjust to get the same timestamp as that returned from Yahoo
    #     now = date_start + date_start.replace(hour=16)
    #     while(True):
    #         if(now > date_end):
    #             break
    #         now = date_start + dt.timedelta(days=1)
    #         orders = orders_by_date[now]
    #         if orders == nil
    #
    #
    #     for order_date in orders_by_date.keys():
    #         orders = orders_by_date.get(order_date)
    #         for order in orders:
    #
    #             adjusted_order_date = order_date.replace(hour=16)
    #             ticker = order[0]
    #             buy_sell = order[1]
    #             number_shares = order[2]
    #             closing_prices_for_ticker = closing_prices[ticker]
    #             closing_price_on_day = closing_prices_for_ticker[adjusted_order_date]
    #             if buy_sell == 'Buy':
    #                 running_total += (Decimal(closing_price_on_day) * Decimal(number_shares))
    #             elif buy_sell == 'Sell':
    #                 running_total -= (Decimal(closing_price_on_day) * Decimal(number_shares))
    #             else:
    #                 raise Exception("Unrecognised buy/sell attribute: %s " % buy_sell)
    #
    #             daily_balances[adjusted_order_date] = running_total
    #
    #     return daily_balances

    def output_balances(self, daily_portfolio_balances, output_file):
        with open(output_file, 'wb') as csvfile:
            writer = csv.writer(csvfile, delimiter=',')
            for date_of_balance in daily_portfolio_balances.keys():
                balance = daily_portfolio_balances.get(date_of_balance)
                balance_string = "%.2f" % float(balance)
                writer.writerow([str(date_of_balance), balance_string])


if __name__ == '__main__':
    if len(sys.argv) != 4:
        raise SyntaxError("Three arguments expected: <<cash value>> <<orders file>> <<output file>>")

    initial_cash_amount = sys.argv[1]
    orders_file = sys.argv[2]
    output_file = sys.argv[3]

    print "Initial cash amount %s " % initial_cash_amount
    print "Orders file: %s " % orders_file
    print "Output file: %s " % output_file

    marketsim = MarketSimulator()
    marketsim.run(initial_cash_amount, orders_file, output_file)
