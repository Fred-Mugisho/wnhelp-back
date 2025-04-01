from users_manager.models import *
from django.utils.text import slugify
from ckeditor.fields import RichTextField

class Rapport(models.Model):
    """Rapports publiés par l'organisation"""
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=300, unique=True, blank=True)
    contenu = RichTextField()  # 🔥 Champ texte riche avec CKEditor
    file = models.FileField(upload_to='reports/')
    cover_image = models.ImageField(upload_to='reports/covers/', blank=True, null=True)
    published_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    author = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)
    
    class Meta:
        verbose_name_plural = "RAPPORTS"
    
    def save(self, *args, **kwargs):
        is_new = not self.pk
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
        
        if self.cover_image:
            compressed_image = ImageCompressor(self.cover_image, format='WEBP').compress()
            self.cover_image.save(compressed_image.name, compressed_image, save=False)

            super().save(update_fields=['cover_image'])

    def __str__(self):
        return self.title
    
class RapportSerializer(serializers.ModelSerializer):
    author = SimpleCustomUserSerializer()
    class Meta:
        model = Rapport
        fields = ['id', 'title', 'slug', 'contenu', 'cover_image', 'file', 'published_at', 'updated_at', 'author']
        
class RapportFormSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rapport
        fields = ['id', 'title', 'slug', 'contenu', 'cover_image', 'file', 'author']
