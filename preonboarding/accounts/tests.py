from django.test import TestCase
from .views import sign_up
import json
from .models import User
from django.shortcuts import get_object_or_404
# Create your tests here.

class SignupTest(TestCase):
    def test_signup_success(self):
        data = '{"email" : "do0134@naver.com", "password" : "12345678"}'
        response = sign_up(json.loads(data))
        self.assertEqual(response.status_code, 201)

    def test_email_failed(self):
        data = '{"email" : "do0134naver.com", "password" : "12345678"}'
        response = sign_up(json.loads(data))
        self.assertEqual(response.status_code, 400)
        
    def test_password_failed(self):
        data = '{"email" : "do0134naver.com", "password" : "1234567"}'
        response = sign_up(json.loads(data))
        print(response)
        self.assertEqual(response.status_code, 400)