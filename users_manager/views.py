from .decorateurs import *
from .modeles.sessions import *
from .modeles.notification import *
from .modeles.role_user import *

# Authentification & Autorisation
@api_view(['POST'])
def login(request):
    try:
        email = request.data.get("email")
        password = request.data.get("password")
        if not check_validate_email(email):
            response = {
                "message": f"Votre adresse mail '{email}' est invalide"
            }
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
        
        user_account = CustomUser.objects.filter(email=email).first()
        if user_account:
            if not user_account.is_active:
                response = {
                    'message': "Votre compte est désactivé"
                }
                return Response(response, status=status.HTTP_401_UNAUTHORIZED)
            
            if user_account.check_password(password):
                user_info = SimpleCustomUserSerializer(user_account).data
                session = UserSession(
                    user=user_account, 
                    ip_address=get_client_ip(request), 
                    user_agent=get_user_agent(request)
                )
                session.set_session_key()
                session.save()
                token = session.session_key
                user_info["token"] = token
                return Response(user_info, status=status.HTTP_200_OK)
            else:
                response = {
                    'message': "Adresse mail et/ou mot de passe incorrect"
                }
                return Response(response, status=status.HTTP_401_UNAUTHORIZED)
        else:
            response = {
                'message': "Adresse mail et/ou mot de passe incorrect"
            }
            return Response(response, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return response_exception(e)
    
@api_view(['GET'])
@login_required
def logout(request):
    try:
        session_key = get_session_key(request)
        if not session_key:
            response = {
                "is_login": False, 
                "message": "Token manquant ou invalide"
            }
            return Response(response, status=status.HTTP_401_UNAUTHORIZED)
        session = UserSession.objects.filter(session_key=session_key).first()
        if not session:
            response = {
                "is_login": False, 
                "message": "Session invalide ou inexistante"
            }
            return Response(response, status=status.HTTP_401_UNAUTHORIZED)
        session.expires_at = now()
        session.save()
        
        response = {
            "message": "Déconnexion réussie"
        }
        return Response(response, status=status.HTTP_200_OK)
    except Exception as e:
        return response_exception(e)
    
@api_view(['GET'])
@login_required
def refresh_token(request):
    try:
        session_key = get_session_key(request)
        if not session_key:
            response = {
                "is_login": False, 
                "message": "Token manquant ou invalide"
            }
            return Response(response, status=status.HTTP_401_UNAUTHORIZED)
        
        session = UserSession.objects.filter(session_key=session_key).first()
        if not session:
            response = {
                "is_login": False, 
                "message": "Session invalide ou inexistante"
            }
            return Response(response, status=status.HTTP_401_UNAUTHORIZED)
        
        session.expires_at = now() + timedelta(days=1)
        session.set_session_key()
        session.save()
        response = {
            "token": session.session_key,
        }
        return Response(response, status=status.HTTP_200_OK)
    except Exception as e:
        return response_exception(e)
    
# Gestion des utilisateurs
@api_view(['GET'])
@login_required
@permission_roles(["Admin"])
def get_users(request):
    try:
        users = CustomUser.objects.all().order_by('nom_complet')
        search_content = request.GET.get("search_content")
        page = request.GET.get("page", 1)
        limit_page = request.GET.get("limit_page", 15)
        
        if search_content:
            users = users.filter(
                Q(email__icontains=search_content)
                | Q(nom_complet__icontains=search_content)
                | Q(telephone__icontains=search_content)
            )
        
        users_data = CustomUserSerializer(users, many=True).data
        users_pagination = KBPaginator(users_data, limit_page).get_page(page)
        return Response(users_pagination, status=status.HTTP_200_OK)
    except Exception as e:
        return response_exception(e)
    
@api_view(['GET'])
@login_required
@permission_roles(["Admin"])
def get_user(request, id):
    try:
        user = CustomUser.objects.get(id=id)
        user_serializer = CustomUserSerializer(user).data
        user_serializer["roles"] = user.roles
        user_serializer["notifications"] = user.notifications
        user_serializer["history_sessions"] = user.history_sessions
        return Response(user_serializer, status=status.HTTP_200_OK)
    except Exception as e:
        return response_exception(e)
    
@api_view(['POST', 'PUT'])
@login_required
@permission_roles(["Admin"])
def create_update_user(request, id=None):
    try:
        user = CustomUser.objects.filter(id=id).first()
        
        email = request.data.get('email')
        if not check_validate_email(email):
            response = {
                "message": f"L'adresse mail '{email}' est invalide"
            }
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
        
        nom_complet = request.data.get('nom_complet')
        telephone = request.data.get('telephone')
        photo_profil = request.FILES.get('photo_profil')
        
        if not photo_profil and user:
            photo_profil = user.photo_profil if user.photo_profil else None
        
        user_data = {
            "email": email,
            "nom_complet": nom_complet,
            "telephone": telephone,
            "photo_profil": photo_profil,
        }
        user_form = CustomUserSerializerCreate(data=user_data, instance=user)
        if user_form.is_valid():
            if user:
                user = user_form.save()
            else:
                user = CustomUser(**user_data)
                password = generate_password()
                user.set_password(password)
                user.save()
                
                subject = "Bienvenue sur la plateforme de World Needs and Help"
                message = f"""
                    <p>Bonjour <strong>{user.nom_complet}</strong>,</p>
                    <p>Nous sommes heureux de vous accueillir sur la plateforme de <strong>World Needs and Help</strong>.</p>
                    <p>Voici vos informations de connexion :</p>
                    <ul>
                        <li><strong>Mot de passe temporaire :</strong> {password}</li>
                    </ul>
                    <p>Veuillez vous connecter dès que possible et <strong>changer votre mot de passe</strong> pour sécuriser votre compte.</p>
                    <p>Si vous avez des questions ou des difficultés, n'hésitez pas à nous contacter.</p>
                    <p style="margin-top: 32px;">
                        Cordialement,<br>
                        L'équipe <strong>World Needs and Help</strong>
                    </p>
                """
                destinateurs = [user.email]
                send_mail_template(subject, message, destinateurs)
            return Response(CustomUserSerializer(user).data, status=status.HTTP_200_OK)
        return Response(user_form.errors, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return response_exception(e)
    
@api_view(['POST'])
@login_required
@permission_roles(["Admin"])
def add_role_user(request, id):
    try:
        user = CustomUser.objects.get(id=id)
        role = request.data.get('role', '').strip()
        if RoleUser.objects.filter(user=user, role=role, is_active=True).exists():
            response = {
                "message": f"Le role '{role}' est déja attribué à l'utilisateur"
            }
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
        
        role_data = {
            "user": user.pk,
            "role": role,
            "is_active": True
        }
        role_form = RoleUserSerializerCreate(data=role_data)
        if role_form.is_valid():
            role = role_form.save()
            role_serializer = RoleUserSerializer(role).data
            return Response(role_serializer, status=status.HTTP_200_OK)
        return Response(role_form.errors, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return response_exception(e)
    
@api_view(['GET'])
@login_required
@permission_roles(["Admin"])
def get_role_user(request, id):
    try:
        role = RoleUser.objects.get(id=id)
        role_serializer = RoleUserSerializer(role).data
        return Response(role_serializer, status=status.HTTP_200_OK)
    except Exception as e:
        return response_exception(e)
    
@api_view(['GET'])
@login_required
@permission_roles(["Admin"])
def desactive_role_user(request, id):
    try:
        role = RoleUser.objects.filter(is_active=True, id=id).first()
        if not role:
            response = {
                "message": f"Le role n'existe pas ou a déjà été désactivé"
            }
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
        
        role.is_active = False
        role.save()
        role_serializer = RoleUserSerializer(role).data
        return Response(role_serializer, status=status.HTTP_200_OK)
    except Exception as e:
        return response_exception(e)

@api_view(['GET'])
@login_required
def my_profil(request):
    try:
        session_key = get_session_key(request)
        if not session_key:
            response = {
                "is_login": False, 
                "message": "Token manquant ou invalide"
            }
            return Response(response, status=status.HTTP_401_UNAUTHORIZED)
        session = UserSession.objects.filter(session_key=session_key).first()
        if not session:
            response = {
                "is_login": False, 
                "message": "Session invalide ou inexistante"
            }
            return Response(response, status=status.HTTP_401_UNAUTHORIZED)
        user = session.user
        user_serializer = CustomUserSerializer(user).data
        user_serializer["roles"] = user.roles
        return Response(user_serializer, status=status.HTTP_200_OK)
    except Exception as e:
        return response_exception(e)
    
@api_view(['PUT'])
@login_required
def update_my_profil(request):
    try:
        session_key = get_session_key(request)
        if not session_key:
            response = {
                "is_login": False, 
                "message": "Token manquant ou invalide"
            }
            return Response(response, status=status.HTTP_401_UNAUTHORIZED)
        session = UserSession.objects.filter(session_key=session_key).first()
        if not session:
            response = {
                "is_login": False, 
                "message": "Session invalide ou inexistante"
            }
            return Response(response, status=status.HTTP_401_UNAUTHORIZED)
        user = session.user
        
        email = request.data.get('email')
        if not check_validate_email(email):
            response = {
                "message": f"L'adresse mail '{email}' est invalide"
            }
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
        
        nom_complet = request.data.get('nom_complet')
        telephone = request.data.get('telephone')
        photo_profil = request.FILES.get('photo_profil')
        
        if not photo_profil and user:
            photo_profil = user.photo_profil if user.photo_profil else None
        
        user_data = {
            "email": email,
            "nom_complet": nom_complet,
            "telephone": telephone,
            "photo_profil": photo_profil,
        }
        user_form = CustomUserSerializerCreate(data=user_data, instance=user)
        if user_form.is_valid():
            user = user_form.save()
            return Response(CustomUserSerializer(user).data, status=status.HTTP_200_OK)
        return Response(user_form.errors, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return response_exception(e)
    
# Gestion des mots de passe
@api_view(['PUT'])
@login_required
def update_password(request):
    try:
        session_key = get_session_key(request)
        if not session_key:
            response = {
                "is_login": False, 
                "message": "Token manquant ou invalide"
            }
            return Response(response, status=status.HTTP_401_UNAUTHORIZED)
        session = UserSession.objects.filter(session_key=session_key).first()
        if not session:
            response = {
                "is_login": False, 
                "message": "Session invalide ou inexistante"
            }
            return Response(response, status=status.HTTP_401_UNAUTHORIZED)
        user = session.user
        
        old_password = request.data.get('old_password')
        new_password = request.data.get('new_password')
        confirm_password = request.data.get('confirm_password')
        
        if not old_password or not new_password or not confirm_password:
            response = {
                "message": "Veuillez fournir tous les champs requis"
            }
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
        
        if not user.check_password(old_password):
            response = {
                "message": "Le mot de passe actuelle est incorrect"
            }
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
        
        if new_password != confirm_password:
            response = {
                "message": "Les mots de passe ne correspondent pas"
            }
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
        
        if old_password == new_password:
            response = {
                "message": "Le nouveau mot de passe doit différer du mot de passe actuel"
            }
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
        
        password_is_valid, erreurs = password_validator(password=new_password)
        if not password_is_valid:
            password_errors = {
                "message": "Le mot de passe doit contenir au moins 8 caractères, une lettre majuscule, une lettre minuscule, un chiffre et un caractère special.",
                "password_errors": erreurs
            }
            return Response(password_errors, status=status.HTTP_400_BAD_REQUEST)
        
        user.set_password(new_password)
        user.close_all_session()
        user.save()
        
        response = {
            "message": "Votre mot de passe a été mis à jour avec succès"
        }
        return Response(response, status=status.HTTP_200_OK)
    except Exception as e:
        return response_exception(e)
    
@api_view(['POST'])
def forgot_password(request):
    try:
        email = request.data.get('email')
        if not check_validate_email(email):
            response = {
                "message": f"L'adresse mail '{email}' est invalide"
            }
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
        
        user = CustomUser.objects.filter(email=email).first()
        if not user:
            response = {
                "message": f"Utilisateur avec l'adresse mail '{email}' introuvable"
            }
            return Response(response, status=status.HTTP_404_NOT_FOUND)
        
        user.set_otp_secret()
        user.save()
        
        subject = "Réinitialisation de votre mot de passe"
        message = f"""
            <p>Bonjour <strong>{user.nom_complet}</strong>,</p>
            <p>Nous avons reçu une demande de réinitialisation de votre mot de passe.</p>
            <p>Veuillez utiliser le code OTP suivant pour confirmer l'opération :</p>
            <p style="font-size: 22px; font-weight: bold; color: #296638;">{user.otp_secret}</p>
            <p>Ce code est temporaire et expirera dans quelques minutes. Si vous n'avez pas demandé cette réinitialisation, veuillez ignorer ce message ou nous contacter immédiatement.</p>
            <p style="margin-top: 32px;">Cordialement,<br>
            L'équipe <strong>World Needs and Help</strong></p>
        """
        send_mail_template(subject, message, [email])
        
        message_notification = f"Une demande de reinitialisation de mot de passe a été faite pour votre compte."
        user.send_notification(message_notification)
        
        response = {
            "message": "Un email avec un code validation a été envoyé vers votre adresse mail, veuillez le fournir pour confirmer la reinitialisation de votre mot de passe."
        }
        return Response(response, status=status.HTTP_200_OK)
    except Exception as e:
        return response_exception(e)
    
@api_view(['POST'])
def reset_password(request):
    try:
        code_validation = request.data.get('code_validation')
        password = request.data.get('password')
        confirm_password = request.data.get('confirm_password')
        
        if not code_validation or not password or not confirm_password:
            response = {
                "message": "Veuillez fournir tous les champs requis"
            }
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
        
        if password != confirm_password:
            response = {
                "message": "Les mots de passe ne correspondent pas"
            }
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
        
        password_is_valid, erreurs = password_validator(password=password)
        if not password_is_valid:
            password_errors = {
                "message": "Le mot de passe doit contenir au moins 8 caractères, une lettre majuscule, une lettre minuscule, un chiffre et un caractère special.",
                "password_errors": erreurs
            }
            return Response(password_errors, status=status.HTTP_400_BAD_REQUEST)
        
        user = CustomUser.objects.filter(otp_secret=code_validation).first()
        if not user:
            response = {
                "message": "Le code de validation fourni est incorrect"
            }
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
        
        user.set_password(password)
        user.otp_secret = None
        user.save()
        
        user.close_all_session()
        user.send_notification("Votre mot de passe a bien été reinitialiser.")
        
        response = {
            "message": "Votre mot de passe a été reinitialisé avec succès"
        }
        return Response(response, status=status.HTTP_200_OK)
    except Exception as e:
        return response_exception(e)
    
# Gestion des sessions
@api_view(['GET'])
@login_required
def mes_sessions(request):
    try:
        session_key = get_session_key(request)
        if not session_key:
            response = {
                "is_login": False, 
                "message": "Token manquant ou invalide"
            }
            return Response(response, status=status.HTTP_401_UNAUTHORIZED)
        session = UserSession.objects.filter(session_key=session_key).first()
        if not session:
            response = {
                "is_login": False, 
                "message": "Session invalide ou inexistante"
            }
            return Response(response, status=status.HTTP_401_UNAUTHORIZED)
        
        page = request.GET.get("page", 1)
        limit_page = request.GET.get("limit_page", 15)
        
        user = session.user
        history_sessions = user.history_sessions
        data_pagination = KBPaginator(history_sessions, limit_page).get_page(page)
        return Response(data_pagination, status=status.HTTP_200_OK)
    except Exception as e:
        return response_exception(e)
    
@api_view(['GET'])
@login_required
def close_all_session(request):
    try:
        session_key = get_session_key(request)
        if not session_key:
            response = {
                "is_login": False, 
                "message": "Token manquant ou invalide"
            }
            return Response(response, status=status.HTTP_401_UNAUTHORIZED)
        session = UserSession.objects.filter(session_key=session_key).first()
        if not session:
            response = {
                "is_login": False, 
                "message": "Session invalide ou inexistante"
            }
            return Response(response, status=status.HTTP_401_UNAUTHORIZED)
        
        user = session.user
        
        sessions = UserSession.objects.filter(user=user)
        for session in sessions:
            if not session.is_expired:
                session.close_session()
        
        response = {
            "message": "Toutes vos sessions ont été fermées avec succès, vous pouvez maintenant vous reconnecter"
        }
        return Response(response, status=status.HTTP_200_OK)
    except Exception as e:
        return response_exception(e)
    
@api_view(['GET'])
@login_required
def close_session(request, id):
    try:
        session_key = get_session_key(request)
        if not session_key:
            response = {
                "is_login": False, 
                "message": "Token manquant ou invalide"
            }
            return Response(response, status=status.HTTP_401_UNAUTHORIZED)
        session = UserSession.objects.filter(session_key=session_key).first()
        if not session:
            response = {
                "is_login": False, 
                "message": "Session invalide ou inexistante"
            }
            return Response(response, status=status.HTTP_401_UNAUTHORIZED)
        
        user = session.user
        session_close = user.all_sessions.filter(id=id).first()
        if not session_close:
            response = {
                "message": "Cette session n'existe pas"
            }
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
        
        if session_close.is_expired:
            response = {
                "message": "Cette session est déjà fermée"
            }
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
        
        if session_close == session:
            response = {
                "message": "Vous ne pouvez pas fermer votre session actuelle"
            }
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
        
        session_close.close_session()
        response = {
            "message": "La session a été fermée avec succès"
        }
        return Response(response, status=status.HTTP_200_OK)
    except Exception as e:
        return response_exception(e)

# Gestion des notifications utilisateur
@api_view(['GET'])
@login_required
def get_notifications(request):
    try:
        session_key = get_session_key(request)
        if not session_key:
            response = {
                "is_login": False, 
                "message": "Token manquant ou invalide"
            }
            return Response(response, status=status.HTTP_401_UNAUTHORIZED)
        session = UserSession.objects.filter(session_key=session_key).first()
        if not session:
            response = {
                "is_login": False, 
                "message": "Session invalide ou inexistante"
            }
            return Response(response, status=status.HTTP_401_UNAUTHORIZED)
        user = session.user
        return Response(user.notifications, status=status.HTTP_200_OK)
    except Exception as e:
        return response_exception(e)
    
@api_view(['GET'])
@login_required
def mark_notification_as_read(request, id):
    try:
        session_key = get_session_key(request)
        if not session_key:
            response = {
                "is_login": False, 
                "message": "Token manquant ou invalide"
            }
            return Response(response, status=status.HTTP_401_UNAUTHORIZED)
        session = UserSession.objects.filter(session_key=session_key).first()
        if not session:
            response = {
                "is_login": False, 
                "message": "Session invalide ou inexistante"
            }
            return Response(response, status=status.HTTP_401_UNAUTHORIZED)
        user = session.user
        notification = user.all_notifications.filter(is_read=False, id=id).first()
        if not notification:
            response = {
                "message": "Cette notification n'existe pas ou elle a déjà été marquée comme lue"
            }
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
        
        notification.mark_as_read()
        notification_sericalizer = MyNotifiacationSerializer(notification).data
        return Response(notification_sericalizer, status=status.HTTP_200_OK)
    except Exception as e:
        return response_exception(e)
    
@api_view(['DELETE'])
@login_required
def delete_notification(request, id):
    try:
        session_key = get_session_key(request)
        if not session_key:
            response = {
                "is_login": False, 
                "message": "Token manquant ou invalide"
            }
            return Response(response, status=status.HTTP_401_UNAUTHORIZED)
        session = UserSession.objects.filter(session_key=session_key).first()
        if not session:
            response = {
                "is_login": False, 
                "message": "Session invalide ou inexistante"
            }
            return Response(response, status=status.HTTP_401_UNAUTHORIZED)
        user = session.user
        notification = user.all_notifications.filter(id=id).first()
        if not notification:
            response = {
                "message": "Cette notification n'existe pas ou elle a déjà été supprimée"
            }
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
        
        notification.delete()
        response = {
            "message": "La notification a bien été supprimée"
        }
        return Response(response, status=status.HTTP_200_OK)
    except Exception as e:
        return response_exception(e)
    
@api_view(['GET'])
@login_required
def mark_all_notifications_as_read(request):
    try:
        session_key = get_session_key(request)
        if not session_key:
            response = {
                "is_login": False, 
                "message": "Token manquant ou invalide"
            }
            return Response(response, status=status.HTTP_401_UNAUTHORIZED)
        session = UserSession.objects.filter(session_key=session_key).first()
        if not session:
            response = {
                "is_login": False, 
                "message": "Session invalide ou inexistante"
            }
            return Response(response, status=status.HTTP_401_UNAUTHORIZED)
        user = session.user
        notifications = user.all_notifications.filter(is_read=False)
        if not notifications:
            response = {
                "message": "Toutes vos notifications sont déjà marquées comme lues"
            }
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
        
        for notification in notifications:
            notification.mark_as_read()
            
        return Response(user.notifications, status=status.HTTP_200_OK)
    except Exception as e:
        return response_exception(e)