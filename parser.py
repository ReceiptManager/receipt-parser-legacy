#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
import re
from os import listdir
from os.path import isfile, join
from difflib import get_close_matches
from collections import defaultdict
from objectview import objectview
import yaml


class Receipt(object):
    def __init__(self, config, raw):
        self.config = config
        self.market = self.date = self.sum = None
        self.raw = self.normalize(raw)
        self.parse()

    def normalize(self, raw):
        """ Inputs a list of raw lines

            1) strip empty lines
            2) convert to lowercase
            3) encoding?

        """
        normalized_lines = []
        for line in raw:
            norm_line = line.strip()
            if not norm_line:
                continue
            norm_line = norm_line.lower()
            normalized_lines.append(norm_line)
        return normalized_lines

    def parse(self):
        self.market = self.parse_market()
        self.date = self.parse_date()
        self.sum = self.parse_sum()

    def fuzzy_find(self, keyword, accuracy=0.6):
        """
        Returns the first line in lines that contains a keyword.
        It runs a fuzzy match if 0 < accuracy < 1.0
        :param keyword: The keyword string to look for
        :param accuracy: Required accuracy for a match of a string with the keyword
        """
        for line in self.raw:
            words = line.split()
            # Get the single best match in line
            matches = get_close_matches(keyword, words, 1, accuracy)
            if matches:
                return line

    def parse_date(self):
        for line in self.raw:
            m = re.match(self.config.date_format, line)
            if m:
                # We're happy with the first match for now
                return m.group(1)

    def parse_market(self):
        for int_accuracy in range(10, 6, -1):
            accuracy = int_accuracy / 10.0
            for market, spellings in self.config.markets.items():
                for spelling in spellings:
                    line = self.fuzzy_find(spelling, accuracy)
                    if line:
                        print(line, accuracy, market)
                        return market

    def parse_sum(self):
        for sum_key in self.config.sum_keys:
            sum_line = self.fuzzy_find(sum_key)
            if sum_line:
                # Replace all commas with a dot to make
                # finding and parsing the sum easier
                sum_line = sum_line.replace(',', '.')
                # Parse the sum
                sum_float = re.search(self.config.sum_format, sum_line)
                if sum_float:
                    return sum_float.group(0)


def main():
    config = read_config()
    receipt_files = [f for f in listdir(config.receipts_path)
                     if isfile(join(config.receipts_path, f))]
    # Ignore hidden files like .DS_Store
    receipt_files = [f for f in receipt_files if not f.startswith('.')]
    stats = defaultdict(int)

    print('Text, Market, Date, Sum')
    for receipt_file in receipt_files:
        receipt_path = join(config.receipts_path, receipt_file)
        with open(receipt_path) as receipt:
            lines = receipt.readlines()
            receipt = Receipt(config, lines)
            print(receipt_path, receipt.market, receipt.date, receipt.sum)
            stats["total"] += 1
            if receipt.market:
                stats["market"] += 1
            if receipt.date:
                stats["date"] += 1
            if receipt.sum:
                stats["sum"] += 1
    statistics(stats, False)


def read_config():
    stream = open("config.yml", "r")
    docs = yaml.safe_load(stream)
    return objectview(docs)


def statistics(stats, write=False):
    stats_str = "{0:10.0f},{1:d},{2:d},{3:d},{4:d},\n".format(
        time.time(), stats["total"], stats["market"], stats["date"], stats["sum"])
    print(stats_str)
    if write:
        with open("stats.csv", "a") as stats_file:
            stats_file.write(stats_str)


def percent(nom, denom):
    return str(int(nom / float(denom) * 100)) + "%"


if __name__ == "__main__":
    main()
