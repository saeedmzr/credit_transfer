from abc import ABC
from typing import Type

from django.db.models import QuerySet

from .models import BaseModel
from .repositories import BaseRepository
from .exceptions import NotFoundError


class BaseService(ABC):
    _repository: BaseRepository = None

    @classmethod
    def get_repository(cls) -> BaseRepository:
        return cls._repository

    @classmethod
    def get_all(cls):
        return cls._repository.get_all()

    @classmethod
    def get_by_pk(cls, pk: int | str):
        return cls._repository.get_by_pk(pk=pk)

    @classmethod
    def get_and_lock_for_update(cls, id: int | str):
        return cls.get_repository().get_and_lock_for_update(id)

    @classmethod
    def pagination(cls, queryset: QuerySet, page_size=10, page=1):
        return cls.get_repository().get_by_pagination(queryset=queryset, page_size=page_size, page=page)

    @classmethod
    def create(cls, data: dict):
        return cls._repository.create(data)

    @classmethod
    def update(cls, id: int | str, data: dict):
        instance = cls.get_by_pk(id)
        return cls._repository.update(instance, data)

    @classmethod
    def delete(cls, id: int | str):
        instance = cls.get_by_pk(id)
        cls._repository.delete(instance)

    @classmethod
    def check_related_user_id(cls, id: int, user_id: int):
        cls._repository.check_related_user_id(id, user_id)

    @classmethod
    def get_owned(cls, user_id: int):
        return cls._repository.owned(user_id)
    @classmethod
    def get_list(cls, queryset: QuerySet = None, filters=None, sort=None):
        try:
            if queryset is None:
                queryset = cls._repository.get_queryset()
            # Apply sorting is entered
            if sort is not None:
                sort_op = cls._repository.sort(sort)
                queryset = queryset.order_by(sort_op)
            # Apply filters is entered
            if filters is not None:
                filters_op = cls._repository.filter(filters)
                queryset = queryset.filter(filters_op)
            return queryset
        except Exception as e:
            raise e
