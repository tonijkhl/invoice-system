# Módulo `invoice-website`

Este módulo implementa la **interfaz web del sistema de facturación**, permitiendo que los usuarios finales interactúen con las funcionalidades del backend a través de vistas HTML renderizadas por Flask. El sistema administra sesiones seguras y persistentes, e implementa lógica para autenticación, navegación entre vistas, y verificación de sesiones activas.

**Funcionalidades clave:**
* Vistas: `/`, `/sign_in`, `/docs`, `/user_info`, `/logout`
* Autenticación con sesiones seguras (`session` de Flask)
* Persistencia de sesiones durante 7 días (configurable)
* Inicio de sesión con verificación de contraseña usando `check_password_hash`
* Soporte para CORS en el puerto 5001 (ideal para aplicaciones separadas backend/frontend)

Este módulo `database.py`, compartido también con `invoice-API`, administra un **pool de conexiones PostgreSQL** mediante `psycopg2`, permitiendo conexiones concurrentes y eficientes desde múltiples vistas o rutas del servidor web.

**Características:**
* Uso de `psycopg2.pool.SimpleConnectionPool`
* Métodos de obtención (`get_connection`), liberación (`put_connection`) y cierre (`close_all`)
* Base de datos `invoice-db` en localhost con puerto `5431`