__author__ = 'mquinlan'
# QSTK Imports
import QSTK.qstkutil.qsdateutil as du
import QSTK.qstkutil.tsutil as tsu
import QSTK.qstkutil.DataAccess as da

# Third Party Imports
import datetime as dt
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import time
import itertools
from decimal import *

class Simulator:

    TRADING_DAYS_PER_YEAR = 252
    RISK_FREE_RATE = 0
    TOTAL_TO_INVEST_DOLLARS = 100

    def readData(self, start_date, end_date, ls_symbols):
        #Create datetime objects for Start and End dates (STL)
        dt_start = dt.datetime(start_date[0], start_date[1], start_date[2])
        dt_end = dt.datetime(end_date[0], end_date[1], end_date[2])

        #Initialize daily timestamp: closing prices, so timestamp should be hours=16 (STL)
        dt_timeofday = dt.timedelta(hours=16)

        #Get a list of trading days between the start and end dates (QSTK)
        ldt_timestamps = du.getNYSEdays(dt_start, dt_end, dt_timeofday)

        #Create an object of the QSTK-dataaccess class with Yahoo as the source (QSTK)
        c_dataobj = da.DataAccess('Yahoo', cachestalltime=0)

        #Keys to be read from the data
        ls_keys = ['open', 'high', 'low', 'close', 'volume', 'actual_close']

        #Read the data and map it to ls_keys via dict() (i.e. Hash Table structure)
        ldf_data = c_dataobj.get_data(ldt_timestamps, ls_symbols, ls_keys)
        d_data = dict(zip(ls_keys, ldf_data))

        # Filling the data for NAN
        # for s_key in ls_keys:
        #     d_data[s_key] = d_data[s_key].fillna(method='ffill')
        #     d_data[s_key] = d_data[s_key].fillna(method='bfill')
        #     d_data[s_key] = d_data[s_key].fillna(1.0)

        return [d_data, dt_start, dt_end, dt_timeofday, ldt_timestamps]

    '''
    ' Calculate Portfolio Statistics
    ' @param na_normalized_price: NumPy Array for normalized prices (starts at 1)
    ' @param lf_allocations: allocation list
    ' @return list of statistics:
    ' (Volatility, Average Return, Sharpe, Cumulative Return)
    '''
    def calc_stats(self, na_normalized_price, lf_allocations):
        #Calculate cumulative daily portfolio value
        #row-wise multiplication by weights
        na_weighted_price = na_normalized_price * lf_allocations
        #row-wise sum
        na_portf_value = na_weighted_price.copy().sum(axis=1)

        #Calculate daily returns on portfolio
        na_portf_rets = na_portf_value.copy()
        tsu.returnize0(na_portf_rets)

        #Calculate volatility (stdev) of daily returns of portfolio
        f_portf_volatility = np.std(na_portf_rets)

        #Calculate average daily returns of portfolio
        f_portf_avgret = np.mean(na_portf_rets)

        #Calculate portfolio sharpe ratio (avg portfolio return / portfolio stdev) * sqrt(252)
        f_portf_sharpe = (f_portf_avgret / f_portf_volatility) * np.sqrt(Simulator.TRADING_DAYS_PER_YEAR)

        #Calculate cumulative daily return
        #...using recursive function
        def cumret(t, lf_returns):
            #base-case
            if t==0:
                return (1 + lf_returns[0])
            #continuation
            return (cumret(t-1, lf_returns) * (1 + lf_returns[t]))

        f_portf_cumrets = cumret(na_portf_rets.size - 1, na_portf_rets)

        return [f_portf_volatility, f_portf_avgret, f_portf_sharpe, f_portf_cumrets, na_portf_value]

    '''
    ' Simulate and assess performance of multi-stock portfolio
    ' @param li_startDate:	start date in list structure: [year,month,day] e.g. [2012,1,28]
    ' @param li_endDate:	end date in list structure: [year,month,day] e.g. [2012,12,31]
    ' @param ls_symbols:	list of symbols: e.g. ['GOOG','AAPL','GLD','XOM']
    ' @param lf_allocations:	list of allocations: e.g. [0.2,0.3,0.4,0.1]
    ' @param b_print:       print results (True/False)
    '''
    def simulate(self, start_date, end_date, ls_symbols, lf_allocations, b_print):

        start = time.time()

        #Check if ls_symbols and lf_allocations have same length
        if len(ls_symbols) != len(lf_allocations):
            print "ERROR: Make sure symbol and allocation lists have same number of elements."
            return
        #Check if lf_allocations adds up to 1
        sumAllocations = 0
        for x in lf_allocations:
            sumAllocations += x
        if sumAllocations != 1:
            print "ERROR: Make sure allocations add up to 1."
            return

        #Prepare data for statistics
        d_data = self.readData(start_date, end_date, ls_symbols)[0]

        #Get numpy ndarray of close prices (numPy)
        na_price = d_data['close'].values

        #Normalize prices to start at 1 (if we do not do this, then portfolio value
        #must be calculated by weight*Budget/startPriceOfStock)
        na_normalized_price = na_price / na_price[0,:]

        lf_Stats = self.calc_stats(na_normalized_price, lf_allocations)

        #Print results
        if b_print:
            print "Start Date: ", start_date
            print "End Date: ", end_date
            print "Symbols: ", ls_symbols
            print "Volatility (stdev daily returns): " , lf_Stats[0]
            print "Average daily returns: " , lf_Stats[1]
            print "Sharpe ratio: " , lf_Stats[2]
            print "Cumulative daily return: " , lf_Stats[3]

            print "Run in: " , (time.time() - start) , " seconds."

        #Return list: [Volatility, Average Returns, Sharpe Ratio, Cumulative Return]
        return lf_Stats[0:4]

    def optimize(self, start_date, end_date, ls_symbols):

        increments = np.arange(0, 1.1, 0.1)
        # combinations = it.combinations(range, len(ls_symbols))
        valid_portfolio_allocations = self.discover_valid_allocation_combinations()

        #Now have all the combinations that add up to 1, get the data then calculate figures and save the best sharp ratio
        d_data = self.readData(start_date, end_date, ls_symbols)[0]
        na_price = d_data['close'].values
        na_normalized_price = na_price / na_price[0, :]
        best_allocation = []
        best_sharp_ratio = 0
        for combination in valid_portfolio_allocations:
            f_portf_sharpe = self.calc_stats(na_normalized_price, combination)[2]
            if f_portf_sharpe > best_sharp_ratio:
                best_sharp_ratio = f_portf_sharpe
                best_allocation = combination
        print "After optimisation, the results are:"
        print "\nBest Sharpe Ratio: %s" % best_sharp_ratio
        print "\nBest allocation:"
        print (best_allocation)

    def discover_valid_allocation_combinations(self):
        min = 0.0
        max = 1.0
        increment = 0.1

        valid_allocations = []
        candidate_allocation = [0.0, 0.0, 0.0, 0.0]

        for first_allocation in self.frange(min, max, increment):
            for second_allocation in self.frange(min, max, increment):
                for third_allocation in self.frange(min, max, increment):
                    for fourth_allocation in self.frange(min, max, increment):
                        candidate_allocation[0] = first_allocation
                        candidate_allocation[1] = second_allocation
                        candidate_allocation[2] = third_allocation
                        candidate_allocation[3] = fourth_allocation
                        if self.is_valid_allocation(candidate_allocation):
                            valid_allocations.append(list(candidate_allocation))

        return valid_allocations

    def frange(self, start, end=None, inc=None):
        "A range function, that does accept float increments..."
        if end == None:
            end = start + 0.0
            start = 0.0

        if inc == None:
            inc = 1.0

        L = []
        while 1:
            next = start + len(L) * inc
            if inc > 0 and next >= end:
                break
            elif inc < 0 and next <= end:
                break
            L.append(next)

        return L

    def is_valid_allocation(self, allocations):
        if len(allocations) == 4:
            sum_allocations = 0.0
            for x in allocations:
                sum_allocations += x
            if sum_allocations == 1.0:
                return True

        return False


if __name__ == '__main__':
    start_date = [2011, 01, 01]
    end_date = [2011, 12, 31]
    # symbols = ['AAPL', 'GLD', 'GOOG', 'XOM']
    symbols = ['AXP', 'HPQ', 'IBM', 'HNZ']
    # allocations = [0.4, 0.4, 0.0, 0.2]
    allocations = [0.0, 0.0, 0.0, 1.0]

    simulator = Simulator()

    #volatility_std_dev, daily_ret, sharpe, cum_ret = simulator.simulate(start_date, end_date, symbols, allocations, True)
    simulator.optimize(start_date, end_date, symbols)

