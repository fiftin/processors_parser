import re


def prepare_brand(value):
    return value.replace('™', '').replace('®', '')


def parse_page(rows, label_selector, value_selector, field_labels, field_types, url):
    fields = {}

    for field_row in rows:
        label = label_selector(field_row)
        field_name = field_labels.get(label, None)
        value = value_selector(field_row, field_name)

        if field_name is None:
            continue

        if value is None:
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


def extract_number(value):
    m = re.search(r'([\d.]+)', value)
    if m is None:
        return None
    return m[1]


def extract_number_with_tail(value):
    m = re.search(r'(\$?\d.*)$', value)
    if m is None:
        return None
    return m[1]


def parse_value(value, value_type):
    value = value.strip()
    if value_type == 'TEXT':
        return prepare_brand(value)
    if value_type == 'INT':
        num = extract_number_with_tail(value)
        b = parse_bytes(num)
        if b is not None:
            return b
        return int(extract_number(num))
    if value_type == 'REAL':
        return float(extract_number(value))
    if value_type == 'NUMERIC':
        return float(extract_number(value))
    raise Exception('invalid value type')
