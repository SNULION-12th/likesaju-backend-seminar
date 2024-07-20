from django.db import models
# Create your models here.
class ProfilePic(models.Model):
    imagelink = models.CharField(max_length=256)
    def __str__(self):
        return self.imagelink
