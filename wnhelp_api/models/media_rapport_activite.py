from .rapports import Rapport
from django.db import models
from rest_framework import serializers
from django.core.exceptions import ValidationError
from utils.functions import ImageCompressor

class MediaRapportActivite(models.Model):
    TYPE_MEDIA_CHOICES = (
        ('image', 'Image'),
        ('video', 'Video'),
    )
    rapport = models.ForeignKey(Rapport, on_delete=models.CASCADE)
    order = models.PositiveIntegerField(default=1)
    type_media = models.CharField(max_length=10, choices=TYPE_MEDIA_CHOICES, default='image')
    image = models.ImageField(upload_to='rapports/', null=True, blank=True)
    link_video = models.URLField(null=True, blank=True)
    caption = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.image and not self.image.name.endswith('.webp'):
            # Compression de l'image si elle n'est pas en format WEBP
            compressed_image = ImageCompressor(self.image, format='WEBP').compress_image()
            self.image.save(compressed_image.name, compressed_image, save=False)

            super().save(update_fields=['image'])
    
    class Meta:
        verbose_name_plural = 'MEDIA RAPPORT ACTIVITE'
        ordering = ['order']
        unique_together = ('rapport', 'order')
    
    def __str__(self):
        return self.rapport.title
    
    def clean(self):
        errors = {}

        if self.type_media == 'image' and not self.image:
            errors['image'] = "Le champ 'image' est obligatoire pour le type 'image'."
        
        if self.type_media == 'video' and not self.link_video:
            errors['link_video'] = "Le champ 'link_video' est obligatoire pour le type 'video'."

        if self.order <= 0:
            errors['order'] = "L'ordre doit avoir une valeur superieur à 0."
        
        if errors:
            raise ValidationError(errors)

        super().clean()

class MediaRapportActiviteSerializer(serializers.ModelSerializer):
    class Meta:
        model = MediaRapportActivite
        fields = ['id', 'rapport', 'order', 'type_media', 'image', 'link_video', 'caption', 'created_at', 'updated_at']