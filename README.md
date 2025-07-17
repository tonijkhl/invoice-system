## Sistema de generacion y envio por correo de recibos digitales

#### Diagrama de flujo de datos
![!\[alt text\](<Untitled Diagram.drawio.png>)](dfd.png)
El sistema se muestra acoplado a un sistema ya existente (sistema del usuario), genera recibos con los datos de los distintos clientes del sistema y los envia a una cola de mensajeria que a su vez es consumida por el modulo de notificaciones el cual se encarga de enviar el recibo en formato PDF al email de los distintos clientes.

#### Procesos o modulos principales
* Modulo principal de generacion de recibos digitales
* Modulo servidor web
* Modulo de notificaciones