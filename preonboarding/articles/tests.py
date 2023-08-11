from django.test import TestCase
from .models import Article
from django.core.paginator import Paginator
from .serializers import ArticleSerializer
from django.contrib.auth import get_user_model
from accounts.serializers import UserSerializer
from django.shortcuts import get_object_or_404
# Create your tests here.

User = get_user_model()

class ArticleTest(TestCase):
    # 테스트 용 유저 생성
    def create_user(self):
        data = {"email" : "wantedwant@naver.com", "password" : "12345678"}
        serializer = UserSerializer(data=data)

        if serializer.is_valid():
            user = serializer.save()
            return user
        else:
            return 1
        

    # 테스트용 게시글 생성 함수
    def article_create(self, user_pk):
        # create_user로 만들어진 유저를 받은 다음,
        user = get_object_or_404(User, pk=user_pk)
        # 테스트 데이터를 넣고
        data = {
            "title" : "1234",
            "content" : "1234",
        }
       # 저장
        serializer = ArticleSerializer(data=data)
        # valid 데이터라면 저장
        if serializer.is_valid(raise_exception=True):
            new_data = serializer.save(user=user)
        
        # 만약 article을 조회할 수 있다면 OK 아니면 AssertionError가 난다.
        try : 
            article = Article.objects.get(pk=new_data.pk)
        except : 
            raise AssertionError
        
    
    def article_valid(self, data):
        if not data["title"]:
            return "No Title"
        elif not data["content"]:
            return "No Content"
        return "Valid"

    # 게시글 리스트 페이지네이션 테스트
    def test_article_list(self):
        # 유저 생성
        test_user = self.create_user()
        user_pk = test_user.pk

        # 게시글을 총 몇 번 생성할지
        num = 31
        # 한 페이지에 게시글을 몇 개 보여줄지
        article_cnt = 5
        # num만큼 게시글 생성
        try: 
            for _ in range(num):
                self.article_create(user_pk)
        except:
            raise AssertionError
        
        # 생성된 게시글 목록을 가져오고
        articles = Article.objects.all().order_by('-pk')
        paginator = Paginator(articles, article_cnt)
        # max_len은 총 게시글 // 한 페이지당 보이는 게시글 + 1
        max_len = num // article_cnt + 1
        # 반복문을 통해서 페이지마다 정확한 수의 게시글을 보여주는지 확인
        for i in range(1,max_len):
            page = i
            article_list = paginator.get_page(page)
            serializer = ArticleSerializer(article_list,many=True)

            if i != max_len:
                self.assertTrue(len(serializer.data) == article_cnt)
            # 마지막 페이지만 예외처리 해준다.
            else:
                self.assertTrue(len(serializer.data) == num%article_cnt)

    
    def test_article_create_success(self):
        test_user = self.create_user()
        user = get_object_or_404(User, pk=test_user.pk)
        data = {
            "title" : "안녕하세요!",
            "content" : "좋은 아침입니다!"
        }
        serializer = ArticleSerializer(data=data)
        if serializer.is_valid(raise_exception=True):
            article = serializer.save(user=user)
            self.assertEquals(article.title == data["title"], article.content == data["content"])

    def test_article_title_failed(self):

        title_data = {
            "title" : "             ",
            "content": "1234 ",
        }

        title_data["title"] = title_data["title"].strip()

        msg = self.article_valid(title_data)
        self.assertEqual(msg, "No Title")

    def test_article_content_failed(self):
        content_data = {
            "title": "1234",
            "content": "                               "
        }
        content_data["content"] = content_data["content"].strip()
        msg = self.article_valid(content_data)
        self.assertEqual(msg, "No Content")
       
