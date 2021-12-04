import re


def format_date(value):
    if value is None:
        return None

    quarter_to_month = {
        '1': '02',
        '2': '05',
        '3': '08',
        '4': '11',
    }

    m = re.search(r'Q(\d)\'(\d\d)', value)

    if m is not None:
        century = '19' if m[2][0] == '9' else '20'
        return century + m[2] + '-' + quarter_to_month[m[1]] + '-01'

    m = re.search(r'(\d?\d)/(\d?\d)/(\d\d\d\d)', value)

    if m is not None:
        return m[3] + '-' + m[1].zfill(2) + '-' + m[2].zfill(2)

    m = re.search(r'(\d?\d)/(\d\d\d\d)', value)

    if m is not None:
        return m[2] + '-' + m[1].zfill(2) + '-15'


def prepare_brand(value):
    return value.replace('™', '').replace('®', '')


def parse_page(rows, label_selector, value_selector, field_labels, field_types, url):
    fields = {}

    for field_row in rows:
        label = label_selector(field_row)
        if label is not None:
            label = label.strip()
        field_name = field_labels.get(label, None)

        if field_name is None:
            continue

        value = value_selector(field_row, field_name)

        if value is None:
            continue

        value = value.strip()

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


def parse_units(value, unit, multiplier=1000):
    if value is None or value == '':
        return None

    m = re.search(r'([\d.]+)\s*(' + unit + '|K' + unit + '|M' + unit + '|G' + unit + '|T' + unit + ')', value)
    if m is None:
        return None
    rank = 1
    if m[2] == 'K' + unit:
        rank = multiplier
    elif m[2] == 'M' + unit:
        rank = multiplier * multiplier
    elif m[2] == 'G' + unit:
        rank = multiplier * multiplier * multiplier
    elif m[2] == 'T' + unit:
        rank = multiplier * multiplier * multiplier * multiplier
    return round(float(m[1]) * rank)


def parse_hertz(value):
    res = parse_units(value, 'Hz')
    if res is not None:
        res = res / 1000_000
    return res


def parse_bytes(value):
    res = parse_units(value, 'B', 1024)
    if res is not None:
        res = res / 1024
    return res


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
        num2 = parse_bytes(num)
        if num2 is not None:
            return num2
        num2 = parse_hertz(num)
        if num2 is not None:
            return num2
        num3 = extract_number(num)
        if num3 is None:
            return None
        return int(num3)
    if value_type == 'NUMERIC':
        num = extract_number_with_tail(value)
        num2 = parse_bytes(num)
        if num2 is not None:
            return num2
        num2 = parse_hertz(num)
        if num2 is not None:
            return num2
        num3 = extract_number(value)
        if num3 is None:
            return None
        return float(num3)
    raise Exception('invalid value type')
