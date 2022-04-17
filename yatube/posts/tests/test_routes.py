from django.test import TestCase
from django.urls import reverse

POST_ID = 1
USER = 'User'
GROUP = 'Group'
CASES = [
    ('index', None, '/'),
    ('group_list', [GROUP], f'/group/{GROUP}/'),
    ('profile', [USER], f'/profile/{USER}/'),
    ('post_create', None, '/create/'),
    ('post_edit', [POST_ID], f'/posts/{POST_ID}/edit/'),
    ('post_detail', [POST_ID], f'/posts/{POST_ID}/'),
    ('add_comment', [POST_ID], f'/posts/{POST_ID}/comment/'),
    ('profile_follow', [USER], f'/profile/{USER}/follow/'),
    ('profile_unfollow', [USER], f'/profile/{USER}/unfollow/'),
    ('follow_index', None, '/follow/')
]


class RoutesTest(TestCase):
    def test_correct_routes(self):
        """Тест маршрутов для имен урлов"""
        for url_name, args, url in CASES:
            reversed_url = reverse(f'posts:{url_name}', args=args)
            with self.subTest(reverse=reversed_url, url=url):
                self.assertEqual(reversed_url, url)
