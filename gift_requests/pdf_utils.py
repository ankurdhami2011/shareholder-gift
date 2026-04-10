from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.units import mm


def draw_label_value(c, label, value, x, y, label_width=38 * mm):
    c.setFont("Helvetica-Bold", 10)
    c.setFillColor(colors.HexColor("#1F2937"))
    c.drawString(x, y, str(label or ""))

    c.setFont("Helvetica", 10)
    c.setFillColor(colors.black)
    c.drawString(x + label_width, y, str(value or ""))


def draw_box(c, x, y, width, height, title=None):
    c.setStrokeColor(colors.HexColor("#D1D5DB"))
    c.setLineWidth(1)
    c.roundRect(x, y - height, width, height, 6, stroke=1, fill=0)

    if title:
        c.setFillColor(colors.HexColor("#EAF3FF"))
        c.roundRect(x + 4, y - 22, width - 8, 18, 4, stroke=0, fill=1)
        c.setFillColor(colors.HexColor("#0E5A97"))
        c.setFont("Helvetica-Bold", 10)
        c.drawString(x + 10, y - 15, title)

    c.setFillColor(colors.black)


def draw_status_badge(c, status, x, y):
    status = (status or "").upper()

    color_map = {
        "PENDING": "#D97706",
        "ACCEPTED": "#15803D",
        "REJECTED": "#DC2626",
        "SHIPPED": "#4F46E5",
        "DELIVERED": "#16A34A",
    }

    badge_color = color_map.get(status, "#6B7280")
    badge_width = max(62, len(status) * 7 + 18)

    c.setFillColor(colors.HexColor(badge_color))
    c.roundRect(x, y - 10, badge_width, 18, 5, stroke=0, fill=1)

    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 9)
    c.drawCentredString(x + badge_width / 2, y - 4, status)
    c.setFillColor(colors.black)


def wrap_text(text, max_chars=55):
    text = str(text or "").strip()
    if not text:
        return [""]

    words = text.split()
    lines = []
    current = ""

    for word in words:
        candidate = word if not current else current + " " + word
        if len(candidate) <= max_chars:
            current = candidate
        else:
            lines.append(current)
            current = word

    if current:
        lines.append(current)

    return lines

def draw_horizontal_timeline(c, x, y, width, history):
    color_map = {
        "PENDING": "#D97706",
        "ACCEPTED": "#16A34A",
        "REJECTED": "#DC2626",
        "SHIPPED": "#4F46E5",
        "DELIVERED": "#16A34A",
    }

    history = history[:4]
    if not history:
        return

    points = len(history)
    if points == 1:
        xs = [x + width / 2]
    else:
        gap = width / (points - 1)
        xs = [x + i * gap for i in range(points)]

    line_y = y - 40

    # visible connector line
    c.setStrokeColor(colors.HexColor("#94A3B8"))
    c.setLineWidth(2)
    if len(xs) > 1:
        c.line(xs[0], line_y, xs[-1], line_y)

    for idx, item in enumerate(history):
        status = (item.new_status or "").upper()
        dot_color = colors.HexColor(color_map.get(status, "#6B7280"))
        x_pos = xs[idx]

        # colored dot
        c.setFillColor(dot_color)
        c.setStrokeColor(dot_color)
        c.circle(x_pos, line_y, 5, stroke=1, fill=1)

        # status
        c.setFillColor(colors.HexColor("#111827"))
        c.setFont("Helvetica-Bold", 10)
        c.drawCentredString(x_pos, line_y - 18, status)

        # datetime
        dt_text = item.created_at.strftime("%d-%m-%Y %I:%M %p") if item.created_at else ""
        c.setFillColor(colors.HexColor("#64748B"))
        c.setFont("Helvetica", 7.5)
        c.drawCentredString(x_pos, line_y - 29, dt_text)

        # remarks
        remarks = item.remarks or "No remarks"
        remarks_lines = wrap_text(remarks, 16)

        c.setFillColor(colors.HexColor("#374151"))
        c.setFont("Helvetica", 7.5)

        text_y = line_y - 40
        for line in remarks_lines[:2]:
            c.drawCentredString(x_pos, text_y, line)
            text_y -= 9

def build_acknowledgement_pdf(gift_request):
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)

    width, height = A4
    margin_x = 15 * mm
    content_width = width - (2 * margin_x)
    y = height - 18 * mm

    # outer border
    c.setStrokeColor(colors.HexColor("#C7D2E0"))
    c.setLineWidth(1)
    c.roundRect(10 * mm, 10 * mm, width - 20 * mm, height - 20 * mm, 8, stroke=1, fill=0)

    # header
    c.setFont("Helvetica-Bold", 18)
    c.setFillColor(colors.HexColor("#0E5A97"))
    c.drawCentredString(width / 2, y, "THE CO-OPERATIVE BANK OF RAJKOT LTD.")

    y -= 16
    c.setFont("Helvetica-Bold", 11)
    c.setFillColor(colors.HexColor("#29ABE2"))
    c.drawCentredString(width / 2, y, "Multi State Co-Operative Bank")

    y -= 20
    c.setFont("Helvetica-Bold", 15)
    c.setFillColor(colors.HexColor("#111827"))
    c.drawCentredString(width / 2, y, "GIFT REQUEST ACKNOWLEDGEMENT")

    y -= 8
    c.setStrokeColor(colors.HexColor("#0E5A97"))
    c.setLineWidth(1.2)
    c.line(margin_x + 25, y, width - margin_x - 25, y)

    y -= 10

    # request summary
    summary_height = 36 * mm
    draw_box(c, margin_x, y, content_width, summary_height, "Request Summary")

    line1 = y - 14 * mm
    line2 = line1 - 7 * mm

    draw_label_value(c, "Request No", gift_request.request_no, margin_x + 8, line1, 28 * mm)
    draw_label_value(
        c,
        "Submitted At",
        gift_request.submitted_at.strftime("%d-%m-%Y %I:%M %p") if gift_request.submitted_at else "",
        margin_x + 95 * mm,
        line1,
        26 * mm
    )

    c.setFont("Helvetica-Bold", 10)
    c.setFillColor(colors.HexColor("#1F2937"))
    c.drawString(margin_x + 8, line2, "Status")
    draw_status_badge(c, gift_request.request_status, margin_x + 28 * mm, line2 + 2)

    draw_label_value(
        c,
        "Branch",
        gift_request.branch.branch_name if gift_request.branch else "",
        margin_x + 95 * mm,
        line2,
        26 * mm
    )

    y -= summary_height + 6

    # request timeline
    history = list(gift_request.status_history.all().order_by("created_at"))
    if history:
        history = history[:4]
        timeline_height = 45 * mm
        draw_box(c, margin_x, y, content_width, timeline_height, "Request Timeline")

        draw_horizontal_timeline(
            c,
            margin_x + 14 * mm,
            y - 2 * mm,
            content_width - 28 * mm,
            history
        )

        y -= timeline_height + 6

    # shareholder details
    shareholder_height = 54 * mm
    draw_box(c, margin_x, y, content_width, shareholder_height, "Shareholder Details")

    line1 = y - 14 * mm
    line2 = line1 - 7 * mm
    line3 = line2 - 7 * mm
    line4 = line3 - 7 * mm

    draw_label_value(
        c,
        "Shareholder Name",
        gift_request.shareholder.shareholder_name if gift_request.shareholder else "",
        margin_x + 8,
        line1,
        34 * mm
    )
    draw_label_value(
        c,
        "Mobile Number",
        gift_request.mobile_number or "",
        margin_x + 95 * mm,
        line1,
        30 * mm
    )

    draw_label_value(
        c,
        "Share Number",
        gift_request.share.share_number if gift_request.share else "",
        margin_x + 8,
        line2,
        34 * mm
    )

    draw_label_value(
        c,
        "Certificate Number",
        gift_request.share.certificate_number if gift_request.share else "",
        margin_x + 8,
        line3,
        34 * mm
    )

    draw_label_value(
        c,
        "Gift Cycle",
        gift_request.gift_cycle.cycle_name if gift_request.gift_cycle else "",
        margin_x + 8,
        line4,
        34 * mm
    )

    y -= shareholder_height + 6

    # delivery details
    try:
        addr = gift_request.delivery_address
    except Exception:
        addr = None

    shareholder_addr = gift_request.shareholder

    recipient_name = ""
    delivery_mobile = ""
    address_line1 = ""
    address_line2 = ""
    city = ""
    state = ""
    pincode = ""

    if addr:
        recipient_name = getattr(addr, "recipient_name", "") or ""
        delivery_mobile = getattr(addr, "mobile_number", "") or ""
        address_line1 = getattr(addr, "address_line1", "") or ""
        address_line2 = getattr(addr, "address_line2", "") or ""
        city = getattr(addr, "city", "") or ""
        state = getattr(addr, "state", "") or ""
        pincode = getattr(addr, "pincode", "") or ""

    if not recipient_name:
        recipient_name = getattr(shareholder_addr, "shareholder_name", "") or ""
    if not delivery_mobile:
        delivery_mobile = getattr(shareholder_addr, "mobile_number", "") or ""
    if not address_line1:
        address_line1 = getattr(shareholder_addr, "address_line1", "") or ""
    if not address_line2:
        address_line2 = getattr(shareholder_addr, "address_line2", "") or ""
    if not city:
        city = getattr(shareholder_addr, "city", "") or ""
    if not state:
        state = getattr(shareholder_addr, "state", "") or ""
    if not pincode:
        pincode = getattr(shareholder_addr, "pincode", "") or ""

    delivery_height = 58 * mm
    draw_box(c, margin_x, y, content_width, delivery_height, "Delivery Address")

    line1 = y - 14 * mm
    line2 = line1 - 7 * mm
    line3 = line2 - 7 * mm
    line4 = line3 - 7 * mm
    line5 = line4 - 7 * mm

    draw_label_value(c, "Recipient Name", recipient_name, margin_x + 8, line1, 34 * mm)
    draw_label_value(c, "Mobile Number", delivery_mobile, margin_x + 95 * mm, line1, 30 * mm)

    draw_label_value(c, "Address Line 1", address_line1, margin_x + 8, line2, 34 * mm)
    draw_label_value(c, "Address Line 2", address_line2, margin_x + 8, line3, 34 * mm)

    draw_label_value(c, "City", city, margin_x + 8, line4, 34 * mm)
    draw_label_value(c, "State", state, margin_x + 95 * mm, line4, 30 * mm)
    draw_label_value(c, "Pincode", pincode, margin_x + 8, line5, 34 * mm)

    y -= delivery_height + 6

    # courier details
    if gift_request.courier_name or gift_request.tracking_number:
        courier_height = 30 * mm
        draw_box(c, margin_x, y, content_width, courier_height, "Courier Details")

        line1 = y - 14 * mm
        line2 = line1 - 7 * mm

        draw_label_value(
            c,
            "Courier Name",
            gift_request.courier_name or "",
            margin_x + 8,
            line1,
            34 * mm
        )
        draw_label_value(
            c,
            "Tracking Number",
            gift_request.tracking_number or "",
            margin_x + 8,
            line2,
            34 * mm
        )

        y -= courier_height + 8

    # footer
    footer_height = 16 * mm
    draw_box(c, margin_x, y, content_width, footer_height, None)

    c.setFont("Helvetica-Oblique", 8)
    c.setFillColor(colors.HexColor("#4B5563"))
    c.drawString(margin_x + 8, y - 6 * mm, "Note: This is a system-generated acknowledgement slip.")
    c.drawString(margin_x + 8, y - 10 * mm, "Please keep this document for future reference.")   

    # bottom meta line
    c.setFont("Helvetica", 7.5)
    c.setFillColor(colors.HexColor("#6B7280"))
    c.drawString(
        margin_x + 4,
        y - footer_height + 8,
        f"Requested on: {gift_request.submitted_at.strftime('%d-%m-%Y %I:%M %p') if gift_request.submitted_at else ''}"
    )
    c.drawRightString(
        width - margin_x - 4,
        y - footer_height + 8,
        f"Request No: {gift_request.request_no}"
    )
    c.save()
    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes


def generate_acknowledgement_pdf(gift_request):
    return build_acknowledgement_pdf(gift_request)