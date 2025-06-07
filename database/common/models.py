import os
from datetime import datetime, timedelta

import peewee as pw
from dotenv import load_dotenv

load_dotenv()
exp_age = int(os.getenv("EXPIRY_PERIOD"))

db = pw.SqliteDatabase("yadro_test.db")


class ModelBase(pw.Model):
    datetime_now = datetime.now()
    created_at = pw.DateTimeField(default=datetime_now)

    class Meta():
        database = db


class User(ModelBase):
    db_table = "users"
    id = pw.BigIntegerField(primary_key=True, index=True)
    username = pw.TextField(unique=True, index=True)
    hashed_password = pw.TextField(index=True)


class URL(ModelBase):
    db_table = "urls"
    id = pw.BigIntegerField(primary_key=True, index=True)
    original_url = pw.TextField(index=True)
    short_code = pw.TextField(unique=True, index=True)
    is_active = pw.BooleanField(default=True)
    expired_at = pw.DateTimeField(null=True, default=ModelBase.datetime_now +
                                                     timedelta(days=exp_age))


class Visit(ModelBase):
    __tablename__ = "visits"
    id = pw.BigIntegerField(primary_key=True, index=True)
    original_url = pw.TextField(index=True)
    short_url = pw.TextField(index=True)
