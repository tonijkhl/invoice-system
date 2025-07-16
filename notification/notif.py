import pika
import json
import base64
import smtplib
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email import encoders
import traceback
from dotenv import load_dotenv
import os


# === SMTP CONFIG ===
load_dotenv()  # Load from .env

SMTP_SERVER = os.getenv('SMTP_SERVER')
SMTP_PORT = int(os.getenv('SMTP_PORT', 587))  # with default
SMTP_USER = os.getenv('SMTP_USER')
SMTP_PASS = os.getenv('SMTP_PASS')

def send_email_with_pdf(to_email, pdf_bytes, client_name, invoice_number):
    try:
        # Create the email message
        message = MIMEMultipart()
        message['From'] = SMTP_USER
        message['To'] = to_email
        message['Subject'] = f"Your Invoice - {invoice_number or 'No. Not Provided'}"

        # Email body
        body = f"Dear {client_name},\n\nPlease find your invoice attached.\n\nBest regards,\nPharmacy Billing Team"
        message.attach(MIMEText(body, 'plain'))

        # PDF attachment
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(pdf_bytes)
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', f'attachment; filename="invoice_{invoice_number or "attached"}.pdf"')
        message.attach(part)

        # Send email
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SMTP_USER, SMTP_PASS)
        server.send_message(message)
        server.quit()

        print(f"✅ Email sent to {to_email}")
    except Exception as e:
        print(f"❌ Failed to send email: {e}")
        traceback.print_exc()

def callback(ch, method, properties, body):
    try:
        print("📩 Received new message")
        data = json.loads(body)

        email = data['email']
        pdf_base64 = data['pdf']
        client_name = data.get('client_name', 'Customer')
        invoice_number = data.get('invoice_number', '0000')

        pdf_bytes = base64.b64decode(pdf_base64)
        send_email_with_pdf(email, pdf_bytes, client_name, invoice_number)

        # Acknowledge message
        ch.basic_ack(delivery_tag=method.delivery_tag)
    except Exception as e:
        print(f"❌ Error processing message: {e}")
        traceback.print_exc()

def start_notification_service():
    try:
        print("🔌 Connecting to RabbitMQ...")
        connection_params = pika.ConnectionParameters(
            host='localhost',
            port=5672,
            credentials=pika.PlainCredentials('guest', 'guest')
        )
        connection = pika.BlockingConnection(connection_params)
        channel = connection.channel()

        channel.queue_declare(
            queue='invoice_queue',
            durable=True,
            exclusive=False,
            auto_delete=False
        )

        channel.basic_qos(prefetch_count=1)  # Fair dispatch
        channel.basic_consume(queue='invoice_queue', on_message_callback=callback)

        print("🚀 Waiting for invoice messages...")
        channel.start_consuming()
    except KeyboardInterrupt:
        print("👋 Shutting down...")
    except Exception as e:
        print(f"❌ Could not connect: {e}")
        traceback.print_exc()

if __name__ == '__main__':
    start_notification_service()
