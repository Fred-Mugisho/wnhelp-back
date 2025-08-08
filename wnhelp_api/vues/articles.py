from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view
from rest_framework import status
from django.db.models import Q

from utils.functions import response_exception
from wnhelp_api.models.articles import *
from users_manager.decorateurs import login_required



@api_view(["POST"])
@login_required
def create_article(request):
    try:
        serializer = ArticleFormSerializer(data=request.data)
        if serializer.is_valid():
            article = serializer.save()
            return Response(ArticleSerializer(article).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return response_exception(e)


@api_view(["GET"])
def get_articles(request):
    try:
        articles = Article.objects.filter(status="published").order_by("-id")
        search_content = request.GET.get("search_content")
        page = request.GET.get("page", 1)
        limit_page = request.GET.get("limit_page", 15)
        categories_id = request.GET.get("categories", "").split(",")
        categories = [int(cat) for cat in categories_id if is_convertible_to_int(cat)]

        if search_content:
            articles = articles.filter(
                Q(title__icontains=search_content)
                | Q(contenu__icontains=search_content)
            )
        if categories:
            articles = articles.filter(categorie__id__in=categories)

        serializer_data = ArticleSerializer(articles, many=True).data
        pagination = KBPaginator(serializer_data, limit_page).get_page(page)
        return Response(pagination, status=status.HTTP_200_OK)
    except Exception as e:
        return response_exception(e)


@api_view(["GET"])
def get_recents_articles(request):
    try:
        articles = Article.objects.filter(status="published").order_by("-id")[:3]

        serializer_data = ArticleSerializer(articles, many=True).data
        return Response(serializer_data, status=status.HTTP_200_OK)
    except Exception as e:
        return response_exception(e)


@api_view(["GET"])
def get_article(request, slug):
    try:
        article = Article.objects.filter(slug=slug, status="published").first()
        if not article:
            return Response(
                {"message": "Article n'existe pas"}, status=status.HTTP_404_NOT_FOUND
            )

        autres_article = (
            Article.objects.filter(status="published")
            .exclude(slug=slug)
            .order_by("-id")[:3]
        )
        autres_article_serializer = OthersArticleSerializer(
            autres_article, many=True
        ).data

        serializer_data = DetailsArticleSerializer(article).data
        serializer_data["autres_articles"] = autres_article_serializer
        return Response(serializer_data, status=status.HTTP_200_OK)
    except Exception as e:
        return response_exception(e)


# @login_required
@api_view(["PUT", "PATCH"])
def update_article(request, id):
    try:
        article = get_object_or_404(Article, id=id)
        serializer = ArticleFormSerializer(article, data=request.data, partial=True)
        if serializer.is_valid():
            article = serializer.save()
            return Response(ArticleSerializer(article).data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return response_exception(e)

@api_view(["DELETE"])
@login_required
def delete_article(request, id):
    try:
        article = Article.objects.get(id=id)
        article.delete()
        return Response({"detail": "Article supprimée."}, status=status.HTTP_204_NO_CONTENT)
    except Article.DoesNotExist:
        return Response({"detail": "Article introuvable."}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return response_exception(e)


