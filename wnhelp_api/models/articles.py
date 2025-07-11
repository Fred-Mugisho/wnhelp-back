from .categories import *
from users_manager.models import *
from ckeditor.fields import RichTextField

class Article(models.Model):
    """Articles du blog"""
    
    STATUS_CHOICES = [
        ('draft', 'Brouillon'),
        ('published', 'Publié'),
        ('archived', 'Archivé'),
    ]
    
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=300, unique=True, blank=True)
    author = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)
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
        is_new = not self.pk
        
        super().save(*args, **kwargs)  # Sauvegarde initiale pour obtenir un fichier valide

        if is_new and self.status == 'published':
            self.send_notification_newsletter()
            
        # Compression de l'image
        compressed_image = ImageCompressor(self.cover_image, format='WEBP').compress_image()
        self.cover_image.save(compressed_image.name, compressed_image, save=False)

        super().save(update_fields=['cover_image'])
        
    def send_notification_newsletter(self):
        from wnhelp_api.models.subscribe_newsletters import SubscriberNewsletter
        
        if SubscriberNewsletter.objects.exists():
            subscribers = SubscriberNewsletter.objects.all()
            subject = "Nouvel article"
            message = f"""
                <p>Bonjour,</p>
                <p>Nous venons de publier un <strong>nouvel article</strong> sur notre site :</p>
                <p style="font-size: 18px;"><strong>{self.title}</strong></p>
                <p>Vous pouvez le consulter depuis le lien : <a href="https://rdc.wnhelp.org/actualites/{self.slug}" target="_blank" style="text-decoration: underline;">Lire l'article</a></p>
                <p style="margin-top: 32px;">Merci de faire partie de notre communauté,<br>
                L’équipe <strong>World Needs and Help</strong></p>
            """
            destinateurs = [sub.email for sub in subscribers]
            send_mail_template_async(
                subject=subject,
                message=message,
                destinateurs=['admin@wnhelp.org'],
                bcc=destinateurs
            )

    def __str__(self):
        return self.title
    
    @property
    def all_sections(self):
        from .sections_article import SectionArticle, SectionArticleSerializer
        sects = SectionArticle.objects.filter(article=self).order_by('order')
        serialized_data = SectionArticleSerializer(sects, many=True).data
        return serialized_data
    
    @property
    def all_comments(self):
        from .commentaires import Comment, CommentSerializer
        comments = Comment.objects.filter(article=self, approved=True).order_by('-created_at')
        serialized_data = CommentSerializer(comments, many=True).data
        return serialized_data
    
class ArticleSerializer(serializers.ModelSerializer):
    author = SimpleCustomUserSerializer()
    categorie = CategorieSerializer()
    class Meta:
        model = Article
        fields = ['id', 'title', 'slug', 'author', 'categorie', 'cover_image', 'contenu', 'status', 'views', 'created_at', 'updated_at']
        
class OthersArticleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = ['id', 'title', 'slug', 'cover_image', 'contenu', 'created_at', 'updated_at']
        
        
class DetailsArticleSerializer(serializers.ModelSerializer):
    author = SimpleCustomUserSerializer()
    categorie = CategorieSerializer()
    class Meta:
        model = Article
        fields = ['id', 'title', 'slug', 'author', 'categorie', 'cover_image', 'contenu', 'status', 'views', 'created_at', 'updated_at', 'all_comments']
        
class ArticleFormSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = ['id', 'title', 'categorie', 'cover_image', 'contenu', 'author']