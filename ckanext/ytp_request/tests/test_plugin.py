# encoding: utf-8

import pytest
import mock
from ckan.lib.helpers import url_for

import ckan.logic as logic
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


@pytest.mark.ckan_config(u'ckan.plugins', u'ytp_request')
@pytest.mark.ckan_config(u'ckanext.ytp_request.include', u'')
@pytest.mark.ckan_config(u'ckanext.ytp_request.exclude', u'')
@pytest.mark.usefixtures(u'with_plugins')
@pytest.mark.usefixtures(u'with_request_context')
def test_available_organizations_return_single_entry_per_name():
    org = factories.Organization()
    member = factories.User()
    sysadmin = factories.Sysadmin()

    helpers.call_action(
        'member_create',
        {'user': sysadmin['name']},
        id=org['name'],
        object=member['name'],
        object_type='user',
        capacity='member',
    )

    organisations = helpers.call_action(
        'get_available_organizations',
        {'user': member['name']},
    )

    matches = [o for o in organisations if o['name'] == org['name']]
    assert len(matches) == 1


@pytest.mark.ckan_config(u'ckan.plugins', u'ytp_request')
@pytest.mark.ckan_config(u'ckanext.ytp_request.include', u'')
@pytest.mark.ckan_config(u'ckanext.ytp_request.exclude', u'')
@pytest.mark.ckan_config(u'ckanext.oidc_pkce_bpa.role_org_mapping', u'{"managed-role": "managed-org"}')
@pytest.mark.usefixtures(u'with_plugins')
@pytest.mark.usefixtures(u'with_request_context')
def test_available_organizations_excludes_oidc_managed_org():
    managed_org = factories.Organization(name=u'managed-org')
    open_org = factories.Organization(name=u'open-org')
    requester = factories.User()

    organisations = helpers.call_action(
        'get_available_organizations',
        {'user': requester['name']},
    )

    names = {o['name'] for o in organisations}
    assert managed_org['name'] not in names
    assert open_org['name'] in names


@pytest.mark.ckan_config(u'ckan.plugins', u'ytp_request')
@pytest.mark.ckan_config(u'ckanext.oidc_pkce_bpa.role_org_mapping', u'{"managed-role": "managed-org"}')
@pytest.mark.usefixtures(u'with_plugins')
@pytest.mark.usefixtures(u'with_request_context')
def test_member_request_create_blocked_for_oidc_managed_org():
    managed_org = factories.Organization(name=u'managed-org')
    requester = factories.User()

    with pytest.raises(logic.NotAuthorized):
        helpers.call_action(
            'member_request_create',
            {'user': requester['name']},
            group=managed_org['name'],
            role='member',
        )


@pytest.mark.ckan_config(u'ckan.plugins', u'ytp_request')
@pytest.mark.ckan_config(u'ckanext.oidc_pkce_bpa.role_org_mapping', u'{"managed-role": "managed-org"}')
@pytest.mark.usefixtures(u'with_plugins')
@pytest.mark.usefixtures(u'with_request_context')
def test_membership_cancel_blocked_for_oidc_managed_org():
    managed_org = factories.Organization(name=u'managed-org')
    requester = factories.User()
    sysadmin = factories.Sysadmin()

    helpers.call_action(
        'member_create',
        {'user': sysadmin['name']},
        id=managed_org['name'],
        object=requester['name'],
        object_type='user',
        capacity='member',
    )

    with pytest.raises(logic.NotAuthorized):
        helpers.call_action(
            'member_request_membership_cancel',
            {'user': requester['name']},
            organization_id=managed_org['id'],
        )
