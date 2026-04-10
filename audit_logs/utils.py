from audit_logs.models import AuditLog, AuditLogDetail


def to_audit_value(value):
    if value is None:
        return None
    if hasattr(value, 'isoformat'):
        try:
            return value.isoformat()
        except Exception:
            return str(value)
    return str(value)


def create_audit_log(
    module_name,
    table_name,
    record_id,
    action_type,
    changed_by_type,
    changed_by_id=None,
    branch=None,
    ip_address=None,
    user_agent=None,
    remarks=None,
    field_changes=None
):
    """
    field_changes format:
    [
        {"column_name": "request_status", "old_value": "PENDING", "new_value": "ACCEPTED"},
        ...
    ]
    """

    audit_log = AuditLog.objects.create(
        module_name=module_name,
        table_name=table_name,
        record_id=record_id,
        action_type=action_type,
        changed_by_type=changed_by_type,
        changed_by_id=changed_by_id,
        branch=branch,
        ip_address=ip_address,
        user_agent=user_agent,
        remarks=remarks,
    )

    if field_changes:
        details = []
        for change in field_changes:
            details.append(
                AuditLogDetail(
                    audit_log=audit_log,
                    column_name=change['column_name'],
                    old_value=to_audit_value(change.get('old_value')),
                    new_value=to_audit_value(change.get('new_value')),
                )
            )
        AuditLogDetail.objects.bulk_create(details)

    return audit_log