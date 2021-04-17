Module receipt_parser_core.parse
================================

Functions
---------

    
`get_files_in_folder(folder, include_hidden=False)`
:   :param folder: str
        Path to folder to list
    :param include_hidden: bool
        True iff you want also hidden files
    :return: [] of str
        List of full path of files in folder

    
`ocr_receipts(config, receipt_files)`
:   :param config: ObjectView
        Parsed config file
    :param receipt_files: [] of str
        List of files to parse
    :return: {}
        Stats about files

    
`output_statistics(stats, write_file='stats.csv')`
:   :param stats: {}
        Statistics details
    :param write_file: obj
        str iff you want output file (or else None)
    :return: void
        Prints stats (and eventually writes them)

    
`percent(numerator, denominator)`
:   :param numerator: float
        Numerator of fraction
    :param denominator: float
        Denominator of fraction
    :return: str
        Fraction as percentage

    
`results_to_json(config, receipt_files)`
: