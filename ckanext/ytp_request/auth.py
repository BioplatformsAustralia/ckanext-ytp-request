from ckan.plugins import toolkit
from ckan import authz, model
from ckan.common import c, _


def member_requests_mylist(context, data_dict):
    """Allow any logged-in user to view their own membership requests."""
    user = context.get("user")
    if not user:
        return {"success": False, "msg": _("User must be logged in")}
    return {"success": True}


def member_requests_status(context, data_dict):
    """Allow sysadmins or organization admins to view request status."""
    user = context.get("user")
    if not user:
        return {"success": False, "msg": _("User must be logged in")}

    if authz.is_sysadmin(user):
        return {"success": True}

    target_user = data_dict.get("mrequest_user")
    if not target_user:
        return {"success": False, "msg": _("Target user not specified")}

    # Check if the current user is admin in any group
    current_user = model.User.get(user)
    admin_in_groups = model.Session.query(model.Member).filter(
        model.Member.table_name == "user",
        model.Member.table_id == current_user.id,
        model.Member.capacity == "admin",
        model.Member.state == "active"
    ).count()

    if admin_in_groups > 0:
        return {"success": True}

    return {"success": False, "msg": _("User is not authorized to view member request status")}


def member_requests_list(context, data_dict):
    """Allow sysadmins and organization admins to view requests list."""
    user = context.get("user")
    if not user:
        return {"success": False, "msg": _("User must be logged in")}

    if authz.is_sysadmin(user):
        return {"success": True}

    current_user = model.User.get(user)
    admin_in_groups = model.Session.query(model.Member).filter(
        model.Member.table_name == "user",
        model.Member.table_id == current_user.id,
        model.Member.capacity == "admin",
        model.Member.state == "active"
    ).count()

    if admin_in_groups > 0:
        return {"success": True}

    return {"success": False, "msg": _("User is not authorized to list membership requests")}


def member_request_show(context, data_dict):
    """Allow sysadmins and group admins to view individual requests."""
    # Reuse the logic from member_requests_list
    return member_requests_list(context, data_dict)


def organization_list_without_memberships(context, data_dict):
    """Allow any logged-in user to see orgs where they aren't members."""
    user = context.get("user")
    if not user:
        return {"success": False, "msg": _("User must be logged in")}
    return {"success": True}
