from users_manager.decorateurs import *

@api_view(['GET'])
@login_required
@permission_roles(["Admin", "Editeur"])
def articles(request):
    try:
        search_content = request.GET.get("search_content")
        page = request.GET.get("page", 1)
        limit_page = request.GET.get("limit_page", 15)
        categories = request.GET.get("categories", None)
        articles = [
            {
                "id": 1,
                "title": "Article 1",
                "content": "Contenu de l'article 1"
            },
            {
                "id": 2,
                "title": "Article 2",
                "content": "Contenu de l'article 2"
            }
        ]
        pagination = KBPaginator(articles, limit_page).get_page(page)
        return Response(pagination, status=status.HTTP_200_OK)
    except Exception as e:
        return response_exception(e)