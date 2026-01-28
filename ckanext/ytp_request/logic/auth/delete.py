from ckan.common import c, _
from ckanext.ytp_request.helper import get_user_member, is_oidc_managed_organization
import logging
log = logging.getLogger(__name__)


def _member_common_access_check(context, data_dict, status):
    if not c.userobj:
        return {'success': False}

    organization_id = data_dict.get("organization_id")
    if not organization_id:
        return {'success': False}

    if is_oidc_managed_organization(organization_id):
        return {
            'success': False,
            'msg': _('Membership for this organization is managed automatically via Auth0 roles.'),
        }

    member = get_user_member(organization_id, state=status)

    if not member:
        return {'success': False}

    if member.table_name == 'user' and member.table_id == c.userobj.id and member.state == status:
        return {'success': True}
    return {'success': False}


def member_request_membership_cancel(context, data_dict):
    return _member_common_access_check(context, data_dict, 'active')


def member_request_cancel(context, data_dict):
    return _member_common_access_check(context, data_dict, 'pending')
