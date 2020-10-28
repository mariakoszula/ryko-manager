import datetime
from rykomanager.name_strings import COMMON_DATE_PATTERN
import re

class DateConversionError(Exception):
    ERROR_MSG = "Failed to convert"

    def __init__(self, date_to_convert=None):
        self.date_to_convert = date_to_convert

    def __str__(self):
        if self.date_to_convert:
            return f"{DateConversionError.ERROR_MSG} date: {self.date} of type {self.type(self.date)}"
        else:
            return DateConversionError.ERROR_MSG


class DateConverter(object):
    @staticmethod
    def to_string(date, pattern=COMMON_DATE_PATTERN):
        return datetime.datetime.strftime(date, pattern)

    @staticmethod
    def to_date(date, pattern=COMMON_DATE_PATTERN):
        if isinstance(date, str):
            return datetime.datetime.strptime(date, pattern)
        elif isinstance(date, datetime.datetime):
            return date
        elif isinstance(date, datetime.date):
            return datetime.datetime.combine(date, datetime.datetime.min.time())
        else:
            raise DateConversionError(date)

    @staticmethod
    def two_digits(date_part):
        date_part_len = len(str(date_part))
        if date_part_len == 2:
            return "{}".format(date_part)
        elif date_part_len == 1:
            return "0{}".format(date_part)
        else:
            raise DateConversionError()

    @staticmethod
    def get_year():
        now = datetime.datetime.now()
        return now.year
