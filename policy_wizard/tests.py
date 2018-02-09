from django.test import TestCase
from django.urls import reverse, resolve
from .views import published_policy_to_display_view

# Create your tests here.
class studentViewTests(TestCase):
    def test_lti_launch_status_code(self):
        url = reverse('published_policy_to_display')
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)

    def test_student_url_resolves_published_policy_view(self):
        view = resolve('/student')
        self.assertEquals(view.func, published_policy_to_display_view)
