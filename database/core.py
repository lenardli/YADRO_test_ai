from database.utils.CRUD import CRUDInterface
from database.common.models import db, User, URL, Visit


def create_tables():
    db.connect()
    db.create_tables([User, URL, Visit], safe=True)


def close_db():
    if not db.is_closed():
        db.close()


crud = CRUDInterface()
