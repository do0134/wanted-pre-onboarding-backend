
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
        articles = Article.objects.all().order_by('-pk')
        page = int(request.GET.get('page') or 1)
        paginator = Paginator(articles, 5)
        article_list = paginator.get_page(page)
        serializer = ArticleSerializer(article_list,many=True)

        return Response(serializer.data,status=status.HTTP_200_OK)

    def article_create():
        pass
    
    if request.method == "GET":
        return article_list()
    elif request.method == "POST":
        return article_create()
    


@api_view(['GET', 'PUT', 'DELETE'])
def article_detail_or_update_or_delete(request, article_pk):
    pass