from enum import Enum

class UserRoleEnum(Enum):
    ADMIN = "admin"
    USER = "user"

    @classmethod
    def choices(cls):
        return [(role.value, role.name.title()) for role in cls]
