import arrow


def write_to_log(isLogging, logString, valueDict={}):
    """
    (bool, str, dict)
    If isLogging is True, append the formatted string with the values to
    log/DD-MM-YYYY.txt

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
        now = arrow.now('local')
        date = now.format('DD-MM-YYYY')
        with open('./log/' + date, 'a') as f:
            log = logString.format(**valueDict)
            f.write(now.isoformat() + ": " + log + "\n")

    return None



