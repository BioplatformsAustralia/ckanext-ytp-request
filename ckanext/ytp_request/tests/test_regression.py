# encoding: utf-8

import pytest
import mock
import ckan.model as model
import ckanext.ytp_request.model as rmodel
from ckan.logic import ValidationError
import ckan.tests.helpers as helpers
import ckan.tests.factories as factories


@pytest.fixture
def initdb():
    model.Session.remove()
    model.Session.configure(bind=model.meta.engine)
    rmodel.init_tables()


@pytest.mark.usefixtures(u'initdb')
@pytest.mark.usefixtures(u'clean_db')
@pytest.mark.ckan_config(u'ckan.plugins', u'ytp_request')
@pytest.mark.usefixtures(u'with_plugins')
@pytest.mark.usefixtures(u'with_request_context')
@pytest.mark.usefixtures(u'mail_server')
class TestRegression(object):
    '''
        Regression tests to ensure previous bugs do not re-occur.
    '''

    @mock.patch('ckanext.ytp_request.request.logic.action.create.flash_success')  # mock1
    @mock.patch('ckanext.ytp_request.request.logic.action.update.flash_success')  # mock2
    def test_update_request_with_all_valid_roles(self, update_success, create_success, app):
        """
        Checks that the member request can be updated using any of the valid
        roles returned by core ckan member_roles_list action.
        """
        org = factories.Organization()
        sysadmin = factories.Sysadmin()
        regular_user = factories.User()

        # Get all valid roles
        valid_roles = helpers.call_action('member_roles_list', {})
        valid_roles = [r['value'] for r in valid_roles] + [None]

        for (count, role) in enumerate(valid_roles):
            # user creates membership request
            membership_request = helpers.call_action(
                'member_request_create',
                {'user': regular_user['name']},
                group=org['name'],
                role='editor'
            )

            # admin approves membership
            helpers.call_action(
                'member_request_approve',
                {'user': sysadmin['name']},
                approve='approve',
                mrequest_id=membership_request['id'],
                role=role
            )

            assert update_success.call_count == count+1, "Failed with role {}".format(role)

    @mock.patch('ckanext.ytp_request.request.logic.action.create.flash_success')  # mock1
    @mock.patch('ckanext.ytp_request.request.logic.action.update.flash_success')  # mock2
    def test_update_request_fails_for_invalid_roles(self, update_success, create_success, app):
        """
        Checks that the member request cannot be approved with an invalid role.
        """

        org = factories.Organization()
        sysadmin = factories.Sysadmin()
        regular_user = factories.User()

        # user creates membership request
        membership_request = helpers.call_action(
            'member_request_create',
            {'user': regular_user['name']},
            group=org['name'],
            role='editor'
        )

        invalid_role = "invalidrole"

        with pytest.raises(ValidationError):
            # admin updates membership request role and approves
            helpers.call_action(
                'member_request_approve',
                {'user': sysadmin['name']},
                approve='approve',
                mrequest_id=membership_request['id'],
                role=invalid_role
            )
