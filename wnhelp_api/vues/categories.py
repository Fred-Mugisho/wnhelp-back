from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view
from utils.functions import response_exception
from users_manager.decorateurs import login_required
from wnhelp_api.models.categories import Categorie, CategorieFormSerializer, CategorieSerializer


@api_view(["GET"])
def get_categories(request):
    try:
        categories = Categorie.objects.all().order_by("name")
        serializer_data = CategorieSerializer(categories, many=True).data
        return Response(serializer_data, status=status.HTTP_200_OK)
    except Exception as e:
        return response_exception(e)


@api_view(["POST"])
@login_required
def create_categorie(request):
    try:
        serializer = CategorieFormSerializer(data=request.data)
        if serializer.is_valid():
            categorie = serializer.save()
            return Response(CategorieSerializer(categorie).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return response_exception(e)


@api_view(["GET"])
def get_categorie(request, pk):
    try:
        categorie = Categorie.objects.get(pk=pk)
        serializer = CategorieSerializer(categorie)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Categorie.DoesNotExist:
        return Response({"detail": "Catégorie introuvable."}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return response_exception(e)


@api_view(["PUT"])
@login_required
def update_categorie(request, pk):
    try:
        categorie = Categorie.objects.get(pk=pk)
        serializer = CategorieFormSerializer(categorie, data=request.data)
        if serializer.is_valid():
            categorie = serializer.save()
            return Response(CategorieSerializer(categorie).data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Categorie.DoesNotExist:
        return Response({"detail": "Catégorie introuvable."}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return response_exception(e)


@api_view(["DELETE"])
@login_required
def delete_categorie(request, pk):
    try:
        categorie = Categorie.objects.get(pk=pk)
        categorie.delete()
        return Response({"detail": "Catégorie supprimée."}, status=status.HTTP_204_NO_CONTENT)
    except Categorie.DoesNotExist:
        return Response({"detail": "Catégorie introuvable."}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return response_exception(e)





