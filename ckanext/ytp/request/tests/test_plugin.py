# encoding: utf-8
from nose.tools import assert_equal

import mock
from ckan.lib.helpers import url_for

import ckan.tests.helpers as helpers
import ckan.tests.factories as factories

webtest_submit = helpers.webtest_submit
PLUGIN_CONTROLLER = 'ckanext.ytp.request.controller:YtpRequestController'


class TestViewingActionedReferral(helpers.FunctionalTestBase):
    '''
        Test that viewing an already actioned membership request does not 404
    '''

    _load_plugins = (u'ytp_request', )

    @mock.patch('ckanext.ytp.request.logic.action.create.flash_success')  # mock1
    @mock.patch('ckanext.ytp.request.logic.action.update.flash_success')  # mock2
    def test_viewing_actioned_referral(self, mock1, mock2):
        app = self._get_test_app()

        # setup
        org = factories.Organization()
        sysadmin = factories.Sysadmin()
        regular_user = factories.User()

        # user creates membership request
        membership_request = helpers.call_action(
            'member_request_create',
            {'user': regular_user['name']},
            group=org['name'],
            role='member'
        )

        # admin approves membership
        helpers.call_action(
            'member_request_approve',
            {'user': sysadmin['name']},
            approve='approve',
            mrequest_id=membership_request['id']
        )

        # admin view membership request page again
        url = url_for(
            controller=PLUGIN_CONTROLLER,
            action='show',
            mrequest_id=membership_request['id']
        )

        # test request no longer 404s
        response = app.get(
            url,
            extra_environ={'REMOTE_USER': sysadmin['name'].encode('ascii')},
            expect_errors=True
        )
        assert_equal(response.status_int, 200)
