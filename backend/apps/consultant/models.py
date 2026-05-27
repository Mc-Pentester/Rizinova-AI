from django.db import models
from django.contrib.auth.models import User

class FarmProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    surface_ha = models.FloatField(null=True, blank=True)
    region = models.CharField(max_length=100, null=True, blank=True)
    irrigation_type = models.CharField(max_length=50, null=True, blank=True)
    typical_yield = models.FloatField(null=True, blank=True)

class ConsultantSession(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    session_id = models.CharField(max_length=100)
    role = models.CharField(max_length=20)  # user / assistant
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
