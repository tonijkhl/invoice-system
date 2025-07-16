import pika
import json
import base64

def send_invoice_to_queue(email, pdf_buffer, client_name):
    """
    Send invoice information to RabbitMQ queue
    
    Args:
        email (str): Recipient email address
        pdf_buffer (BytesIO): PDF file buffer
        client_name (str): Name of the client
    """
    try:
        # Encode PDF to base64 for transmission
        pdf_base64 = base64.b64encode(pdf_buffer.getvalue()).decode('utf-8')
        
        # Connection parameters - adjust as needed
        connection_params = pika.ConnectionParameters(
            host='localhost',  # RabbitMQ server address
            port=5672,
            credentials=pika.PlainCredentials('guest', 'guest')  # Default RabbitMQ credentials
        )
        
        # Create connection and channel
        connection = pika.BlockingConnection(connection_params)
        channel = connection.channel()
        
        # Declare the queue (if it doesn't exist)
        channel.queue_declare(
            queue='invoice_queue',
            durable=True,  # Messages persist after broker restart
            exclusive=False,
            auto_delete=False
        )
        
        # Prepare message
        message = {
            'email': email,
            'pdf': pdf_base64,
            'client_name': client_name,
            #'invoice_number': data.get('invoice_number')  # Assuming data is available
        }
        
        # Publish message
        channel.basic_publish(
            exchange='',
            routing_key='invoice_queue',
            body=json.dumps(message),
            properties=pika.BasicProperties(
                delivery_mode=2,  # Make message persistent
            )
        )
        
        connection.close()
        return True
    except Exception as e:
        print(f"Error sending to queue: {str(e)}")
        return False