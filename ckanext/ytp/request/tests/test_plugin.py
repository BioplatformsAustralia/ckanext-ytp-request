# encoding: utf-8
import logging
from nose.tools import assert_true, assert_equal

import mock
import __builtin__ as builtins
from bs4 import BeautifulSoup
from ckan.lib.helpers import url_for
from ckan.common import config

import ckan.model as model
import ckan.tests.helpers as helpers
import ckan.tests.factories as factories
from ckan.model.system_info import get_system_info
from ckan.tests.helpers import submit_and_follow

webtest_submit = helpers.webtest_submit
PLUGIN_CONTROLLER = 'ckanext.ytp.request.controller:YtpRequestController'

class TestViewingActionedReferral(helpers.FunctionalTestBase):
    '''
        Test that viewing an already actioned membership request does not 404
    '''

    _load_plugins = (u'ytp_request', )

    @mock.patch('ckanext.ytp.request.logic.action.create.flash_success')
    @mock.patch('ckanext.ytp.request.logic.action.update.flash_success')
    def test_viewing_actioned_referral(self, mocked_create_flash, mocked_update_flash):
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
        membership_approval = helpers.call_action(
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
        response = app.get(
            url,
            extra_environ={'REMOTE_USER': sysadmin['name'].encode('ascii')},
            status=200
        )

        # app.get() will raise a "Bad response" error if the page 404s