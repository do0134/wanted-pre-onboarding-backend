
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Article
from .serializers import ArticleSerializer
from django.shortcuts import get_object_or_404
from django.core.paginator import Paginator
from accounts.views import jwt_decode
from django.contrib.auth import get_user_model

# Create your views here.

User = get_user_model()

def article_title_valid(title:str) -> bool:
    title = title.strip()
    
    return bool(title)

def article_content_valid(content:str) -> bool:
    content = content.strip()
    return bool(content)


@api_view(["GET", "POST"])
def article_list_or_create(request):
    def article_list():
        articles = Article.objects.all().order_by('-pk')
        page = int(request.GET.get('page') or 1)
        paginator = Paginator(articles, 5)
        article_list = paginator.get_page(page)
        serializer = ArticleSerializer(article_list,many=True)

        return Response(serializer.data,status=status.HTTP_200_OK)

    def article_create():
        user_pk = jwt_decode(request.COOKIES)
        user = get_object_or_404(User, pk=user_pk)
        if not user.is_authenticated:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        
        title = request.data['title']
        content = request.data['content']
        if not article_title_valid(title):
            context = {
                'message' : '제목을 입력해주세요'
            }
            return Response(context, status=status.HTTP_400_BAD_REQUEST)
        elif not article_content_valid(content):
            context = {
                'message' : '내용을 입력해주세요'
            }
            return Response(context, status=status.HTTP_400_BAD_REQUEST)
        
        else:
            data = {
                "title" : title,
                "content" : content
            }
            serializer = ArticleSerializer(data=data)
            if serializer.is_valid(raise_exception=True):
                serializer.save(user=user)
                return Response(status=status.HTTP_200_OK)
            
            return Response(status=status.HTTP_400_BAD_REQUEST)
    
    if request.method == "GET":
        return article_list()
    elif request.method == "POST":
        return article_create()
    


@api_view(['GET', 'PUT', 'DELETE'])
def article_detail_or_update_or_delete(request, article_pk):
    pass