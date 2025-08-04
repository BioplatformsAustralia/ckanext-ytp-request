import ckan.plugins as plugins
from ckan.plugins import implements, toolkit
from ckan.lib.plugins import DefaultTranslation
import logging
from .cli import get_commands
from . import views
from .helper import (
        get_member_request_list, 
        is_admin,
        get_available_organizations,
        pending_approvals,
        is_org_autoregister,
    )

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
        toolkit.add_resource('fanstatic', 'request_css')
        logging.warning("ytp_request plugin enabled")

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
            'get_member_request_list': get_member_request_list,
            'is_admin': is_admin,
            'get_available_organizations': get_available_organizations,
            'pending_approvals': pending_approvals,
            'is_org_autoregister': is_org_autoregister,
        }
