Module receipt_parser_core.receipt
==================================

Classes
-------

`Receipt(config, raw)`
:   Market receipt to be parsed 
    
    :param config: ObjectView
        Config object
    :param raw: [] of str
        Lines in file

    ### Methods

    `fuzzy_find(self, keyword, accuracy=0.6)`
    :   :param keyword: str
            The keyword string to look for
        :param accuracy: float
            Required accuracy for a match of a string with the keyword
        :return: str
            Returns the first line in lines that contains a keyword.
            It runs a fuzzy match if 0 < accuracy < 1.0

    `normalize(self)`
    :   :return: void
            1) strip empty lines
            2) convert to lowercase
            3) encoding?

    `parse(self)`
    :   :return: void
            Parses obj data

    `parse_date(self)`
    :   :return: date
            Parses data

    `parse_items(self)`
    :

    `parse_market(self)`
    :   :return: str
            Parses market data

    `parse_sum(self)`
    :   :return: str
            Parses sum data

    `to_json(self)`
    :   :return: json
            Convert Receipt object to json