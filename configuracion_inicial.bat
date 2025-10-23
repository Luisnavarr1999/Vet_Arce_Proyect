@echo off
echo .::CONFIGURACION INICIAL DEL PROYECTO::.
echo Copyright (c) Copicoders Soluciones Informaticas
echo Realizando migraciones a la base de datos...
py manage.py migrate
echo OK
echo Obteniendo archivos estaticos...
py manage.py collectstatic
echo OK
echo Configurando permisos...
py manage.py configurar_permisos
echo OK
echo Proceso en particular finalizado.
echo No olvide correr el servidor ahora.
echo Gracias por utilizar Copicoders.