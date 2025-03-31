from django.contrib import admin
from django.contrib.auth.models import Group
from .modeles.sessions import *
from .modeles.notification import *
from .modeles.role_user import *

admin.site.unregister(Group)

admin.site.site_header = "CHALU PAY"
admin.site.index_title = "CHALU PAY ADMINISTRATION"
admin.site.site_title = "CHALU PAY"

@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ['email', 'nom_complet', 'telephone', 'is_active', 'update_at']
    search_fields = ['email', 'nom_complet', 'telephone']
    list_filter = ['is_active', 'is_staff']
    ordering = ('email',)
    
    filter_horizontal = ()
    fieldsets = (
        ('Informations de connexion', {'fields': ('email', 'password')}),
        ('Informations personnelles', {'fields': ('nom_complet', 'telephone', 'photo_profil')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser')}),
        ('Dates', {'fields': ('create_at', 'update_at', 'last_login')}),
    )
    readonly_fields = ['create_at', 'update_at', 'last_login', 'password']
    
    def has_add_permission(self, request):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
    
@admin.register(UserSession)
class UserSessionAdmin(admin.ModelAdmin):
    list_display = ['user__email', '_session_key', 'ip_address', 'created_at', 'expires_at', 'is_expired']
    search_fields = ['user__email', 'user__nom_complet', 'ip_address']
    list_filter = ['user']
    ordering = ('created_at',)
    
    def has_add_permission(self, request):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
    
@admin.register(RoleUser)
class RoleUserAdmin(admin.ModelAdmin):
    list_display = ['user__email', 'role', 'is_active', 'created_at']
    search_fields = ['user__email', 'user__nom_complet', 'role']
    list_filter = ['user', 'role', 'is_active', 'created_at']
    ordering = ('user__email',)
    
    def has_add_permission(self, request):
        return True
    
    def has_delete_permission(self, request, obj=None):
        return False
    
    def has_change_permission(self, request, obj=None):
        return True
    
@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['user__email', 'message', 'is_read', 'created_at']
    search_fields = ['user__email', 'user__nom_complet', 'message']
    list_filter = ['user', 'is_read', 'created_at']
    ordering = ('user__email', 'is_read')
    
    def has_add_permission(self, request):
        return True
    
    def has_delete_permission(self, request, obj=None):
        return False
    
    def has_change_permission(self, request, obj=None): 
        return True
