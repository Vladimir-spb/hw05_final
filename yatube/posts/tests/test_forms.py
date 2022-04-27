import tempfile

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings
from django.test import TestCase, Client, override_settings
from django.urls import reverse

from ..models import Group, Post, Comment

User = get_user_model()


TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class CreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        """Создание записи в БД"""
        super().setUpClass()
        cls.user = User.objects.create_user(username='TestauthTest')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='TESTSLUG',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            text="Тестовая пост",
            author=cls.user,
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
        self.user_2 = User.objects.create_user(username='Newauthor')
        self.client_2 = Client()
        self.client_2.force_login(self.user_2)

    def test_form_create(self):
        """Тест на создание нового поста"""
        post_count = Post.objects.count()
        post_1 = 'Новый текст'
        form_data = {
            'text': post_1,
            'group': self.group.id,
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'), data=form_data, follow=True
        )
        post_create_0 = Post.objects.order_by('-id')[0]
        self.assertRedirects(response, reverse(
            'posts:profile', kwargs={'username': self.user})
        )
        self.assertEqual(Post.objects.count(), post_count + 1)
        self.assertEqual(post_create_0.text, form_data['text'])
        self.assertEqual(post_create_0.group.id, form_data['group'])
        self.assertEqual(post_create_0.author, self.user)

    def test_edit_post(self):
        """Тест редактирования поста"""
        post_edit = Post.objects.order_by('-id')[0]
        edit_post_1 = 'Отредактированный текст'
        form_data = {
            'text': edit_post_1,
            'group': self.group.id
        }
        posts_count = Post.objects.count()
        response = self.authorized_client.post(reverse(
            'posts:post_edit', kwargs={'post_id': post_edit.id}),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse(
            'posts:post_detail', kwargs={'post_id': post_edit.id}))
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertTrue(
            Post.objects.filter(
                text=edit_post_1,
                group=self.group.id,
                id=self.post.id,
                author=self.user,
            ).exists()
        )

    def test_comment_create(self):
        """Тест на создание нового комента"""
        post_create_0 = Post.objects.order_by('-id')[0]
        comment_count = Comment.objects.filter(post=post_create_0.id).count()
        comment_1 = 'test_comment'
        form_data = {
            'text': comment_1,
        }
        self.client_2.post(reverse(
            'posts:add_comment', kwargs={'post_id': post_create_0.id}),
            data=form_data,
        )
        comment_create_0 = Comment.objects.filter(
            post=post_create_0.id).last()
        self.assertEqual(Comment.objects.filter(post=post_create_0.id)
                         .count(), comment_count + 1)
        self.assertEqual(comment_create_0.text, form_data['text'])
        self.assertEqual(comment_create_0.author, self.user_2)

    def test_upload_image(self):
        """Тест на создание поста с картинкой"""
        image = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        upload = SimpleUploadedFile(
            name="image.png",
            content=image,
            content_type="small/png"
        )
        text_post = 'Пост с картинкой'
        form_data = {
            'text': text_post,
            'image': upload,
        }
        self.authorized_client.post(
            reverse('posts:post_create'), data=form_data, follow=True
        )
        post_create_image = Post.objects.order_by('-id')[0]
        self.assertEqual(post_create_image.text, form_data['text'])
        self.assertTrue(post_create_image.image)
