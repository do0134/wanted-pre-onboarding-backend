from django.urls import path
from . import views


app_name = 'articles'

urlpatterns = [
    path('', views.article_list_or_create),
    path('<int:article_pk>', views.article_detail_or_update_or_delete),
]