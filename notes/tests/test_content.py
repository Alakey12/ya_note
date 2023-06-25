from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class TestContent(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.users = User.objects.create(username='Юзер')
        cls.another_users = User.objects.create(username='ЮзерД')
        cls.notes = Note.objects.create(
            title='Заголовок', text='Текст', author=cls.users
        )

    def test_note_in_list_for_author(self):
        url = reverse('notes:list')
        self.client.force_login(self.users)
        response = self.client.get(url)
        object_list = response.context['object_list']
        self.assertIn(self.notes, object_list)

    def test_note_not_in_list_for_another_user(self):
        url = reverse('notes:list')
        self.client.force_login(self.another_users)
        response = self.client.get(url)
        object_list = response.context['object_list']
        self.assertNotIn(self.notes, object_list)

    def test_create_note_page_contains_form(self):
        url = reverse('notes:add')
        self.client.force_login(self.users)
        response = self.client.get(url)
        self.assertIn('form', response.context)

    def test_edit_note_page_contains_form(self):
        url = reverse('notes:edit', args=(self.notes.slug,))
        self.client.force_login(self.users)
        response = self.client.get(url)
        self.assertIn('form', response.context)
