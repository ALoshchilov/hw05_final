from django.test import TestCase

from posts.models import Comment, Follow, Group, Post, User


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.another_user = User.objects.create_user(username='another')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост_1234567890',
        )
        cls.comment = Comment.objects.create(
            text='Тестовый комментарий',
            author=cls.another_user,
            post=cls.post
        )
        cls.follow = Follow.objects.create(
            user=cls.another_user,
            author=cls.user
        )

    def test_models_have_correct_object_names(self):
        """Тест корректной работы метода __str__ у моделей."""
        CASES = [
            (Post, str(self.post), self.post.text[:15]),
            (Comment, str(self.comment), self.comment.text[:15]),
            (Group, str(self.group), self.group.title),
            (
                Follow,
                str(self.follow),
                f'{self.another_user} follows {self.user}'
            ),
        ]
        for model, actual_str, expected_str in CASES:
            with self.subTest(
                model=model.__name__,
                actual_str=actual_str,
                expected_str=expected_str
            ):
                self.assertEqual(actual_str, expected_str)

    def test_models_have_correct_helptext(self):
        """Тест наличия подсказок"""
        CASES = [
            (Post, {
                'text': 'Введите текст поста',
                'group': 'Группа, к которой будет относиться пост',
                'image': 'Загрузите изображение',
            }),
            (Comment, {
                'text': 'Введите текст комментария'
            })
        ]
        for model, field_help_texts in CASES:
            for field, expected_value in field_help_texts.items():
                with self.subTest(model=model.__name__, field=field):
                    self.assertEqual(
                        model._meta.get_field(field).help_text, expected_value)

    def test_models_have_correct_verbosename(self):
        """Тест наличия удобочитаемых имен"""
        CASES = [
            (Post, {
                'text': 'Текст поста',
                'created': 'Дата создания',
                'author': 'Автор',
                'group': 'Группа',
                'image': 'Картинка',
            }),
            (Group, {
                'title': 'Заголовок',
                'slug': 'Код группы',
                'description': 'Описание',
            }),
            (Comment, {
                'text': 'Текст комментария',
                'created': 'Дата создания',
                'author': 'Автор комментария',
                'post': 'Комментриуемый пост',
            }),
            (Follow, {
                'user': 'Подписчик',
                'author': 'Автор'
            })
        ]
        for model, field_verbose_names in CASES:
            for field, expected_value in field_verbose_names.items():
                with self.subTest(model=model.__name__, field=field):
                    self.assertEqual(
                        model._meta.get_field(field).verbose_name,
                        expected_value
                    )
