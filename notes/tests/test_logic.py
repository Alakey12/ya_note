from pytils.translit import slugify
from http import HTTPStatus
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.models import Note
from notes.forms import WARNING

User = get_user_model()


class TestLogic(TestCase):
    NEWS_TITLE = 'Заголовок'
    NEWS_TEXT = 'Текст'

    @classmethod
    def setUpTestData(cls):
        cls.url = reverse('notes:add')
        cls.user = User.objects.create(username='Юзер')
        cls.user_client = Client()
        cls.user_client.force_login(cls.user)
        cls.another_users = User.objects.create(username='ЮзерД')
        cls.another_users_client = Client()
        cls.another_users_client.force_login(cls.another_users)
        cls.note = Note.objects.create(
            title='Цапля', text='Цапля цапля', author=cls.user
        )
        cls.form_data = {
            'title': cls.NEWS_TITLE,
            'text': cls.NEWS_TEXT,
            'slug': slugify(cls.NEWS_TITLE),
            'author': cls.user,
        }

    def get_notes_count(self):
        return Note.objects.count()

    def test_user_can_create_note(self):
        notes_count_befor_requst = self.get_notes_count()
        response = self.user_client.post(self.url, data=self.form_data)
        self.assertRedirects(response, reverse('notes:success'))
        notes_count = self.get_notes_count()
        self.assertNotEqual(notes_count, notes_count_befor_requst)
        new_note = Note.objects.get(id=notes_count)
        self.assertEqual(new_note.title, self.form_data['title'])
        self.assertEqual(new_note.text, self.form_data['text'])
        self.assertEqual(new_note.slug, self.form_data['slug'])
        self.assertEqual(new_note.author, self.form_data['author'])

    def test_anonymous_user_cant_create_note(self):
        notes_count_befor_requst = self.get_notes_count()
        response = self.client.post(self.url, data=self.form_data)
        notes_count = self.get_notes_count()
        login_url = reverse('users:login')
        expected_url = f'{login_url}?next={self.url}'
        self.assertRedirects(response, expected_url)
        self.assertEqual(notes_count, notes_count_befor_requst)

    def test_not_unique_slug(self):
        self.user_client.post(self.url, data=self.form_data)
        notes_count_befor_requst = self.get_notes_count()
        response = self.user_client.post(self.url, data=self.form_data)
        self.assertFormError(
            response, 'form', 'slug', errors=(self.form_data['slug'] + WARNING)
        )
        notes_count = self.get_notes_count()
        self.assertEqual(notes_count, notes_count_befor_requst)

    def test_empty_slug(self):
        self.form_data.pop('slug')
        notes_count_befor_requst = self.get_notes_count()
        response = self.user_client.post(self.url, data=self.form_data)
        self.assertRedirects(response, reverse('notes:success'))
        notes_count = self.get_notes_count()
        self.assertNotEqual(notes_count, notes_count_befor_requst)
        new_note = Note.objects.get(id=notes_count)
        expected_slug = slugify(self.form_data['title'])
        self.assertEqual(new_note.slug, expected_slug)

    def test_author_can_edit_note(self):
        url = reverse('notes:edit', args=(self.note.slug,))
        response = self.user_client.post(url, self.form_data)
        self.assertRedirects(response, reverse('notes:success'))
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, self.form_data['title'])
        self.assertEqual(self.note.text, self.form_data['text'])
        self.assertEqual(self.note.slug, self.form_data['slug'])

    def test_other_user_cant_edit_note(self):
        url = reverse('notes:edit', args=(self.note.slug,))
        response = self.another_users_client.post(url, self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        note_from_db = Note.objects.get(id=self.note.id)
        self.assertEqual(self.note.title, note_from_db.title)
        self.assertEqual(self.note.text, note_from_db.text)
        self.assertEqual(self.note.slug, note_from_db.slug)

    def test_author_can_delete_note(self):
        url = reverse('notes:delete', args=(self.note.slug,))
        notes_count_befor_requst = self.get_notes_count()
        response = self.user_client.post(url)
        self.assertRedirects(response, reverse('notes:success'))
        notes_count = self.get_notes_count()
        self.assertNotEqual(notes_count, notes_count_befor_requst)

    def test_other_user_cant_delete_note(self):
        url = reverse('notes:delete', args=(self.note.slug,))
        notes_count_befor_requst = self.get_notes_count()
        response = self.another_users_client.post(url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        notes_count = self.get_notes_count()
        self.assertEqual(notes_count, notes_count_befor_requst)
