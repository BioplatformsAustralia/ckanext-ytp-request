import logging
from ckanext.ytp_request.helper import get_user_member
from ckan import authz, model
from ckan.common import _, config
import ckan.plugins.toolkit as toolkit

log = logging.getLogger(__name__)


def member_request_approve(context, data_dict):
    return _check_admin_access(context, data_dict)


def member_request_reject(context, data_dict):
    return _check_admin_access(context, data_dict)


def _check_admin_access(context, data_dict):
    """ Approve access check """
    if authz.is_sysadmin(context.get('user', None)):
        return {'success': True}

    user = model.User.get(context.get('user', None))
    if not user:
        return {'success': False}

    member = model.Member.get(data_dict.get("mrequest_id"))
    if not member:
        return {'success': False}

    if member.table_name != 'user':
        return {'success': False}

    query = model.Session.query(model.Member) \
        .filter(model.Member.state == 'active') \
        .filter(model.Member.table_name == 'user') \
        .filter(model.Member.capacity == 'admin') \
        .filter(model.Member.table_id == user.id) \
        .filter(model.Member.group_id == member.group_id)

    return {'success': query.count() > 0}


def member_request_autoapprove(context, data_dict):
    """ Only allow to logged in users """
    if not authz.auth_is_loggedin_user():
        return {'success': False, 'msg': _('User is not logged in')}

    organization_id = None if not data_dict else data_dict.get(
        'organization_id', None)
    if organization_id:
        org = toolkit.get_action('organization_show')(data_dict={'id': organization_id})
	if 'name' not in org:
            return {'success': False, 'msg': _('Organization not found')}

        if org['name'] not in config.get('ckanext.ytp_request.autoregister').split():
            return {'success': False, 'msg': _('Organization not available to be auto-approved')}

        member = get_user_member(organization_id, state='active')
        if member:
            return {'success': False, 'msg': _('The user already has an active membership')}
    return {'success': True}
