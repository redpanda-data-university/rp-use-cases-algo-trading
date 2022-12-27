from datetime import timedelta


def date_range(start_date, end_date, interval=1):
    date_from = start_date
    while date_from < end_date:
        date_to = date_from + timedelta(interval)
        yield date_from, date_to
        date_from = date_to
