from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('signup/', views.sign_up),
    path('login/', views.login),
]
