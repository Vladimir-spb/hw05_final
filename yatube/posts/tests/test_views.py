from django.core.cache import cache
from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django import forms

from ..models import Group, Post, Follow

User = get_user_model()


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='auth')
        cls.authorized__author_client = Client()
        cls.authorized__author_client.force_login(cls.author)
        cls.group = Group.objects.create(
            title='тестовая группа',
            slug='TESTSLUG',
            description='тестовая группа',
        )
        for i in range(13):
            author = cls.author
            group = cls.group
            cls.post = Post.objects.create(
                author=author,
                text=f'Текст {i}',
                group=group)

    def test_first_page_paginator(self):
        """Тест пагинатора на первой странице PAGES = 10"""
        templates_pages_names = {
            reverse('posts:home'): settings.PAGES,
            reverse('posts:group_posts', kwargs={'slug': self.group.slug}):
            settings.PAGES,
            reverse('posts:profile', kwargs={'username': self.author}):
            settings.PAGES,
        }
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.client.get(reverse_name)
                self.assertEqual(len(response.context['page_obj']), template)

    def test_second_page_paginator(self):
        """Тест пагинатора на второй странице остаток"""
        count_post = Post.objects.count() - settings.PAGES
        templates_pages_names = {
            reverse('posts:home') + '?page=2': count_post,
            reverse('posts:group_posts', kwargs={'slug': self.group.slug})
            + '?page=2': count_post,
            reverse('posts:profile', kwargs={'username': self.author})
            + '?page=2': count_post,
        }
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.client.get(reverse_name)
                self.assertEqual(len(response.context['page_obj']), template)


class PostViewTest(TestCase):
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
            text='Тестовая пост',
            group=cls.group,
        )
        cls.image = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )

    def setUp(self):
        """Создание клиента авторизованного"""
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_pages_uses_correct_template(self):
        """Тест адреса используют правильные шаблоны"""
        self.user = self.post.author
        self.authorized_client.force_login(self.user)
        templates_pages_names = {
            reverse('posts:home'): 'posts/index.html',
            reverse('posts:group_posts', kwargs={'slug': self.group.slug}):
            'posts/group_list.html',
            reverse('posts:profile', kwargs={'username': self.user}):
            'posts/profile.html',
            reverse('posts:post_detail', kwargs={'post_id': self.post.id}):
            'posts/post_detail.html',
            reverse('posts:post_edit', kwargs={'post_id': self.post.id}):
            'posts/create_post.html',
            reverse('posts:post_create'): 'posts/create_post.html',
        }
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_post_form_context(self):
        """Тест формы на правильный констекст заполняемых полей при создании"""
        response = self.authorized_client.get(reverse('posts:post_create'))
        form_fields = {
            'group': forms.fields.ChoiceField,
            'text': forms.fields.CharField,
            'image': forms.fields.ImageField
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_fields = response.context['form'].fields[value]
                self.assertIsInstance(form_fields, expected)

    def test_group_page_show_correct_context(self):
        """Отображение постов на главной и в группе"""
        templates_names_list = [
            reverse('posts:home'),
            reverse('posts:group_posts', kwargs={'slug': self.group.slug})
        ]
        for test_name in templates_names_list:
            response = self.authorized_client.get(test_name)
            first_object = response.context['page_obj'][0]
            post_text_0 = first_object.text
            post_group_0 = first_object.group
            post_author_0 = first_object.author
            task_post_id = first_object.id
            self.assertEqual(post_group_0, self.group)
            self.assertEqual(post_text_0, self.post.text)
            self.assertEqual(post_author_0, self.post.author)
            self.assertEqual(task_post_id, self.post.id)

    def test_image_page_correct_context(self):
        templates_names_list = [
            reverse('posts:home'),
            reverse('posts:group_posts', kwargs={'slug': self.group.slug}),
            reverse('posts:profile', kwargs={'username': self.user}),
        ]
        for test_name in templates_names_list:
            response = self.authorized_client.get(test_name)
            first_object = response.context['page_obj'][0]
            post_image_0 = first_object.image
            self.assertEqual(post_image_0, self.post.image)

    def test_image_page_correct_context_post_diteil(self):
        templates_name = reverse(
            'posts:post_detail',
            kwargs={'post_id': self.post.id}
        )
        response = self.authorized_client.get(templates_name)
        first_object = response.context['post']
        post_image_0 = first_object.image
        self.assertEqual(post_image_0, self.post.image)


class CashTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='auth')
        cls.authorized__author_client = Client()
        cls.authorized__author_client.force_login(cls.author)
        cls.group = Group.objects.create(
            title='тестовая группа',
            slug='TESTSLUG',
            description='тестовая группа',
        )

    def test_cache_home(self):
        """Проверяем работу кэша главной страницы"""
        cache.clear()
        response = self.client.get(reverse('posts:home'))
        posts_text = response.content
        Post.objects.create(
            text='New text after cashe',
            author=self.author,
            group=self.group
        )
        response = self.client.get(reverse('posts:home'))
        self.assertEqual(response.content, posts_text)
        cache.clear()
        response = self.client.get(reverse('posts:home'))
        self.assertNotEqual(response.content, posts_text)


class FollowTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.follower = User.objects.create_user(
            username="follower"
        )
        cls.another_follower = User.objects.create_user(
            username="another_follower"
        )
        cls.following = User.objects.create_user(
            username="following"
        )

    def setUp(self):
        """Создаем авторизованных клиентов"""
        follower = FollowTests.follower
        another_follower = FollowTests.another_follower
        following = FollowTests.following
        self.follower_client = Client()
        self.follower_client.force_login(follower)
        self.another_follower_client = Client()
        self.another_follower_client.force_login(another_follower)
        self.following_client = Client()
        self.following_client.force_login(following)

    def test_follow(self):
        """
        Проверяем что автозизованный пользователь
        может подписаться и у него отображается
        пост на странице с подписками.
        У неподписчиков не отображается
        """
        self.follower_client.get(
            reverse(
                "posts:profile_follow",
                kwargs={"username": self.following}
            )
        )
        text_post = "Новый пост"
        form_data = {
            'text': text_post
        }
        self.following_client.post(
            reverse(
                'posts:post_create'
            ),
            data=form_data,
            follow=True
        )
        post_create_0 = Post.objects.order_by('-id')[0]
        response = self.follower_client.get(reverse("posts:follow_index"))
        self.assertContains(response, post_create_0.text)
        response = self.another_follower_client.get(
            reverse("posts:follow_index"))
        self.assertNotContains(response, post_create_0.text)
        self.assertTrue(Follow.objects.filter(
            user=FollowTests.follower,
            author=FollowTests.following).exists())

    def test_unfollow(self):
        """
        Проверяем что автозизованный пользователь
        может отписаться и посты больше не отображаются
        """
        self.follower_client.get(
            reverse(
                "posts:profile_unfollow",
                kwargs={"username": self.following}
            )
        )
        self.assertFalse(Follow.objects.filter(
            user=FollowTests.follower,
            author=FollowTests.following).exists())
