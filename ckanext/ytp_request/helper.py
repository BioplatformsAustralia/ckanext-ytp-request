from ckan import model, authz
from ckan.common import c
from ckan.lib import helpers
from sqlalchemy.sql.expression import or_
from ckan.plugins.toolkit import config
from ckan.plugins import toolkit


def get_user_member(organization_id, user_id=None, state=None):
    """ Helper function to get member states """
    if user_id is None:
        user_id = c.userobj.id

    state_query = None
    if not state:
        state_query = or_(model.Member.state == 'active',
                          model.Member.state == 'pending')
    else:
        state_query = or_(model.Member.state == state)

    query = model.Session.query(model.Member) \
        .filter(state_query) \
        .filter(model.Member.table_name == 'user') \
        .filter(model.Member.group_id == organization_id)\
        .filter(model.Member.table_id == user_id)
    return query.first()


def get_organization_admins(group_id):
    admins = set(model.Session.query(model.User).join(model.Member, model.User.id == model.Member.table_id).
                 filter(model.Member.table_name == "user").filter(model.Member.group_id == group_id).
                 filter(model.Member.state == 'active').filter(model.Member.capacity == 'admin'))

    return admins


def get_ckan_admins():
    admins = set(model.Session.query(model.User).filter(model.User.sysadmin == True))  # noqa

    return admins


def get_default_locale():
    return config.get('ckan.locale_default', 'en')


def get_safe_locale():
    return helpers.lang()


def get_member_request_list(org_id='hello'):
    """Get membership requests filtered by organisation ID"""
    context = {'user': c.user or c.author}
    member_requests = toolkit.get_action(
            'member_requests_list'
    )(context, {})
    if org_id:
        member_requests = filter(
            lambda x: x['group_id'] == org_id,
            member_requests
        )
    return member_requests


def is_admin(user):
    """Determine if current user is an admin of any organization"""
    if authz.is_sysadmin(user):
        return True
    context = {'user': c.user or c.author }

    mylist = toolkit.get_action(
        'member_requests_mylist')(context, {})

    return len([o for o in mylist if o['role'] == 'admin' and o['state'] == 'active']) > 0


def pending_approvals():
    """Get count of pending membership approval requests"""
    return len(get_member_request_list(org_id=None))


def get_available_organizations():
    """Return the list of publicly available organizations to join"""
    context = {}

    return toolkit.get_action(
        'get_available_organizations')(context, {})
