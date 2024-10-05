from abc import ABC
from typing import Type

from .models import BaseModel
from .repositories import BaseRepository
from .exceptions import NotFoundError


class BaseService(ABC):
    _repository: BaseRepository = None

    @classmethod
    def get_repository(cls) -> BaseRepository:
        return cls._repository

    @classmethod
    def set_filters(cls, params):
        cls._repository.set_filters(params)

    @classmethod
    def get_all(cls):
        return cls._repository.get_all()

    @classmethod
    def get_by_id(cls, id: int | str):
        return cls._repository.get_by_id(id)

    @classmethod
    def create(cls, data: dict):
        return cls._repository.create(data)

    @classmethod
    def update(cls, id: int | str, data: dict):
        instance = cls.get_by_id(id)
        return cls._repository.update(instance, data)

    @classmethod
    def delete(cls, id: int | str):
        instance = cls.get_by_id(id)
        cls._repository.delete(instance)

    @classmethod
    def check_related_user_id(cls, id: int, user_id: int):
        cls._repository.check_related_user_id(id, user_id)
