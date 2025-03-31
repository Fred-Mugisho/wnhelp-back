from django.db import models
from ..models import *

class RoleUser(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    role = models.CharField(max_length=100, choices=ROLES_CHOICES)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = "ROLES UTILISATEURS"
        verbose_name = "Role utilisateur"

    def __str__(self):
        return self.role

class RoleUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = RoleUser
        fields = ['id', 'role', 'is_active', 'created_at', 'updated_at']
        
class RoleUserSerializerCreate(serializers.ModelSerializer):
    class Meta:
        model = RoleUser
        fields = ['id', 'user', 'role', 'is_active']