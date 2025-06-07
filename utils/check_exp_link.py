from database.core import crud
from database.common.models import db, URL
import datetime


def check_row(short_code):
    cr = crud
    row = cr.retrieve_single()(db, URL, "short_code", short_code)
    is_active = row[0].is_active
    if is_active and datetime.datetime.now() > row[0].expired_at:
        cr.update_data()(db, URL, "is_active", False, "short_code", short_code)
        return False
    return is_active
