from .categories import *
from users_manager.models import *
from ckeditor.fields import RichTextField
from django.core.files.storage import default_storage

class Article(models.Model):
    """Articles du blog"""
    
    STATUS_CHOICES = [
        ('draft', 'Brouillon'),
        ('published', 'Publié'),
        ('archived', 'Archivé'),
    ]
    
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=300, unique=True, blank=True)
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    categorie = models.ForeignKey(Categorie, on_delete=models.SET_NULL, null=True, related_name='articles')
    cover_image = models.ImageField(upload_to='blog/covers/')
    contenu = RichTextField()  # 🔥 Champ texte riche avec CKEditor
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')
    views = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = "ARTICLES"
        
    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)

        super().save(*args, **kwargs)  # Sauvegarde initiale pour obtenir un fichier valide

        # Compression de l'image
        compressed_image = ImageCompressor(self.cover_image, format='WEBP').compress()
        self.cover_image.save(compressed_image.name, compressed_image, save=False)

        super().save(update_fields=['cover_image'])

    def __str__(self):
        return self.title
    
    @property
    def sections(self):
        from .sections_article import SectionArticle, SectionArticleSerializer
        sects = SectionArticle.objects.filter(article=self).order_by('order')
        serialized_data = SectionArticleSerializer(sects, many=True).data
        return serialized_data
    
    @property
    def comments(self):
        from .commentaires import Comment, CommentSerializer
        comments = Comment.objects.filter(article=self).order_by('-created_at')
        serialized_data = CommentSerializer(comments, many=True).data
        return serialized_data
    
class ArticleSerializer(serializers.ModelSerializer):
    author = SimpleCustomUserSerializer()
    categorie = CategorieSerializer()
    class Meta:
        model = Article
        fields = ['id', 'title', 'slug', 'author', 'categorie', 'cover_image', 'contenu', 'status', 'views', 'created_at', 'updated_at']
        
class DetailsArticleSerializer(serializers.ModelSerializer):
    author = SimpleCustomUserSerializer()
    categorie = CategorieSerializer()
    class Meta:
        model = Article
        fields = ['id', 'title', 'slug', 'author', 'categorie', 'cover_image', 'contenu', 'sections', 'status', 'views', 'created_at', 'updated_at', 'comments']
        
class ArticleFormSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = ['id', 'title', 'categorie', 'cover_image', 'contenu', 'author']