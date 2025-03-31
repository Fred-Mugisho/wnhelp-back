from django.db import models
from rest_framework import serializers
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils.timezone import now
from utils.choices import *
from utils.functions import *
from decimal import Decimal

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("L'email est obligatoire")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None):
        return self.create_user(email, password, is_staff=True, is_superuser=True)

class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True, error_messages={"unique": "Un utilisateur avec cette adresse email existe déjà."})
    nom_complet = models.CharField(max_length=255)
    telephone = models.CharField(max_length=20, unique=True, error_messages={"unique": "Un utilisateur avec ce numéro de téléphone existe déjà."}, blank=True, null=True)
    photo_profil = models.ImageField(blank=True, null=True, upload_to='photos_profil/')
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    otp_secret = models.CharField(max_length=16, unique=True, editable=False, null=True, blank=True)  # 2FA
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)
    last_login = models.DateTimeField(blank=True, null=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = CustomUserManager()
    
    class Meta:
        verbose_name_plural = "UTILISATEURS"
        verbose_name = "Utilisateur"

    def __str__(self):
        return self.email
    
    def send_notification(self, message):
        from .modeles.notification import Notification
        Notification.objects.create(user=self, message=message)
            
    def set_otp_secret(self):
        max_attempts = 5
        for _ in range(max_attempts):
            otp_secret = generate_otp()
            if not CustomUser.objects.filter(otp_secret=otp_secret).exists():
                self.otp_secret = otp_secret
                return
        raise ValueError("Impossible de générer un OTP unique.")
    
    @property
    def all_notifications(self):
        from .modeles.notification import Notification
        return Notification.objects.filter(user=self).order_by('-id')
    
    @property
    def unread_notifications_count(self):
        return self.all_notifications.filter(is_read=False).count()
    
    @property
    def notifications(self):
        from .modeles.notification import MyNotifiacationSerializer
        notifications_read = self.all_notifications.filter(is_read=True)
        notifications_unread = self.all_notifications.filter(is_read=False)
        return {
            "unread": MyNotifiacationSerializer(notifications_unread, many=True).data,
            "read": MyNotifiacationSerializer(notifications_read, many=True).data,
        }
        
    @property
    def all_sessions(self):
        from .modeles.sessions import UserSession
        sessions = UserSession.objects.filter(user=self).order_by('-id')
        return sessions
    
    @property
    def history_sessions(self):
        from .modeles.sessions import MyUserSessionSerializer
        serialized_data = MyUserSessionSerializer(self.all_sessions, many=True).data
        return serialized_data
        
    @property
    def sessions_active(self):
        from .modeles.sessions import MyUserSessionSerializer
        sessions = self.all_sessions.filter(expires_at__gt=now()).order_by('-id')
        serialized_data = MyUserSessionSerializer(sessions, many=True).data
        return serialized_data
    
    def close_all_session(self):
        from .modeles.sessions import UserSession
        sessions = UserSession.objects.filter(user=self)
        for session in sessions:
            session.close_session()
            
    @property
    def all_roles(self):
        from .modeles.role_user import RoleUser
        return RoleUser.objects.filter(user=self)
    
    @property
    def roles(self):
        from .modeles.role_user import RoleUserSerializer
        roles_active = self.all_roles.filter(is_active=True)
        roles_inactive = self.all_roles.filter(is_active=False)
        response = {
            "active": RoleUserSerializer(roles_active, many=True).data,
            "inactive": RoleUserSerializer(roles_inactive, many=True).data
        }
        return response
            
class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'email', 'nom_complet', 'telephone', 'photo_profil', 'is_active', 'unread_notifications_count', 'create_at', 'update_at', 'last_login']
        
class SimpleCustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'email', 'nom_complet', 'telephone', 'photo_profil', 'is_active']
        
class CustomUserSerializerCreate(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'email', 'nom_complet', 'telephone', 'photo_profil']