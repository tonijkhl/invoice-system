# Módulo `message-queue`

#### `docker-compose.yml`

Este archivo configura un contenedor Docker que levanta un servicio RabbitMQ con panel de administración habilitado. RabbitMQ se utiliza como **middleware de mensajería asíncrona**, permitiendo el **envío diferido de facturas** generadas en el módulo `invoice-API`.

**Características clave del servicio `queue-invoice`:**
* Imagen base: `rabbitmq:3.8-management-alpine` (ligera y con interfaz web de gestión)
* Puertos expuestos:
  * `5672`: Puerto estándar para el protocolo AMQP.
  * `15672`: Interfaz web de gestión para supervisar colas, conexiones y mensajes.
* Volúmenes persistentes:
  * Datos: `~/.docker-conf/rabbitmq/data/`
  * Logs: `~/.docker-conf/rabbitmq/log/`
* Permite que otros módulos (`invoice-API`) se conecten a RabbitMQ para colocar mensajes (facturas codificadas en base64).