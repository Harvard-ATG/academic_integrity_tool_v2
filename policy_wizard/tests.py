from django.test import TestCase, RequestFactory
from django.urls import reverse, resolve
from django.contrib.auth.models import User
from .views import process_lti_launch_request_view
from .models import Policies, PolicyTemplates
from .views import student_published_policy_view, policy_templates_list_view
from .middleware import lti_launch_params_dict


# Create your tests here.

class AdministratorRoleTests(TestCase):

    def setUp(self):
        self.policyTemplate1 = PolicyTemplates.objects.create(name="Collaboration Permitted: Written Work", body="Foo")
        self.policyTemplate2 = PolicyTemplates.objects.create(name="Collaboration Permitted: Problem Sets", body="Bar")
        self.policyTemplate3 = PolicyTemplates.objects.create(name="Collaboration Prohibited", body="Bar")
        self.policyTemplate4 = PolicyTemplates.objects.create(name="Custom Policy", body="Bar")

    def test_administrator_launch(self):
        url = reverse('policy_templates_list', kwargs={'role': 'Administrator'})
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)

class studentRoleTests(TestCase):

    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            username='jacob', email='jacob@…', password='top_secret')

        self.publishedPolicy = Policies.objects.create(
            context_id='z2gd5dn5nkg7tb5et6fb',
            published_by=self.user,
            is_published=True,
            body='important policy'
        )

    def test_student_lti_launch_status_code(self):
        url = reverse('student_published_policy')
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)

    def test_student_published_policy_view(self):
        lti_launch_params_dict['context_id'] = self.publishedPolicy.context_id
        request = self.factory.get('student_published_policy')
        response = student_published_policy_view(request)
        self.assertEquals(response.status_code, 200)
        self.assertTrue(Policies.objects.exists())


class InstructorRoleTests(TestCase):

    def setUp(self):
        self.policyTemplate1 = PolicyTemplates.objects.create(name="Collaboration Permitted: Written Work", body="Foo")
        self.policyTemplate2 = PolicyTemplates.objects.create(name="Collaboration Permitted: Problem Sets", body="Bar")
        self.policyTemplate3 = PolicyTemplates.objects.create(name="Collaboration Prohibited", body="Bar")
        self.policyTemplate4 = PolicyTemplates.objects.create(name="Custom Policy", body="Bar")

    def test_instructor_launch(self):
        url = reverse('policy_templates_list', kwargs={'role': 'Instructor'})
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)



