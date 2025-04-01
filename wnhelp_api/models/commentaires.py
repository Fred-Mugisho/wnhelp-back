from .articles import *

class Comment(models.Model):
    """Commentaires des articles"""
    article = models.ForeignKey(Article, related_name='comments', on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    email = models.EmailField()
    content = models.TextField()
    approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Commentaire de {self.name} sur {self.article.title}"
    
    class Meta:
        verbose_name_plural = "COMMENTAIRES"
        
    def approve(self):
        self.approved = True
        self.save()
        
class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['id', 'article', 'name', 'email', 'content', 'approved', 'created_at']