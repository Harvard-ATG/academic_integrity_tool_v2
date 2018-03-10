from django.test import TestCase, RequestFactory
from django.shortcuts import reverse
from django.contrib.sessions.middleware import SessionMiddleware
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from .models import Policies, PolicyTemplates
from . import views

import pylti
import mock


def annotate_request_with_session(request, params=None):
    middleware = SessionMiddleware()
    middleware.process_request(request)
    if params is not None:
        for k, v in params.items():
            request.session[k] = v
    return request

def create_default_policy_templates():
    policies = [
        PolicyTemplates.objects.create(name="Collaboration Permitted: Written Work", body="Foo"),
        PolicyTemplates.objects.create(name="Collaboration Permitted: Problem Sets", body="Bar"),
        PolicyTemplates.objects.create(name="Collaboration Prohibited", body="Bar"),
        PolicyTemplates.objects.create(name="Custom Policy", body="Bar"),
    ]
    return policies


class LtiLaunchTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def testGetRequest(self):
        request = self.factory.get('process_lti_launch_request')
        annotate_request_with_session(request)
        with self.assertRaises(pylti.common.LTIException):
            views.process_lti_launch_request_view(request)

    def testPostIsEmpty(self):
        request = self.factory.post('process_lti_launch_request')
        annotate_request_with_session(request)
        with self.assertRaises(pylti.common.LTIException):
            views.process_lti_launch_request_view(request)

    @mock.patch('policy_wizard.views.validate_request')
    def testPostNotValidLtiRequest(self, mock_validate_request):
        mock_validate_request.return_value = False
        request = self.factory.post('process_lti_launch_request', {
            'lti_message_type': 'basic-lti-launch-request',
        })
        annotate_request_with_session(request)
        with self.assertRaises(PermissionDenied):
            views.process_lti_launch_request_view(request)

    @mock.patch('policy_wizard.views.validate_request')
    def testPostValidLtiRequest(self, mock_validate_request):
        mock_validate_request.return_value = True
        request = self.factory.post('process_lti_launch_request', {
            'lti_message_type': 'basic-lti-launch-request',
            'ext_roles': 'urn:lti:instrole:ims/lis/Student,urn:lti:role:ims/lis/Learner,urn:lti:sysrole:ims/lis/User',
        })
        annotate_request_with_session(request)
        response = views.process_lti_launch_request_view(request)
        self.assertTrue(response.status_code, 200)

    @mock.patch('policy_wizard.views.validate_request')
    def testStudentLaunch(self, mock_validate_request):
        mock_validate_request.return_value = True
        postparams = {
            'lti_message_type': 'basic-lti-launch-request',
            'context_id': 'abcd1234',
            'ext_roles': 'urn:lti:instrole:ims/lis/Student,urn:lti:role:ims/lis/Learner,urn:lti:sysrole:ims/lis/User',
        }
        request = self.factory.post('process_lti_launch_request', postparams)
        annotate_request_with_session(request)
        response = views.process_lti_launch_request_view(request)
        self.assertTrue(response.status_code, 301)
        self.assertEquals(response['Location'], reverse('student_published_policy'))
        self.assertEquals(request.session['context_id'], postparams['context_id'])
        self.assertEquals(request.session['role'], 'Student')

    @mock.patch('policy_wizard.views.validate_request')
    def testInstructorLaunch(self, mock_validate_request):
        mock_validate_request.return_value = True
        postparams = {
            'lti_message_type': 'basic-lti-launch-request',
            'context_id': 'abcd1234',
            'ext_roles': 'urn:lti:role:ims/lis/Instructor,urn:lti:instrole:ims/lis/Student,urn:lti:sysrole:ims/lis/User',
        }
        request = self.factory.post('process_lti_launch_request', postparams)
        annotate_request_with_session(request)
        response = views.process_lti_launch_request_view(request)
        self.assertTrue(response.status_code, 301)
        self.assertEquals(response['Location'], reverse('policy_templates_list'))
        self.assertEquals(request.session['context_id'], postparams['context_id'])
        self.assertEquals(request.session['role'], 'Instructor')

    @mock.patch('policy_wizard.views.validate_request')
    def testAdministratorLaunch(self, mock_validate_request):
        mock_validate_request.return_value = True
        postparams = {
            'lti_message_type': 'basic-lti-launch-request',
            'context_id': 'abcd1234',
            'ext_roles': 'urn:lti:instrole:ims/lis/Administrator,urn:lti:instrole:ims/lis/Instructor,urn:lti:instrole:ims/lis/Student,urn:lti:sysrole:ims/lis/User',
        }
        request = self.factory.post('process_lti_launch_request', postparams)
        annotate_request_with_session(request)
        response = views.process_lti_launch_request_view(request)
        self.assertTrue(response.status_code, 301)
        self.assertEquals(response['Location'], reverse('policy_templates_list'))
        self.assertEquals(request.session['context_id'], postparams['context_id'])
        self.assertEquals(request.session['role'], 'Administrator')


class RoleAndPermissionTests(TestCase):

    def setUp(self):
        self.factory = RequestFactory()
        self.studentSession = {
            'context_id': 'abcd1234',
            'role': 'Student',
        }
        self.instructorSession = {
            'context_id': 'abcd1234',
            'role': 'Instructor',
        }
        self.policyTemplates = create_default_policy_templates()

    def tearDown(self):
        for policyTemplate in self.policyTemplates:
            policyTemplate.delete()

    def testStudentDeniedPolicyTemplatesListView(self):
        request = self.factory.get('policy_templates_list')
        annotate_request_with_session(request, self.studentSession)
        with self.assertRaises(PermissionDenied):
            views.policy_templates_list_view(request)

    def testInstructorAllowedPolicyTemplatesListView(self):
        request = self.factory.get('policy_templates_list')
        annotate_request_with_session(request, self.studentSession)
        response = views.policy_templates_list_view(request)
        self.assertEquals(response.status_code, 200)

    def testStudentDeniedInstructorPolicyEditView(self):
        request = self.factory.get('policy_templates_list')
        annotate_request_with_session(request, self.studentSession)
        with self.assertRaises(PermissionDenied):
            views.instructor_level_policy_edit_view(request, self.policyTemplates[0].pk)

    def testStudentDeniedAdminTemplateEditView(self):
        request = self.factory.get('policy_templates_list')
        annotate_request_with_session(request, self.studentSession)
        with self.assertRaises(PermissionDenied):
            views.admin_level_template_edit_view(request, self.policyTemplates[0].pk)

    def testInstructorDeniedAdminTemplateEditView(self):
        request = self.factory.get('policy_templates_list')
        annotate_request_with_session(request, self.instructorSession)
        with self.assertRaises(PermissionDenied):
            views.admin_level_template_edit_view(request, self.policyTemplates[0].pk)

class AdministratorRoleTests(TestCase):

    def setUp(self):
        self.factory = RequestFactory()
        self.policyTemplates = create_default_policy_templates()

    def tearDown(self):
        for policyTemplate in self.policyTemplates:
            policyTemplate.delete()

    def testPolicyTemplatesListView(self):
        request = self.factory.get('policy_templates_list')
        annotate_request_with_session(request, {
            'context_id': 'fgvsxrzpdbcmiuawhwet',
            'role': 'Administrator'
        })
        response = views.policy_templates_list_view(request)
        self.assertEquals(response.status_code, 200)

class InstructorRoleTests(TestCase):

    def setUp(self):
        self.factory = RequestFactory()
        self.policyTemplates = create_default_policy_templates()
        self.instructorSession = {
            'context_id': 'tlhzlqzolkhapmnoukgm',
            'lis_person_sourcedid': '123456789',
            'role': 'Instructor'
        }
        self.user = User.objects.create_user(
            username='jacob', email='jacob@…', password='top_secret')

    def tearDown(self):
        for policyTemplate in self.policyTemplates:
            policyTemplate.delete()

    def testPolicyTemplatesListView(self):
        request = self.factory.get('policy_templates_list')
        annotate_request_with_session(request, self.instructorSession)
        response = views.policy_templates_list_view(request)
        self.assertEquals(response.status_code, 200)

    def testPublishNewPolicy(self):
        postparams = {'body': 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Aenean in volutpat purus.'}
        policy_template_id = self.policyTemplates[3].pk
        request = self.factory.post('instructor_level_policy_edit', postparams)
        annotate_request_with_session(request, self.instructorSession)
        response = views.instructor_level_policy_edit_view(request, policy_template_id)
        self.assertEquals(response.status_code, 302)

        try:
            policy = Policies.objects.get(body=postparams['body'])
        except Policies.DoesNotExist:
            self.fail("policy should have been created")

        self.assertEqual(policy.related_template_id, policy_template_id)
        self.assertEqual(policy.body, postparams['body'])
        self.assertTrue(policy.is_published)
        self.assertEqual(policy.published_by, self.instructorSession['lis_person_sourcedid'])


class StudentRoleTests(TestCase):

    def setUp(self):
        self.factory = RequestFactory()
        self.policyTemplates = create_default_policy_templates()

        self.user = User.objects.create_user(
            username='jacob', email='jacob@…', password='top_secret')

        self.context_id = 'z2gd5dn5nkg7tb5et6fb'

        self.studentSession = {
            'context_id': self.context_id,
            'role': 'Student'
        }

        self.publishedPolicy = Policies.objects.create(
            context_id=self.context_id,
            published_by=self.user,
            is_published=True,
            body='this is an important policy. please read!'
        )

    def tearDown(self):
        for policyTemplate in self.policyTemplates:
            policyTemplate.delete()

    def testStudentPublishedPolicyView(self):
        request = self.factory.get('student_published_policy')
        annotate_request_with_session(request, self.studentSession)
        response = views.student_published_policy_view(request)
        self.assertEquals(response.status_code, 200)
        self.assertInHTML(self.publishedPolicy.body, response.content.decode("utf-8"))
