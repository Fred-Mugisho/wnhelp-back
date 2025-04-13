from email.mime.image import MIMEImage
from rest_framework.response import Response
from rest_framework import status
import secrets
import string
from wnhelp_back.settings import EMAIL_HOST_USER, BASE_DIR, EMAIL_HOST
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from datetime import datetime, date
import os
import logging
import re
from PIL import Image
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.core.files.base import ContentFile
from wnhelp_api.tasks import send_mail_template_async

logger = logging.getLogger(__name__)

def password_validator(password: str):
    special_chars = "$@#%&"
    erreurs = {}

    if len(password) < 8:
        erreurs["min_length"] = "Le mot de passe doit contenir au moins 8 caractères."

    if not any(char.isdigit() for char in password):
        erreurs["min_digit"] = "Le mot de passe doit contenir au moins un chiffre."

    if not any(char.isupper() for char in password):
        erreurs["min_uppercase"] = "Le mot de passe doit contenir au moins une lettre majuscule."

    if not any(char.islower() for char in password):
        erreurs["min_lowercase"] = "Le mot de passe doit contenir au moins une lettre minuscule."

    if not any(char in special_chars for char in password):
        erreurs["min_special_char"] = f"Le mot de passe doit contenir au moins un caractère special dans la liste suivante : {special_chars}."

    if erreurs:
        return False, erreurs

    return True, None

def generate_session_key():
    """Génère une clé de session aléatoire sécurisée."""
    return secrets.token_hex(32)

def generate_password(length: int = 10) -> str:
    if length < 8:
        raise ValueError("La longueur du mot de passe doit être d'au moins 8 caractères.")

    special_chars = "@#$%&"
    password = [
        secrets.choice(string.ascii_uppercase),  # Majuscule
        secrets.choice(string.ascii_lowercase),  # Minuscule
        secrets.choice(string.digits),           # Chiffre
        secrets.choice(special_chars)            # Caractère spécial
    ]
    
    # Compléter le reste du mot de passe
    password += [secrets.choice(string.ascii_letters + string.digits + special_chars) for _ in range(length - 4)]

    # Mélanger le tout
    secrets.SystemRandom().shuffle(password)

    return ''.join(password)

def generate_otp() -> str:
    return ''.join(secrets.choice(string.digits) for _ in range(6))

def send_mail_template(subject: str, message: str, destinateurs: list, bcc: list = None, file_attach: str = None):
    send_mail_template_async(subject, message, destinateurs, file_attach)        

class KBPaginator:
    def __init__(self, items: list, page_size):
        page_size = int(page_size) if is_convertible_to_int(page_size) else 15
        
        self.items = items
        self.page_size = int(page_size) if page_size > 0 else 15
        self.total_pages = (len(items) + self.page_size - 1) // self.page_size  # Calcul du nombre total de pages

    def get_page(self, page_number):
        page_number = int(page_number) if is_convertible_to_int(page_number) else 1
        if not self.items:
            return {
                "previous_page_number": None,
                "current_page_number": 1,
                "next_page_number": None,
                "nombre_total_pages": 1,
                "page_content": [],
            }

        if page_number < 1 or page_number > self.total_pages:
            page_number = max(1, min(page_number, self.total_pages))

        # Calcul des indices de début et de fin pour la page actuelle
        start_index = (page_number - 1) * self.page_size
        end_index = min(start_index + self.page_size, len(self.items))  # Limiter à la taille de la liste

        # Extraire les éléments de la page actuelle
        page_content = self.items[start_index:end_index]

        # Déterminer les pages précédente et suivante
        previous_page_number = page_number - 1 if page_number > 1 else None
        next_page_number = page_number + 1 if page_number < self.total_pages else None

        return {
            "previous_page_number": previous_page_number,
            "current_page_number": page_number,
            "next_page_number": next_page_number,
            "nombre_total_pages": self.total_pages,
            "page_content": page_content,
        }

def is_convertible_to_int(s):
    try:
        r = int(s)
        return True
    except ValueError:
        return False

def response_exception(e):
    response = {
        "message": f"Un problème est survenu, veuillez reessayer plus tard",
        "error": str(e)
    }
    logging.error(f"Error --> {e}")
    return Response(response, status=status.HTTP_400_BAD_REQUEST)

def get_client_ip(request):
    """Récupère l'adresse IP réelle du client en prenant en compte les proxys."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR', "")
    
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()  # Prend la première IP (IP réelle du client)
    else:
        ip = request.META.get('REMOTE_ADDR', "")  # IP directe si pas de proxy

    return ip

def get_user_agent(request):
    """Récupère l'User-Agent du client (appareil, navigateur, OS)."""
    return request.META.get("HTTP_USER_AGENT", "Unknown")

def get_session_key(request):
    auth_header = request.META.get("HTTP_AUTHORIZATION", "")
    if not auth_header.startswith("Bearer "):
        return None

    session_key = auth_header.split(" ")[1].strip()
    if not session_key:
        return None
    
    return session_key

def check_validate_email(email):
    # Regular expression to validate email
    email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    
    if re.match(email_regex, email):
        return True
    else:
        return False
    
class ImageCompressor:
    def __init__(self, image, format='WEBP'):
        self.image = image
        self.format = format.upper()
        self.output = BytesIO()
        self.size = (1200, 600)  # Taille uniforme pour toutes les images
    
    def compress(self):
        try:
            img = Image.open(self.image)

            # Convertir en mode RGB si nécessaire (évite les erreurs sur PNG)
            if img.mode in ("RGBA", "P"):
                img = img.convert("RGB")

            # Redimensionner l'image en conservant le ratio
            img.thumbnail(self.size)
            
            # Définir l'extension et le type MIME
            ext = self.format.lower()
            content_type = f'image/{ext}'
            
            # Sauvegarde avec compression
            img.save(self.output, format=self.format, quality=80)
            self.output.seek(0)

            # 🔥 Correction : Utiliser uniquement le **nom du fichier**, sans le chemin complet
            filename = os.path.basename(self.image.name).rsplit('.', 1)[0] + f".{ext}"

            return ContentFile(self.output.getvalue(), name=filename)

        except Exception as e:
            print(f"Erreur lors de la compression de l'image : {e}")
            return self.image  # Retourner l'image originale en cas d'échec


