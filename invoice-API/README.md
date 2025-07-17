El archivo `main.py`, implementa una **API RESTful en Flask** para la gestión de usuarios, claves API y la generación de facturas. La funcionalidad incluye:

* Registro, edición, eliminación y visualización de usuarios.
* Generación de claves API seguras.
* Validación de acceso a rutas protegidas mediante decorador `@api_key_required`.
* Generación de facturas en formato PDF a partir de datos estructurados, incluyendo envío opcional a una cola de mensajes para procesamiento posterior.
* Exposición de métricas de facturación.

El módulo `invoice_template.py` usa la librería `reportlab` para generar facturas en formato PDF. Los aspectos clave incluyen:
* Inclusión de logo corporativo.
* Estructura profesional con sección para datos de la empresa, cliente, tabla de ítems, subtotal, impuestos y total.
* Manejo de múltiples páginas si hay muchos ítems.
* Personalización de términos de pago y notas de agradecimiento.

El módulo `message_queue.py` maneja el **envío de facturas codificadas en base64** a una cola RabbitMQ llamada `invoice_queue`. Características:
* Uso de `pika` como cliente de AMQP.
* Configuración por defecto de conexión a `localhost`.
* Publicación de mensajes JSON con metadatos (cliente, email y PDF codificado).
* Persistencia de mensajes para evitar pérdida tras reinicio del broker.

`database.py` proporciona una clase `Database` que implementa un **pool de conexiones** a una base de datos PostgreSQL utilizando `psycopg2`. Detalles clave:
* Configuración de parámetros como usuario, contraseña, host y puerto.
* Métodos para obtener, devolver y cerrar conexiones.
* Se usa en toda la API para operaciones consistentes y escalables sobre la base de datos.
