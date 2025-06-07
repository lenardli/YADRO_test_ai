from typing import List, Dict, TypeVar

from database.common.models import db, ModelBase
from peewee import ModelSelect

T = TypeVar("T")


def _store_date(db: db, model: T, *data: List[Dict]) -> None:
    with db.atomic():
        result = model.insert_many(*data).execute()
    return result


def _update_data(db: db, model: T, upd_field, condition, query_field, query) \
        -> None:
    with db.atomic():
        update_field = {upd_field: condition}
        model.update(**update_field). \
            where(getattr(model, query_field) == query).execute()


def _retrieve_single_row(db: db, model: T, query_column: str, query,
                         operation: str = "eq") -> \
        ModelSelect:
    with db.atomic():
        if operation == "eq":
            response = model.select().where(
                getattr(model, query_column) == query)
        elif operation == "ge":
            response = model.select().where(
                getattr(model, query_column) >= query)
    return response


def _retrieve_all_data(db: db, model: T, *columns: ModelBase) -> ModelSelect:
    with db.atomic():
        response = model.select(*columns)
    return response


def _check_exists(db: db, model: T, query_column: str, query):
    with db.atomic():
        response = model.select().where(
            getattr(model, query_column) == query).exists()

    return response


class CRUDInterface:
    @classmethod
    def create(cls):
        return _store_date

    @classmethod
    def retrieve_all(cls):
        return _retrieve_all_data

    @classmethod
    def retrieve_single(cls):
        return _retrieve_single_row

    @classmethod
    def update_data(cls):
        return _update_data

    @classmethod
    def check_exists(cls):
        return _check_exists
