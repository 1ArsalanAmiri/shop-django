from django.db import models
from uuid import uuid4

from telegram import Invoice

# from django.contrib.auth.models import User
from account.models import User
from django.contrib.auth import get_user_model

# Create your models here.

User = get_user_model()

class Base(models.Model):
    uuid          = models.UUIDField      (unique=True,default=uuid4)
    create_date   = models.DateTimeField  (auto_now_add=True) # auto_now_add  یعنی به محض سیو اولیه ست میشه 
    modified_date = models.DateTimeField  (auto_now=True) 
    delete_date   = models.DateTimeField  (default=None, null=True , blank=True)
    deleted       = models.BooleanField   (default=False)
    user          = models.ForeignKey     (User ,default = 1 ,on_delete=models.PROTECT)

    class Meta:
        abstract = True


class Product(Base):
    
    #Static Attribute
    # STATUS_ENABLED  =  'enabled'
    # STATUS_DISABLED =  'disabled'
    # STATUS_DELETED  =  'deleted' 
    
    # STATUS_CHOICES = (
    #     (STATUS_ENABLED ,'Enabled' ),
    #     (STATUS_DISABLED,'Disabled'),
    #     (STATUS_DELETED ,'Deleted' )

    name          = models.CharField      (max_length=255)
    slug          = models.SlugField      (unique=True)
    price         = models.IntegerField   (default=0)
    discount      = models.FloatField     (default=0)
    enabled       = models.BooleanField   (default=True)
    description   = models.TextField      ()
    category      = models.ForeignKey     ("Category", related_name="products" , on_delete=models.PROTECT)
    image         = models.ImageField     (upload_to="covers/" ,null=True , blank=True)
    button        = models.BooleanField   (default=False)
    count         = models.IntegerField   (default=0)
    # old_category  = models.ForeignKey     ("Category", related_name="old_products" , on_delete=models.PROTECT)

    def __str__(self):
        return f"{self.name}"


class Tag(Base):
    name          = models.CharField      (max_length=255)
    def __str__(self):
        return f"{self.name}"


class Comment(Base):
    name          = models.CharField      (max_length=255)
    def __str__(self):
        return f"{self.name}"

class Like(Base):
    pass
    def __str__(self):
        return f"{self.name}"


class Category(Base):
    name          = models.CharField      (max_length=255)
    parent        = models.ForeignKey     ('Category',null=True ,default=None, blank=True, on_delete=models.PROTECT, related_name='childs')

    def __str__(self):
        return f"{self.name}"




class InvoiceItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    invoice = models.ForeignKey('Invoice', on_delete=models.CASCADE)
    count = models.IntegerField ()
    price = models.IntegerField ()
    discount = models.FloatField ()
    name = models.CharField (max_length=255)
    total = models.IntegerField ()


class Invoice(models.Model):
    date = models.DateTimeField(auto_now_add=True)
    number = models.IntegerField(null = True , blank=True)
    user = models.ForeignKey(User,on_delete=models.PROTECT)
    total = models.IntegerField()
    discount = models.IntegerField(default = 0)
    description = models.TextField(null = True , blank=True)
    address = models.CharField(max_length=255)
    vat = models.FloatField(default = 0.09)

    def __str__(self):
        return f"{self.number}"



class Payment(models.Model):
    STATUS_PENDING = 'Pending'
    STATUS_DONE = 'Done'
    STATUS_ERROR = 'Error'
    STATUS_CHOICES = ((STATUS_PENDING, 'Pending'),
                      (STATUS_DONE, 'Done'),
                      (STATUS_ERROR, 'Error'))


    invoice = models.OneToOneField(Invoice , on_delete=models.PROTECT)
    total = models.IntegerField()
    ref = models.CharField (max_length=255 , null=True , blank=True)
    status = models.CharField (choices = STATUS_CHOICES , max_length=20, default = STATUS_PENDING)

    authority = models.CharField(max_length=255)
    description = models.TextField()
    user_ip = models.CharField(max_length=255)
