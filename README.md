# Prueba técnica Dinahosting en Django

Reimplementación funcional del [repositorio original en PHP, JavaScript, HTML y CSS](https://github.com/rodrigosambadesaa/admision-dinahosting).

## Equivalencia funcional

- **Portada**: ruta / con acceso a los tres ejercicios.
- **Calculadora web**: /fibonacci/ muestra el mes actual en UTC, año actual en UTC y un rango personalizado.
- **CLI**: python manage.py fibonacci INICIO FIN devuelve el mismo contrato JSON del PHP original: current_month, current_year, custom_range; timestamps y valores Fibonacci como cadenas.
- **Formulario HTML5**: /login/ mantiene la validación y los estilos Bootstrap, pero es una demostración sin autenticación.
- **Rangos**: los límites se incluyen y se normalizan si llegan invertidos.
- **Fechas**: formato estricto YYYY-MM-DD HH:MM:SS, en UTC, incluidos años 0000 a 0099 (calendario gregoriano proléptico).
- **Timestamps sintéticos**: ts:<bigint>, entero con signo opcional de hasta 256 dígitos decimales; no es necesario que represente una fecha real.
- **Fibonacci**: se conserva la secuencia original 0, 1, 1, 2, 3, 5… y la repetición del valor 1.

El cálculo de timestamps usa aritmética entera, sin conversiones de precisión reducida.

## Desarrollo local

Requiere Python 3.12 o posterior y Django 6.0.6 (requirements.txt).

~~~bash
python -m pip install -r requirements.txt
export DJANGO_DEBUG=1
python manage.py migrate
python manage.py runserver
~~~

En Windows PowerShell, usa la variable de entorno equivalente:

~~~powershell
$env:DJANGO_DEBUG="1"
python manage.py migrate
python manage.py runserver
~~~

La aplicación estará disponible en http://127.0.0.1:8000/.

## Docker (solo desarrollo)

~~~bash
docker compose up --build web
~~~

Abre http://localhost:8087. Para cambiar de puerto, define WEB_PORT=8081.

Comando CLI:

~~~bash
docker compose run --rm django-cli python manage.py fibonacci "ts:5" "ts:13"
docker compose run --rm django-cli python manage.py fibonacci "2024-02-29 00:00:00" "2024-02-29 23:59:59"
~~~

La configuración de Compose activa explícitamente DEBUG y utiliza una clave **exclusivamente de desarrollo**. No es adecuada para una aplicación expuesta a internet; en producción usa HTTPS, servidor WSGI/ASGI, un secreto único, hosts autorizados y despliegue correcto de archivos estáticos.

## Tests y GitHub Actions

~~~bash
DJANGO_DEBUG=1 python manage.py test
DJANGO_DEBUG=1 python manage.py check
~~~

La CI ejecuta: tests de Django con Python 3.12, 3.13 y 3.14; verificación de migraciones; comparación diferencial de resultados contra PHP y JavaScript; chequeos de configuración de seguridad para producción; compilación Docker y comprobación HTTP de las rutas públicas y cabeceras.

Para comparar manualmente contra el código original, clona este en la carpeta reference/ y selecciona el commit 3019da805198f46c72656ac673c49ede7fa89406. Con PHP y Node.js instalados:

~~~bash
DJANGO_DEBUG=1 python tests/compare_reference.py
~~~

## Configuración y seguridad

- DJANGO_DEBUG=1 habilita desarrollo local. Si no se especifica, DEBUG está desactivado.
- DJANGO_SECRET_KEY es obligatoria cuando DEBUG está desactivado.
- DJANGO_ALLOWED_HOSTS contiene los hosts permitidos, separados por comas.
- Con DEBUG desactivado se activan HTTPS obligatorio, cookies secure y HSTS.
- La Content Security Policy se devuelve como cabecera HTTP además de las restricciones en plantillas.

**Login solo de demostración:** no guarda ni autentica credenciales. No introduzcas contraseñas reales. El formulario envía únicamente a la propia aplicación y esta rechaza los POST. Su objetivo es reproducir el ejercicio visual HTML5/CSS.
