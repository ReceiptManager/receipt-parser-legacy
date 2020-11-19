from .config import read_config
from .parse import *

def main():
  config = read_config()
  receipt_files = get_files_in_folder(config.receipts_path)
  stats = ocr_receipts(config, receipt_files)  
  #output_statistics(stats)

