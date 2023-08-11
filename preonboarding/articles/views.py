
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

# 제목이 비워져있지 않은지 확인
def article_title_valid(title:str) -> bool:
    title = title.strip()
    return bool(title)
# 내용이 비워져있지 않은지 확인
def article_content_valid(content:str) -> bool:
    content = content.strip()
    return bool(content)

"""
get 요청이라면 
page를 받을 수도 있고, 안 받을 수도 있다. 안 받는 다면 디폴트 페이지는 1
page: int

post 요청일 때,
title과 content를 받는다.
title: str
content: str
"""
@api_view(["GET", "POST"])
def article_list_or_create(request):
    # article 전체 list를 받아오는 함수
    # page가 request body에 있다면 받고 없다면 디폴트 페이지 1
    def article_list():
        articles = Article.objects.all().order_by('-pk')
        page = int(request.GET.get('page') or 1)
        paginator = Paginator(articles, 5)
        article_list = paginator.get_page(page)
        serializer = ArticleSerializer(article_list,many=True)

        return Response(serializer.data,status=status.HTTP_200_OK)

    # article을 create하는 함수
    # 먼저 jwt를 통해 유효한 사용자인지 확인한다. 
    # 만약 유효한 사용자라면 article의 title과 content가 채워져 있는지 확인한다.
    # 모두 채워져 있다면 저장하고 201 status 반환
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
                return Response(status=status.HTTP_201_CREATED)
            
            return Response(status=status.HTTP_400_BAD_REQUEST)
    
    if request.method == "GET":
        return article_list()
    elif request.method == "POST":
        return article_create()
    

"""
공통적으로 path parameter로 article_pk를 받는다.
article_pk: int

get 요청일 때 추가로 데이터를 받지 않는다. 

put 요청일 때  
body에 title, content를 받는다.

body
title: str
content: str

delete 요청일 때 추가로 데이터를 받지 않는다.
"""
@api_view(['GET', 'PUT', 'DELETE'])
def article_detail_or_update_or_delete(request, article_pk):
    # path parameter로 받은 article_pk로 article data를 가져온다.
    article = get_object_or_404(Article, pk=article_pk)
    
    # COOKIES에 있는 jwt로 User 유효성 검증
    def authenticate_user():
        user_pk = jwt_decode(request.COOKIES)
        user = get_object_or_404(User, pk=user_pk)
        if not user.is_authenticated:
            return 0
        return user_pk

    # user_pk로 article.user가 같은지 검증
    def check_creator(user_pk):
        user = get_object_or_404(User, pk=user_pk)
        return user == article.user

    # "GET"요청일 때, article 데이터를 그대로 return 해준다.
    def article_detail():
        serialzier = ArticleSerializer(article)
        return Response(serialzier.data, status=status.HTTP_200_OK)

    # "PUT" 요청일 때, User 유효성을 검증하고, article 작성한 유저인지 확인
    # User에 대한 검증이 끝났다면, data를 수정하고 수정한 데이터를 return
    def update_article():
        user_pk = authenticate_user()
        user = get_object_or_404(User, pk=user_pk)
        if check_creator(user_pk):
            serializer = ArticleSerializer(instance=article, data=request.data)
            if serializer.is_valid(raise_exception=True):
                serializer.save(user=user)
                return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    # "DELETE" 요청이라면 User 유효성과 article.user와 User가 같은지 확인하고
    # User 검증이 끝났다면 삭제
    def delete_article():
        user_pk = authenticate_user()
        if check_creator(user_pk):
            article.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    if request.method == 'GET':
        return article_detail()
    elif request.method == 'PUT':
        return update_article()
    elif request.method == 'DELETE':
        return delete_article()
