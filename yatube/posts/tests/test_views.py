from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, Client
from django.urls import reverse

from posts.models import Follow, Post, Group, User
from posts.settings import POSTS_ON_PAGE

SLUG = 'TestGroupSlug'
SLUG_1 = 'TestGroupSlug1'
NICK = 'AutoTestUser'
NOT_AUTHOR = 'NotAuthor'
INDEX_URL = reverse('posts:index')
INDEX_2ND_PAGE_URL = f'{INDEX_URL}?page=2'
POST_CREATE_URL = reverse('posts:post_create')
USER_LOGIN_URL = reverse('users:login')
PROFILE_URL = reverse('posts:profile', args=[NICK])
PROFILE_NOT_AUTHOR_URL = reverse('posts:profile', args=[NOT_AUTHOR])
PROFILE_2ND_PAGE_URL = f'{PROFILE_URL}?page=2'
GROUP_URL = reverse('posts:group_list', args=[SLUG])
GROUP_2ND_PAGE_URL = f'{GROUP_URL}?page=2'
GROUP_URL_1 = reverse('posts:group_list', args=[SLUG_1])
FOLLOW_INDEX_URL = reverse('posts:follow_index')
FOLLOW_INDEX_2ND_PAGE_URL = f'{FOLLOW_INDEX_URL}?page=2'
FOLLOW_URL = reverse('posts:profile_follow', args=[NICK])
ANOTHER_FOLLOW_URL = reverse('posts:profile_follow', args=[NOT_AUTHOR])
UNFOLLOW_URL = reverse('posts:profile_unfollow', args=[NICK])


class ContextViewsTest(TestCase):

    @classmethod
    def setUpClass(cls):

        super().setUpClass()
        cls.user = User.objects.create_user(username=NICK)
        cls.another_user = User.objects.create_user(username=NOT_AUTHOR)
        cls.group_1 = Group.objects.create(
            title='Тестовая группа 1. Заголовок',
            slug=SLUG,
            description='Тестовая группа 1. Описание',
        )
        cls.group_2 = Group.objects.create(
            title='Тестовая группа 2. Заголовок',
            slug=SLUG_1,
            description='Тестовая группа 2. Проверка ',
        )
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        cls.ref_post = Post.objects.create(
            author=cls.user,
            text='Текст. Автотест. Эталонный пост',
            group=cls.group_1,
            image=uploaded
        )
        cls.ref_follow = Follow.objects.create(
            user=cls.another_user,
            author=cls.user
        )
        cls.POST_EDIT_URL = reverse('posts:post_edit', args=[cls.ref_post.id])
        cls.POST_DETAIL_URL = reverse(
            'posts:post_detail', args=[cls.ref_post.id]
        )

    def setUp(self):
        self.guest = Client()
        self.author = Client()
        self.another = Client()
        self.author.force_login(self.user)
        self.another.force_login(self.another_user)

    def test_paginator(self):
        """Тест пагинатора."""
        CASES = [
            # Первая страница
            (INDEX_URL, POSTS_ON_PAGE),
            (GROUP_URL, POSTS_ON_PAGE),
            (PROFILE_URL, POSTS_ON_PAGE),
            (FOLLOW_INDEX_URL, POSTS_ON_PAGE),
            # Последняя страница
            (INDEX_2ND_PAGE_URL, 1),
            (GROUP_2ND_PAGE_URL, 1),
            (PROFILE_2ND_PAGE_URL, 1),
            (FOLLOW_INDEX_2ND_PAGE_URL, 1),

        ]
        Post.objects.bulk_create(
            Post(
                author=self.user,
                text=f'Текст. Автотест. Пост № {post_num}',
                group=self.group_1
            ) for post_num in range(POSTS_ON_PAGE)
        )
        for url, posts_count in CASES:
            with self.subTest(url=url, posts_count=posts_count):
                self.assertEqual(
                    len(self.another.get(url).context['page_obj']),
                    posts_count
                )

    def test_post_in_correct_feeds_and_details(self):
        """
        Тест наличия эталонного поста на страницах, содержащих ленты постов
        либо содержащих подробности о посте.
        """
        CASES = [
            (INDEX_URL, self.guest, 'page_obj'),
            (GROUP_URL, self.guest, 'page_obj'),
            (PROFILE_URL, self.guest, 'page_obj'),
            (FOLLOW_INDEX_URL, self.another, 'page_obj'),
            (self.POST_DETAIL_URL, self.guest, 'post'),
        ]
        for url, client, obj in CASES:
            with self.subTest(url=url, posts_obj=obj):
                response = client.get(url)
                if obj == 'post':
                    post = response.context[obj]
                else:
                    context_objs = response.context[obj]
                    self.assertEqual(len(context_objs), 1)
                    post = context_objs[0]
                self.assertIsInstance(post, Post)
                self.assertEqual(post.pk, self.ref_post.pk)
                self.assertEqual(post.author, self.ref_post.author)
                self.assertEqual(post.group, self.ref_post.group)
                self.assertEqual(post.text, self.ref_post.text)
                self.assertEqual(post.image, self.ref_post.image)

    def test_post_not_in_wrong_pages(self):
        """
        Тест отсутствия эталонного поста на страницах,на которых он
        отображаться не должен
        """
        CASES = [
            GROUP_URL_1,
            PROFILE_NOT_AUTHOR_URL,
            FOLLOW_INDEX_URL,
        ]
        for url in CASES:
            num_pages = self.author.get(
                url
            ).context['page_obj'].paginator.num_pages
            with self.subTest(
                url=url,
                group=self.ref_post.group.slug,
                author=self.ref_post.author.username
            ):
                self.assertEqual(num_pages, 1)
                self.assertNotIn(
                    self.ref_post,
                    self.author.get(url).context['page_obj']
                )

    def test_context_post_create_edit_detail(self):
        """Тест контекста на страницах создания и редактирования поста."""
        CASES = [
            (POST_CREATE_URL, ['form']),
            (self.POST_EDIT_URL, ['form', 'post']),
            (self.POST_DETAIL_URL, ['form', 'post', 'comments']),
        ]
        for url, context in CASES:
            response = self.author.get(url)
            for context_item in context:
                with self.subTest(url=url, context=context):
                    self.assertIn(context_item, response.context)

    def test_context_post_correct_profile(self):
        """Тест корректного автора в контексте страницы профиля."""
        self.assertEqual(
            self.guest.get(PROFILE_URL).context['author'],
            self.user
        )

    def test_context_post_correct_group(self):
        """Тест корректной группы в контексте страницы."""
        group = self.guest.get(GROUP_URL).context['group']
        self.assertEqual(group.pk, self.group_1.pk)
        self.assertEqual(group.title, self.group_1.title)
        self.assertEqual(group.slug, self.group_1.slug)
        self.assertEqual(group.description, self.group_1.description)

    def test_index_page_cached(self):
        """Тест кэширования главной страницы"""
        content1 = self.guest.get(INDEX_URL).content
        Post.objects.create(
            author=self.user,
            text='Текст. Автотест. Изменение кэшируемой страницы',
            group=self.group_1
        )
        content2 = self.guest.get(INDEX_URL).content
        self.assertEqual(content1, content2)
        cache.clear()
        content3 = self.guest.get(INDEX_URL).content
        self.assertNotEqual(content1, content3)

    def test_unfollow(self):
        """Тест подписки/отписки от авторов"""
        # Подписка и пост созданы в фикстуре как объекты, о какой
        # функциональности приложения идет речь!?
        self.assertEqual(
            len(self.another.get(FOLLOW_INDEX_URL).context['page_obj']), 1
        )
        # Follow.objects.filter(
        #     author=self.user, user=self.another_user
        # ).delete()
        self.another.get(UNFOLLOW_URL)
        self.assertEqual(
            len(self.another.get(FOLLOW_INDEX_URL).context['page_obj']), 0
        )

    def test_follow(self):
        """Тест подписки/отписки от авторов"""
        Post.objects.create(
            author=self.another_user,
            text='Текст. Автотест. Отписка',
            group=self.group_1,
        )
        self.assertEqual(
            len(self.author.get(FOLLOW_INDEX_URL).context['page_obj']), 0
        )
        # Follow.objects.create(
        #     user=self.user,
        #     author=self.another_user,
        # )
        self.author.get(ANOTHER_FOLLOW_URL)
        self.assertEqual(
            len(self.author.get(FOLLOW_INDEX_URL).context['page_obj']), 1
        )
