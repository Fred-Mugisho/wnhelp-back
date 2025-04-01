from .articles import *

class SectionArticle(models.Model):
    """Sections d'un article"""
    article = models.ForeignKey(Article, related_name='sections', on_delete=models.CASCADE)
    title = models.CharField(max_length=255, blank=True, null=True)
    contenu = RichTextField()  # 🔥 Champ texte riche avec CKEditor
    image = models.ImageField(upload_to='blog/sections/', blank=True, null=True)
    order = models.PositiveIntegerField()

    class Meta:
        verbose_name_plural = "SECTIONS ARTICLES"
        ordering = ['order']

    def __str__(self):
        return f"{self.article.title} - {self.title if self.title else 'Section'}"
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        
        if self.image:
            # Compression de l'image
            compressed_image = ImageCompressor(self.image, format='WEBP').compress()
            self.image.save(compressed_image.name, compressed_image, save=False)

            super().save(update_fields=['image'])
        
class SectionArticleSerializer(serializers.ModelSerializer):
    class Meta:
        model = SectionArticle
        fields = ['id', 'article', 'title', 'content', 'image', 'order']