from abc import ABC
from typing import Type

from django.db.models import QuerySet, Q

from .models import BaseModel
from .serializers import BaseModelSerializer
from .exceptions import NotFoundError, PermissionDeniedError, FilterIsInvalid


class BaseRepository(ABC):
    _model: Type[BaseModel] = None
    _serializer: Type[BaseModelSerializer] = None

    @classmethod
    def _get_model(cls) -> Type[BaseModel]:
        return cls._model

    @classmethod
    def _get_serializer(cls) -> Type[BaseModelSerializer]:
        return cls._serializer

    @classmethod
    def get_queryset(cls) -> QuerySet:
        return cls._model.objects.get_queryset()

    @classmethod
    def filter(cls, filters: dict):
        q_object = Q()

        for filter_item in filters:
            key = filter_item['key']
            value = filter_item['value']
            op = filter_item['op']

            try:
                q_object &= Q(**{f"{key}__{op}": value})
            except ValueError:
                raise FilterIsInvalid()
        return q_object

    @classmethod
    def sort(cls, sort: dict):
        key = {}
        for sort_item in sort:
            key = sort_item['key']
            order = sort_item['type']

            if order == 'desc':
                key = f"-{key}"

        return key

    @classmethod
    def get_all(cls):
        return cls._model.objects.get_queryset().all()

    @classmethod
    def get_by_pk(cls, pk: int | str):
        instance = cls._model.objects.filter(pk=pk).first()
        if instance is None:
            raise NotFoundError()
        return instance

    @classmethod
    def create(cls, data: dict):
        serializer = cls._serializer(data=data)
        serializer.is_valid(raise_exception=True)
        return serializer.save()

    @classmethod
    def update(cls, instance: BaseModel, data: dict):
        serializer = cls._serializer(instance=instance, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        return serializer.save()

    @classmethod
    def delete(cls, instance: BaseModel):
        instance.delete()

    @classmethod
    def check_related_user_id(cls, id: int, user_id: int):
        instance = cls.get_by_id(id)
        if instance.user_id != user_id:
            raise PermissionDeniedError()
