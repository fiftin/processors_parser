import re

def parse_bytes(value):
    m = re.search(r'([\d.]+)\s*(B|KB|MB|GB|TB)', value)
    if m is None:
        return None
    rank = 1
    if m[2] == 'KB':
        rank = 1000
    elif m[2] == 'MB':
        rank = 1000_0000
    elif m[2] == 'GB':
        rank = 1000_000_000
    elif m[2] == 'TB':
        rank = 1000_000_000_000
    return round(float(m[1]) * rank)

def parse_value(value, value_type):
    value = value.strip()
    if value_type == 'TEXT':
        return value
    if value_type == 'INT':
        b = parse_bytes(value)
        if b is not None:
            return b
        return int(value.split(' ')[0])
    if value_type == 'REAL':
        return float(value.split(' ')[0])
    if value_type == 'NUMERIC':
        if value.startswith('$'):
            value = value[1:]
        return float(value.split(' ')[0])
    raise Exception('invalid value type')
