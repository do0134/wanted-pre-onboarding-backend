
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Article
from .serializers import ArticleSerializer
from django.shortcuts import get_object_or_404
from django.core.paginator import Paginator
# Create your views here.



@api_view(["GET", "POST"])
def article_list_or_create(request):
    def article_list():
        articles = Article.objects.all()
        page = int(request.GET.get('page') or 1)
        paginator = Paginator(articles, 10)
        article_list = paginator.get_page(page)
        context = {
            "article_list" : article_list
        }

        return Response(context,status=status.HTTP_200_OK)

    def article_create():
        
        pass
    
    if request.method == "GET":
        return article_list()
    elif request.method == "POST":
        return article_create()
    

@api_view(['GET', 'PUT', 'DELETE'])
def article_detail_or_update_or_delete(request, article_pk):
    article = get_object_or_404(Article, pk=article_pk)

    def article_detail():
        serializer = ArticleSerializer(article)
        return Response(serializer.data)

    def update_article():
        if request.user == article.user:
            serializer = ArticleSerializer(instance=article, data=request.data)
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                return Response(serializer.data)

    def delete_article():
        if request.user == article.user:
            article.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    if request.method == 'GET':
        return article_detail()
    elif request.method == 'PUT':
        if request.user == article.user:
            return update_article()
    elif request.method == 'DELETE':
        if request.user == article.user:
            return delete_article()
   