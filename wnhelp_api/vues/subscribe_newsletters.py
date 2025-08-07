from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view
from utils.functions import check_validate_email, response_exception, send_mail_template
from wnhelp_api.models.subscribe_newsletters import SubscriberNewsletter, SubscriberNewsletterSerializer 


@api_view(["POST", "PUT"])
def subscribe_newsletters(request):
    try:
        email = request.data.get("email")
        if not email:
            return Response(
                {"message": "Veuillez entrer une adresse email"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if not check_validate_email(email):
            return Response(
                {"message": "Veuillez entrer une adresse email valide"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        if SubscriberNewsletter.objects.filter(email=email).exists():
            # Envoyer un email de confirmation à l'utilisateur
            subject = "Confirmation de votre abonnement à notre newsletter"
            message = """
                <p>Bonjour,</p>
                <p>Merci pour votre abonnement à notre <strong>newsletter</strong> ! 🎉</p>
                <p>Désormais, vous recevrez régulièrement nos dernières <strong>actualités et rapports</strong> directement dans votre boîte mail.</p>
                <p>Si ce message ne vous était pas destiné ou si vous vous êtes inscrit par erreur, vous pouvez vous désabonner à tout moment via le lien en bas de nos emails.</p>
                <p style="margin-top: 32px;">Cordialement,<br>
                L’équipe <strong>World Needs and Help</strong></p>
            """
            send_mail_template(subject, message, [email])
            return Response(
                {"message": "Abonnement effectué avec succès"},
                status=status.HTTP_201_CREATED,
            )

        subscriber_data = {"email": email}
        message_form = SubscriberNewsletterSerializer(data=subscriber_data)
        if message_form.is_valid():
            message_form.save()

            # Envoyer un email de confirmation à l'utilisateur
            subject = "Confirmation de votre abonnement à notre newsletter"
            message = """
                <p>Bonjour,</p>
                <p>Merci pour votre abonnement à notre <strong>newsletter</strong> ! 🎉</p>
                <p>Désormais, vous recevrez régulièrement nos dernières <strong>actualités et rapports</strong> directement dans votre boîte mail.</p>
                <p>Si ce message ne vous était pas destiné ou si vous vous êtes inscrit par erreur, vous pouvez vous désabonner à tout moment via le lien en bas de nos emails.</p>
                <p style="margin-top: 32px;">Cordialement,<br>
                L’équipe <strong>World Needs and Help</strong></p>
            """
            send_mail_template(subject, message, [email])

            return Response(
                {"message": "Abonnement effectué avec succès"},
                status=status.HTTP_201_CREATED,
            )
        else:
            return Response(
                {
                    "message": "Veuillez vérifier votre message",
                    "error": message_form.errors,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
    except Exception as e:
        return response_exception(e)




