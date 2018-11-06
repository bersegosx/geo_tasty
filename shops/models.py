from django.contrib.auth.models import AbstractUser
from django.contrib.gis.db import models


class User(AbstractUser):
    point = models.PointField(null=True, spatial_index=True, geography=True)


class Shop(models.Model):

    title = models.CharField('Title', max_length=255)
    image = models.ImageField('Image', null=True)
    point = models.PointField(null=True, spatial_index=True, geography=True)

    def __str__(self):
        return self.title
