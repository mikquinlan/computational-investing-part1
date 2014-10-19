__author__ = 'mquinlan'

import sys
import csv
import datetime
import collections

class MarketSimulator:
    def run(self, initial_cash_amount, orders_file, output_file):
        symbols = self.extract_symbols(orders_file)
        print 'Symbols %s ' % symbols

        orders_per_day = self.collate_orders_per_day(orders_file)
        print 'Orders per day %s ' % orders_per_day

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
                print "order %s " % order
                order_entry = []
                order_entry.append(order[3]) # ticker
                order_entry.append(order[4]) # Buy/Sell
                order_entry.append(order[5]) # Number shares

                date_of_order = datetime.datetime(int(order[0]), int(order[1]), int(order[2]), 0, 0, 0, 0)
                current_orders = orders_by_date.get(date_of_order)
                if current_orders is None:
                    list_of_orders = []
                    list_of_orders.append(order_entry)
                    orders_by_date[date_of_order] = list_of_orders
                else:
                    current_orders.append(order_entry)

        return collections.OrderedDict(sorted(orders_by_date.items()))


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
