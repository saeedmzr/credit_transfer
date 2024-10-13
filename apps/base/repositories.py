from abc import ABC
from typing import Type

from django.db.models import QuerySet, Q

from .models import BaseModel
from .serializers import BaseModelSerializer
from .exceptions import NotFoundError, PermissionDeniedError, FilterIsInValid


class BaseRepository(ABC):
    _model: Type[BaseModel] = None

    @classmethod
    def _get_model(cls) -> Type[BaseModel]:
        return cls._model

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
                raise FilterIsInValid()
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
    def get_by_pagination(cls, queryset: QuerySet, page_size: int = 10, page: int = 1) -> (QuerySet, dict):
        count = queryset.count()
        total_page = (count + page_size - 1) // page_size
        return queryset[(page - 1) * page_size:page * page_size], {
            'page': page,
            'count': count,
            'total_page': total_page
        }

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
        obj = cls._get_model().objects.create(**data)
        return obj

    @classmethod
    def update(cls, pk: int | str, data: dict):
        obj = cls.get_by_pk(pk)
        obj.update(data)
        return obj

    @classmethod
    def delete(cls, instance: BaseModel):
        instance.delete()

    @classmethod
    def check_related_user_id(cls, id: int | str, user_id: int):
        instance = cls.get_by_pk(id)
        if instance.user_id != user_id:
            raise PermissionDeniedError()
