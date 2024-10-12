from django.db import models


class UserRoles(models.TextChoices):
    ADMIN = 'admin', 'Admin'
    CUSTOMER = 'customer', 'Customer'
