import os
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.lib import colors

def generate_invoice(data):
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    margin_left = 50
    margin_right = 550

    # Fonts and Colors
    font_large = 16
    font_medium = 12
    font_small = 10

    # === Business Info ===
    c.setFont("Helvetica-Bold", font_large)
    c.drawString(margin_left, height - 60, data['business_name'])

    c.setFont("Helvetica", font_small)
    c.drawString(margin_left, height - 80, data['business_address'])
    c.drawString(margin_left, height - 95, f"Phone: {data['business_phone']}")
    c.drawString(margin_left, height - 110, f"Email: {data['business_email']}")

    # === Business Logo ===
    if 'logo_path' in data and os.path.exists(data['logo_path']):
        logo = ImageReader(data['logo_path'])
        c.drawImage(logo, width - 130, height - 100, width=80, height=80, preserveAspectRatio=True)

    # === Invoice Header ===
    c.setFont("Helvetica-Bold", 22)
    c.drawString(margin_left, height - 160, "INVOICE")
    c.line(margin_left, height - 165, margin_right, height - 165)

    c.setFont("Helvetica", font_medium)
    c.drawString(margin_left, height - 185, f"Invoice #: {data['invoice_number']}")
    c.drawString(margin_left, height - 200, f"Date: {data['invoice_date']}")
    c.drawString(margin_left, height - 215, f"Due Date: {data['due_date']}")

    # === Client Info ===
    c.setFont("Helvetica-Bold", font_medium)
    c.drawString(margin_left, height - 250, "Bill To:")
    c.setFont("Helvetica", font_medium)
    c.drawString(margin_left, height - 270, data['client_name'])
    c.drawString(margin_left, height - 285, data['client_address'])
    c.drawString(margin_left, height - 300, f"Phone: {data['client_phone']}")
    c.drawString(margin_left, height - 315, f"Email: {data['client_email']}")

    # === Items Table Header ===
    y = height - 350
    c.setFont("Helvetica-Bold", font_medium)
    c.drawString(margin_left, y, "Description")
    c.drawString(300, y, "Quantity")
    c.drawString(370, y, "Unit Price")
    c.drawString(460, y, "Amount")
    c.line(margin_left, y - 5, margin_right, y - 5)

    # === Invoice Items ===
    c.setFont("Helvetica", font_small)
    y -= 20
    subtotal = 0

    for item in data['items']:
        amount = item['quantity'] * item['unit_price']
        subtotal += amount

        c.drawString(margin_left, y, item['description'])
        c.drawRightString(330, y, str(item['quantity']))
        c.drawRightString(440, y, f"${item['unit_price']:,.2f}")
        c.drawRightString(550, y, f"${amount:,.2f}")
        y -= 20

        # If the page is too full, move to next page (optional enhancement)
        if y < 100:
            c.showPage()
            y = height - 100

    # === Totals ===
    tax = subtotal * (data.get('tax_rate', 0) / 100)
    total = subtotal + tax

    c.setFont("Helvetica-Bold", font_medium)
    y -= 10
    c.line(370, y, margin_right, y)
    y -= 20
    c.drawString(400, y, "Subtotal:")
    c.drawRightString(550, y, f"${subtotal:,.2f}")
    y -= 20
    c.drawString(400, y, f"Tax ({data.get('tax_rate', 0)}%):")
    c.drawRightString(550, y, f"${tax:,.2f}")
    y -= 20
    c.drawString(400, y, "TOTAL:")
    c.drawRightString(550, y, f"${total:,.2f}")

    # === Payment Terms & Footer ===
    y -= 50
    c.setFont("Helvetica", font_small)
    c.drawString(margin_left, y, f"Payment Terms: {data.get('payment_terms', 'Due on receipt')}")
    c.drawString(margin_left, y - 15, "Thank you for your business!")

    # Save the PDF
    c.save()
    buffer.seek(0)
    return buffer
