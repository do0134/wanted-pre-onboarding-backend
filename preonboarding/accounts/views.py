from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from argon2 import PasswordHasher
from django.http import JsonResponse
from .serializers import UserSerializer
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, TokenRefreshSerializer
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
import jwt
from preonboarding.settings import SECRET_KEY

User = get_user_model()
# Create your views here.

"""
이메일이 적합한 형식인지 확인하는 함수
@가 있는지 여부만 체크한다.
"""
def email_validate(email:str) -> (bool, dict):
    flag = False
    if "@" not in email:
        context = {
            'message' : "올바른 이메일 형식을 입력해주세요"
        }
    else:
        flag = True
        context = {}

    return flag, context

"""
비밀번호가 적합한 형식인지 확인하는 함수
8자리 이상인지만 체크한다.
"""
def password_validate(password:str) -> (bool, dict):
    flag = False
    if len(password) < 8:
        context = {
            'message' : "비밀번호는 8자리 이상이어야 합니다."
        }
    else:
        flag = True
        context = {}

    return flag, context


"""
회원가입 함수
email과 password만 받는다.

email의 경우 @가 들어갔는지 여부만 확인
password의 경우 8자리 이상인지 여부만 확인
두 경우 모두 status = 400 Bad request

만약 valid하다면, argon2알고리즘으로 비밀번호를 해싱하여 저장
이 경우 status = 201 Created
"""
@api_view(["POST"])
def sign_up(request):
    # 테스트용
    # email = request['email']
    # password = request['password']

    email = request.data['email']
    password = request.data['password']

    email_valid, email_context = email_validate(email)
    
    # email에 @가 없어 부적합하다면 메세지와 함께 400을 리턴
    if not email_valid:
        return JsonResponse(email_context,status=status.HTTP_400_BAD_REQUEST,json_dumps_params={'ensure_ascii': False})
    
    password_valid, password_context = password_validate(password)
    # 비밀번호가 8자리 미만이라면 메세지와 함께 400을 리턴
    if not password_valid:
        return JsonResponse(password_context,status=status.HTTP_400_BAD_REQUEST,json_dumps_params={'ensure_ascii': False})
        
    # 모든 데이터가 적합하다면, password를 해싱 후 저장. 201을 리턴
    else:
        crypto = PasswordHasher().hash(password)
        new_user = {
            'email' : email,
            'password' : crypto,
        }
        serializer = UserSerializer(data=new_user)
        
        if serializer.is_valid(raise_exception=True):
            user = serializer.save()
            # jwt token 접근해주기

            token = TokenObtainPairSerializer.get_token(user)
            refresh_token = str(token)
            access_token = str(token.access_token)
            context = {
                'message' : '회원가입 되었습니다.',
                'refresh_token' : refresh_token,
                'access_token' : access_token,
            }

            return JsonResponse(context,status=status.HTTP_201_CREATED,json_dumps_params={'ensure_ascii': False})
        
"""
로그인 함수

email과 password만 받는다.
email에 @가 들어갔는지 패스워드가 8자리 이상인지 확인 
실패한다면 HTTP status는 400

그리고 argon2로 해싱된 패스워드와 비교하여 적합한지 확인받는다.
실패한다면 HTTP status는 400

로그인이 성공했다면, refresh_token과 access_token을 받는다.
성공한다면 HTTP status는 200

만약 DB에 없는 user라면 HTTP status는 404
"""
@api_view(["POST"])
def login(request):
    email = request.data['email']
    password = request.data['password']

    email_valid, email_context = email_validate(email)
    # email에 @가 없어 부적합하다면 메세지와 함께 400을 리턴
    if not email_valid:
        return JsonResponse(email_context,status=status.HTTP_400_BAD_REQUEST,json_dumps_params={'ensure_ascii': False})

    password_valid, password_context = password_validate(password)
    # 비밀번호가 8자리 미만이라면 메세지와 함께 400을 리턴
    if not password_valid:
        return JsonResponse(password_context,status=status.HTTP_400_BAD_REQUEST,json_dumps_params={'ensure_ascii': False})

    # 모든 데이터가 적합하다면, password가 적합한지 확인
    account = get_object_or_404(User, email=email)


    # 적합하다면 토큰을 발급한다.
    if PasswordHasher().verify(hash=account.password, password=password):
        token = TokenObtainPairSerializer.get_token(account)
        refresh_token = str(token)
        access_token = str(token.access_token)
        context = {
            "refresh" : refresh_token,
            "access" : access_token,
        }
        response = Response(context,status=status.HTTP_200_OK)
        # access_token과 refresh_token을 쿠키에 저장
        response.set_cookie("access", access_token)
        response.set_cookie("refresh", refresh_token)
        return response
    else:
        # 아니라면 400을 반환
        context = {
        "message" : "비밀번호가 틀렸습니다.",
        }
        
        return JsonResponse(context,status=status.HTTP_400_BAD_REQUEST,json_dumps_params={'ensure_ascii': False})

"""
jwt를 디코딩하여 User 데이터를 가져오는 함수
reqeust.COOKIES dict를 arg로 받는다.

jwt를 디코딩하여 user_pk를 return

refresh token 구현은 아직
"""
def jwt_decode(cookies_dict):
    try:
        access_token = cookies_dict["access"]
        payload = jwt.decode(access_token, SECRET_KEY, algorithms=['HS256'])
        pk = payload.get('user_id')
        return pk
    except (jwt.exceptions.ExpiredSignatureError):
        refresh_token = cookies_dict["refresh"]
        
        data = {
            "refresh": refresh_token,
        }

        serializer = TokenRefreshSerializer(data=data)
        if serializer.is_valid(raise_exception=True):
            print(serializer.data)
