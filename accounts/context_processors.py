from .permission_utils import user_has_role_permission


def user_roles(request):
    if request.user.is_authenticated:
        roles = list(request.user.groups.values_list('name', flat=True))
    else:
        roles = []

    return {
        'user_roles': roles,
        'perm_can_view_requests': user_has_role_permission(request.user, 'can_view_requests'),
        'perm_can_create_request': user_has_role_permission(request.user, 'can_create_request'),
        'perm_can_accept_request': user_has_role_permission(request.user, 'can_accept_request'),
        'perm_can_reject_request': user_has_role_permission(request.user, 'can_reject_request'),
        'perm_can_ship_request': user_has_role_permission(request.user, 'can_ship_request'),
        'perm_can_deliver_request': user_has_role_permission(request.user, 'can_deliver_request'),
        'perm_can_bulk_tracking': user_has_role_permission(request.user, 'can_bulk_tracking'),
        'perm_can_bulk_delivery': user_has_role_permission(request.user, 'can_bulk_delivery'),
        'perm_can_bulk_share_upload': user_has_role_permission(request.user, 'can_bulk_share_upload'),
        'perm_can_bulk_share_status': user_has_role_permission(request.user, 'can_bulk_share_status'),
        'perm_can_view_reports': user_has_role_permission(request.user, 'can_view_reports'),
        'perm_can_manage_users': user_has_role_permission(request.user, 'can_manage_users'),
        'perm_can_manage_roles': user_has_role_permission(request.user, 'can_manage_roles'),
        'perm_can_manage_branches': user_has_role_permission(request.user, 'can_manage_branches'),
        'perm_can_manage_share_status': user_has_role_permission(request.user, 'can_manage_share_status'),
        'perm_can_reset_user_password': user_has_role_permission(request.user, 'can_reset_user_password'),
    }