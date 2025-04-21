from decimal import Decimal


def clean_amount(value):
    if isinstance(value, str):
        value = abs(Decimal(value.replace(",", "")))
    else:
        value = abs(value)
    return value