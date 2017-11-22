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
import re
import time
from collections import defaultdict
from difflib import get_close_matches

import yaml

from objectview import ObjectView

THIS_FOLDER = os.getcwd()
STATS_OUTPUT_FORMAT = "{0:10.0f},{1:d},{2:d},{3:d},{4:d},\n"
VERBOSE_OUTPUT_FORMAT = "Text, Market, Date, Sum"


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
        self.market = self.date = self.sum = None
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
            m = re.match(self.config.date_format, line)
            if m:  # We"re happy with the first match for now
                return m.group(1)

    def parse_market(self):
        """
        :return: str
            Parses market data
        """
        
        for int_accuracy in range(10, 6, -1):
            accuracy = int_accuracy / 10.0

            for market, spellings in self.config.markets.items():
                for spelling in spellings:
                    line = self.fuzzy_find(spelling, accuracy)
                    if line:
                        print(line, accuracy, market)
                        return market

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


def read_config(file="config.yml"):
    """
    :param file: str
        Name of file to read
    :return: ObjectView
        Parsed config file
    """

    stream = open(os.path.join(THIS_FOLDER, file), "r")
    docs = yaml.safe_load(stream)
    return ObjectView(docs)


def get_files_in_folder(folder, include_hidden=False):
    """
    :param folder: str
        Path to folder to list
    :param include_hidden: bool
        True iff you want also hidden files
    :return: [] of str
        List of full path of files in folder
    """

    files = os.listdir(folder)  # list content of folder
    if not include_hidden:  # avoid files starting with "."
        files = [
            f for f in files if not f.startswith(".")
        ]  # 

    files = [
        os.path.join(folder, f) for f in files
    ]  # complete path
    return [
        f for f in files if os.path.isfile(f)
    ]  # just files


def output_statistics(stats, write_file=False):
    """
    :param stats: {}
        Statistics details
    :param write_file: bool
        True iff you want output file
    :return: void
        Prints stats (and eventually writes them)
    """

    stats_str = STATS_OUTPUT_FORMAT.format(
        time.time(), stats["total"], stats["market"], stats["date"],
        stats["sum"]
    )
    print(stats_str)

    if write_file:
        with open("stats.csv", "a") as stats_file:
            stats_file.write(stats_str)


def percent(numerator, denominator):
    """
    :param numerator: float
        Numerator of fraction
    :param denominator: float
        Denominator of fraction
    :return: str
        Fraction as percentage
    """

    if denominator == 0:
        out = "0"
    else:
        out = str(int(numerator / float(denominator) * 100))

    return out + "%"


def ocr_receipts(config, receipt_files):
    """
    :param config: ObjectView
        Parsed config file
    :param receipt_files: [] of str
        List of files to parse
    :return: {}
        Stats about files
    """

    stats = defaultdict(int)
    print(VERBOSE_OUTPUT_FORMAT)
    for receipt_path in receipt_files:
        with open(receipt_path) as receipt:
            receipt = Receipt(config, receipt.readlines())
            print(receipt_path, receipt.market, receipt.date, receipt.sum)

            stats["total"] += 1
            if receipt.market:
                stats["market"] += 1
            if receipt.date:
                stats["date"] += 1
            if receipt.sum:
                stats["sum"] += 1
    return stats


def main():
    """
    :return:
    """

    config = read_config()
    receipt_files = get_files_in_folder(config.receipts_path)
    stats = ocr_receipts(config, receipt_files)
    output_statistics(stats, False)


if __name__ == "__main__":
    main()
