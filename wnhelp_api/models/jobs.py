from django.db import models
from django.utils import timezone
from rest_framework import serializers
from users_manager.models import *

class JobOffer(models.Model):
    TYPE_CONTRAT = [
        ('CDI', 'Contrat à Durée Indéterminée'),
        ('CDD', 'Contrat à Durée Déterminée'),
        ('STAGE', 'Stage'),
        ('INTERIM', 'Intérim'),
    ]

    titre = models.CharField(max_length=255)
    description = models.TextField()
    profil_recherche = models.TextField()
    type_contrat = models.CharField(max_length=20, choices=TYPE_CONTRAT)
    lieu = models.CharField(max_length=255)
    date_publication = models.DateField(default=timezone.now)
    date_expiration = models.DateField(null=True, blank=True)
    actif = models.BooleanField(default=True)
    lien_postulation = models.URLField("Lien vers le formulaire de candidature", blank=True, null=True)
    author = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)
    counter_views = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.titre

    class Meta:
        verbose_name_plural = "OFFRES D'EMPLOI"
        ordering = ['-date_publication']
        
class JobOfferSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobOffer
        fields = ['id', 'titre', 'description', 'profil_recherche', 'type_contrat', 'lieu', 'date_publication', 'date_expiration', 'actif', 'lien_postulation', 'author', 'counter_views']
