# https://stackoverflow.com/questions/11410896/python-how-json-dumps-none-to-empty-string
import copy


# convert None to ''
def scrub(data):
    # Converts None to empty string
    ret = copy.deepcopy(data)
    # Handle dictionaries, lits & tuples. Scrub all values
    if isinstance(data, dict):
        for k, v in ret.items():
            ret[k] = scrub(v)
    if isinstance(data, (list, tuple)):
        for k, v in enumerate(ret):
            ret[k] = scrub(v)
    # Handle None
    if data is None:
        ret = ""
    # Finished scrubbing
    return ret
