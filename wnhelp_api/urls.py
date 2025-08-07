from django.urls import path
from . import views
from .vues import categories
from .vues import articles
from .vues import rapports
from .vues import partenaires
from .vues import subscribe_newsletters

urlpatterns = [
    path("categories/", categories.get_categories, name="get_categories"),
    path("categories/create/", categories.create_categorie, name="create_categorie"),
    path("categories/<int:pk>/", categories.get_categorie, name="get_categorie"),
    path("categories/<int:pk>/update/", categories.update_categorie, name="update_categorie"),
    path("categories/<int:pk>/delete/", categories.delete_categorie, name="delete_categorie"),
    

    path('articles/', articles.get_articles, name='get_articles'),
    path('recents_articles/', articles.get_recents_articles, name='get_recents_articles'),
    path('articles/<slug:slug>/', articles.get_article, name='get_article'),
    path("articles/create/", articles.create_article, name="create_article"),
    path("articles/<int:id>/update/", articles.update_article, name="update_article"),
    path("articles/<int:id>/delete/", articles.delete_article, name="delete_article"),
    
    
    path('articles/commenter/<slug:slug>/', views.commenter_article, name='commenter_article'),
    
    
    path("rapports/", rapports.get_rapports, name="get_rapports"),
    path("rapports/<slug:slug>/", rapports.get_rapport, name="get_rapport"),
    path("rapports/create/", rapports.create_rapport, name="create_rapport"),
    path("rapports/<int:id>/update/", rapports.update_rapport, name="update_rapport"),
    path("rapports/<int:id>/delete/", rapports.delete_rapport, name="delete_rapport"),

        
    
    path('contactez_nous/', views.contactez_nous, name='contactez_nous'),
    
    
    path('subscribe_newsletters/', subscribe_newsletters.subscribe_newsletters, name='subscribe_newsletters'),
    
    
    path('gallerie/', views.gallerie, name='gallerie'),
    
    
    path('partenaires/', partenaires.get_partenaires, name='get_partenaires'),
    path('partenaires/', partenaires.get_partenaires, name='get_partenaires'),
    path('partenaires/<int:pk>/', partenaires.get_partenaire_detail, name='get_partenaire_detail'),
    path('partenaires/create/', partenaires.create_partenaire, name='create_partenaire'),
    path('partenaires/<int:pk>/update/', partenaires.update_partenaire, name='update_partenaire'),
    path('partenaires/<int:pk>/delete/', partenaires.delete_partenaire, name='delete_partenaire'),
    
    
    # Jobs API
    path('offres_emploi/', views.offres_emploi, name='offres_emploi'),
    path('offres_emploi/<int:id>/', views.offres_emploi, name='offres_emploi_id'),
]
