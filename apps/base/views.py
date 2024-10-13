from abc import ABC, abstractmethod

from rest_framework.viewsets import GenericViewSet

from .services import BaseService


class BaseViewSet(ABC, GenericViewSet):
    _service: BaseService = None

    @classmethod
    def get_service(cls) -> BaseService:
        return cls._service

    
