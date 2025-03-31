from django.urls import path
from . import views

urlpatterns = [
    # Authentification & Autorisation
    path('login/', views.login), # OK
    path('logout/', views.logout), # OK
    path('refresh-token/', views.refresh_token), # OK
    
    # Gestion des utilisateurs
    path('users/', views.get_users), # OK
    path('user/<int:id>/', views.get_user), # OK
    path('users/create/', views.create_update_user), # OK
    path('user/<int:id>/update/', views.create_update_user), # OK
    
    path('user/<int:id>/add-role/', views.add_role_user), # OK
    path('user/role/<int:id>/', views.get_role_user), # OK
    path('user/role/<int:id>/desactive/', views.desactive_role_user), # OK
    
    # Profil utilisateur
    path('me/', views.my_profil), # OK
    path('update-profil/', views.update_my_profil), # OK
    
    # Gestion des mots de passe
    path('password/change/', views.update_password),
    path('forgot-password/', views.forgot_password),
    path('password/reset/', views.reset_password),
    
    # Gestion des sessions
    path('sessions/', views.mes_sessions), # OK
    path('sessions/close-all/', views.close_all_session), # OK
    path('session/<int:id>/close/', views.close_session), # OK
    
    # Gestion des notifications utilisateur
    path('notifications/', views.get_notifications),
    path('notification/<int:id>/mark-as-read/', views.mark_notification_as_read),
    path('notification/<int:id>/delete/', views.delete_notification),
    path('notifications/mark-all-as-read/', views.mark_all_notifications_as_read),
]
