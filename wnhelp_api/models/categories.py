from django.db import models
from django.utils.text import slugify
from rest_framework import serializers

class Categorie(models.Model):
    """Catégories des articles"""
    name = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(max_length=300, unique=True)
    
    class Meta:
        verbose_name_plural = "CATEGORIES"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
    
class CategorieSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categorie
        fields = ['id', 'name', 'slug']
        
class CategorieFormSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categorie
        fields = ['id', 'name']