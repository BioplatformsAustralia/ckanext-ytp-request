from ckan import model, logic, authz
from ckan.lib.dictization import model_dictize
from ckan.common import _
from pylons import config
from ckanext.ytp_request.model import MemberRequest
from ckan.lib.helpers import url_for, flash_success
from ckanext.ytp_request.mail import mail_new_membership_request
from ckanext.ytp_request.helper import get_safe_locale
import logging
import os

log = logging.getLogger(__name__)


def member_request_create(context, data_dict):
    '''
    Create new member request. User is taken from context.
    Sysadmins should not be able to create "member" requests since they have
    full access to all organizations
    :param group: name of the group or organization
    :type group: string
    '''
    logic.check_access('member_request_create', context, data_dict)
    member = _create_member_request(context, data_dict)
    return model_dictize.member_dictize(member, context)


def _create_member_request(context, data_dict):
    """ Helper to create member request """
    role = data_dict.get('role', None)
    if not role:
        raise logic.NotFound
    group = model.Group.get(data_dict.get('group', None))
    if not group or group.type != 'organization':
        raise logic.NotFound

    message = data_dict.get('message', "")

    user = context.get('user', None)

    if authz.is_sysadmin(user):
        raise logic.ValidationError({}, {_("Role"): _(
            "As a sysadmin, you already have access to all organizations")})

    userobj = model.User.get(user)

    member = model.Session.query(model.Member) \
        .filter(model.Member.table_name == "user") \
        .filter(model.Member.table_id == userobj.id) \
        .filter(model.Member.group_id == group.id).first()

    # If there is a member for this organization and it is NOT deleted. Reuse
    # existing if deleted
    if member:
        if member.state == 'pending':
            message = _(
                "You already have a pending request to the organization")
        elif member.state == 'active':
            message = _("You are already part of the organization")
        # Unknown status. Should never happen..
        elif member.state != 'deleted':
            raise logic.ValidationError(
                {"organization": _("Duplicate organization request")},
                {_("Organization"): message}
            )
    else:
        member = model.Member(table_name="user", table_id=userobj.id,
                              group_id=group.id, capacity=role, state='pending')

    # TODO: Is there a way to get language associated to all admins.
    # User table there is nothing as such stored
    locale = get_safe_locale()

    member.state = 'pending'
    member.capacity = role
    member.group = group

    revision = model.repo.new_revision()
    revision.author = user
    revision.message = u'New member request'

    logging.warning("Member's Group ID: " + str(type(member.group_id)))
    logging.warning(repr(member))

    model.Session.add(member)
    # We need to flush since we need membership_id (member.id) already
    model.Session.flush()

    memberRequest = MemberRequest(
        membership_id=member.id,
        role=role,
        message=message,
        status="pending",
        language=locale)
    member_id = member.id
    model.Session.add(memberRequest)
    model.repo.commit()

    fetched_member = model.Session.query(model.Member).filter(
        model.Member.id == member_id
    ).first()
    logging.warning(repr(group))
    logging.warning("Fetched member's group ID: " + str(fetched_member.group_id))

    url = config.get('ckan.site_url', "")
    site_name = config.get('ckan.site_description', "")
    site_email = os.environ.get('BIOPLATFORMS_HELPDESK_ADDRESS',config.get('error_email_from', ""))

    if url:
        url = url + url_for('member_request_show', mrequest_id=member.id)
    # Locale should be admin locale since mail is sent to admins
    if role == 'admin':
        for admin in _get_ckan_admins():
            mail_new_membership_request(
                locale, admin, group.display_name, url, userobj.display_name, userobj.email, site_name, site_email, message)
    else:
        for admin in _get_organization_admins(group.id):
            mail_new_membership_request(
                locale, admin, group.display_name, url, userobj.display_name, userobj.email, site_name, site_email, message)

    flash_success(
        _("Membership request sent to organisation administrator")
    )

    return member


def _get_organization_admins(group_id):
    admins = set(
        model.Session.query(model.User)
        .join(model.Member, model.User.id == model.Member.table_id)
        .filter(model.Member.table_name == "user")
        .filter(model.Member.group_id == group_id)
        .filter(model.Member.state == 'active')
        .filter(model.Member.capacity == 'admin')
    )

    admins.update(set(
        model.Session.query(model.User).filter(model.User.sysadmin is True)
    ))  # noqa

    return admins


def _get_ckan_admins():
    admins = set(
        model.Session.query(model.User).filter(model.User.sysadmin is True)
    )  # noqa

    return admins
