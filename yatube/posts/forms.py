from django import forms
from django.contrib.auth import get_user_model

from posts.models import Post, Comment

User = get_user_model()


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        labels = {'group': 'Группа', 'text': 'Текст поста'}
        fields = ('text', 'group', 'image')


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        labels = {'text': 'Текст коментария'}
        fields = ('text',)
