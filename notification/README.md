# Módulo `notificacion`

#### `notif.py`

Este módulo implementa un **servicio consumidor de mensajes RabbitMQ** que procesa mensajes JSON codificados, decodifica PDFs adjuntos en base64, y envía correos electrónicos con las facturas en formato PDF a los clientes.

**Características principales:**
* Conexión a RabbitMQ para consumir mensajes de la cola `invoice_queue`.
* Uso de variables de entorno para configuración SMTP segura mediante `dotenv`.
* Envío de correos electrónicos con archivos PDF adjuntos usando `smtplib` y módulos MIME de Python.
* Manejo robusto de errores con trazas detalladas para facilitar debugging.
* Configuración para desconexión ordenada con captura de interrupciones de teclado (`KeyboardInterrupt`).

### Ejemplo de funcionamiento
* Recibe un mensaje con estructura JSON que contiene:

  * `email`: dirección de destino.
  * `pdf`: factura en base64.
  * `client_name`: nombre del cliente.
  * `invoice_number`: número de factura.
* Decodifica el PDF y envía el correo con asunto personalizado.
* Confirma la recepción del mensaje a RabbitMQ para evitar reprocesos.