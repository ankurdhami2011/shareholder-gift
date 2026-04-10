import ssl
import urllib.parse
import urllib.request

from django.conf import settings
from django.utils import timezone

from .models import SmsTemplate, SmsLog


def render_sms_template(template_body, context):
    message = template_body
    for key, value in context.items():
        placeholder = '{' + str(key) + '}'
        message = message.replace(placeholder, str(value if value is not None else ''))
    return message


def get_sms_template(template_code):
    return SmsTemplate.objects.filter(
        template_code=template_code,
        is_active=True
    ).first()


def send_sms_via_provider(mobile_number, message_text):
    """
    Real SMS provider integration.
    Uses Soft Tech Solutions SMS gateway.
    """
    base_url = getattr(settings, 'SMS_BASE_URL', 'https://sms.soft-techsolutions.com/v3/sms/submit')
    user = getattr(settings, 'SMS_USER', '')
    authkey = getattr(settings, 'SMS_AUTHKEY', '')
    senderid = getattr(settings, 'SMS_SENDER_ID', '')
    smstype = getattr(settings, 'SMS_TYPE', 'T')
    rmspace = getattr(settings, 'SMS_RMSPACE', 'Y')

    if not user or not authkey or not senderid:
        return {
            'success': False,
            'provider_response': 'SMS gateway settings missing'
        }

    params = {
        "user": user,
        "authkey": authkey,
        "mobile": str(mobile_number),
        "message": str(message_text),
        "senderid": senderid,
        "smstype": smstype,
        "rmspace": rmspace,
    }

    url = base_url + "?" + urllib.parse.urlencode(params)

    # same behavior as your working script
    ssl_context = ssl._create_unverified_context()

    try:
        with urllib.request.urlopen(url, timeout=20, context=ssl_context) as resp:
            txt = resp.read().decode().strip()

            bad_words = ("error", "invalid", "failed", "unauthorized")

            if any(word in txt.lower() for word in bad_words):
                return {
                    'success': False,
                    'provider_response': txt
                }

            return {
                'success': True,
                'provider_response': txt or 'OK'
            }

    except Exception as exc:
        return {
            'success': False,
            'provider_response': str(exc)
        }


def send_sms_from_template(template_code, mobile_number, context=None, reference_type=None, reference_id=None):
    context = context or {}

    template = get_sms_template(template_code)
    if not template:
        log = SmsLog.objects.create(
            mobile_number=mobile_number,
            template_code=template_code,
            message_text='',
            send_status='FAILED',
            provider_response='SMS template not found or inactive',
            reference_type=reference_type,
            reference_id=reference_id,
        )
        return {
            'success': False,
            'message': 'SMS template not found',
            'log_id': log.id
        }

    message_text = render_sms_template(template.message_body, context)

    sms_log = SmsLog.objects.create(
        mobile_number=mobile_number,
        template_code=template_code,
        message_text=message_text,
        send_status='PENDING',
        reference_type=reference_type,
        reference_id=reference_id,
    )

    try:
        provider_result = send_sms_via_provider(mobile_number, message_text)

        if provider_result.get('success'):
            sms_log.send_status = 'SENT'
            sms_log.provider_response = provider_result.get('provider_response')
            sms_log.sent_at = timezone.now()
            sms_log.save(update_fields=['send_status', 'provider_response', 'sent_at', 'updated_at'])

            return {
                'success': True,
                'message': 'SMS sent successfully',
                'log_id': sms_log.id
            }
        else:
            sms_log.send_status = 'FAILED'
            sms_log.provider_response = provider_result.get('provider_response')
            sms_log.save(update_fields=['send_status', 'provider_response', 'updated_at'])

            return {
                'success': False,
                'message': 'SMS sending failed',
                'log_id': sms_log.id
            }

    except Exception as exc:
        sms_log.send_status = 'FAILED'
        sms_log.provider_response = str(exc)
        sms_log.save(update_fields=['send_status', 'provider_response', 'updated_at'])

        return {
            'success': False,
            'message': str(exc),
            'log_id': sms_log.id
        }

    """
    message_text = f"Enter OTP {otp_code} to access your TCBRL Gift Application. Valid for 5 minutes. Do not share this code. – The Co-operative Bank of Rajkot Ltd."
    """

def send_login_otp_sms(mobile_number, otp_code):
    message_text = (f"Your TCBRL Gift App OTP is {otp_code}. Valid for 5 minutes.The Co-Operative Bank of Rajkot Limited\n"
        f"WA0RLCpEd8h"
    )
    sms_log = SmsLog.objects.create(
        mobile_number=mobile_number,
        template_code='LOGIN_OTP',
        message_text=message_text,
        send_status='PENDING',
        reference_type='OTP_LOGIN',
        reference_id=None,
    )

    try:
        provider_result = send_sms_via_provider(mobile_number, message_text)

        if provider_result.get('success'):
            sms_log.send_status = 'SENT'
            sms_log.provider_response = provider_result.get('provider_response')
            sms_log.sent_at = timezone.now()
            sms_log.save(update_fields=['send_status', 'provider_response', 'sent_at', 'updated_at'])

            return {
                'success': True,
                'message': 'OTP SMS sent successfully',
                'log_id': sms_log.id
            }

        sms_log.send_status = 'FAILED'
        sms_log.provider_response = provider_result.get('provider_response')
        sms_log.save(update_fields=['send_status', 'provider_response', 'updated_at'])

        return {
            'success': False,
            'message': 'OTP SMS sending failed',
            'log_id': sms_log.id
        }

    except Exception as exc:
        sms_log.send_status = 'FAILED'
        sms_log.provider_response = str(exc)
        sms_log.save(update_fields=['send_status', 'provider_response', 'updated_at'])

        return {
            'success': False,
            'message': str(exc),
            'log_id': sms_log.id
        }


def send_request_submitted_sms(gift_request):
    return send_sms_from_template(
        template_code='REQUEST_SUBMITTED',
        mobile_number=gift_request.mobile_number,
        context={
            'request_no': gift_request.request_no,
            'share_number': gift_request.share.share_number,
            'branch_name': gift_request.branch.branch_name if gift_request.branch else '',
        },
        reference_type='GIFT_REQUEST',
        reference_id=gift_request.id,
    )


def send_request_accepted_sms(gift_request):
    return send_sms_from_template(
        template_code='REQUEST_ACCEPTED',
        mobile_number=gift_request.mobile_number,
        context={
            'request_no': gift_request.request_no,
            'share_number': gift_request.share.share_number,
            'branch_name': gift_request.branch.branch_name if gift_request.branch else '',
        },
        reference_type='GIFT_REQUEST',
        reference_id=gift_request.id,
    )


def send_request_rejected_sms(gift_request):
    return send_sms_from_template(
        template_code='REQUEST_REJECTED',
        mobile_number=gift_request.mobile_number,
        context={
            'request_no': gift_request.request_no,
            'share_number': gift_request.share.share_number,
            'branch_name': gift_request.branch.branch_name if gift_request.branch else '',
            'rejection_reason': gift_request.rejection_reason or '',
        },
        reference_type='GIFT_REQUEST',
        reference_id=gift_request.id,
    )


def send_tracking_created_sms(gift_request):
    return send_sms_from_template(
        template_code='TRACKING_CREATED',
        mobile_number=gift_request.mobile_number,
        context={
            'request_no': gift_request.request_no,
            'share_number': gift_request.share.share_number,
            'branch_name': gift_request.branch.branch_name if gift_request.branch else '',
            'tracking_number': gift_request.tracking_number or '',
            'courier_name': gift_request.courier_name or '',
        },
        reference_type='GIFT_REQUEST',
        reference_id=gift_request.id,
    )


def send_request_delivered_sms(gift_request):
    return send_sms_from_template(
        template_code='REQUEST_DELIVERED',
        mobile_number=gift_request.mobile_number,
        context={
            'request_no': gift_request.request_no,
            'share_number': gift_request.share.share_number,
            'branch_name': gift_request.branch.branch_name if gift_request.branch else '',
        },
        reference_type='GIFT_REQUEST',
        reference_id=gift_request.id,
    )