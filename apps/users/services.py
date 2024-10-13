from ..base.repositories import BaseRepository
from ..base.services import BaseService
from .repositories import UserRepository


class UserService(BaseService):
    _repository = UserRepository

    @classmethod
    def reset_password(cls, id, password):
        user = cls.get_by_pk(id)
        return cls._repository.change_password(user, password)
