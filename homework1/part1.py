__author__ = 'mquinlan'
# QSTK Imports
import QSTK.qstkutil.qsdateutil as du
import QSTK.qstkutil.tsutil as tsu
import QSTK.qstkutil.DataAccess as da

# Third Party Imports
import datetime as dt
import matplotlib.pyplot as plt
import pandas as pd

class Simulator:

    TRADING_DAYS_PER_YEAR = 265
    RISK_FREE_RATE = 0

    # Return vol, daily_return, sharp_ration, cumulative_return
    def simulate(self, start_date, end_date, symbols, allocations):
        print "Using start date %s " % start_date
        print "Using end date %s " % end_date
        print "Using symbols %s " % symbols
        print "Using allocations %s " % allocations

        volume = 1
        daily_ret = 2
        sharpe = 3
        cum_ret = 4

        return volume, daily_ret, sharpe, cum_ret


if __name__ == '__main__':
    start_date = dt.datetime(2011, 01, 01)
    end_date = dt.datetime(2011, 12, 31)
    symbols = ['GOOG', 'AAPL', 'GLD', 'XOM']
    allocations = [0.2, 0.3, 0.4, 0.1]

    simulator = Simulator()

    vol, daily_ret, sharpe, cum_ret = simulator.simulate(start_date, end_date, symbols, allocations)

    print "For portfolio with stock %s" % symbols + " and allocations %s" %allocations
    print "Volume = %s" % vol
    print "Daily Return = %s" % daily_ret
    print "Sharpe Ration = %s" % sharpe
    print "Cumulative Return = %s" % cum_ret
