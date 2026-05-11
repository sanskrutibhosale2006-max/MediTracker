import datetime

LOW_STOCK_THRESHOLD = 20

def get_status(item):

    expiry_date_str = item["expiry"]

    stock = item["stock"]

    try:

        expiry_date = datetime.datetime.strptime(
            expiry_date_str,
            "%Y-%m-%d"
        ).date()

        today = datetime.date.today()

        time_to_expiry = expiry_date - today

        if time_to_expiry.days <= 0:
            return "🔴 EXPIRED"

        if stock <= 0:
            return "⚫ OUT OF STOCK"

        if stock <= LOW_STOCK_THRESHOLD:
            return "🟠 LOW STOCK"

        if time_to_expiry.days <= 90:
            return "🟡 Expiring Soon"

        return "🟢 OK"

    except ValueError:
        return "⚠ Invalid Date"