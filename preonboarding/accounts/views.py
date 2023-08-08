from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from argon2 import PasswordHasher
from django.http import JsonResponse
from .serializers import UserSerializer

# Create your views here.

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
    
    # email에 @가 없어 부적합하다면 메세지와 함께 400을 리턴
    if "@" not in email:
        context = {
            'message' : "올바른 이메일 형식을 입력해주세요"
        }
        return JsonResponse(context,status=status.HTTP_400_BAD_REQUEST,json_dumps_params={'ensure_ascii': False})
    # 비밀번호가 8자리 미만이라면 메세지와 함께 400을 리턴
    elif len(password) < 8:
        context = {
            'message' : "비밀번호는 8자리 이상이어야 합니다."
        }
        return JsonResponse(context,status=status.HTTP_400_BAD_REQUEST,json_dumps_params={'ensure_ascii': False})
    # 모든 데이터가 적합하다면, password를 해싱 후 저장. 201을 리턴
    else:
        crypto = PasswordHasher().hash(password)
        new_user = {
            'email' : email,
            'password' : crypto,
        }
        serializer = UserSerializer(data=new_user)
        
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            context = {
                'message' : '회원가입 되었습니다.'
            }
            return JsonResponse(context,status=status.HTTP_201_CREATED,json_dumps_params={'ensure_ascii': False})
        

