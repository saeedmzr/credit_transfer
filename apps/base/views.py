from abc import ABC, abstractmethod
from typing import TypeVar, Type

from rest_framework.viewsets import GenericViewSet

from .pagination import StandardResultsSetPagination
from .services import BaseService

T = TypeVar('T', bound='BaseService')


class BaseViewSet(ABC, GenericViewSet):
    _service: BaseService = None
    pagination_class = StandardResultsSetPagination

    @classmethod
    def get_service(cls: Type[T]) -> T:
        return cls._service
