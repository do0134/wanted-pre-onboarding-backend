from rest_framework import serializers
from .models import Article
from django.contrib.auth import get_user_model


User = get_user_model()


class ArticleSerializer(serializers.ModelSerializer):
    class UserSerializer(serializers.ModelSerializer):
        class Meta:
            model = User
            fields = ('pk', 'email')
    
    user = UserSerializer(read_only=True)

    class Meta:
        model = Article
        fields = ('pk', 'user', 'title', 'content')


