from django.db import models
from rest_framework import serializers

class SubscriberNewsletter(models.Model):
    """Liste des abonnés à la newsletter"""
    email = models.EmailField(unique=True)
    subscribed_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = "SUBSCRIBERS NEWSLETTERS"

    def __str__(self):
        return self.email

class SubscriberNewsletterSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubscriberNewsletter
        fields = ['id', 'email', 'subscribed_at']