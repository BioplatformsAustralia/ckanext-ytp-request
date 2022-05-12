from ckan.lib.i18n import set_lang, get_lang
from ckan.lib.mailer import mail_user
from pylons import i18n
from ckan.common import _
import logging

log = logging.getLogger(__name__)


def _SUBJECT_MEMBERSHIP_REQUEST():
    return _(
            "New membership request (%(organization)s)")


def _MESSAGE_MEMBERSHIP_REQUEST():
    return _("""\
User %(user)s (%(email)s) has requested membership to organization:
    %(organization)s.

%(link)s

Please click on the link above to either approve or deny their request.

Details of their request are:

%(user_message)s

Current memberships and requests for this user can be viewed by clicking the link below:
    %(status_link)s

Best wishes,
%(sitename)s
%(siteemail)s
""")


def _SUBJECT_MEMBERSHIP_AUTOAPPROVED():
    return _(
        "Organization membership automatically approved (%(organization)s)"
    )


def _MESSAGE_MEMBERSHIP_AUTOAPPROVED():
    return _(
        """\
Your membership request to access data from %(organization)s as
a %(role)s has been automatically approved.  

Please log in using your username - %(username)s (do not use your email).
 
For information on how to find or download data from the portal, please see 
our support guides at:
    https://usersupport.bioplatforms.com/

Please make sure you check the Data Use Agreement for the initiative.

Feel free to contact us if you have any questions.
 

Best wishes,
%(sitename)s
%(siteemail)s
"""
    )


def _SUBJECT_MEMBERSHIP_APPROVED():
    return _(
        "Organization membership approved (%(organization)s)"
    )


def _MESSAGE_MEMBERSHIP_APPROVED():
    return _(
        """\
Your membership request to access data from %(organization)s as
a %(role)s has been approved.  

Please log in using your username - %(username)s (do not use your email).
 
For information on how to find or download data from the portal, please see 
our support guides at:
    https://usersupport.bioplatforms.com/

Please make sure you check the Data Use Agreement for the initiative.

Feel free to contact us if you have any questions.
 

Best wishes,
%(sitename)s
%(siteemail)s
"""
    )


def _SUBJECT_MEMBERSHIP_REJECTED():
    return _(
        "Organization membership rejected (%(organization)s)"
    )


def _MESSAGE_MEMBERSHIP_REJECTED():
    return _(
        """\
Unfortunately, your membership request to access data from %(organization)s has not been granted. 

This is because:
%(reason)s

If you think this was a mistake, please contact the initiatives project manager directly.

Please make sure you check the Data Use Agreement for the initiative.


Best wishes,
%(sitename)s
%(siteemail)s
"""
    )


def mail_new_membership_request(locale, admin, group_name, member_request_show_url, user_name, user_email, site_name, site_email, user_message, member_request_status_url):

    subject = _SUBJECT_MEMBERSHIP_REQUEST() % {
        'organization': group_name
    }
    message = _MESSAGE_MEMBERSHIP_REQUEST() % {
        'user': user_name,
        'email': user_email,
        'organization': group_name,
        'link': member_request_show_url,
        'user_message': user_message,
        'sitename': site_name,
        'siteemail': site_email,
        'status_link': member_request_status_url
    }
    headers = {
        'Reply-To': "{} <{}>".format(user_name, user_email),
    }

    try:
        mail_user(admin, subject, message, headers)
    except Exception:
        log.exception(message)
        log.exception("Mail could not be sent")


def mail_process_status(locale, member_user, action, approve, group_name, capacity, site_name, site_email, reason=None):
    current_locale = get_lang()
    if locale == 'en':
        _reset_lang()
    else:
        set_lang(locale)

    role_name = _(capacity)

    if approve and action is 'autoapprove':
        subject_template = _SUBJECT_MEMBERSHIP_AUTOAPPROVED()
    elif approve:
        subject_template = _SUBJECT_MEMBERSHIP_APPROVED()
    else:
        subject_template = _SUBJECT_MEMBERSHIP_REJECTED()

    if approve and action is 'autoapprove':
        message_template = _MESSAGE_MEMBERSHIP_AUTOAPPROVED()
    elif approve:
        message_template = _MESSAGE_MEMBERSHIP_APPROVED()
    else:
        message_template = _MESSAGE_MEMBERSHIP_REJECTED()

    subject = subject_template % {
        'organization': group_name
    }
    message = message_template % {
        'role': role_name,
        'organization': group_name,
        'sitename': site_name,
        'siteemail': site_email,
        'reason': reason,
        'username': member_user.name,
    }

    try:
        mail_user(member_user, subject, message)
    except Exception:
        log.exception("Mail could not be sent")
        # raise MailerException("Mail could not be sent")
    finally:
        set_lang(current_locale)


def _reset_lang():
    try:
        i18n.set_lang(None)
    except TypeError:
        pass
