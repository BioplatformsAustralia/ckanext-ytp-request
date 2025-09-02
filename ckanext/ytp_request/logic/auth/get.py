import logging
import ckan.plugins.toolkit as tk
from ckan import model, authz
from ckan.common import g, c, config, _
from ckan.logic.auth import get_package_object
from ckanext.ytp_request.helper import get_user_member

log = logging.getLogger(__name__)


def member_request(context, data_dict):
    """ Only allowed to sysadmins or organization admins """
    if not c.userobj:
        return {'success': False}

    if authz.is_sysadmin(c.user):
        return {'success': True}

    membership = model.Member.get(data_dict.get("mrequest_id"))
    if not membership:
        return {'success': False}

    if membership.table_name != 'user':
        return {'success': False}

    query = (model.Session.query(model.Member)
                          .filter(model.Member.state == 'active')
                          .filter(model.Member.table_name == 'user')
                          .filter(model.Member.capacity == 'admin')
                          .filter(model.Member.table_id == c.userobj.id)
                          .filter(model.Member.group_id == membership.group_id))
    return {'success': query.count() > 0}


def member_requests_mylist(context, data_dict):
    """ Show request access check """
    # TODO: Sysadmins dont have this functionality since it is pointless. Make
    # it at the logical level
    return _only_registered_user()


def member_requests_list(context, data_dict):
    """ Show request access check """
    return _only_registered_user()


def member_requests_status(context, data_dict):
    """ Show request access check """
    return _only_admin_user()


def _only_registered_user():
    if not authz.auth_is_loggedin_user():
        return {'success': False, 'msg': _('User is not logged in')}
    return {'success': True}


def _only_admin_user():
    """ Only allowed to sysadmins or organization admins """
    if not authz.auth_is_loggedin_user():
        return {'success': False, 'msg': _('User is not logged in')}

    if not c.userobj:
        return {'success': False}

    if authz.is_sysadmin(c.user):
        return {'success': True}

    # Can be an admin in any group
    query = model.Session.query(model.Member) \
        .filter(model.Member.state == 'active') \
        .filter(model.Member.table_name == 'user') \
        .filter(model.Member.capacity == 'admin') \
        .filter(model.Member.table_id == c.userobj.id)
    return {'success': query.count() > 0}


def organization_list_without_memberships(context, data_dict):
    return {'success': True}

def _get_username_from_context(context):
    auth_user_obj = context.get("auth_user_obj", None)
    user_name = ""
    if auth_user_obj:
        user_name = auth_user_obj.as_dict().get("name", "")
    else:
        if authz.get_user_id_for_username(context.get("user"), allow_none=True):
            user_name = context.get("user", "")
    return user_name

def _apply_on_access(context, package):
    user_name = _get_username_from_context(context)
    user_id = authz.get_user_id_for_username(user_name)

    if not isinstance(package, dict):
        package = package.as_dict()
    # Get organisation for package
    pkg_organization_id = package.get("owner_org", "")

    # Check if user is already part of org
    if get_user_member(pkg_organization_id, user_id):
        return

    # Check if organisation is autoregister
    org = tk.get_action('organization_show')(data_dict={'id': pkg_organization_id})
    if 'name' not in org:   #something hinky here
        return

    if org['name'] not in config.get('ckanext.ytp_request.autoregister').split():
        # Not an autoapprove org
        return

    # Apply for access automagically
    try:
        log.info("Create automatic registration on access for %s to %s for package %s" % (user_name, org.get("name"), package.get("name")))
        data_dict = {
                'user': user_name,
                'role': 'member',
                'group': org.get("id"),
                'message': 'Registration on access',
            }
        member = tk.get_action(
            'member_request_create')(context, data_dict)
    except:
        log.warn("Failed to create automatic registration on access for %s to %s for package %s" % (user_name, org.get("name"), package.get("name")))

    return

@tk.auth_allow_anonymous_access
@tk.chained_auth_function
def package_show(next_auth, context, data_dict=None):
    # if not enabled, fall through
    if tk.asbool(config.get('ckanext.ytp_request.autoregister_on_access', False)):
        return next_auth(context, data_dict)

    # no user, fall through
    if not c.userobj:
        return next_auth(context, data_dict)

    package = get_package_object(context, data_dict)

    _apply_on_access(context, package)
    # fall through
    return next_auth(context, data_dict)
