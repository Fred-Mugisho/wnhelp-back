from functools import wraps
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view
from .modeles.sessions import *
from utils.functions import *
from django.db.models import Q

def login_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        session_key = get_session_key(request)
        if not session_key:
            response = {
                "message": "Token manquant ou invalide"
            }
            return Response(response, status=status.HTTP_401_UNAUTHORIZED)
        
        session = UserSession.objects.filter(session_key=session_key).first()
        if not session:
            response = {
                "message": "Session invalide ou expirée"
            }
            return Response(response, status=status.HTTP_401_UNAUTHORIZED)
        
        if session.is_expired:
            response = {
                "message": "Votre session est expirée"
            }
            return Response(response, status=status.HTTP_401_UNAUTHORIZED)
        
        user = session.user
        if not user.is_active:
            response = {
                "message": "Votre compte est désactivé"
            }
            return Response(response, status=status.HTTP_401_UNAUTHORIZED)
        
        user.last_login = now()
        user.save()
        return view_func(request, *args, **kwargs)
    return wrapper

def permission_roles(roles):
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            session_key = get_session_key(request)
            if not session_key:
                return Response({"message": "Token manquant ou invalide"}, status=status.HTTP_401_UNAUTHORIZED)

            session = UserSession.objects.filter(session_key=session_key).first()
            if not session or session.is_expired:
                return Response({"message": "Votre session est expirée"}, status=status.HTTP_401_UNAUTHORIZED)

            user = session.user
            if not user.is_active:
                return Response({"message": "Votre compte est désactivé"}, status=status.HTTP_403_FORBIDDEN)

            if "Super Admin" in roles and user.is_superuser:
                return view_func(request, *args, **kwargs)
            
            # Vérification du rôle
            roles_active_user = user.all_roles.filter(is_active=True)
            for role in roles_active_user:
                if role.role in roles:
                    return view_func(request, *args, **kwargs)
            return Response({"message": "Vous n'avez pas les permissions requises"}, status=status.HTTP_403_FORBIDDEN)
        return wrapper
    return decorator