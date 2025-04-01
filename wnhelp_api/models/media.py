from users_manager.models import *

class Media(models.Model):
    """Images et vidéos pour la galerie"""
    MEDIA_TYPES = (
        ('image', 'Image'),
        ('video', 'Vidéo'),
    )
    title = models.CharField(max_length=255)
    file = models.FileField(upload_to='gallery/')
    media_type = models.CharField(max_length=10, choices=MEDIA_TYPES)
    description = models.TextField(blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)
    
    class Meta:
        verbose_name_plural = "MEDIAS"

    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        if self.media_type == 'image':
            compressed_image = ImageCompressor(self.file, format='WEBP').compress()
            self.file.save(compressed_image.name, compressed_image, save=False)

            super().save(update_fields=['file'])
            
class MediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Media
        fields = ['id', 'title', 'file', 'media_type', 'description', 'uploaded_at', 'author']
