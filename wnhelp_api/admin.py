from django.contrib import admin
from .models.articles import *
from .models.categories import *
from .models.commentaires import *
from .models.contact_message import *
from .models.media import *
from .models.partenaires import *
from .models.rapports import *
from .models.sections_article import *
from .models.subscribe_newsletters import *
from django.utils.safestring import mark_safe
from django.utils.html import format_html
from adminsortable2.admin import SortableInlineAdminMixin, SortableAdminBase
from ckeditor.widgets import CKEditorWidget

@admin.register(SubscriberNewsletter)
class SubscriberNewsletterAdmin(admin.ModelAdmin):
    list_display = ('email', 'subscribed_at')
    list_filter = ('subscribed_at',)
    search_fields = ('email',)
    
@admin.register(Categorie)
class CategorieAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}
    ordering = ('name',)
    
class SectionArticleInline(admin.TabularInline):
    """Inline pour les sections d'un article (avec glisser-déposer)"""
    model = SectionArticle
    extra = 0

class CommentInline(admin.TabularInline):
    """Inline pour afficher les commentaires sous un article"""
    model = Comment
    extra = 0
    readonly_fields = ['name', 'email', 'content', 'created_at', 'approved']  # Les champs à afficher en lecture seule
    can_delete = False  # Empêche la suppression des commentaires
    can_add = False  # Empêche l'ajout de nouveaux commentaires
    show_change_link = False  # Empêche le lien de modification du commentaire

@admin.register(Article)
class ArticleAdmin(SortableAdminBase, admin.ModelAdmin):
    list_display = ('title', 'author', 'categorie', 'status', 'views', 'created_at', 'cover_preview')
    list_filter = ('status', 'created_at', 'categorie')
    search_fields = ('title', 'author__username', 'categorie__name')
    prepopulated_fields = {'slug': ('title',)}
    ordering = ('-created_at',)
    date_hierarchy = 'created_at'
    list_editable = ('status',)
    readonly_fields = ('views', 'created_at', 'updated_at', 'cover_preview', 'author')
    formfield_overrides = {
        models.TextField: {'widget': CKEditorWidget()},  # Ajoute CKEditor au champ contenu
    }
    actions = ['publish_articles', 'unpublish_articles']
    inlines = [SectionArticleInline, CommentInline]
    
    def save_model(self, request, obj, form, change):
        # Si l'auteur n'est pas déjà défini (par exemple, lors de la création d'un article)
        if not obj.author:
            obj.author = request.user  # Définit l'auteur comme l'utilisateur connecté
        super().save_model(request, obj, form, change)

    def cover_preview(self, obj):
        """Affiche un aperçu de l'image de couverture dans l'admin"""
        if obj.cover_image:
            return mark_safe(f'<img src="{obj.cover_image.url}" width="50" height="50" style="border-radius:5px;" />')
        return "-"
    cover_preview.short_description = "Image"

    def publish_articles(self, request, queryset):
        queryset.update(status='published')
        self.message_user(request, "Les articles sélectionnés ont été publiés.")
    publish_articles.short_description = "Publier les articles sélectionnés"

    def unpublish_articles(self, request, queryset):
        queryset.update(status='draft')
        self.message_user(request, "Les articles sélectionnés ont été mis en brouillon.")
    unpublish_articles.short_description = "Mettre en brouillon les articles sélectionnés"
    
@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('name', 'article', 'approved', 'created_at')
    list_filter = ('approved', 'created_at', 'article')
    search_fields = ('name', 'email', 'content', 'article__title')
    ordering = ('-created_at',)
    actions = ['approve_comments', 'unapprove_comments']
    # readonly_fields = ['name', 'email', 'content', 'created_at']
    
    def has_delete_permission(self, request, obj=None):
        return False

    def approve_comments(self, request, queryset):
        """Action pour approuver plusieurs commentaires"""
        queryset.update(approved=True)
        self.message_user(request, "Les commentaires sélectionnés ont été approuvés.")
    approve_comments.short_description = "Approuver les commentaires sélectionnés"

    def unapprove_comments(self, request, queryset):
        """Action pour désapprouver plusieurs commentaires"""
        queryset.update(approved=False)
        self.message_user(request, "Les commentaires sélectionnés ont été désapprouvés.")
    unapprove_comments.short_description = "Désapprouver les commentaires sélectionnés"

@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'subject', 'sent_at', 'short_message')
    list_filter = ('sent_at',)
    search_fields = ('name', 'email', 'subject', 'message')
    ordering = ('-sent_at',)

    def short_message(self, obj):
        """Affiche un aperçu du message dans l’admin"""
        return obj.message[:50] + "..." if len(obj.message) > 50 else obj.message
    short_message.short_description = "Message"
    
@admin.register(Media)
class MediaAdmin(admin.ModelAdmin):
    list_display = ('title', 'media_type', 'uploaded_at', 'author', 'preview')
    list_filter = ('media_type', 'uploaded_at')
    search_fields = ('title', 'description', 'author__username')
    ordering = ('-uploaded_at',)
    readonly_fields = ['preview', 'author']
    
    def save_model(self, request, obj, form, change):
        # Si l'auteur n'est pas déjà défini (par exemple, lors de la création d'un article)
        if not obj.author:
            obj.author = request.user  # Définit l'auteur comme l'utilisateur connecté
        super().save_model(request, obj, form, change)
    
    def preview(self, obj):
        """Affiche un aperçu des images dans l’admin"""
        if obj.media_type == 'image' and obj.file:
            return format_html(f'<img src="{obj.file.url}" width="50" height="50" style="border-radius: 5px;" />')
        return "Aperçu non disponible"
    preview.short_description = "Aperçu"
    
@admin.register(Partenaires)
class PartenairesAdmin(admin.ModelAdmin):
    list_display = ('name', 'website', 'joined_at', 'logo_preview')
    list_filter = ('joined_at',)
    search_fields = ('name', 'description', 'website')
    ordering = ('-joined_at',)

    def logo_preview(self, obj):
        """Affiche un aperçu du logo dans l’admin"""
        if obj.logo:
            return format_html(f'<img src="{obj.logo.url}" width="50" height="50" style="border-radius: 5px;" />')
        return "Pas de logo"
    logo_preview.short_description = "Logo"
    
@admin.register(Rapport)
class RapportAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'published_at', 'updated_at', 'cover_preview', 'download_link')
    list_filter = ('published_at', 'updated_at', 'author')
    search_fields = ('title', 'contenu', 'author__username')
    ordering = ('-published_at',)
    readonly_fields = ['cover_preview', 'download_link', 'author']
    formfield_overrides = {
        models.TextField: {'widget': CKEditorWidget()},  # Ajoute CKEditor au champ contenu
    }
    
    def save_model(self, request, obj, form, change):
        # Si l'auteur n'est pas déjà défini (par exemple, lors de la création d'un article)
        if not obj.author:
            obj.author = request.user  # Définit l'auteur comme l'utilisateur connecté
        super().save_model(request, obj, form, change)

    def cover_preview(self, obj):
        """Affiche un aperçu de l'image de couverture dans l’admin"""
        if obj.cover_image:
            return format_html(f'<img src="{obj.cover_image.url}" width="50" height="50" style="border-radius: 5px;" />')
        return "Pas d'image"
    cover_preview.short_description = "Couverture"

    def download_link(self, obj):
        """Ajoute un lien de téléchargement du rapport"""
        if obj.file:
            return format_html(f'<a href="{obj.file.url}" target="_blank">Télécharger</a>')
        return "Aucun fichier"
    download_link.short_description = "Fichier"
    
@admin.register(SectionArticle)
class SectionArticleAdmin(admin.ModelAdmin):
    list_display = ('article', 'title', 'order', 'image_preview')
    list_filter = ('article',)
    search_fields = ('title', 'article__title')
    ordering = ('article', 'order')
    formfield_overrides = {
        models.TextField: {'widget': CKEditorWidget()},  # Ajoute CKEditor au champ contenu
    }

    def image_preview(self, obj):
        """Affiche un aperçu de l'image associée à la section"""
        if obj.image:
            return format_html(f'<img src="{obj.image.url}" width="50" height="50" style="border-radius: 5px;" />')
        return "Pas d'image"
    image_preview.short_description = "Aperçu"