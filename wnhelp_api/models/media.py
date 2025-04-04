# models.py
from django.db import models
from django.conf import settings
from utils.functions import *
from rest_framework import serializers

class Gallerie(models.Model):
    """Groupe d'images pour la galerie"""
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    
    class Meta:
        verbose_name_plural = "GALERIES"

    def __str__(self):
        return self.title
    
class GallerieSerializer(serializers.ModelSerializer):
    class Meta:
        model = Gallerie
        fields = ['id', 'title', 'description', 'uploaded_at']

class GallerieImage(models.Model):
    """Images associées à une galerie"""
    galerie = models.ForeignKey(Gallerie, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to='gallery/')
    
    class Meta:
        verbose_name_plural = "IMAGES DE LA GALERIE"

    def __str__(self):
        return f"Image de {self.galerie.title}"
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)  # Sauvegarde initiale pour obtenir un fichier valide

        compressed_image = ImageCompressor(self.image, format='WEBP').compress()
        self.image.save(compressed_image.name, compressed_image, save=False)

        super().save(update_fields=['image'])
        
class GallerieImageSerializer(serializers.ModelSerializer):
    galerie = GallerieSerializer(read_only=True)
    class Meta:
        model = GallerieImage
        fields = ['id', 'galerie', 'image']