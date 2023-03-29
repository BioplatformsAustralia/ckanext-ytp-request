from flask import Blueprint
from ckan.plugins import toolkit
from ckan import logic, model, authz


not_auth_message = toolkit._('Unauthorized')
request_not_found_message = toolkit._('Request not found')


member_request = Blueprint('member_request', __name__, url_prefix='/member-request')


def get_blueprint():
    return [member_request]


def _list_organizations(context, errors=None, error_summary=None):
    # TODO: Filter our organizations where the user is already a member or
    # has a pending request

    return toolkit.get_action('get_available_organizations')({}, {})


@member_request.route('/new', methods=['GET', 'POST'])
def new(errors=None, error_summary=None):
    context = {'user': toolkit.g.get('user') or toolkit.g.get('author'),
               'save': 'save' in toolkit.request.args}
    try:
        toolkit.check_access('member_request_create', context)
    except toolkit.NotAuthorized:
        toolkit.abort(401, not_auth_message)

    try:
        my_requests = toolkit.get_action(
            'member_requests_mylist')(context, {})
    except logic.NotAuthorized:
        toolkit.abort(401, self.not_auth_message)

    organizations = _list_organizations(context)

    if toolkit.request.method == 'POST' and not errors:
        success, results = _save_new(context)
        if success:
            member_id = results
            returnto = toolkit.g.get('return', None)
            if returnto:
                return toolkit.redirect_to(returnto)
            return toolkit.redirect_to('member_request.new')
        else:
            errors, error_summary = results

    # FIXME: Don't send as request parameter selected organization. kinda
    # weird
    selected_organization = toolkit.request.args.get(
        'selected_organization', None)
    roles = _get_available_roles(context, selected_organization)
    user_role = 'admin'

    extra_vars = {'selected_organization': selected_organization, 'organizations': organizations,
                  'my_requests': my_requests,
                  'errors': errors or {}, 'error_summary': error_summary or {},
                  'roles': roles, 'user_role': user_role}
    extra_vars['form'] = toolkit.render("request/new_request_form.html", extra_vars=extra_vars)
    return toolkit.render("request/new.html", extra_vars=extra_vars)


def _save_new(context):
    errors = None
    error_summary = None
    try:
        data_dict = {
                'user': toolkit.g.user,
                'role': toolkit.get_or_bust(toolkit.request.form, 'role'),
                'group': toolkit.get_or_bust(toolkit.request.form, 'organization'),
                'message': toolkit.get_or_bust(toolkit.request.form, 'message')}

        # TODO: Do we need info message at the UI level when e-mail could
        # not be sent?
        member = toolkit.get_action(
            'member_request_create')(context, data_dict)
        return (True, member['id'])
    except logic.NotFound:
        toolkit.abort(404, toolkit._('Item not found'))
    except logic.NotAuthorized:
        toolkit.abort(405, not_auth_message)
    except logic.ValidationError as e:
        errors = e.error_dict
        error_summary = e.error_summary
    return (False, (errors, error_summary))


@member_request.route('/mylist')
def mylist():
    """" Lists own members requests (possibility to cancel and view current status)"""
    context = {'user': toolkit.g.get('user') or toolkit.g.get('author')}
    id = toolkit.request.args.get('id', None)
    if not authz.is_sysadmin(toolkit.c.user):
        try:
            my_requests = toolkit.get_action(
                'member_requests_mylist')(context, {})
            message = None
            if id:
                message = toolkit._("Member request processed successfully")
            extra_vars = {'my_requests': my_requests, 'message': message}
            return toolkit.render('request/mylist.html', extra_vars=extra_vars)
        except logic.NotAuthorized:
            toolkit.abort(401, not_auth_message)
    else:
        return toolkit.render('request/mylist.html', extra_vars={
            'my_requests': [],
            'message': toolkit._("As a sysadmin, you already have access to all organizations")})

@member_request.route('/status/<mrequest_user>')
def status(mrequest_user):
    """" Lists members requests for user"""
    context = {'user': toolkit.g.get('user') or toolkit.g.get('author')}
    data_dict = {}
    data_dict['all_fields'] = True
    data_dict['groups'] = []
    data_dict['type'] = 'organization'
    try:
        member_user = model.User.get(mrequest_user)
        organizations = _list_organizations(context)
        all_organizations = toolkit.get_action('organization_list')({}, data_dict)
        status = toolkit.get_action(
            'member_requests_status')(context, {'mrequest_user': mrequest_user})
        message = None
        if id:
            message = toolkit._("Member request processed successfully")
        extra_vars = {
	   'status': status,
	   'mrequest_user': mrequest_user,
           'organizations': organizations,
           'all_organizations': all_organizations,
           "member_user": member_user,
	   'message': message}
        return toolkit.render('request/status.html', extra_vars=extra_vars)
    except logic.NotAuthorized:
        toolkit.abort(401, not_auth_message)

@member_request.route('/list')
def member_requests_list():
    """ Lists member requests to be approved by admins"""
    context = {'user': toolkit.g.get('user') or toolkit.g.get('author')}
    id = toolkit.request.args.get('id', None)
    try:
        member_requests = toolkit.get_action(
            'member_requests_list')(context, {})
        message = None
        if id:
            message = toolkit._("Member request processed successfully")
        extra_vars = {
            'member_requests': member_requests, 'message': message}
        return toolkit.render('request/list.html', extra_vars=extra_vars)
    except logic.NotAuthorized:
        toolkit.abort(401, not_auth_message)


@member_request.route('/reject/<mrequest_id>', methods=['GET', 'POST'])
def reject(mrequest_id):
    """ Controller to reject member request (only admins or group editors can do that """
    return _processbyadmin(mrequest_id, "reject")


@member_request.route('/remove/<mrequest_id>', methods=['GET', 'POST'])
def remove(mrequest_id):
    """ Controller to remove member request (only admins or group editors can do that """
    return _processbyadmin(mrequest_id, "remove")


@member_request.route('/approve/<mrequest_id>', methods=['GET', 'POST'])
def approve(mrequest_id):
    """ Controller to approve member request (only admins or group editors can do that) """
    return _processbyadmin(mrequest_id, "approve")


@member_request.route('/autoapprove/<mrequest_id>', methods=['GET', 'POST'])
def autoapprove(mrequest_id):
    """ Controller to auto approve member request """
    return _process(mrequest_id)


@member_request.route('/cancel', methods=['GET', 'POST'])
def cancel():
    """ Logged in user can cancel pending requests not approved yet by admins/editors"""
    context = {'user': toolkit.g.get('user') or toolkit.g.get('author')}
    organization_id = toolkit.request.args.get('organization_id', None)
    try:
        toolkit.get_action('member_request_cancel')(
            context, {"organization_id": organization_id})
        id = 'cancel'
        returnto = toolkit.g.get('return', None)
        if returnto:
            return toolkit.redirect_to(returnto)
        else:
            return toolkit.redirect_to('member_request.mylist', id=id)
    except logic.NotAuthorized:
        toolkit.abort(401, not_auth_message)
    except logic.NotFound:
        toolkit.abort(404, request_not_found_message)


@member_request.route('/membership-cancel/<organization_id>', methods=['GET', 'POST'])
def membership_cancel(organization_id):
    """ Logged in user can cancel already approved/existing memberships """
    context = {'user': toolkit.g.get('user') or toolkit.g.get('author')}
    try:
        toolkit.get_action('member_request_membership_cancel')(
            context, {"organization_id": organization_id})
        id = 'cancel'
        return toolkit.redirect_to('member_request.mylist', id=id)
    except logic.NotAuthorized:
        toolkit.abort(401, not_auth_message)
    except logic.NotFound:
        toolkit.abort(404, request_not_found_message)


@member_request.route('/<mrequest_id>')
def show(mrequest_id):
    """" Shows a single member request.
    To be used by admins in case they want to modify granted role or accept via e-mail """
    context = {'user': toolkit.g.get('user') or toolkit.g.get('author')}
    try:
        membershipdto = toolkit.get_action('member_request_show')(
            context, {'mrequest_id': mrequest_id})
        member_user = model.Session.query(
            model.User).get(membershipdto['user_id'])
        context = {'user': member_user.name}
        roles = _get_available_roles(
            context, membershipdto['organization_name'])
        extra_vars = {"membership": membershipdto,
                      "member_user": member_user, "roles": roles}
        return toolkit.render('request/show.html', extra_vars=extra_vars)
    except logic.NotFound:
        toolkit.abort(404, request_not_found_message)
    except logic.NotAuthorized:
        toolkit.abort(401, not_auth_message)


def _get_available_roles(context, organization_id):
    data_dict = {'organization_id': organization_id}
    return toolkit.get_action('get_available_roles')(context, data_dict)


def _processbyadmin(mrequest_id, action):
    context = {'user': toolkit.g.get('user') or toolkit.g.get('author')}
    role = toolkit.request.args.get('role', None)
    message = toolkit.request.form.get('message', "")
    data_dict = {"mrequest_id": mrequest_id, 'role': role, 'message': message}
    try:
        if action == 'approve':
            toolkit.get_action('member_request_approve')(
                context, data_dict)
            id = 'approved'
        elif action == 'remove':
            toolkit.get_action('member_request_remove')(
                context, data_dict)
            id = 'removed'
        else:
            toolkit.get_action('member_request_reject')(context, data_dict)
            id = 'rejected'
        return toolkit.redirect_to('member_request.member_requests_list', id=id)
    except logic.NotAuthorized:
        toolkit.abort(401, not_auth_message)
    except logic.NotFound:
        toolkit.abort(404, request_not_found_message)
    except logic.ValidationError as e:
        toolkit.abort(400, str(e))


def _process(mrequest_id):
    context = {'user': toolkit.g.get('user') or toolkit.g.get('author')}
    message = toolkit.request.args.get('message', None)
    data_dict = {"mrequest_id": mrequest_id, 'message': message}
    try:
        toolkit.get_action('member_request_autoapprove')(
            context, data_dict)
        id = 'approved'
        return toolkit.redirect_to('member_request.member_requests_mylist', id=id)
    except logic.NotAuthorized:
        toolkit.abort(401, not_auth_message)
    except logic.NotFound:
        toolkit.abort(404, request_not_found_message)
    except logic.ValidationError as e:
        toolkit.abort(400, str(e))
