import os
from io import BytesIO

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader


def draw_text(c, text, x, y, font="Helvetica", size=10, color=colors.black):
    c.setFont(font, size)
    c.setFillColor(color)
    c.drawString(x, y, str(text or ""))


def draw_label_value(c, label, value, x, y, label_width=120):
    c.setFont("Helvetica-Bold", 10)
    c.setFillColor(colors.HexColor("#1F2937"))
    c.drawString(x, y, str(label or ""))

    c.setFont("Helvetica", 10)
    c.setFillColor(colors.black)
    c.drawString(x + label_width, y, str(value or ""))


def draw_rounded_box(c, x, y, width, height, radius=8, stroke_color="#D1D5DB", fill_color=None):
    c.setLineWidth(1)
    c.setStrokeColor(colors.HexColor(stroke_color))

    if fill_color:
        c.setFillColor(colors.HexColor(fill_color))
        c.roundRect(x, y - height, width, height, radius, stroke=1, fill=1)
    else:
        c.roundRect(x, y - height, width, height, radius, stroke=1, fill=0)


def draw_section_header(c, title, x, y, width):
    c.setFillColor(colors.HexColor("#EAF3FF"))
    c.roundRect(x, y - 22, width, 22, 5, stroke=0, fill=1)
    c.setFillColor(colors.HexColor("#0E5A97"))
    c.setFont("Helvetica-Bold", 11)
    c.drawString(x + 8, y - 14, title)


def draw_status_badge(c, status, x, y):
    status = (status or "").upper()

    color_map = {
        "PENDING": "#D97706",
        "ACCEPTED": "#15803D",
        "REJECTED": "#DC2626",
        "SHIPPED": "#2563EB",
        "DELIVERED": "#059669",
    }

    badge_color = color_map.get(status, "#6B7280")
    badge_width = max(62, len(status) * 7 + 18)

    c.setFillColor(colors.HexColor(badge_color))
    c.roundRect(x, y - 10, badge_width, 18, 5, stroke=0, fill=1)

    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 9)
    c.drawCentredString(x + badge_width / 2, y - 4, status)

    c.setFillColor(colors.black)


def draw_watermark(c, page_width, page_height, logo_path):
    if not os.path.exists(logo_path):
        return

    try:
        logo = ImageReader(logo_path)

        wm_width = 110 * mm
        wm_height = 55 * mm
        x = (page_width - wm_width) / 2
        y = (page_height - wm_height) / 2 + 10 * mm

        c.saveState()
        if hasattr(c, "setFillAlpha"):
            c.setFillAlpha(0.08)

        c.drawImage(
            logo,
            x,
            y,
            width=wm_width,
            height=wm_height,
            preserveAspectRatio=True,
            mask="auto"
        )
        c.restoreState()
    except Exception:
        pass


def build_acknowledgement_pdf(gift_request):
    """
    Returns PDF bytes in memory.
    No file is stored on disk.
    """
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)

    width, height = A4
    margin_x = 15 * mm
    top_y = height - 15 * mm
    content_width = width - (2 * margin_x)

    logo_path = os.path.join("media", "logo.png")

    # Watermark
    draw_watermark(c, width, height, logo_path)

    # Outer border
    c.setStrokeColor(colors.HexColor("#C7D2E0"))
    c.setLineWidth(1)
    c.roundRect(10 * mm, 10 * mm, width - 20 * mm, height - 20 * mm, 8, stroke=1, fill=0)

    # Header box
    header_height = 42 * mm
    draw_rounded_box(
        c,
        margin_x,
        top_y,
        content_width,
        header_height,
        radius=10,
        stroke_color="#B9C7D6",
        fill_color="F8FBFF"
    )

    if os.path.exists(logo_path):
        try:
            logo = ImageReader(logo_path)
            c.drawImage(
                logo,
                margin_x + 6 * mm,
                top_y - 34 * mm,
                width=content_width - 12 * mm,
                height=28 * mm,
                preserveAspectRatio=True,
                mask="auto"
            )
        except Exception:
            draw_text(
                c,
                "The Co-Operative Bank of Rajkot Ltd.",
                margin_x + 10,
                top_y - 18,
                "Helvetica-Bold",
                18,
                colors.HexColor("#0E5A97")
            )
            draw_text(
                c,
                "Multi State Co-Operative Bank",
                margin_x + 10,
                top_y - 30,
                "Helvetica-Bold",
                11,
                colors.HexColor("#29ABE2")
            )
    else:
        draw_text(
            c,
            "The Co-Operative Bank of Rajkot Ltd.",
            margin_x + 10,
            top_y - 18,
            "Helvetica-Bold",
            18,
            colors.HexColor("#0E5A97")
        )
        draw_text(
            c,
            "Multi State Co-Operative Bank",
            margin_x + 10,
            top_y - 30,
            "Helvetica-Bold",
            11,
            colors.HexColor("#29ABE2")
        )

    y = top_y - header_height - 10

    # Title
    c.setFont("Helvetica-Bold", 15)
    c.setFillColor(colors.HexColor("#111827"))
    c.drawCentredString(width / 2, y, "GIFT REQUEST ACKNOWLEDGEMENT")

    y -= 6
    c.setStrokeColor(colors.HexColor("#0E5A97"))
    c.setLineWidth(1.5)
    c.line(margin_x + 45, y - 4, width - margin_x - 45, y - 4)
    y -= 14

    # Request Summary
    summary_height = 38 * mm
    draw_rounded_box(c, margin_x, y, content_width, summary_height)
    draw_section_header(c, "Request Summary", margin_x + 4, y - 2, content_width - 8)

    row1_y = y - 14 * mm
    row2_y = row1_y - 7 * mm

    draw_label_value(c, "Request No", gift_request.request_no, margin_x + 8, row1_y, 42 * mm)
    draw_label_value(
        c,
        "Submitted At",
        gift_request.submitted_at.strftime("%d-%m-%Y %I:%M %p") if gift_request.submitted_at else "",
        margin_x + 95 * mm,
        row1_y,
        35 * mm
    )

    draw_text(c, "Status", margin_x + 8, row2_y, "Helvetica-Bold", 10, colors.HexColor("#1F2937"))
    draw_status_badge(c, gift_request.request_status, margin_x + 50 * mm, row2_y + 2)
    draw_label_value(c, "Branch", gift_request.branch.branch_name, margin_x + 95 * mm, row2_y, 35 * mm)

    y -= summary_height + 8

    # Shareholder Details
    shareholder_height = 48 * mm
    draw_rounded_box(c, margin_x, y, content_width, shareholder_height)
    draw_section_header(c, "Shareholder Details", margin_x + 4, y - 2, content_width - 8)

    line1 = y - 14 * mm
    line2 = line1 - 7 * mm
    line3 = line2 - 7 * mm

    draw_label_value(c, "Shareholder Name", gift_request.shareholder.shareholder_name, margin_x + 8, line1, 42 * mm)
    draw_label_value(c, "Mobile Number", gift_request.mobile_number, margin_x + 95 * mm, line1, 35 * mm)
    draw_label_value(c, "Share Number", gift_request.share.share_number, margin_x + 8, line2, 42 * mm)
    draw_label_value(c, "Certificate Number", gift_request.share.certificate_number or "", margin_x + 95 * mm, line2, 35 * mm)
    draw_label_value(c, "Gift Cycle", gift_request.gift_cycle.cycle_name, margin_x + 8, line3, 42 * mm)

    y -= shareholder_height + 8

    # Delivery Address
    # Delivery Address
    try:
        addr = gift_request.delivery_address
    except Exception:
        addr = None

    delivery_height = 56 * mm
    draw_rounded_box(c, margin_x, y, content_width, delivery_height)
    draw_section_header(c, "Delivery Address", margin_x + 4, y - 2, content_width - 8)

    line1 = y - 14 * mm
    line2 = line1 - 7 * mm
    line3 = line2 - 7 * mm
    line4 = line3 - 7 * mm
    line5 = line4 - 7 * mm

    draw_label_value(c, "Recipient Name", getattr(addr, "recipient_name", "") or "", margin_x + 8, line1, 42 * mm)
    draw_label_value(c, "Mobile Number", getattr(addr, "mobile_number", "") or "", margin_x + 95 * mm, line1, 35 * mm)
    draw_label_value(c, "Address Line 1", getattr(addr, "address_line1", "") or "", margin_x + 8, line2, 42 * mm)
    draw_label_value(c, "Address Line 2", getattr(addr, "address_line2", "") or "", margin_x + 8, line3, 42 * mm)
    draw_label_value(c, "City", getattr(addr, "city", "") or "", margin_x + 8, line4, 42 * mm)
    draw_label_value(c, "State", getattr(addr, "state", "") or "", margin_x + 95 * mm, line4, 35 * mm)
    draw_label_value(c, "Pincode", getattr(addr, "pincode", "") or "", margin_x + 8, line5, 42 * mm)

    y -= delivery_height + 8

    # Footer note + signature
    footer_height = 28 * mm
    draw_rounded_box(c, margin_x, y, content_width, footer_height, stroke_color="#D6DCE5", fill_color="FCFCFD")

    draw_text(
        c,
        "Note: This is a system-generated acknowledgement slip for gift request reference.",
        margin_x + 8,
        y - 11 * mm,
        "Helvetica-Oblique",
        9,
        colors.HexColor("#4B5563")
    )
    draw_text(
        c,
        "Please keep this document for future reference.",
        margin_x + 8,
        y - 17 * mm,
        "Helvetica-Oblique",
        9,
        colors.HexColor("#4B5563")
    )

    sign_y = y - 16 * mm
    c.setStrokeColor(colors.HexColor("#6B7280"))
    c.line(width - margin_x - 55 * mm, sign_y, width - margin_x - 10 * mm, sign_y)

    draw_text(
        c,
        "Authorized Signature",
        width - margin_x - 45 * mm,
        sign_y - 12,
        "Helvetica",
        9,
        colors.HexColor("#374151")
    )

    c.setFont("Helvetica", 8)
    c.setFillColor(colors.HexColor("#6B7280"))
    c.drawString(
        margin_x,
        12 * mm,
        f"Generated on: {gift_request.submitted_at.strftime('%d-%m-%Y %I:%M %p') if gift_request.submitted_at else ''}"
    )
    c.drawRightString(width - margin_x, 12 * mm, f"Request No: {gift_request.request_no}")

    c.save()
    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes


# keep old function name also, so existing imports do not break
def generate_acknowledgement_pdf(gift_request):
    return build_acknowledgement_pdf(gift_request)