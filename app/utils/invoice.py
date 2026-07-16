import os
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from flask import current_app


def generate_invoice_pdf(booking):
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('title', parent=styles['Title'], textColor=colors.HexColor('#7B2D8E'))

    folder = current_app.config['INVOICE_FOLDER']
    os.makedirs(folder, exist_ok=True)
    filename = f"invoice_booking_{booking.booking_id}.pdf"
    filepath = os.path.join(folder, filename)

    doc = SimpleDocTemplate(filepath, pagesize=A4, topMargin=20 * mm)
    elements = []

    elements.append(Paragraph("Momenta", title_style))
    elements.append(Paragraph("Creating Moments That Matter", styles['Normal']))
    elements.append(Spacer(1, 12))
    elements.append(Paragraph(f"<b>Invoice - Booking #{booking.booking_id}</b>", styles['Heading2']))
    elements.append(Paragraph(f"Date: {datetime.utcnow().strftime('%d %b %Y')}", styles['Normal']))
    elements.append(Spacer(1, 12))

    client = booking.client
    info_data = [
        ["Client Name", client.name, "Event", booking.event_type.event_name],
        ["Email", client.email, "Event Date", str(booking.event_date)],
        ["Phone", client.phone or '-', "Guests", str(booking.guest_count)],
        ["Venue", booking.venue or '-', "Status", booking.status],
    ]
    info_table = Table(info_data, colWidths=[80, 150, 80, 150])
    info_table.setStyle(TableStyle([
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f0e6f5')),
        ('BACKGROUND', (2, 0), (2, -1), colors.HexColor('#f0e6f5')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    elements.append(info_table)
    elements.append(Spacer(1, 16))

    service_rows = [["Service", "Category", "Price (Rs.)"]]
    for s in booking.services:
        service_rows.append([s.service_name, s.category, f"{s.price:,.2f}"])
    service_rows.append(["", "Total", f"{booking.total_amount:,.2f}"])

    service_table = Table(service_rows, colWidths=[220, 150, 100])
    service_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#7B2D8E')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('ALIGN', (2, 0), (2, -1), 'RIGHT'),
    ]))
    elements.append(service_table)
    elements.append(Spacer(1, 20))
    elements.append(Paragraph("Thank you for choosing Momenta!", styles['Normal']))
    elements.append(Paragraph("Contact: support@momenta.com | +91-90000-00000", styles['Normal']))

    doc.build(elements)
    return filepath, filename
