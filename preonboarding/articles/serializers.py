from rest_framework import serializers
from .models import Article
from ..accounts.serializers import UserArticleSerializer


class ArticleSerializer(serializers.ModelSerializer):
    user = UserArticleSerializer(read_only=True)

    class Meta:
        model = Article
        fields = ('pk', 'user', 'title', 'content')


