from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from utils.functions import response_exception
from wnhelp_api.models.partenaires import Partenaires, PartenairesCreateUpdateSerializer, PartenairesSerializer


@api_view(["GET"])
def get_partenaires(request):
    try:
        partenaires = Partenaires.objects.all().order_by('-joined_at')
        serializer_data = PartenairesSerializer(partenaires, many=True).data
        return Response(serializer_data, status=status.HTTP_200_OK)
    except Exception as e:
        return response_exception(e)


@api_view(["GET"])
def get_partenaire_detail(request, pk):
    try:
        partenaire = Partenaires.objects.get(pk=pk)
        serializer = PartenairesSerializer(partenaire)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Partenaires.DoesNotExist:
        return Response({"error": "Partenaire non trouvé."}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return response_exception(e)


@api_view(["POST"])
def create_partenaire(request):
    try:
        serializer = PartenairesCreateUpdateSerializer(data=request.data)
        if serializer.is_valid():
            partenaire = serializer.save()
            return Response(PartenairesSerializer(partenaire).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return response_exception(e)


@api_view(["PUT"])
def update_partenaire(request, pk):
    try:
        partenaire = Partenaires.objects.get(pk=pk)
        serializer = PartenairesCreateUpdateSerializer(partenaire, data=request.data, partial=True)
        if serializer.is_valid():
            partenaire = serializer.save()
            return Response(PartenairesSerializer(partenaire).data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Partenaires.DoesNotExist:
        return Response({"error": "Partenaire non trouvé."}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return response_exception(e)


@api_view(["DELETE"])
def delete_partenaire(request, pk):
    try:
        partenaire = Partenaires.objects.get(pk=pk)
        partenaire.delete()
        return Response({"message": "Partenaire supprimé avec succès."}, status=status.HTTP_204_NO_CONTENT)
    except Partenaires.DoesNotExist:
        return Response({"error": "Partenaire non trouvé."}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return response_exception(e)








