import ast
import json
import logging
from functools import lru_cache
from typing import FrozenSet, Iterable

from ckan import model, authz
from ckan.common import c
from ckan.lib import helpers
from sqlalchemy.sql.expression import or_
from ckan.plugins.toolkit import config
from ckan.plugins import toolkit

log = logging.getLogger(__name__)


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

    # Only allow to logged in users as member_requests_mylist needs a user
    if not authz.auth_is_loggedin_user():
        return False

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

def is_org_autoregister(organization):
    """Determine if the organization is set for autoregistration"""

    return organization["name"] in config.get('ckanext.ytp_request.autoregister').split()


def _iter_org_identifiers(raw_value) -> Iterable[str]:
    if isinstance(raw_value, str):
        cleaned = raw_value.strip()
        if cleaned:
            yield cleaned
        return

    try:
        iterator = iter(raw_value)
    except TypeError:
        return

    for value in iterator:
        if isinstance(value, str):
            cleaned = value.strip()
            if cleaned:
                yield cleaned


def _load_role_org_mapping() -> FrozenSet[str]:
    mapping_raw = config.get('ckanext.oidc_pkce_bpa.role_org_mapping')
    if not mapping_raw:
        return frozenset()

    parsed = None
    try:
        parsed = json.loads(mapping_raw)
    except json.JSONDecodeError:
        try:
            parsed = ast.literal_eval(mapping_raw)
        except (ValueError, SyntaxError):
            log.warning(
                "Unable to parse 'ckanext.oidc_pkce_bpa.role_org_mapping'; expected JSON or Python literal. Value: %r",
                mapping_raw,
            )
            return frozenset()

    if not isinstance(parsed, dict):
        log.warning(
            "Configuration 'ckanext.oidc_pkce_bpa.role_org_mapping' must be a mapping. Ignoring value: %r",
            mapping_raw,
        )
        return frozenset()

    names = set()
    for role, orgs in parsed.items():
        for org in _iter_org_identifiers(orgs):
            if org:
                names.add(org)

    return frozenset(names)


@lru_cache(maxsize=1)
def oidc_managed_org_identifiers() -> FrozenSet[str]:
    """Return organisation identifiers managed via Auth0 role mapping."""
    return _load_role_org_mapping()


def is_oidc_managed_organization(organization_identifier: str) -> bool:
    """Return True when the given organization is managed externally via OIDC."""
    if not organization_identifier:
        return False

    managed_names = oidc_managed_org_identifiers()
    if not managed_names:
        return False

    group = model.Group.get(organization_identifier)
    if group is None:
        return organization_identifier in managed_names

    identifiers = {str(group.id)}
    if group.name:
        identifiers.add(group.name)

    return any(identifier in managed_names for identifier in identifiers)
