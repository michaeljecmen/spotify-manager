import datetime

DATE_FORMAT = "%Y-%m-%d"

# returns current date as a formatted string
def get_date():
    return datetime.datetime.today().strftime(DATE_FORMAT)

def is_ts_before_yesterday(timestamp):
    today = datetime.datetime.today()
    yesterday = today - datetime.timedelta(days=1)
    date = datetime.datetime.fromtimestamp(timestamp)
    return date < yesterday
