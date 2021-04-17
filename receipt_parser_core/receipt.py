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
import fnmatch
import json
import re
from collections import namedtuple
from difflib import get_close_matches

import dateutil.parser


class Receipt(object):
    """ Market receipt to be parsed """

    def __init__(self, config, raw):
        """
        :param config: ObjectView
            Config object
        :param raw: [] of str
            Lines in file
        """

        self.config = config
        self.market = None
        self.date = None
        self.sum = None
        self.items = None
        self.lines = raw
        self.normalize()
        self.parse()

    def normalize(self):
        """
        :return: void
            1) strip empty lines
            2) convert to lowercase
            3) encoding?

        """

        self.lines = [
            line.lower() for line in self.lines if line.strip()
        ]

    def parse(self):
        """
        :return: void
            Parses obj data
        """

        self.market = self.parse_market()
        self.date = self.parse_date()
        self.sum = self.parse_sum()
        self.items = self.parse_items()

    def fuzzy_find(self, keyword, accuracy=0.6):
        """
        :param keyword: str
            The keyword string to look for
        :param accuracy: float
            Required accuracy for a match of a string with the keyword
        :return: str
            Returns the first line in lines that contains a keyword.
            It runs a fuzzy match if 0 < accuracy < 1.0
        """

        for line in self.lines:
            words = line.split()
            # Get the single best match in line
            matches = get_close_matches(keyword, words, 1, accuracy)
            if matches:
                return line

    def parse_date(self):
        """
        :return: date
            Parses data
        """

        for line in self.lines:
            match = re.search(self.config.date_format, line)
            if match:  # We"re happy with the first match for now
                # validate date using the dateutil library (see: https://dateutil.readthedocs.io/)
                date_str = match.group(1)
                date_str = date_str.replace(" ", "")
                try:
                    dateutil.parser.parse(date_str)
                except ValueError:
                    return None

                return date_str

    def parse_items(self):
        items = []
        item = namedtuple("item", ("article", "sum"))

        ignored_words = self.config.ignore_keys
        stop_words = self.config.sum_keys

        if self.market == "Metro":
            item_format = self.config.item_format_metro
        else:
            item_format = self.config.item_format

        for line in self.lines:
            if self.market != "Metro":
                for stop_word in stop_words:
                    if fnmatch.fnmatch(line, f"*{stop_word}*"):
                        return items

            match = re.search(item_format, line)
            if hasattr(match, 'group'):
                article_name = match.group(1)

                if match.group(2) == "-":
                    article_sum = "-" + match.group(3).replace(",", ".")
                else:
                    article_sum = match.group(3).replace(",", ".")
            else:
                continue

            if len(article_name) > 3:
                parse_stop = None
                for word in ignored_words:
                    parse_stop = fnmatch.fnmatch(article_name, f"*{word}*")
                    if parse_stop:
                        break

                if not parse_stop:
                    items.append(item(article_name, article_sum))

        return items

    def parse_market(self):
        """
        :return: str
            Parses market data
        """

        for int_accuracy in range(10, 6, -1):
            accuracy = int_accuracy / 10.0

            min_accuracy, market_match = -1, None
            for market, spellings in self.config.markets.items():
                for spelling in spellings:
                    line = self.fuzzy_find(spelling, accuracy)
                    if line and (accuracy < min_accuracy or min_accuracy == -1):
                        min_accuracy = accuracy
                        market_match = market
                        return market_match

        return market_match

    def parse_sum(self):
        """
        :return: str
            Parses sum data
        """

        for sum_key in self.config.sum_keys:
            sum_line = self.fuzzy_find(sum_key)
            if sum_line:
                # Replace all commas with a dot to make
                # finding and parsing the sum easier
                sum_line = sum_line.replace(",", ".")
                # Parse the sum
                sum_float = re.search(self.config.sum_format, sum_line)
                if sum_float:
                    return sum_float.group(0)

    def to_json(self):
        """
        :return: json
            Convert Receipt object to json
        """
        object_data = {
            "market": self.market,
            "date": self.date,
            "sum": self.sum,
            "items": self.items,
            "lines": self.lines
        }

        return json.dumps(object_data)
