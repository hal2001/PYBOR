# Copyright © 2017 Ondrej Martinsky, All rights reserved
# http://github.com/omartinsky/pybor
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


from yc_date import *
from pandas import *
import enum, os


class DCC(enum.Enum):
    ACT365 = 0
    ACT360 = 1

    def get_denominator(self):
        if self == DCC.ACT360:
            return 360.
        elif self == DCC.ACT365:
            return 365.
        assert False


class CalculationType(enum.Enum):
    PLAIN = 0
    AVERAGING = 1
    NONE = 2


class CouponFreq(enum.Enum):
    CONTINUOUS = 0
    DAILY = 1
    QUARTERLY = 2
    ZERO = 3

class Convention:
    def __init__(self, reset_frequency, calculation_frequency, payment_frequency, dcc):
        assert_type(reset_frequency, Tenor)
        assert_type(calculation_frequency, Tenor)
        assert_type(payment_frequency, Tenor)
        assert_type(dcc, DCC)
        self.reset_frequency = reset_frequency
        self.calculation_frequency = calculation_frequency
        self.payment_frequency = payment_frequency
        self.dcc = dcc

class Conventions:
    def __init__(self):
        self.map = dict()

    def FromSpreadsheet(excel_file):
        conventions = Conventions()
        conventions.map = dict()
        assert os.path.exists(excel_file)
        xl = ExcelFile(excel_file)
        dataframe = xl.parse('Conventions', index_col='Index', parse_cols='A:E')
        for index, row in dataframe.iterrows():
            conv = Convention(
                reset_frequency = Tenor(row['Reset Frequency']),
                calculation_frequency = Tenor(row['Calculation Period Frequency']),
                payment_frequency = Tenor(row['Payment Frequency']),
                dcc = enum_from_string(DCC, row['Day Count Convention']),
            )
            assert index not in conventions.map
            conventions.map[index] = conv
        return conventions

    def get(self, convention_name):
        if convention_name not in self.map:
            raise BaseException("Unable to get convention %s" % convention_name)
        return self.map[convention_name]

global_conventions = Conventions.FromSpreadsheet('conventions.xlsx')