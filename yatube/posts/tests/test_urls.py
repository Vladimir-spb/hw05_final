from http import HTTPStatus
from django.contrib.auth import get_user_model
from django.test import TestCase, Client

from ..models import Group, Post

User = get_user_model()


class StaticURLTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='HasNoName')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.group = Group.objects.create(
            title='Тестовая группа',
            slug='TESTSLUG',
            description='Тестовое описание',
        )
        self.post = Post.objects.create(
            author=self.user,
            text='Тестовая пост',
        )

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            '/': 'posts/index.html',
            '/create/': 'posts/create_post.html',
            f'/group/{self.group.slug}/': 'posts/group_list.html',
            f'/posts/{self.post.pk}/': 'posts/post_detail.html',
            f'/profile/{self.user}/': 'posts/profile.html',
            f'/posts/{self.post.pk}/edit/': 'posts/create_post.html'
        }
        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_urls_list_guest_200(self):
        """Проверка доступности адресов для гостя."""
        url_list = [
            '/',
            f'/group/{self.group.slug}/',
            f'/profile/{self.user}/',
            f'/posts/{self.post.pk}/'
        ]
        for test_url in url_list:
            response = self.client.get(test_url)
            self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_urls_list_guest(self):
        """Проверка редиректа для гостя."""
        url_list = [
            '/create/',
            f'/posts/{self.post.pk}/edit/',
            f'/posts/{self.post.pk}/comment/'
        ]
        for test_url in url_list:
            response = self.client.get(test_url)
            self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_new_page_not_login_user(self):
        """Проверка страницы 404 для гостя."""
        response = self.client.get('/graf')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_new_page_not_login_user(self):
        """Проверка страницы 404 для авторизованного."""
        response = self.authorized_client.get('/knyaz')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_urls_list(self):
        """Проверка доступности адресов для авторизованного."""
        url_list = [
            '/',
            '/create/',
            f'/group/{self.group.slug}/',
            f'/posts/{self.post.pk}/',
            f'/profile/{self.user}/',
            f'/posts/{self.post.pk}/edit/'
        ]
        for test_url in url_list:
            response = self.authorized_client.get(test_url)
            self.assertEqual(response.status_code, HTTPStatus.OK)
