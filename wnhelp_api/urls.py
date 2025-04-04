from django.urls import path
from . import views

urlpatterns = [
    path('articles/', views.get_articles, name='get_articles'),
    path('articles/<slug:slug>/', views.get_article, name='get_article'),
    path('articles/commenter/<slug:slug>/', views.commenter_article, name='commenter_article'),
    path('rapports/', views.get_rapports, name='get_rapports'),
    path('rapports/<slug:slug>/', views.get_rapport, name='get_rapport'),
    path('contactez_nous/', views.contactez_nous, name='contactez_nous'),
    path('subscribe_newsletters/', views.subscribe_newsletters, name='subscribe_newsletters'),
]
