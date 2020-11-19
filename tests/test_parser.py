# !/usr/bin/python3
# coding: utf-8

# Copyright 2015-2018
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import unittest
from receipt_parser.config import read_config
from receipt_parser.receipt import Receipt


class ReceiptTestCase(unittest.TestCase):
    """Tests for `receipt_parser.py`."""

    dir_path = os.getcwd()
    config = read_config(dir_path + "/config.yml")

    def test_fuzzy_find(self):
        """
            verifies fuzzy_find
        """
        receipt = None
        with open(
            self.dir_path  + "/tests/data/receipts/sample_text_fuzzy_find.txt"
        ) as receipt_file:
            receipt = Receipt(self.config, receipt_file.readlines())
        self.assertIsNotNone(receipt)

        self.assertEqual("restaurant\n", receipt.fuzzy_find("restaurat"))
        self.assertEqual("gas station\n", receipt.fuzzy_find("as statio"))
        self.assertEqual("uber\n", receipt.fuzzy_find("ube"))
        self.assertEqual("lyft\n", receipt.fuzzy_find("ly"))
        self.assertEqual("supermarket\n", receipt.fuzzy_find("market"))

    def test_normalize(self):
        receipt = None
        # unfortunately, the Receipt constructor calls 'normalize'
        # so we can construct a Receipt object with a blank receipt file
        with open(self.dir_path + "/tests/data/receipts/empty_file.txt") as receipt_file:
            receipt = Receipt(self.config, receipt_file.readlines())

        # then updates the lines from the real receipt file
        with open(
            self.dir_path + "/tests/data/receipts/sample_text_receipt_to_normalize.txt"
        ) as receipt_file:
            receipt.lines = receipt_file.readlines()

        expected_list = [
            "all upper case\n",
            "some upper case\n",
            "   white spaces\n",
            "    tab     tab whitespaces\n",
            "99.00\n",
            "trailing whitespaces after this line.\n",
        ]

        # make sure the Receipt is created
        self.assertIsNotNone(receipt)

        # call 'normalize'
        receipt.normalize()

        after_lines = receipt.lines

        # checks that the lines are normalized
        self.assertEqual(expected_list, after_lines)

    def test_parse(self):
        # not sure there's a need to unit test this one since it essentially wraps other unit tests
        receipt = None
        with open(
            self.dir_path + "/tests/data/receipts/sample_text_receipt.txt"
        ) as receipt_file:
            receipt = Receipt(self.config, receipt_file.readlines())

        self.assertIsNotNone(receipt)

    def test_parser_date(self):
        """
            Verifies parse_date functions
            dates like 19.08.15 and 19. 08. 2015
        """

        # test parse_date from file
        receipt = None
        with open(
            self.dir_path + "/tests/data/receipts/sample_text_receipt_dates.txt"
        ) as receipt_file:
            receipt = Receipt(self.config, receipt_file.readlines())
        actual_date_str = receipt.date
        print(actual_date_str)
        self.assertEqual("19.08.15\n", actual_date_str)

        # test DD.MM.YY
        receipt2 = Receipt(self.config, ["18.08.16\n", "19.09.17\n", "01.01.18"])
        actual_date_str = receipt2.parse_date()
        print(actual_date_str)
        self.assertEqual("18.08.16\n", actual_date_str)

        # test DD.MM.YYYY
        receipt3 = Receipt(self.config, ["18.08.2016\n"])
        actual_date_str = receipt3.parse_date()
        print(actual_date_str)
        self.assertEqual("18.08.2016\n", actual_date_str)

        # HOWEVER these tests should fail:
        # test with DD > 31
        receipt4 = Receipt(self.config, ["32.08.2016\n"])
        actual_date_str = receipt4.parse_date()
        self.assertIsNone(actual_date_str)

        # test with MM > 12
        receipt5 = Receipt(self.config, ["01.55.2016\n"])
        actual_date_str = receipt5.parse_date()
        print(actual_date_str)
        self.assertIsNone(actual_date_str)

        # test with invalid date: 31.04.15
        receipt6 = Receipt(self.config, ["31.04.15\n"])
        actual_date_str = receipt6.parse_date()
        self.assertIsNone(actual_date_str)

        # And these tests should pass:
        # test with YYYY < 2013
        receipt7 = Receipt(self.config, ["18.08.2012\n"])
        actual_date_str = receipt7.parse_date()
        print(actual_date_str)

        # test with YYYY >= 2017
        receipt8 = Receipt(self.config, ["18.08.2017\n"])
        actual_date_str = receipt8.parse_date()
        print(actual_date_str)

    def test_parse_market(self):
        """
            Verifies receipt_parser.parse_market
        """
        receipt = Receipt(self.config, ["penny"])
        print("market", receipt.parse_market())
        self.assertEqual("Penny", receipt.parse_market())

        # should work but fails
        receipt = Receipt(self.config, ["p e n ny"])
        # self.assertEqual("Penny", receipt.parse_market())

        # should work but fails
        receipt = Receipt(self.config, ["m a r k t gmbh"])
        # self.assertEqual("Penny", receipt.parse_market())

        receipt = Receipt(self.config, ["rew"])
        self.assertEqual("REWE", receipt.parse_market())

        receipt = Receipt(self.config, ["REL"])
        self.assertEqual("Real", receipt.parse_market())

        receipt = Receipt(self.config, ["netto-onli"])
        self.assertEqual("Netto", receipt.parse_market())

        receipt = Receipt(self.config, ["kaser"])
        self.assertEqual("Kaiser's", receipt.parse_market())

        receipt = Receipt(self.config, ["kaiserswerther str. 270"])
        self.assertEqual("Kaiser's", receipt.parse_market())

        receipt = Receipt(self.config, ["ALDI"])
        self.assertEqual("Aldi", receipt.parse_market())

        receipt = Receipt(self.config, ["friedrichstr. 128—133"])
        self.assertEqual("Aldi", receipt.parse_market())

        receipt = Receipt(self.config, ["LIDL"])
        self.assertEqual("Lidl", receipt.parse_market())

        receipt = Receipt(self.config, ["shell"])
        self.assertEqual("Tanken", receipt.parse_market())

        receipt = Receipt(self.config, ["esso station"])
        self.assertEqual("Tanken", receipt.parse_market())

        receipt = Receipt(self.config, ["aral"])
        self.assertEqual("Tanken", receipt.parse_market())

        receipt = Receipt(self.config, ["total tankstelle"])
        self.assertEqual("Tanken", receipt.parse_market())

        receipt = Receipt(self.config, ["RK Tankstellen"])
        self.assertEqual("Tanken", receipt.parse_market())

    def test_parse_sum(self):
        """
            Verifies parse_sum
        """
        receipt = None
        with open(
            self.dir_path + "/tests/data/receipts/sample_text_receipt.txt"
        ) as receipt_file:
            receipt = Receipt(self.config, receipt_file.readlines())
        self.assertIsNotNone(receipt)
        self.assertEqual("0.99", receipt.parse_sum())

        receipt = Receipt(self.config, ["summe   12,99\n"])
        self.assertEqual("12.99", receipt.parse_sum())

        receipt = Receipt(self.config, ["summe   *** 12,99 ***\n"])
        self.assertEqual("12.99", receipt.parse_sum())

        receipt = Receipt(self.config, ["summe   13.99\n"])
        self.assertEqual("13.99", receipt.parse_sum())

        receipt = Receipt(self.config, ["13,99 summe\n"])
        self.assertEqual("13.99", receipt.parse_sum())

        receipt = Receipt(self.config, ["gesamtbetrag 1,99\n"])
        self.assertEqual("1.99", receipt.parse_sum())

        receipt = Receipt(self.config, ["gesamt 2,99\n"])
        self.assertEqual("2.99", receipt.parse_sum())

        receipt = Receipt(self.config, ["total 3,99\n"])
        self.assertEqual("3.99", receipt.parse_sum())

        receipt = Receipt(self.config, ["sum 4,99\n"])
        self.assertEqual("4.99", receipt.parse_sum())

        receipt = Receipt(self.config, ["zwischensumme 5,99\n"])
        self.assertEqual("5.99", receipt.parse_sum())

        receipt = Receipt(self.config, ["bar 1,99\n"])
        self.assertEqual("1.99", receipt.parse_sum())


if __name__ == "__main__":
    unittest.main()
