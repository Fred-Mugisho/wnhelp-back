from django.contrib import admin
from django.contrib.auth.models import Group
from .modeles.sessions import *
from .modeles.notification import *
from .modeles.role_user import *
from django.utils.safestring import mark_safe
from django.contrib.admin.models import LogEntry
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import gettext_lazy as _
from django.contrib import messages

admin.site.unregister(Group)

admin.site.site_header = "ADMINISTRATION SITE WEBSITE WNHELP"
admin.site.site_title = "WNHelp Admin"
admin.site.index_title = "Bienvenue sur l'administration du site WNHelp"

class CustomAdmin(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        """Enregistre une action lorsqu'un objet est ajouté ou modifié"""
        action_flag = 1 if not change else 2  # 1 = ajout, 2 = modification
        obj.save()
        
        LogEntry.objects.log_action(
            user_id=request.user.id,
            content_type_id=ContentType.objects.get_for_model(obj).id,
            object_id=obj.id,
            object_repr=str(obj),
            action_flag=action_flag,
            change_message="Ajouté" if not change else "Modifié"
        )

    def delete_model(self, request, obj):
        """Enregistre une action lorsqu'un objet est supprimé"""
        LogEntry.objects.log_action(
            user_id=request.user.id,
            content_type_id=ContentType.objects.get_for_model(obj).id,
            object_id=obj.id,
            object_repr=str(obj),
            action_flag=3,  # Suppression
            change_message="Supprimé"
        )
        obj.delete()

@admin.register(LogEntry)
class LogEntryAdmin(admin.ModelAdmin):
    list_display = ('user', 'content_type', 'object_repr', 'action_flag', 'action_time')
    list_filter = ('action_flag', 'user')
    search_fields = ('object_repr', 'change_message')

@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('email', 'nom_complet', 'telephone', 'is_active', 'is_staff', 'last_login')
    list_filter = ('is_staff', 'is_active')
    search_fields = ('email', 'nom_complet', 'telephone')
    ordering = ('email',)
    readonly_fields = ('last_login', 'create_at', 'update_at', 'otp_secret')

    fieldsets = (
        (_("Informations personnelles"), {"fields": ("email", "nom_complet", "telephone", "photo_profil")}),
        (_("Permissions"), {"fields": ("is_active", "is_staff", "is_superuser", "user_permissions")}),
        (_("Dates"), {"fields": ("last_login", "create_at", "update_at")}),
        (_("Sécurité"), {"fields": ("otp_secret",)}),
    )
    
    add_fieldsets = (
        (_("Créer un utilisateur"), {
            "classes": ("wide",),
            "fields": ("email", "nom_complet", "telephone", "password1", "password2", "is_staff", "is_active"),
        }),
    )
    
    @admin.action(description="Réinitialiser le mot de passe des utilisateurs sélectionnés")
    def reset_password(self, request, queryset):
        for user in queryset:
            new_password = generate_password()
            user.set_password(new_password)
            user.save()
            messages.success(request, f"Mot de passe de {user.email} réinitialisé : {new_password}")

    actions = ['reset_password']
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(id=request.user.id)
    
    def has_view_permission(self, request, obj = ...):
        if request.user.is_superuser:
            return True
        return False
    
    def has_add_permission(self, request):
        if request.user.is_superuser:
            return True
        return False
    
    def has_delete_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        return False
    
    def has_change_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        return False
    
    def profil_preview(self, obj):
        """Affiche un aperçu de la photo de"""
        if obj.photo_profil:
            return mark_safe(f'<img src="{obj.photo_profil.url}" width="70" height="70" style="border-radius:5px;" />')
        return "-"
    profil_preview.short_description = "Image"
    
@admin.register(UserSession)
class UserSessionAdmin(admin.ModelAdmin):
    list_display = ['user__email', '_session_key', 'ip_address', 'created_at', 'expires_at', 'is_expired']
    search_fields = ['user__email', 'user__nom_complet', 'ip_address']
    list_filter = ['user']
    ordering = ('created_at',)
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(id=request.user.id)
    
    def has_view_permission(self, request, obj = ...):
        if request.user.is_superuser:
            return True
        return False
    
    def has_add_permission(self, request):
        if request.user.is_superuser:
            return True
        return False
    
    def has_delete_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        return False
    
    def has_change_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        return False
    
@admin.register(RoleUser)
class RoleUserAdmin(admin.ModelAdmin):
    list_display = ['user__email', 'role', 'is_active', 'created_at']
    search_fields = ['user__email', 'user__nom_complet', 'role']
    list_filter = ['user', 'role', 'is_active', 'created_at']
    ordering = ('user__email',)
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(id=request.user.id)
    
    def has_view_permission(self, request, obj = ...):
        if request.user.is_superuser:
            return True
        return False
    
    def has_add_permission(self, request):
        if request.user.is_superuser:
            return True
        return False
    
    def has_delete_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        return False
    
    def has_change_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        return False
    
@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['user__email', 'message', 'is_read', 'created_at']
    search_fields = ['user__email', 'user__nom_complet', 'message']
    list_filter = ['user', 'is_read', 'created_at']
    ordering = ('user__email', 'is_read')
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(id=request.user.id)
    
    def has_view_permission(self, request, obj = ...):
        if request.user.is_superuser:
            return True
        return False
    
    def has_add_permission(self, request):
        if request.user.is_superuser:
            return True
        return False
    
    def has_delete_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        return False
    
    def has_change_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        return False
