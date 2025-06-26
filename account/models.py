import hashlib
import uuid

from click import make_pass_decorator
from django.contrib.auth.models import AbstractUser
from django.db import models
from datetime import datetime
#timezone aware
from django.utils import timezone
import uuid
import os


# Create your models here.

def _get_avatar_upload_path(obj, filename):
    now = timezone.now()
    base_path = 'avatars/'

    new_filename = str(uuid.uuid5(uuid.NAMESPACE_URL,obj.pk))
    ext = os.path.splitext(filename)[1]
    p = os.path.join(base_path, now.strftime("%Y/%m"), f"{new_filename}{ext}")
    return p




class User(AbstractUser):
    email = models.EmailField("Email Address")
    phone = models.CharField("Phone Number", max_length=15)
    address = models.CharField("Address" , max_length=255,null=True,blank=True)
    # avatars/2025/4/image.jpg
    avatar = models.ImageField(upload_to="_get_avatar_upload_path",null=True,blank=True)


    def __str__(self):
        return self.username
