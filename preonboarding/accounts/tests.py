from django.test import TestCase
from .serializers import UserSerializer
from argon2 import PasswordHasher
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
# Create your tests here.
User = get_user_model()

class SignupTest(TestCase):
    # email, password 유효성 검사는 따로 함수를 만들면 좋을 거 같음
    def signup(self, data):
        email = data['email']
        password = data['password']
        if "@" not in email:
            return 'email'
        elif len(password) < 8:
            return 'password'
        else:
            return 'success'
        
    def test_signup_valid(self):
        data = {"email" : "1234@naver.com", "password" : "12345678"}
        response = self.signup(data)
        self.assertEqual(response, 'success')

    def test_email_failed(self):
        data = {"email" : "1234naver.com", "password" : "12345678"}
        response = self.signup(data)
        self.assertEqual(response, 'email')
        
    def test_password_failed(self):
        data = {"email" : "1234@naver.com", "password" : "1234567"}
        response = self.signup(data)
        self.assertEqual(response, 'password')

    def test_signup_total(self):
        data = {"email" : "dodo@naver.com", "password" : "12345678"}

        cryto = PasswordHasher().hash(data['password'])
        new_data = {'email' : data['email'], 'password' : cryto}

        serializer = UserSerializer(data=new_data)

        if serializer.is_valid(raise_exception=True):
            user = serializer.save()
            self.assertTrue(PasswordHasher().verify(hash=user.password, password=data['password']))
            user.delete()
        else:
            self.assertFalse(1)
        
class LoginTest(TestCase):
    email = "dodo@naver.com"
    password = "abcdefghijklmno"
    crypto = PasswordHasher().hash(password)
    new_data = {'email' : email, 'password' : crypto}

    def setup(self): 
        serializer = UserSerializer(data=self.new_data)
        if serializer.is_valid(raise_exception=True):
            user = serializer.save()


    def test_login(self):
        self.setup()
        user = get_object_or_404(User, email=self.email)
        self.assertTrue(PasswordHasher().verify(hash=self.crypto,password=self.password))
        user.delete()
    
    def test_login_withJWT(self):
        self.setup()
        user = get_object_or_404(User, email=self.email)
        if PasswordHasher().verify(hash=self.crypto, password=self.password):
            token = TokenObtainPairSerializer.get_token(user)
            refresh_token = str(token)
            access_token = str(token.access_token)
            
            context = {
                "refresh_token" : refresh_token,
                "access_token" : access_token,
            }
            # print(context['access_token'], context['refresh_token'])
            self.assertTrue(context)
            user.delete()