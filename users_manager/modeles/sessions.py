from ..models import *
from datetime import timedelta

class UserSession(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    session_key = models.CharField(max_length=255, unique=True)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    
    class Meta:
        verbose_name_plural = "SESSIONS UTILISATEURS"
        verbose_name = "Session"
    
    def __str__(self):
        return f"Session {self.session_key[:10]}... - Expire le {self.expires_at}"
    
    def get_user_email(self):
        return self.user.email
    
    def get_user_name(self):
        return self.user.nom_complet
    
    @property
    def _session_key(self):
        return f"{self.session_key[:10]}...{self.session_key[60:]}"

    @property
    def is_expired(self):
        """Vérifie si la session est expirée."""
        return now() > self.expires_at
    
    def set_session_key(self):
        max_attempts = 5
        for _ in range(max_attempts):
            session_key = generate_session_key()
            if not UserSession.objects.filter(session_key=session_key).exists():
                self.session_key = session_key
                return
        raise ValueError("Impossible de générer une clé de session unique.")

    def save(self, *args, **kwargs):
        """Définit l'expiration automatique (ex: 1 jour)."""
        if not self.expires_at:
            self.expires_at = now() + timedelta(days=1)  # Expire après 1 jour
            
        if self.user and not self.pk:
            message = f"Nouvelle connexion détectée depuis {self.ip_address} ({self.user_agent})"
            self.user.send_notification(message)
        super().save(*args, **kwargs)
        
    def close_session(self):
        self.expires_at = now()
        self.save()
    
class UserSessionSerializer(serializers.ModelSerializer):
    user = SimpleCustomUserSerializer()
    ip_address = serializers.CharField()
    class Meta:
        model = UserSession
        fields = ['id', 'user', 'ip_address', 'user_agent', 'created_at', 'expires_at', 'is_expired']
        
class MyUserSessionSerializer(serializers.ModelSerializer):
    ip_address = serializers.CharField()
    class Meta:
        model = UserSession
        fields = ['id', 'ip_address', 'user_agent', 'created_at', 'expires_at', 'is_expired']