import ckan.plugins as plugins
from ckan.plugins import implements, toolkit
from ckan.lib.plugins import DefaultTranslation
import logging
from .cli import get_commands
from . import views
from .helper import get_member_request_list

log = logging.getLogger(__name__)


class YtpRequestPlugin(plugins.SingletonPlugin, DefaultTranslation):
    implements(plugins.IConfigurer, inherit=True)
    implements(plugins.IActions, inherit=True)
    implements(plugins.IAuthFunctions, inherit=True)
    implements(plugins.ITranslation)
    implements(plugins.IClick)
    implements(plugins.IBlueprint)
    implements(plugins.ITemplateHelpers)

    # IConfigurer #
    def update_config(self, config):
        toolkit.add_template_directory(config, 'templates')
        toolkit.add_public_directory(config, 'public')
        toolkit.add_resource('public', 'request_js')
        toolkit.add_resource('fanstatic', 'request')
        logging.warning("ytp_request plugin enabled")

    def get_helpers(self):

        def is_admin(user):
            """Determine if current user is an admin of any organization"""
            if authz.is_sysadmin(user):
                return True
            context = {'user': c.user or c.author }

            mylist = toolkit.get_action(
                'member_requests_mylist')(context, {})

            return len([o for o in mylist if o['role'] == 'admin' and o['state'] == 'active']) > 0

        def is_sysadmin(user):
            """Determine if current user is sys admin"""
            return authz.is_sysadmin(user)

        def get_list(org_id='hello'):
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

        def pending_approvals():
            """Get count of pending membership approval requests"""
            return len(get_list(org_id=None))

        def get_available_organizations():
            """Return the list of publicly available organizations to join"""
            context = {}

            return toolkit.get_action(
                'get_available_organizations')(context, {})

        return {
            'is_sysadmin': is_sysadmin,
            'is_admin': is_admin,
            'get_member_request_list': get_list,
            'get_available_organizations': get_available_organizations,
            'pending_approvals': pending_approvals,
        }

    # IActions
    def get_actions(self):
        from ckanext.ytp_request.logic.action import get, create, update, delete

        return {
            "member_request_create": create.member_request_create,
            "member_request_cancel": delete.member_request_cancel,
            "member_request_remove": update.member_request_remove,
            "member_request_reject": update.member_request_reject,
            "member_request_approve": update.member_request_approve,
            "member_request_autoapprove": update.member_request_autoapprove,
            "member_request_membership_cancel": delete.member_request_membership_cancel,
            "member_requests_list": get.member_requests_list,
            "member_requests_mylist": get.member_requests_mylist,
            "member_requests_status": get.member_requests_status,
            "get_available_roles": get.get_available_roles,
            "get_available_organizations": get.get_available_organizations,
            "member_request_show": get.member_request,
            "organization_list_without_memberships": get.organization_list_without_memberships,
        }

    # IAuthFunctions
    def get_auth_functions(self):
        from ckanext.ytp_request.logic.auth import get, create, update, delete

        return {
            "member_request_create": create.member_request_create,
            "member_request_cancel": delete.member_request_cancel,
            "member_request_remove": update.member_request_remove,
            "member_request_reject": update.member_request_reject,
            "member_request_approve": update.member_request_approve,
            "member_request_autoapprove": update.member_request_autoapprove,
            "member_request_membership_cancel": delete.member_request_membership_cancel,
            "member_requests_list": get.member_requests_list,
            "member_requests_mylist": get.member_requests_mylist,
            "member_requests_status": get.member_requests_status,
            "member_request_show": get.member_request,
            "organization_list_without_memberships": get.organization_list_without_memberships,
        }

    # IClick
    def get_commands(self):
        return get_commands()

    # IBlueprint
    def get_blueprint(self):
        return views.get_blueprint()

    # ITemplateHelpers
    def get_helpers(self):
        return {
            'get_member_request_list': get_member_request_list
        }
