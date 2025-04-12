# wnhelp_api/tasks.py
import os
import logging
from django.conf import settings
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from celery import shared_task

logger = logging.getLogger(__name__)

@shared_task
def send_mail_template_async(subject: str, message: str, destinateurs: list, file_attach: str = None):
    try:
        if not destinateurs:
            raise ValueError("La liste des destinataires ne peut pas être vide.")

        objet = subject
        from_email = settings.EMAIL_HOST_USER
        subject = f"WNHelp - {objet}"

        context = {
            'message': message,
            'objet': objet,
        }
        html_render = render_to_string('mail_template.html', context)

        to_send = EmailMultiAlternatives(subject, "", from_email, destinateurs)
        to_send.attach_alternative(html_render, "text/html")

        # Attacher un fichier si fourni
        if file_attach:
            attach_file_path = os.path.join(settings.BASE_DIR, file_attach)
            if os.path.exists(attach_file_path):
                to_send.attach_file(attach_file_path)
            else:
                logger.warning(f"Le fichier attaché {attach_file_path} n'a pas été trouvé.")

        to_send.send()

    except Exception as e:
        logger.error(f"Erreur lors de l'envoi de l'email (asynchrone) : {e}")
        print(f"Erreur EMAIL (async) --> {e}")
