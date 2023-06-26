from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class TestContent(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create(username='Юзер')
        cls.user_client = Client()
        cls.user_client.force_login(cls.user)
        cls.another_user = User.objects.create(username='ЮзерД')
        cls.notes = Note.objects.create(
            title='Заголовок', text='Текст', author=cls.user
        )

    def test_note_in_list_for_author(self):
        url = reverse('notes:list')
        response = self.user_client.get(url)
        object_list = response.context['object_list']
        self.assertIn(self.notes, object_list)

    def test_note_not_in_list_for_another_user(self):
        url = reverse('notes:list')
        self.client.force_login(self.another_user)
        response = self.client.get(url)
        object_list = response.context['object_list']
        self.assertNotIn(self.notes, object_list)

    def test_create_note_page_contains_form(self):
        url = reverse('notes:add')
        response = self.user_client.get(url)
        self.assertIn('form', response.context)

    def test_edit_note_page_contains_form(self):
        url = reverse('notes:edit', args=(self.notes.slug,))
        response = self.user_client.get(url)
        self.assertIn('form', response.context)
