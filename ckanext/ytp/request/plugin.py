import ckan.plugins as plugins
from ckan.plugins import implements
from ckan.common import c
import ckantoolkit as toolkit
import logging
import authz
import os
import sys


log = logging.getLogger(__name__)


class YtpRequestPlugin(plugins.SingletonPlugin):

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
        from ckanext.ytp.request.logic.action import get, create, update, delete

        return {
            "member_request_create": create.member_request_create,
            "member_request_cancel": delete.member_request_cancel,
            "member_request_reject": update.member_request_reject,
            "member_request_approve": update.member_request_approve,
            "member_request_membership_cancel": delete.member_request_membership_cancel,
            "member_requests_list": get.member_requests_list,
            "member_requests_mylist": get.member_requests_mylist,
            "get_available_roles": get.get_available_roles,
            "member_request_show": get.member_request
        }

    # IAuthFunctions
    def get_auth_functions(self):
        from ckanext.ytp.request.logic.auth import get, create, update, delete

        return {
            "member_request_create": create.member_request_create,
            "member_request_cancel": delete.member_request_cancel,
            "member_request_reject": update.member_request_reject,
            "member_request_approve": update.member_request_approve,
            "member_request_membership_cancel": delete.member_request_membership_cancel,
            "member_requests_list": get.member_requests_list,
            "member_requests_mylist": get.member_requests_mylist,
            "member_request_show": get.member_request
        }

    # IRoutes #
    def before_map(self, m):
        """ CKAN autocomplete discards vocabulary_id from request. Create own api for this. """
        controller = 'ckanext.ytp.request.controller:YtpRequestController'
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

    # ITranslation

    def i18n_directory(self):
        '''Change the directory of the *.mo translation files

        The default implementation assumes the plugin is
        ckanext/myplugin/plugin.py and the translations are stored in
        i18n/
        '''
        # assume plugin is called ckanext.<myplugin>.<...>.PluginClass
        plugin_module_name = '.'.join(self.__module__.split('.')[:4])
        plugin_module = sys.modules[plugin_module_name]
        plugin_module_path = os.path.join(os.path.dirname(plugin_module.__file__))
        i18n_path = "/".join(plugin_module_path.split('/')[:-3] + ['i18n'])
        return i18n_path

    def i18n_locales(self):
        '''Change the list of locales that this plugin handles

        By default the will assume any directory in subdirectory in the
        directory defined by self.directory() is a locale handled by this
        plugin
        '''
        directory = self.i18n_directory()
        return [ d for
                 d in os.listdir(directory)
                 if os.path.isdir(os.path.join(directory, d))
        ]

    def i18n_domain(self):
        '''Change the gettext domain handled by this plugin

        This implementation assumes the gettext domain is
        ckanext-{extension name}, hence your pot, po and mo files should be
        named ckanext-{extension name}.mo'''
        return 'ckanext-{name}'.format(name=self.name)
