import ckan.plugins as plugins
from ckan.plugins import implements
from ckan.common import c
from ckan.lib.plugins import DefaultTranslation

import ckantoolkit as toolkit
import logging
import authz


log = logging.getLogger(__name__)


class YtpRequestPlugin(plugins.SingletonPlugin, DefaultTranslation):

    implements(plugins.IRoutes, inherit=True)
    implements(plugins.IConfigurer, inherit=True)
    implements(plugins.IActions, inherit=True)
    implements(plugins.IAuthFunctions, inherit=True)
    implements(plugins.ITemplateHelpers)
    implements(plugins.ITranslation)

    # IConfigurer #
    def update_config(self, config):
        toolkit.add_template_directory(config, 'templates')
        toolkit.add_public_directory(config, 'public')
        toolkit.add_resource('public/javascript/', 'request_js')
        logging.warning("ytp_request plugin enabled")

    def get_helpers(self):

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

        return {
            'is_sysadmin': is_sysadmin,
            'get_member_request_list': get_list
        }

    # IActions
    def get_actions(self):
        from ckanext.ytp_request.logic.action import get, create, update, delete

        return {
            "member_request_create": create.member_request_create,
            "member_request_cancel": delete.member_request_cancel,
            "member_request_reject": update.member_request_reject,
            "member_request_approve": update.member_request_approve,
            "member_request_autoapprove": update.member_request_autoapprove,
            "member_request_membership_cancel": delete.member_request_membership_cancel,
            "member_requests_list": get.member_requests_list,
            "member_requests_mylist": get.member_requests_mylist,
            "get_available_roles": get.get_available_roles,
            "member_request_show": get.member_request
        }

    # IAuthFunctions
    def get_auth_functions(self):
        from ckanext.ytp_request.logic.auth import get, create, update, delete

        return {
            "member_request_create": create.member_request_create,
            "member_request_cancel": delete.member_request_cancel,
            "member_request_reject": update.member_request_reject,
            "member_request_approve": update.member_request_approve,
            "member_request_autoapprove": update.member_request_autoapprove,
            "member_request_membership_cancel": delete.member_request_membership_cancel,
            "member_requests_list": get.member_requests_list,
            "member_requests_mylist": get.member_requests_mylist,
            "member_request_show": get.member_request
        }

    # IRoutes #
    def before_map(self, m):
        """ CKAN autocomplete discards vocabulary_id from request. Create own api for this. """
        controller = 'ckanext.ytp_request.controller:YtpRequestController'
        m.connect('member_request_create', '/member-request/new',
                  action='new', controller=controller)
        m.connect('member_requests_mylist', '/member-request/mylist',
                  action='mylist', controller=controller)
        m.connect('member_requests_list', '/member-request/list',
                  action='list', controller=controller)
        m.connect('member_request_reject',
                  '/member-request/reject/{mrequest_id}', action='reject', controller=controller)
        m.connect('member_request_approve',
                  '/member-request/approve/{mrequest_id}', action='approve', controller=controller)
        m.connect('member_request_cancel', '/member-request/cancel',
                  action='cancel', controller=controller)
        m.connect('member_request_membership_cancel',
                  '/member-request/membership-cancel/{organization_id}', action='membership_cancel', controller=controller),
        m.connect('member_request_show',
                  '/member-request/{mrequest_id}', action='show', controller=controller)
        return m

    # ITranslations
    def i18n_domain(self):
        domain = 'ckanext-ytp-request'
        return domain
