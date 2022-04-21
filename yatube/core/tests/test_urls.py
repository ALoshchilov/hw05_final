from django.test import TestCase, Client

UNEXISTING_PAGE_URL = '/ThisPageIsALieAndTheTestAsWell/'


class StaticUrlTest(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.client = Client()

    def test_direct_access_unexisting_page(self):
        self.assertEqual(self.client.get(UNEXISTING_PAGE_URL).status_code, 404)

    def test_unexisting_page_template(self):
        self.assertTemplateUsed(
            self.client.get(UNEXISTING_PAGE_URL), 'core/404.html'
        )
