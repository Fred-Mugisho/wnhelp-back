from django.db import models
from rest_framework import serializers

class ContactMessage(models.Model):
    """Messages envoyés via la page de contact"""
    name = models.CharField(max_length=255)
    email = models.EmailField()
    subject = models.CharField(max_length=255)
    message = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message de {self.name} - {self.subject}"

    class Meta:
        verbose_name_plural = "CONTACT MESSAGES"
        

class ContactMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactMessage
        fields = ['id', 'name', 'email', 'subject', 'message', 'sent_at', 'responded']