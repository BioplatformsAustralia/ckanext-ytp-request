# encoding: utf-8

import pytest
import mock
from ckan.lib.helpers import url_for

import ckan.tests.helpers as helpers
import ckan.tests.factories as factories


@pytest.mark.ckan_config(u'ckan.plugins', u'ytp_request')
@pytest.mark.usefixtures(u'with_plugins')
@pytest.mark.usefixtures(u'with_request_context')
@pytest.mark.usefixtures(u'mail_server')
class TestViewingActionedReferral(object):
    '''
        Test that viewing an already actioned membership request does not 404
    '''

    @mock.patch('ckanext.ytp_request.logic.action.create.flash_success')  # mock1
    @mock.patch('ckanext.ytp_request.logic.action.update.flash_success')  # mock2
    def test_viewing_actioned_referral(self, mock1, mock2, app):

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
        print(membership_request['id'])

        # admin view membership request page again
        url = url_for(
            'member_request.show',
            mrequest_id=membership_request['id']
        )

        response_for_existing_request = app.get(
            url,
            extra_environ={'REMOTE_USER': sysadmin['name'].encode('ascii')},
            expect_errors=True
        )
        assert response_for_existing_request.status_code == 200

        # admin approves membership
        helpers.call_action(
            'member_request_approve',
            {'user': sysadmin['name']},
            approve='approve',
            mrequest_id=membership_request['id']
        )

        # test request no longer 404s
        response_for_approved_request = app.get(
            url,
            extra_environ={'REMOTE_USER': sysadmin['name'].encode('ascii')},
            expect_errors=True
        )
        assert response_for_approved_request.status_code == 404
