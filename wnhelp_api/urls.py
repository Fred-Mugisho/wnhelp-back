from django.urls import path
from . import views

urlpatterns = [
    path('categories/', views.get_categories, name='get_categories'),
    path('articles/', views.get_articles, name='get_articles'),
    path('recents_articles/', views.get_recents_articles, name='get_recents_articles'),
    path('articles/<slug:slug>/', views.get_article, name='get_article'),
    path('articles/commenter/<slug:slug>/', views.commenter_article, name='commenter_article'),
    path('rapports/', views.get_rapports, name='get_rapports'),
    path('rapports/<slug:slug>/', views.get_rapport, name='get_rapport'),
    path('contactez_nous/', views.contactez_nous, name='contactez_nous'),
    path('subscribe_newsletters/', views.subscribe_newsletters, name='subscribe_newsletters'),
    path('gallerie/', views.gallerie, name='gallerie'),
    path('partenaires/', views.get_partenaires, name='get_partenaires'),
    
    # Jobs API
    path('offres_emploi/', views.offres_emploi, name='offres_emploi'),
    path('offres_emploi/<int:id>/', views.offres_emploi, name='offres_emploi_id'),
]
