from django.db import models
from django.utils import timezone


class Landlord(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True,blank=True,null=True)
    phone = models.CharField(max_length=15)
    address = models.TextField(blank=True,null=True)
    remark= models.TextField(blank=True,null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    def __str__(self):
        return self.name

    @property
    def billboard_count(self):
        return self.billboards.count()  # Related name from Billboard model

class Billboard(models.Model):
    landlord=models.ForeignKey(Landlord,on_delete=models.CASCADE,related_name="billboards", default=1)
    hid = models.CharField(max_length=50, unique=True)  # HID (Assumed as an identifier)
    district = models.CharField(max_length=100,blank=True,null=True)
    city = models.CharField(max_length=100,blank=True,null=True)
    area = models.CharField(max_length=100,blank=True,null=True)
    location = models.TextField(blank=True,null=True)
    width = models.DecimalField(max_digits=5, decimal_places=2)
    height = models.DecimalField(max_digits=5, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.city} - {self.location}"


