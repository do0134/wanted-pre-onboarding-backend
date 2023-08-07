from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from argon2 import PasswordHasher
from django.http import JsonResponse
from .serializers import UserSerializer

# Create your views here.
@api_view(["Post"])
def sign_up(request):
    email = request.email
    password = request.password

    if "@" not in email:
        context = {
            'message' : "올바른 이메일 형식을 입력해주세요"
        }
        return JsonResponse(context)
    elif len(password) < 8:
        context = {
            'message' : "비밀번호는 8자리 이상이어야 합니다."
        }
        return JsonResponse(context)
    else:
        crypto = PasswordHasher.hash(password)
        new_user = {
            'email' : email,
            'password' : crypto,
        }
        serializer = UserSerializer(data=new_user)
        
        if serializer.is_valid(raise_exception=True):
            return Response(serializer.data, status=status.HTTP_201_CREATED)
