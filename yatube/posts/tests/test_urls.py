from django.contrib.auth import get_user
from django.test import TestCase, Client
from django.urls import reverse

from posts.models import Post, Group, User

NICK = 'AutoTestUser'
NOT_AUTHOR = 'NotAuthor'
SLUG = 'TestGroupSlug'
UNEXISTING_PAGE_URL = '/ThisPageIsALieAndTheTestAsWell/'
INDEX_URL = reverse('posts:index')
POST_CREATE_URL = reverse('posts:post_create')
USER_LOGIN_URL = reverse('users:login')
PROFILE_URL = reverse('posts:profile', args=[NICK])
GROUP_URL = reverse('posts:group_list', args=[SLUG])
POST_CREATE_TO_LOGIN = f'{USER_LOGIN_URL}?next={POST_CREATE_URL}'
FOLLOW_INDEX_URL = reverse('posts:follow_index')
FOLLOW_URL = reverse('posts:profile_follow', args=[NICK])
UNFOLLOW_URL = reverse('posts:profile_unfollow', args=[NICK])
FOLLOW_TO_LOGIN = f'{USER_LOGIN_URL}?next={FOLLOW_URL}'


class StaticUrlTest(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username=NICK)
        cls.another_user = User.objects.create_user(username=NOT_AUTHOR)
        cls.group = Group.objects.create(
            title='Тестовая группа. Заголовок',
            slug=SLUG,
            description='Тестовая группа. Описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            group=cls.group,
            text='Текст. Автотест',
        )
        cls.POST_EDIT_URL = reverse('posts:post_edit', args=[cls.post.id])
        cls.POST_DETAIL_URL = reverse('posts:post_detail', args=[cls.post.id])
        cls.POST_EDIT_TO_LOGIN = f'{USER_LOGIN_URL}?next={cls.POST_EDIT_URL}'
        cls.POST_ADD_COMMENT_URL = reverse(
            'posts:add_comment', args=[cls.post.id]
        )
        cls.ADD_COMMENT_TO_DETAIL = (
            f'{USER_LOGIN_URL}'
            f'?next={cls.POST_ADD_COMMENT_URL}')

    def setUp(self):
        self.guest = Client()
        self.author = Client()
        self.author.force_login(self.user)
        self.another = Client()
        self.another.force_login(self.another_user)

    def test_user_direct_access(self):
        """Тест кодов HTTP-ответов страниц для различных типов клиентов"""
        CASES = [
            (INDEX_URL, self.guest, 200),
            (GROUP_URL, self.guest, 200),
            (PROFILE_URL, self.guest, 200),
            (self.POST_DETAIL_URL, self.guest, 200),
            (POST_CREATE_URL, self.author, 200),
            (POST_CREATE_URL, self.guest, 302),
            (self.POST_EDIT_URL, self.author, 200),
            (self.POST_EDIT_URL, self.guest, 302),
            (self.POST_EDIT_URL, self.another, 302),
            (UNEXISTING_PAGE_URL, self.guest, 404),
            (self.POST_ADD_COMMENT_URL, self.guest, 302),
            (FOLLOW_INDEX_URL, self.guest, 302),
            (FOLLOW_INDEX_URL, self.author, 200),
            (FOLLOW_URL, self.guest, 302),
            (UNFOLLOW_URL, self.guest, 302),
        ]
        for url, client, status in CASES:
            with self.subTest(
                url=url,
                user=get_user(client).username or 'Guest',
                HTTP_Status=status
            ):
                self.assertEqual(client.get(url).status_code, status)

    def test_user_redirect(self):
        """Тест редиректов"""
        CASES = [
            (POST_CREATE_URL, self.guest, POST_CREATE_TO_LOGIN),
            (self.POST_EDIT_URL, self.guest, self.POST_EDIT_TO_LOGIN),
            (self.POST_EDIT_URL, self.another, self.POST_DETAIL_URL),
            (FOLLOW_URL, self.guest, FOLLOW_TO_LOGIN),
            (
                self.POST_ADD_COMMENT_URL,
                self.guest,
                self.ADD_COMMENT_TO_DETAIL
            ),
        ]
        for url, client, redirect_url in CASES:
            with self.subTest(
                url=url,
                redirect=redirect_url,
                user=get_user(client).username or 'Guest',
            ):
                self.assertRedirects(
                    client.get(url, follow=True),
                    redirect_url
                )

    def test_correct_template(self):
        """Тест используемых шаблонов для урлов"""
        CASES = [
            (INDEX_URL, self.author, 'posts/index.html'),
            (GROUP_URL, self.author, 'posts/group_list.html'),
            (PROFILE_URL, self.author, 'posts/profile.html'),
            (self.POST_DETAIL_URL, self.author, 'posts/post_detail.html'),
            (POST_CREATE_URL, self.author, 'posts/create_post.html'),
            (self.POST_EDIT_URL, self.author, 'posts/create_post.html'),
            (FOLLOW_INDEX_URL, self.author, 'posts/follow.html'),
        ]
        for url, client, template in CASES:
            with self.subTest(url=url, template=template):
                self.assertTemplateUsed(client.get(url), template)
