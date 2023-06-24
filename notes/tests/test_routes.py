from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class TestRoutes(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.users = User.objects.create(username='Юзер')
        cls.another_users = User.objects.create(username='ЮзерД')
        cls.notes = Note.objects.create(
            title='Заголовок', text='Текст', author=cls.users
        )

    def test_pages_availability(self):
        urls = (
            ('notes:home', 'users:login', 'users:logout', 'users:signup')
        )
        for url in urls:
            with self.subTest(url=url):
                response = self.client.get(reverse(url))
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_pages_availability_for_auth_user(self):
        urls = (
            ('notes:list', 'notes:add', 'notes:success')
        )
        for url in urls:
            self.client.force_login(self.users)
            with self.subTest(url=url):
                response = self.client.get(reverse(url))
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_pages_availability_for_author(self):
        users_statuses = (
            (self.users, HTTPStatus.OK),
            (self.another_users, HTTPStatus.NOT_FOUND),
        )
        for user, stutus in users_statuses:
            self.client.force_login(user)
            for name in ('notes:detail', 'notes:edit', 'notes:delete'):
                with self.subTest(user=user, name=name):
                    url = reverse(name, args=(self.notes.slug,))
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, stutus)

    def test_redirect_for_anonymous_client(self):
        login_url = reverse('users:login')
        slug = (self.notes.slug,)
        urls = (
            ('notes:detail', slug),
            ('notes:edit', slug),
            ('notes:delete', slug),
            ('notes:add', None),
            ('notes:success', None),
            ('notes:list', None),
        )
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)
