from django.test import TestCase, RequestFactory
from django.shortcuts import reverse
from django.contrib.sessions.middleware import SessionMiddleware
from django.core.exceptions import PermissionDenied
from .models import Policies, PolicyTemplates
from . import views

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

    def testLTILaunchFailure(self):
        request = self.factory.post('process_lti_launch_request')
        annotate_request_with_session(request)
        response = views.process_lti_launch_request_view(request)
        self.assertEquals(response['Location'], reverse('lti_exception_view'))

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
        self.assertEquals(response['Location'], reverse('student_active_policy'))
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
        self.context_id = 'context123abcd'
        self.studentSession = {
            'context_id': self.context_id,
            'lis_person_sourcedid': '123456789',
            'role': 'Student',
            'course_id': 1
        }
        self.instructorSession = {
            'context_id': self.context_id,
            'lis_person_sourcedid': '123456789',
            'role': 'Instructor',
            'course_id': 1
        }
        self.administratorSession = {
            'context_id': self.context_id,
            'lis_person_sourcedid': '123456789',
            'role': 'Administrator',
            'course_id': 1
        }
        self.policy_templates = create_default_policy_templates()
        self.active_policy = Policies.objects.create(
            context_id=self.context_id,
            is_published=True,
            is_active=True,
            published_by=self.instructorSession['lis_person_sourcedid'],
            body='this is an important policy. please read!',
            course_id=1
        )

    def tearDown(self):
        for policy_template in self.policy_templates:
            policy_template.delete()

    def testStudentDeniedPolicyTemplatesListView(self):
        request = self.factory.get('policy_templates_list')
        annotate_request_with_session(request, self.studentSession)
        with self.assertRaises(PermissionDenied):
            views.policy_templates_list_view(request)

    def testStudentDeniedInstructorPolicyEditView(self):
        request = self.factory.get('policy_templates_list')
        annotate_request_with_session(request, self.studentSession)
        with self.assertRaises(PermissionDenied):
            views.instructor_level_policy_edit_view(request, self.policy_templates[0].pk)

    def testStudentDeniedInactivatePolicyView(self):
        request = self.factory.get('policy_templates_list')
        annotate_request_with_session(request, self.studentSession)
        with self.assertRaises(PermissionDenied):
            views.instructor_inactivate_policies_view(request)

    def testStudentDeniedAdminTemplateEditView(self):
        request = self.factory.get('policy_templates_list')
        annotate_request_with_session(request, self.studentSession)
        with self.assertRaises(PermissionDenied):
            views.admin_level_template_edit_view(request, self.policy_templates[0].pk)

    def testStudentDeniedInstructorActivePolicyView(self):
        request = self.factory.get('policy_templates_list')
        annotate_request_with_session(request, self.studentSession)
        with self.assertRaises(PermissionDenied):
            views.instructor_active_policy(request, self.active_policy.pk)

    def testStudentDeniedEditActivePolicyView(self):
        request = self.factory.get('policy_templates_list')
        annotate_request_with_session(request, self.studentSession)
        with self.assertRaises(PermissionDenied):
            views.edit_active_policy(request, self.active_policy.pk)

    def testStudentDeniedAdminUpdatedTemplateView(self):
        request = self.factory.get('policy_templates_list')
        annotate_request_with_session(request, self.studentSession)
        with self.assertRaises(PermissionDenied):
            views.admin_updated_template_view(request, self.policy_templates[0].pk)

    def testStudentDeniedAdminEditUpdatedTemplateView(self):
        request = self.factory.get('policy_templates_list')
        annotate_request_with_session(request, self.studentSession)
        with self.assertRaises(PermissionDenied):
            views.admin_edit_updated_template_view(request, self.policy_templates[0].pk)

    def testInstructorDeniedAdminTemplateEditView(self):
        request = self.factory.get('policy_templates_list')
        annotate_request_with_session(request, self.instructorSession)
        with self.assertRaises(PermissionDenied):
            views.admin_level_template_edit_view(request, self.policy_templates[0].pk)

    def testInstructorDeniedStudentActivePolicyView(self):
        request = self.factory.get('policy_templates_list')
        annotate_request_with_session(request, self.instructorSession)
        with self.assertRaises(PermissionDenied):
            views.student_active_policy_view(request)

    def testInstructorAllowedPolicyTemplatesListView(self):
        request = self.factory.get('policy_templates_list')
        annotate_request_with_session(request, self.instructorSession)
        response = views.policy_templates_list_view(request)
        self.assertEquals(response.status_code, 200)

    def testInstructorAllowedInstructorActivePolicyView(self):
        request = self.factory.get('policy_templates_list')
        annotate_request_with_session(request, self.instructorSession)
        response = views.instructor_active_policy(request, self.active_policy.pk)
        self.assertEquals(response.status_code, 200)

    def testInstructorAllowedEditActivePolicyView(self):
        request = self.factory.get('policy_templates_list')
        annotate_request_with_session(request, self.instructorSession)
        response = views.edit_active_policy(request, self.active_policy.pk)
        self.assertEquals(response.status_code, 200)

    def testInstructorAllowedInactivateOldPublishNewView(self):
        request = self.factory.get('policy_templates_list')
        annotate_request_with_session(request, self.instructorSession)
        response = views.instructor_inactivate_policies_view(request)
        self.assertEquals(response.status_code, 302)

    def testInstructorDeniedAdminUpdatedTemplateView(self):
        request = self.factory.get('policy_templates_list')
        annotate_request_with_session(request, self.instructorSession)
        with self.assertRaises(PermissionDenied):
            views.admin_updated_template_view(request, self.policy_templates[0].pk)

    def testInstructorDeniedAdminEditUpdatedTemplateView(self):
        request = self.factory.get('policy_templates_list')
        annotate_request_with_session(request, self.instructorSession)
        with self.assertRaises(PermissionDenied):
            views.admin_edit_updated_template_view(request, self.policy_templates[0].pk)

    def testAdministratorDeniedInstructorPolicyEditView(self):
        request = self.factory.get('policy_templates_list')
        annotate_request_with_session(request, self.administratorSession)
        with self.assertRaises(PermissionDenied):
            views.instructor_level_policy_edit_view(request, self.policy_templates[0].pk)

    def testAdministratorDeniedInstructorActivePolicyView(self):
        request = self.factory.get('policy_templates_list')
        annotate_request_with_session(request, self.administratorSession)
        with self.assertRaises(PermissionDenied):
            views.instructor_active_policy(request, self.active_policy.pk)

    def testAdministratorDeniedEditActivePolicyView(self):
        request = self.factory.get('policy_templates_list')
        annotate_request_with_session(request, self.administratorSession)
        with self.assertRaises(PermissionDenied):
            views.edit_active_policy(request, self.active_policy.pk)

    def testAdministratorDeniedInactivatePolicyView(self):
        request = self.factory.get('policy_templates_list')
        annotate_request_with_session(request, self.administratorSession)
        with self.assertRaises(PermissionDenied):
            views.instructor_inactivate_policies_view(request)

    def testAdministratorDeniedStudentActivePolicyView(self):
        request = self.factory.get('policy_templates_list')
        annotate_request_with_session(request, self.administratorSession)
        with self.assertRaises(PermissionDenied):
            views.student_active_policy_view(request)

    def testAdministratorAllowedAdminTemplateEditView(self):
        request = self.factory.get('policy_templates_list')
        annotate_request_with_session(request, self.administratorSession)
        response = views.admin_level_template_edit_view(request, self.policy_templates[0].pk)
        self.assertEquals(response.status_code, 200)

class AdministratorRoleTests(TestCase):

    def setUp(self):
        self.factory = RequestFactory()
        self.policy_templates = create_default_policy_templates()

    def tearDown(self):
        for policy_template in self.policy_templates:
            policy_template.delete()

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
        self.policy_templates = create_default_policy_templates()
        self.instructorSession = {
            'context_id': 'tlhzlqzolkhapmnoukgm',
            'lis_person_sourcedid': '123456789',
            'role': 'Instructor',
            'course_id': 1
        }

    def tearDown(self):
        for policy_template in self.policy_templates:
            policy_template.delete()

    def testPolicyTemplatesListView(self):
        request = self.factory.get('policy_templates_list')
        annotate_request_with_session(request, self.instructorSession)
        response = views.policy_templates_list_view(request)
        self.assertEquals(response.status_code, 200)

    def testPublishNewPolicy(self):
        postparams = {'body': 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Aenean in volutpat purus.'}
        policy_template_id = self.policy_templates[3].pk
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
        self.assertTrue(policy.is_active)
        self.assertEqual(policy.published_by, self.instructorSession['lis_person_sourcedid'])

class StudentRoleTests(TestCase):

    def setUp(self):
        self.factory = RequestFactory()
        self.policy_templates = create_default_policy_templates()

        self.lis_person_sourcedid='123456789',

        self.studentSessionWithActivePolicy = {
            'context_id': 'context123',
            'role': 'Student',
            'course_id': 1
        }
        self.studentSessionNoActivePolicy = {
            'context_id': 'context456',
            'role': 'Student',
            'course_id': 2
        }

        self.active_policy = Policies.objects.create(
            context_id=self.studentSessionWithActivePolicy['context_id'],
            published_by=self.lis_person_sourcedid,
            is_published=True,
            is_active=True,
            body='this is an important policy. please read!',
            course_id=1
        )

    def tearDown(self):
        for policy_template in self.policy_templates:
            policy_template.delete()

    def testStudentActivePolicyView(self):
        request = self.factory.get('student_active_policy')
        annotate_request_with_session(request, self.studentSessionWithActivePolicy)
        response = views.student_active_policy_view(request)
        self.assertEquals(response.status_code, 200)
        self.assertInHTML(self.active_policy.body, response.content.decode("utf-8"))

    def testStudentNoActivePolicyView(self):
        request = self.factory.get('student_active_policy')
        annotate_request_with_session(request, self.studentSessionNoActivePolicy)
        response = views.student_active_policy_view(request)
        self.assertEquals(response.status_code, 200)
        self.assertInHTML('There is no published academic integrity policy in record for this course.', response.content.decode("utf-8"))
