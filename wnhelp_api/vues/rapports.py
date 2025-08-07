from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from utils.functions import KBPaginator, response_exception
from wnhelp_api.models.rapports import OthersRapportSerializer, Rapport, RapportFormSerializer, RapportSerializer
from django.db.models import Q
from users_manager.decorateurs import login_required


@api_view(["GET"])
def get_rapports(request):
    try:
        rapports = Rapport.objects.all().order_by("-published_at")
        search_content = request.GET.get("search_content")
        page = request.GET.get("page", 1)
        limit_page = request.GET.get("limit_page", 15)

        if search_content:
            rapports = rapports.filter(
                Q(title__icontains=search_content)
                | Q(contenu__icontains=search_content)
            )

        serializer_data = RapportSerializer(rapports, many=True).data
        pagination = KBPaginator(serializer_data, limit_page).get_page(page)
        return Response(pagination, status=status.HTTP_200_OK)
    except Exception as e:
        return response_exception(e)


@api_view(["GET"])
def get_rapport(request, slug):
    try:
        rapport = Rapport.objects.filter(slug=slug).first()
        if not rapport:
            return Response(
                {"message": "Rapport n'existe pas"}, status=status.HTTP_404_NOT_FOUND
            )

        autres_rapport = Rapport.objects.all().exclude(slug=slug).order_by("-published_at")[:3]
        autres_rapport_serializer = OthersRapportSerializer(
            autres_rapport, many=True
        ).data

        serializer_data = RapportSerializer(rapport).data
        serializer_data["autres_rapports"] = autres_rapport_serializer
        return Response(serializer_data, status=status.HTTP_200_OK)
    except Exception as e:
        return response_exception(e)


@api_view(["POST"])
@login_required
def create_rapport(request):
    try:
        serializer = RapportFormSerializer(data=request.data)
        if serializer.is_valid():
            rapport = serializer.save()
            return Response(RapportSerializer(rapport).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return response_exception(e)


@api_view(["PUT", "PATCH"])
@login_required
def update_rapport(request, id):
    try:
        rapport = Rapport.objects.get(id=id)
        serializer = RapportFormSerializer(rapport, data=request.data, partial=True)
        if serializer.is_valid():
            rapport = serializer.save()
            return Response(RapportSerializer(rapport).data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Rapport.DoesNotExist:
        return Response({"message": "Rapport introuvable"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return response_exception(e)


@api_view(["DELETE"])
@login_required
def delete_rapport(request, id):
    try:
        rapport = Rapport.objects.get(id=id)
        rapport.delete()
        return Response({"message": "Rapport supprimé"}, status=status.HTTP_204_NO_CONTENT)
    except Rapport.DoesNotExist:
        return Response({"message": "Rapport introuvable"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return response_exception(e)




