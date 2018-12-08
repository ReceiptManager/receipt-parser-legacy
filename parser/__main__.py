from parser import parser

def main():
    config = parser.read_config()
    receipt_files = parser.get_files_in_folder(config.receipts_path)
    stats = parser.ocr_receipts(config, receipt_files)
    parser.output_statistics(stats)


if __name__ == "__main__":
    main()
