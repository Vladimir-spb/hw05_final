from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Group, Post

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        """Создание записи в БД"""
        cls.user = User.objects.create(
            username='auth'
        )
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='TESTSLUG',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый текст длинной более чем 15 символов',
        )
        cls.image = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )

    def test_models_have_correct_post(self):
        """Проверяем, что у моделей корректно работает __str__."""
        post1 = PostModelTest.post
        object_name = post1.text
        self.assertEqual(object_name[:15], str(post1))

    def test_models_have_correct_group(self):
        """Проверяем, что у моделей корректно работает __str__."""
        group1 = PostModelTest.group
        object_name = group1.title
        self.assertEqual(object_name, str(group1))
