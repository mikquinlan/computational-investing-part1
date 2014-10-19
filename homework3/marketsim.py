__author__ = 'mquinlan'

import sys


if __name__ == '__main__':
    if len(sys.argv) != 4:
        raise SyntaxError("Three arguments expected: <<cash value>> <<orders file>> <<output file>>")

    initial_cash_amount = sys.argv[1]
    orders_file = open(sys.argv[2], 'r')
    output_file = open(sys.argv[3], 'w')

    print "Initial cash amount %d " % initial_cash_amount
    print "Orders file: %s " % orders_file
    print "Output file: %s " % output_file
