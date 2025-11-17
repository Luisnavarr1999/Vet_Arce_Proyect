# Vet Arce Manager

Plataforma web desarrollada con Django para digitalizar la gestión de una clínica veterinaria moderna. Incluye un sitio público orientado a clientes y un panel interno para el equipo clínico y administrativo, permitiendo reservar horas, mantener fichas médicas, administrar inventario y coordinar la atención diaria.

## Tabla de contenidos
- [Arquitectura del proyecto](#arquitectura-del-proyecto)
- [Características principales](#características-principales)
- [Requisitos previos](#requisitos-previos)
- [Configuración del entorno](#configuración-del-entorno)
- [Ejecución de migraciones y datos iniciales](#ejecución-de-migraciones-y-datos-iniciales)
- [Comandos útiles](#comandos-útiles)
- [Respaldo automático de la base de datos](#respaldo-automático-de-la-base-de-datos)
- [Estructura de carpetas](#estructura-de-carpetas)
- [Buenas prácticas y convenciones](#buenas-prácticas-y-convenciones)
- [Pruebas automatizadas](#pruebas-automatizadas)
- [Despliegue](#despliegue)
- [Contacto y soporte](#contacto-y-soporte)

## Arquitectura del proyecto
El proyecto sigue la arquitectura estándar de Django (MTV) y se organiza en dos aplicaciones principales:

- **`ambpublica/`**: vista pública para los clientes de la clínica. Incluye la página principal, formulario de contacto, asistente de chat con respuestas guiadas, flujo de reserva de horas y la capa de confirmaciones vía correo electrónico.
- **`paneltrabajador/`**: panel interno para el equipo de la veterinaria. Permite administrar clientes, mascotas, historial clínico, agenda, facturación, inventario de productos y conversaciones del chat.

La configuración global reside en el paquete `ficatsmanager/`, que define la conexión a la base de datos MySQL, la configuración de correo SMTP, localización regional (es-CL) y la integración de [WhiteNoise](https://whitenoise.evans.io/) para servir archivos estáticos.

## Características principales
- **Agenda médica centralizada**: creación, reasignación y confirmación de citas con control de estados, asistencia y servicios ofrecidos.
- **Gestión de clientes y mascotas**: fichas completas con validaciones de RUT chileno, teléfonos en formato internacional, historial clínico y documentos adjuntos.
- **Historial clínico y adjuntos**: carga y descarga de documentos asociados a evoluciones médicas, con limpieza automática del almacenamiento al eliminar registros.
- **Panel de facturación e inventario**: registro de productos/servicios utilizados y emisión de comprobantes (ver vistas en `paneltrabajador/views/factura.py` y `paneltrabajador/views/producto.py`).
- **Portal público con autoservicio**: flujo guiado para solicitar horas, cancelar citas, actualizar datos y un chatbot con respuestas frecuentes (`ambpublica/views.py`).
- **Notificaciones por correo**: envío de correos mediante SMTP configurable para contactos, confirmaciones y restablecimiento de contraseñas.
Integre las credenciales, claves y endpoints externos mediante el sistema de gestión de secretos que utilice su equipo (por ejemplo, variables de entorno protegidas o servicios como Vault). Consulte `ficatsmanager/settings.py` para conocer los nombres de cada variable esperada. Defina `DJANGO_PROD=1` en los ambientes publicados para habilitar HTTPS forzado, cookies seguras y Argon2.

## Requisitos previos
- Python 3.10 o superior.
- MySQL 8.x (o MariaDB equivalente) con una base de datos vacía accesible.
- Herramientas de desarrollo básicas: `git`, `pip`, `virtualenv` (recomendado).
- Credenciales SMTP para el envío de correos (cualquier proveedor transaccional).

## Configuración del entorno
1. **Clonar el repositorio**
   ```bash
   git clone https://github.com/<organizacion>/Vet_Arce_Proyect.git
   cd Vet_Arce_Proyect
   ```
2. **Crear y activar un entorno virtual**
   ```bash
   python -m venv .venv
   source .venv/bin/activate   # En Windows: .venv\Scripts\activate
   ```
3. **Instalar dependencias**
   ```bash
   pip install -r requirements.txt
   ```
4. **Configurar parámetros sensibles**
   Integre las credenciales, claves y endpoints externos mediante el sistema de gestión de secretos que utilice su equipo (por ejemplo, variables de entorno protegidas o servicios como Vault). Consulte `ficatsmanager/settings.py` para conocer los nombres de cada variable esperada.

## Ejecución de migraciones y datos iniciales
1. **Aplicar migraciones**
   ```bash
   python manage.py migrate
   ```
2. **Crear un superusuario**
   ```bash
   python manage.py createsuperuser
   ```
3. **Configurar grupos y permisos base**: se crean automáticamente después de `migrate`, pero puedes reejecutar el comando si necesitas forzar la sincronización manual.
   ```bash
   python manage.py configurar_permisos
   ```
4. **Cargar datos de prueba** (cuando existan fixtures personalizadas):
   ```bash
   python manage.py loaddata <fixture.json>
   ```

## Comandos útiles
- **Servidor de desarrollo**
  ```bash
  python manage.py runserver
  ```
- **Recolectar archivos estáticos** (para producción con WhiteNoise)
  ```bash
  python manage.py collectstatic
  ```
- **Auditoría de dependencias** (OWASP):
  ```bash
  pip install -r requirements-dev.txt
  pip-audit
  ```
  Ejecuta este comando antes de desplegar para detectar librerías vulnerables.

## Respaldo automático de la base de datos
Para cumplir con el requerimiento de respaldos diarios en Dropbox se añadió el comando
personalizado `backup_database`. Sigue estos pasos para dejarlo operando:

1. **Configura las credenciales de Dropbox** en tu `.env` (o en el servicio de secretos que uses):
   ```bash
   DROPBOX_ACCESS_TOKEN=<token_proporcionado>
   DROPBOX_BACKUP_FOLDER=/vet_arce_backups  # opcional, por defecto apunta a esta ruta
   ```
   > _Nunca_ subas el token al repositorio. Solo tiene que existir como variable de entorno.
2. **Instala/actualiza dependencias** para incluir el SDK de Dropbox:
   ```bash
   pip install -r requirements.txt
   ```
3. **Prueba el comando en local** (el flag `--local-only` evita subir el archivo y deja una copia en la carpeta actual):
   ```bash
   python manage.py backup_database --local-only
   ```
   - Para bases MySQL el comando ejecuta `mysqldump`, por lo que debes tener esa utilidad disponible en el servidor.
   - Para SQLite simplemente copia el archivo `.sqlite3`.
4. **Programa la ejecución diaria** usando `cron`, systemd timers o el scheduler que utilices. Ejemplo con cron ejecutándose todos los días a las 03:00:
   ```cron
   0 3 * * * cd /ruta/a/Vet_Arce_Proyect && /ruta/a/.venv/bin/python manage.py backup_database >> /var/log/vet_arce_backup.log 2>&1
   ```

El comando genera archivos con sello temporal y los sube a la carpeta `/vet_arce_backups` del Dropbox asociado al token. Si el envío falla se mostrará un error detallado en la salida estándar para facilitar el monitoreo.

## Estructura de carpetas
```
Vet_Arce_Proyect/
├── ambpublica/              # Sitio público (reservas, contacto, chatbot)
├── paneltrabajador/         # Panel interno (clientes, mascotas, agenda, facturación)
├── ficatsmanager/           # Configuración global de Django
├── templates/               # Plantillas compartidas (Bootstrap 5)
├── static/                  # Recursos estáticos (CSS, JS, imágenes)
├── media/                   # Archivos subidos (carpeta generada en tiempo de ejecución)
├── requirements.txt         # Dependencias del proyecto
├── manage.py                # Punto de entrada para comandos Django
└── README.md                # Este documento
```

## Buenas prácticas y convenciones
- **Idioma**: todo el contenido público y los mensajes del panel están en español (Chile).
- **Zonificación**: la configuración regional utiliza `America/Santiago` y formatos locales (`pytz`, `django.utils.formats`).
- **Validaciones personalizadas**: utilice los formularios incluidos (`forms.py`) para garantizar formatos correctos de RUT, teléfono y número de chip.
- **Documentos clínicos**: al eliminar una evolución o documento, se limpia automáticamente el archivo asociado mediante la lógica en `MascotaDocumento.delete`.
- **Mensajería y notificaciones**: se usan los tags de mensajes de Django adaptados a Bootstrap 5 (`ficatsmanager/settings.py`).

## Pruebas automatizadas
Ejecute la suite de tests con:
```bash
python manage.py test
```
Se recomienda correr las pruebas antes de cada despliegue o integración para verificar formularios, vistas y permisos críticos.

## Despliegue
1. Replicar la configuración sensible del entorno (con `DEBUG=False` y `ALLOWED_HOSTS` apuntando al dominio oficial) utilizando el mecanismo seguro definido por su infraestructura.
2. Ejecutar `collectstatic` y servir la carpeta `productionfiles/` en el servidor web (WhiteNoise permite servirla directamente desde la aplicación WSGI).
3. Configurar el servicio (uWSGI, Gunicorn o similar) apuntando a `ficatsmanager.wsgi`.
4. Habilitar HTTPS con certificados válidos (Let’s Encrypt recomendado).
5. Programar tareas de respaldo para la base de datos MySQL y la carpeta `media/`.

## Contacto y soporte
Para dudas técnicas o solicitudes de nuevas funcionalidades, utilice el panel de issues del repositorio o escriba directamente al contacto interno definido para su despliegue (por ejemplo, `equipo-ti@example.com`). También puede coordinar reuniones con el equipo de desarrollo interno a través del panel de trabajadores.