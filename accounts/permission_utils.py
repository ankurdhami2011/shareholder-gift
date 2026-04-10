from django.core.exceptions import PermissionDenied


def user_has_role_permission(user, permission_name):
    if not user.is_authenticated:
        return False

    if user.is_superuser:
        return True

    groups = user.groups.all()
    if not groups.exists():
        return False

    for group in groups:
        role_permission = getattr(group, 'role_permission', None)
        if role_permission and getattr(role_permission, permission_name, False):
            return True

    return False


def permission_required(permission_name):
    def decorator(view_func):
        def wrapper(request, *args, **kwargs):
            if not user_has_role_permission(request.user, permission_name):
                raise PermissionDenied
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator