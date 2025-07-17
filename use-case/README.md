# Módulo caso de uso sistema de ventas de una farmacia


### `pharma.py`
Este módulo es una aplicación web construida con Flask que sirve como interfaz para un sistema de gestión farmacéutica. Permite la visualización y consulta de clientes, productos, órdenes (facturas) y sus detalles asociados.

### Funcionalidades principales
* **Rutas HTML para interfaces**: `/clients`, `/products`, `/orders`, etc.
* **API para datos dinámicos JSON**:
  * `/get_invoice_items/<invoice_id>`: detalles de productos por factura.
  * `/get_client_info/<invoice_id>`: datos del cliente relacionado con una factura.
  * `/show_clients`: listado JSON de todos los clientes.
  * `/show_orders`: listado HTML con órdenes y datos de clientes.
  * `/show_products`: listado JSON con productos disponibles.

### Conexión a base de datos PostgreSQL
* Parámetros para conexión están codificados (puedes parametrizar).
* Consultas con joins para obtener datos completos de clientes y facturas.
* Uso correcto de cierres de cursores y conexiones para evitar fugas.

## 2. Resumen de tablas en base de datos `parhma-db`
Base de datos PostgreSQL con estructura para gestión farmacéutica, compuesta por:

### Tablas principales
* **customers**: Información de clientes, incluyendo datos de seguro.
* **products**: Catálogo de productos farmacéuticos con información de precios y tasas.
* **invoices**: Facturas emitidas a clientes con estado de pago.
* **invoice\_items**: Detalle de productos vendidos en cada factura.

### Índices
* Índices para optimizar consultas en `invoice_items` por `invoice_id` y `product_id`.

### Datos de ejemplo
* Clientes reales con nombre, contacto y seguro.
* Productos comunes con códigos, nombres, dosis, forma y precios.
* Facturas con estado pagado o pendiente.
* Detalles de items por factura para consultas detalladas.

## 3. Ejemplo de uso típico
* El usuario accede a `/orders` y ve listado de facturas recientes con nombre de cliente, monto total y estado.
* Al seleccionar una factura, el frontend puede hacer llamadas AJAX a `/get_invoice_items/<id>` y `/get_client_info/<id>` para mostrar detalles de compra y datos de contacto.
* Los datos de clientes y productos pueden mostrarse en tablas con información relevante para administración y análisis.

## 4. Dependencias (requirements.txt)
* Flask 3.1.1
* psycopg2-binary 2.9.10 (para conexión PostgreSQL)
* blinker, click, itsdangerous, Jinja2, MarkupSafe, Werkzeug (dependencias de Flask)

## 5. Ejecución
```bash
python pharma.py
```

La aplicación se ejecuta en puerto 5004 por defecto (`app.run(debug=True, port=5004)`).

## 6. Script SQL para creación de base de datos y tablas

Incluye creación de base de datos, tablas, índices, y datos de ejemplo con:
* Clientes con información básica y seguros.
* Productos con detalles farmacéuticos.
* Facturas con detalles de items.
* Inserciones para tener datos con los cuales probar el sistema.