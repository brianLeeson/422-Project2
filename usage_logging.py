import arrow


def write_to_log(isLogging, logString, valueDict={}):
    """
    (bool, str, dict)
    If isLogging is True, append the formatted string with the values to
    log/DD-MM-YYYY.txt

    NOTE: NO SECURE DATA SHOULD BE LOGGED

    :param logString: string. must be in form: "{key1} ... {key2}"
    :param valueDict: dict. must be of the form: {"key1": value1, "key2": value2, ...}
    :param isLogging: Bool
    :return: None

    Example:
    write_to_log(True, "Hello {key1}!", {"key1": "World"})
    ISOTIME: Hello World!
    above will be written to './log/DATE'
    """

    if isLogging:
        date_format = "YYYY-MM-DD"
        log_folder_path = "./log/"
        now = arrow.now('local')
        today = now.format(date_format)
        file = log_folder_path + today

        # opening and closing the file ensure that it exits
        f = open(file, 'w')
        f.close()

        with open(file, 'a') as f:
            log = logString.format(**valueDict)
            f.write(now.format(date_format + ", HH:mm") + ": " + log + "\n")

    return None



