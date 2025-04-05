from users_manager.decorateurs import *
from .models.articles import *
from .models.rapports import *
from .models.commentaires import *
from .models.contact_message import *
from .models.subscribe_newsletters import *
from .models.media import *
from .models.partenaires import *

@api_view(['GET'])
def get_categories(request):
    try:
        categories = Categorie.objects.all().order_by('name')
        serializer_data = CategorieSerializer(categories, many=True).data
        return Response(serializer_data, status=status.HTTP_200_OK)
    except Exception as e:
        return response_exception(e)

@api_view(['GET'])
def get_articles(request):
    try:
        articles = Article.objects.filter(status='published').order_by('-id')
        search_content = request.GET.get("search_content")
        page = request.GET.get("page", 1)
        limit_page = request.GET.get("limit_page", 15)
        categories_id = request.GET.get("categories", '').split(",")
        categories = [int(cat) for cat in categories_id if is_convertible_to_int(cat)]
                
        if search_content:
            articles = articles.filter(
                Q(title__icontains=search_content) |
                Q(contenu__icontains=search_content)
            )
        if categories:
            articles = articles.filter(categorie__id__in=categories)
        
        serializer_data = ArticleSerializer(articles, many=True).data
        pagination = KBPaginator(serializer_data, limit_page).get_page(page)
        return Response(pagination, status=status.HTTP_200_OK)
    except Exception as e:
        return response_exception(e)
    
@api_view(['GET'])
def get_recents_articles(request):
    try:
        articles = Article.objects.filter(status='published').order_by('-id')[:3]
        
        serializer_data = ArticleSerializer(articles, many=True).data
        return Response(serializer_data, status=status.HTTP_200_OK)
    except Exception as e:
        return response_exception(e)
    
@api_view(['GET'])
def get_article(request, slug):
    try:
        article = Article.objects.filter(slug=slug, status='published').first()
        if not article:
            return Response({"message": "Article n'existe pas"}, status=status.HTTP_404_NOT_FOUND)
        
        autres_article = Article.objects.filter(status='published').exclude(slug=slug).order_by('-id')[:3]
        autres_article_serializer = OthersArticleSerializer(autres_article, many=True).data
        
        serializer_data = DetailsArticleSerializer(article).data
        serializer_data['autres_articles'] = autres_article_serializer
        return Response(serializer_data, status=status.HTTP_200_OK)
    except Exception as e:
        return response_exception(e)
    
@api_view(['POST', 'PUT'])
def commenter_article(request, slug):
    try:
        article = Article.objects.filter(slug=slug).first()
        if not article:
            return Response({"message": "Article n'existe pas"}, status=status.HTTP_404_NOT_FOUND)
        
        name = request.data.get('name')
        email = request.data.get('email')
        content = request.data.get('content')
        
        comment_data = {
            'article': article.pk,
            'name': name,
            'email': email,
            'content': content
        }
        comment_form = CommentSerializer(data=comment_data)
        if comment_form.is_valid():
            comment = comment_form.save()
            serializer_data = CommentSerializer(comment).data
            return Response(serializer_data, status=status.HTTP_201_CREATED)
        else:
            return Response({"message": "Veuillez vérifier votre commentaire", "error": comment_form.errors}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return response_exception(e)
    
@api_view(['GET'])
def get_rapports(request):
    try:
        rapports = Rapport.objects.all().order_by('-id')
        search_content = request.GET.get("search_content")
        page = request.GET.get("page", 1)
        limit_page = request.GET.get("limit_page", 15)
                
        if search_content:
            rapports = rapports.filter(
                Q(title__icontains=search_content) |
                Q(contenu__icontains=search_content)
            )
        
        serializer_data = RapportSerializer(rapports, many=True).data
        pagination = KBPaginator(serializer_data, limit_page).get_page(page)
        return Response(pagination, status=status.HTTP_200_OK)
    except Exception as e:
        return response_exception(e)
    
@api_view(['GET'])
def get_rapport(request, slug):
    try:
        rapport = Rapport.objects.filter(slug=slug).first()
        if not rapport:
            return Response({"message": "Rapport n'existe pas"}, status=status.HTTP_404_NOT_FOUND)
        
        autres_rapport = Rapport.objects.all().exclude(slug=slug).order_by('-id')[:3]
        autres_rapport_serializer = OthersRapportSerializer(autres_rapport, many=True).data
        
        serializer_data = RapportSerializer(rapport).data
        serializer_data['autres_rapports'] = autres_rapport_serializer
        return Response(serializer_data, status=status.HTTP_200_OK)
    except Exception as e:
        return response_exception(e)
    
@api_view(['POST', 'PUT'])
def contactez_nous(request):
    try:
        name = request.data.get('name')
        email = request.data.get('email')
        subject = request.data.get('subject')
        message = request.data.get('message')
        
        message_data = {
            'name': name,
            'email': email,
            'subject': subject,
            'message': message
        }
        message_form = ContactMessageSerializer(data=message_data)
        if message_form.is_valid():
            message_form.save()
            
            # Envoyer un email de notification
            subject = "Nouveau message de contact sur le site"
            message = f"Vous avez reçu un nouveau message de contact de {name} ({email}):\n\n{message}"
            destinateurs = ['frederick@wnhelp.org']
            # destinateurs = ['admin@wnhelp.org', 'info@wnhelp.org', 'wnh@wnhelp.org']
            send_mail_template(subject, message, destinateurs)
            
            # Envoyer un email de confirmation à l'utilisateur
            subject = "Confirmation de réception de votre message"
            message = f"Bonjour {name},\n\nMerci pour votre message. Nous vous contacterons bientôt.\n\nCordialement,\nL'équipe WNHelp"
            send_mail_template(subject, message, [email])
            
            return Response({"message": "Message envoyé avec succès"}, status=status.HTTP_201_CREATED)
        else:
            return Response({"message": "Veuillez vérifier votre message", "error": message_form.errors}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return response_exception(e)
    
@api_view(['POST', 'PUT'])
def subscribe_newsletters(request):
    try:
        email = request.data.get('email')
        if not email:
            return Response({"message": "Veuillez entrer une adresse email"}, status=status.HTTP_400_BAD_REQUEST)
        if not check_validate_email(email):
            return Response({"message": "Veuillez entrer une adresse email valide"}, status=status.HTTP_400_BAD_REQUEST)
        if SubscriberNewsletter.objects.filter(email=email).exists():
            # Envoyer un email de confirmation à l'utilisateur
            subject = "Confirmation de votre abonnement à notre newsletter"
            message = f"Bonjour,\n\nMerci pour votre abonnement à notre newsletter. Vous recevrez bientôt nos dernières actualités.\n\nCordialement,\nL'équipe WNHelp"
            send_mail_template(subject, message, [email])
            return Response({"message": "Abonnement effectué avec succès"}, status=status.HTTP_201_CREATED)
        
        subscriber_data = {
            'email': email
        }
        message_form = SubscriberNewsletterSerializer(data=subscriber_data)
        if message_form.is_valid():
            message_form.save()
            
            # Envoyer un email de confirmation à l'utilisateur
            subject = "Confirmation de votre abonnement à notre newsletter"
            message = f"Bonjour,\n\nMerci pour votre abonnement à notre newsletter. Vous recevrez bientôt nos dernières actualités.\n\nCordialement,\nL'équipe WNHelp"
            send_mail_template(subject, message, [email])
            
            return Response({"message": "Abonnement effectué avec succès"}, status=status.HTTP_201_CREATED)
        else:
            return Response({"message": "Veuillez vérifier votre message", "error": message_form.errors}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return response_exception(e)
    
@api_view(['GET'])
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
    
@api_view(['GET'])
def get_partenaires(request):
    try:
        partenaires = Partenaires.objects.all()
        serializer_data = PartenairesSerializer(partenaires, many=True).data
        return Response(serializer_data, status=status.HTTP_200_OK)
    except Exception as e:
        return response_exception(e)