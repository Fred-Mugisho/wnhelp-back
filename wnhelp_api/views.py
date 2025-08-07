from users_manager.decorateurs import *
from .models.articles import *
from .models.rapports import *
from .models.commentaires import *
from .models.contact_message import *
from .models.subscribe_newsletters import *
from .models.media import *
from .models.partenaires import *
from .models.jobs import *


@api_view(["POST", "PUT"])
def commenter_article(request, slug):
    try:
        article = Article.objects.filter(slug=slug).first()
        if not article:
            return Response(
                {"message": "Article n'existe pas"}, status=status.HTTP_404_NOT_FOUND
            )

        name = request.data.get("name")
        email = request.data.get("email")
        content = request.data.get("content")

        comment_data = {
            "article": article.pk,
            "name": name,
            "email": email,
            "content": content,
        }
        comment_form = CommentSerializer(data=comment_data)
        if comment_form.is_valid():
            comment = comment_form.save()
            serializer_data = CommentSerializer(comment).data
            return Response(serializer_data, status=status.HTTP_201_CREATED)
        else:
            return Response(
                {
                    "message": "Veuillez vérifier votre commentaire",
                    "error": comment_form.errors,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
    except Exception as e:
        return response_exception(e)



@api_view(["POST", "PUT"])
def contactez_nous(request):
    try:
        name = request.data.get("name")
        email = request.data.get("email")
        subject = request.data.get("subject")
        message = request.data.get("message")

        message_data = {
            "name": name,
            "email": email,
            "subject": subject,
            "message": message,
        }
        message_form = ContactMessageSerializer(data=message_data)
        if message_form.is_valid():
            message_form.save()

            # Envoyer un email de notification
            subject = "Nouveau message de contact sur le site"
            
            html_message = message.replace('\n', '<br>')
            message = f"""
                <p>Bonjour,</p>
                <p>Vous avez reçu un <strong>nouveau message de contact</strong> via le site web de <strong>World Needs and Help</strong>.</p>
                <p><strong>Expéditeur :</strong> {name}<br>
                <strong>Email :</strong> <a href="mailto:{email}">{email}</a></p>
                <p><strong>Message :</strong></p>
                <blockquote style="border-left: 4px solid #296638; padding-left: 12px; color: #333;">
                    {html_message}
                </blockquote>
                <p style="margin-top: 32px;">Veuillez répondre dans les meilleurs délais.</p>
                <p>Cordialement,<br>
                L'équipe <strong>World Needs and Help</strong></p>
            """
            destinateurs = ["frederick@wnhelp.org"]
            # destinateurs = ['admin@wnhelp.org', 'info@wnhelp.org', 'wnh@wnhelp.org']
            send_mail_template(subject, message, destinateurs)

            # Envoyer un email de confirmation à l'utilisateur
            subject = "Confirmation de réception de votre message"
            message = f"""
                <p>Bonjour <strong>{name}</strong>,</p>
                <p>Merci pour votre message. Nous l’avons bien reçu et vous contacterons dans les plus brefs délais.</p>
                <p>En attendant, vous pouvez consulter notre site pour en savoir plus sur nos actions et nos domaines d’intervention.</p>
                <p>Cordialement,<br>
                L'équipe <strong>World Needs and Help</strong></p>
            """
            send_mail_template(subject, message, [email])

            return Response(
                {"message": "Message envoyé avec succès"},
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


@api_view(["GET"])
def gallerie(request):
    try:
        page = request.GET.get("page", 1)
        limit_page = request.GET.get("limit_page", 12)
        images = GallerieImage.objects.all()
        serializer_data = GallerieImageSerializer(images, many=True).data
        paginate_data = KBPaginator(serializer_data, limit_page).get_page(page)
        return Response(paginate_data, status=status.HTTP_200_OK)
    except Exception as e:
        return response_exception(e)


@api_view(["GET"])
def offres_emploi(request, id=None):
    try:
        if id:
            offre = JobOffer.objects.get(id=id)

            offre.counter_views += 1
            offre.save()

            serializer_data = JobOfferSerializer(offre).data
            return Response(serializer_data, status=status.HTTP_200_OK)

        offres = JobOffer.objects.filter(
            actif=True, date_expiration__gte=timezone.now()
        ).order_by("-date_publication")

        page = request.GET.get("page", 1)
        limit_page = request.GET.get("limit_page", 12)
        search_content = request.GET.get("search_content")

        if search_content:
            offres = offres.filter(
                Q(titre__icontains=search_content)
                | Q(description__icontains=search_content)
                | Q(profil_recherche__icontains=search_content)
                | Q(type_contrat__icontains=search_content)
                | Q(lieu__icontains=search_content)
            )

        page_number = int(page) if is_convertible_to_int(page) else 1
        limit_page_number = int(limit_page) if is_convertible_to_int(limit_page) else 12

        serializer_data = JobOfferSerializer(offres, many=True).data

        offres_pagination = KBPaginator(serializer_data, limit_page_number).get_page(
            page_number
        )
        return Response(offres_pagination, status=status.HTTP_200_OK)
    except JobOffer.DoesNotExist:
        return Response(
            {"message": f"Offre d'emploi avec l'id {id} n'existe pas"},
            status=status.HTTP_404_NOT_FOUND,
        )
    except Exception as e:
        return response_exception(e)



@api_view(["GET"])
def get_partenaires(request):
    try:
        partenaires = Partenaires.objects.all().order_by('-joined_at')
        serializer_data = PartenairesSerializer(partenaires, many=True).data
        return Response(serializer_data, status=status.HTTP_200_OK)
    except Exception as e:
        return response_exception(e)







