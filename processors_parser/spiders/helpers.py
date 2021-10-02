import re


def parse_page(rows, label_selector, value_selector, field_labels, field_types, url):
    fields = {}

    for field_row in rows:
        label = field_row.css(label_selector).get()
        value = field_row.css(value_selector).get()
        field_name = field_labels.get(label, None)
        if field_name is None:
            continue
        try:
            fields[field_name] = parse_value(value, field_types[field_name])
        except BaseException:
            print('Error on page ' + url +
                  ' during parsing field ' + field_name +
                  ' with value ' + value)
            raise

    if len(fields) == 0:
        return None

    fields['url'] = url

    return fields


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
