from django.db import models
from django.contrib.auth.models import User
from ProfilePic.models import ProfilePic
# Create your models here.
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profilepic_id = models.ForeignKey(ProfilePic, on_delete=models.CASCADE, blank=True, null=True)
    nickname = models.CharField(max_length=256, blank=True, null=True)
    remaining_points = models.IntegerField(default=0)
    is_social_login = models.BooleanField(default=False)

    
