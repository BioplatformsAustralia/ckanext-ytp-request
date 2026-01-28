from ckanext.ytp_request.helper import get_user_member, is_oidc_managed_organization
from ckan import authz
import logging
from ckan.common import _
log = logging.getLogger(__name__)


def member_request_create(context, data_dict):
    """ Only allow to logged in users """
    if not authz.auth_is_loggedin_user():
        return {'success': False, 'msg': _('User is not logged in')}

    organization_id = None if not data_dict else data_dict.get('organization_id')
    organization_identifier = organization_id or (data_dict.get('group') if data_dict else None)

    if organization_identifier and is_oidc_managed_organization(organization_identifier):
        return {
            'success': False,
            'msg': _('Membership for this organization is managed automatically via Auth0 roles.'),
        }

    if organization_id:
        member = get_user_member(organization_id)
        if member:
            return {'success': False, 'msg': _('The user has already a pending request or an active membership')}
    return {'success': True}
