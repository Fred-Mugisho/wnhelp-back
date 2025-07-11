from django.db import models
from rest_framework import serializers
from utils.functions import ImageCompressor

class Partenaires(models.Model):
    """Liste des partenaires de l'organisation"""
    name = models.CharField(max_length=255)
    logo = models.ImageField(upload_to='partners/')
    website = models.URLField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    joined_at = models.DateField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = "PARTENAIRES"

    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        compressed_image = ImageCompressor(self.logo, format='WEBP').compress_image()
        self.logo.save(compressed_image.name, compressed_image, save=False)

        super().save(update_fields=['logo'])
            
class PartenairesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Partenaires
        fields = ['id', 'name', 'logo', 'website', 'description', 'joined_at']
    