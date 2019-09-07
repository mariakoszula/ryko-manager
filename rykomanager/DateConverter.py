import datetime


class DateConverter(object):
    @staticmethod
    def to_string(date, pattern=None):
        # @TODO check if given strig has this pattern
        pattern_used = '%Y-%m-%d' if not pattern else pattern
        return datetime.datetime.strftime(date, pattern_used)

    @staticmethod
    def to_date(date, pattern=None):
        if isinstance(date, str):
            pattern_used = '%Y-%m-%d' if not pattern else pattern
            return datetime.datetime.strptime(date, pattern_used)
        elif isinstance(date, datetime.datetime):
            return date
        else:
            print("LOG ERROR")

    @staticmethod
    def two_digits(date_part):
        date_part_len = len(str(date_part))
        if date_part_len == 2:
            return "{}".format(date_part)
        elif date_part_len == 1:
            return "0{}".format(date_part)
        else:
            return "FailedToConvertDate"