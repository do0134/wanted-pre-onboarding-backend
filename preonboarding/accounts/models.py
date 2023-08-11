from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser, PermissionsMixin
)

# Create your models here.
class User(AbstractBaseUser, PermissionsMixin):
    email = models.CharField(
        verbose_name=('Email address'),
        max_length=255,
        unique=True,
    )

    USERNAME_FIELD = 'email'

    