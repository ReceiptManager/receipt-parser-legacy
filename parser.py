#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
from dateutil import parser
import re
from os import listdir
from os.path import isfile, join
from difflib import get_close_matches
from collections import defaultdict
from string import maketrans

# Where the receipts are stored
# Receipts should be simple text files
receipts_path = "txt"

# An ugly regex to match dates like 19.08.15 19. 08. 2015
date_format = '.*?(?P<date>(\d{2,4}(\.\s?|[^a-zA-Z\d])\d{2}(\.\s?|[^a-zA-Z\d])(20)?1[3-6]))\s+'

class Receipt():
  def __init__(self, raw):
    self.market = self.date = self.sum = None
    # Market names roughly ordered by likelyhood.
    self.markets = [
        "penny", "p e n n y", "rewe", "real", "netto",
        "kaiser", "aldi", "drogerie", "kodi", "sb warenhaus", "lidl", "shell",
        "aral", "total", "m a r k t gmbh", "RK Tankstellen", "Schuhhaus"
    ]
    # A number of market locations for fuzzy parsing
    self.market_locations = {
      'kaiserswerther straße 270': "kaiser",
      'friedrichstr 128—133': "aldi"
    }
    # Sum keys roughly ordered by likelyhood.
    self.sum_keys = ["summe", "gesamtbetrag", "gesamt", "total", "sum.",
                     "zwischensumme", "bar"]
    self.raw = map(str.lower, raw)
    self.raw = [line.decode('utf-8') for line in self.raw]
    self.parse()

  def parse(self):
    self.market = self.parse_market()
    self.date = self.parse_date()
    self.sum = self.parse_sum()

  def fuzzy_find(self, keyword, accuracy=0.6):
    """
    Returns the first line in lines that contains a keyword.
    It runs a fuzzy match if 0 < accuracy < 1.0
    """
    for line in self.raw:
      words = line.split()
      # Get the single best match in line
      matches = get_close_matches(keyword, words, 1, accuracy)
      if matches:
        return line

  def fix_numbers(self, line):
    """
    Fix some common OCR number reading errors
    e.g. I => 1, O => 0
    """
    fixed_line = []
    for char in line:
      if char in self.ocr_number_fixes.keys():
        char = self.ocr_number_fixes[char]
      fixed_line.append(char)
    return ''.join(fixed_line)

  def parse_date(self):
    for line in self.raw:
      m = re.match(date_format, line)
      if m:
        # We're happy with the first match for now
        return m.group(1)

  def parse_market(self):
    for line in self.raw:
      for market in self.markets:
        if market in line:
          # Hooray!
          return market
    # Errm... no direct match.
    # We need to do fuzzy matching or so
    for market in self.markets:
      line = self.fuzzy_find(market)
      if line:
        return market
    return self.parse_market_by_location()

  def parse_market_by_location(self):
    for location, market in self.market_locations.iteritems():
      if self.fuzzy_find(location, 0.4):
        return market

  def parse_sum(self):
    for sum_key in self.sum_keys:
      sum_line = self.fuzzy_find(sum_key)
      if sum_line:
        # Replace all commas with a dot to make
        # finding and parsing the sum easier
        sum_line = sum_line.replace(',','.')
        # Parse the sum
        sum_float = re.search('\d+(\.\s?|\,\s?|[^a-zA-Z\d])\d{2}', sum_line)
        if sum_float:
          return sum_float.group(0)

def main():
  receipt_files = [ f for f in listdir(receipts_path) if isfile(join(receipts_path,f)) ]
  # Ignore hidden files like .DS_Store
  receipt_files = [ f for f in receipt_files if not f.startswith('.')]
  stats = defaultdict(int)

  for receipt_file in receipt_files:
    receipt_path = join(receipts_path, receipt_file)
    with open(receipt_path) as receipt:
      lines = receipt.readlines()
      receipt = Receipt(lines)
      print receipt_path, receipt.market, receipt.date, receipt.sum
      stats["total"] += 1
      if receipt.market: stats["market"] += 1
      if receipt.date: stats["date"] += 1
      if receipt.sum: stats["sum"] += 1
  statistics(stats, False)

def statistics(stats, write = False):
  stats_str = "{0},{1},{2},{3},{4},\n".format(
      int(time.time()), stats["total"], stats["market"], stats["date"], stats["sum"])
  print stats_str
  if write:
    with open("stats.csv", "a") as stats_file:
        stats_file.write(stats_str)

def percent(nom, denom):
  return str(int(nom/float(denom)*100)) + "%"

if __name__ == "__main__":
  main()
