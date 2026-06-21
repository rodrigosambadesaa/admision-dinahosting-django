# Prueba técnica Dinahosting en Django

Reimplementación en Django del repositorio original `rodrigosambadesaa/admision-dinahosting`.

## Qué incluye

- Portada con enlaces a los ejercicios.
- Vista web para calcular timestamps Fibonacci en:
  - mes actual en UTC
  - año actual en UTC
  - rango personalizado
- Soporte para fechas `Y-m-d H:i:s` y para `ts:<bigint>`.
- Pantalla de login HTML5 con validación nativa.
- Comando `manage.py fibonacci` para cubrir el ejercicio CLI original.

## Arranque

```bash
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Aplicación disponible en `http://127.0.0.1:8000/`.

## Docker

Levantar la parte web:

```bash
docker compose up web
```

Después abre `http://localhost:8087`.

Si el puerto `8087` está ocupado:

```bash
WEB_PORT=8081 docker compose up web
```

En PowerShell:

```powershell
$env:WEB_PORT=8081; docker compose up web
```

Ejecutar el ejercicio CLI dentro de Docker:

```bash
docker compose run --rm django-cli python manage.py fibonacci "2026-06-01 00:00:00" "2026-06-30 23:59:59"
```

También puedes usar un rango sintético extremo:

```bash
docker compose run --rm django-cli python manage.py fibonacci "ts:12345678901234567890" "ts:12345678901234567999"
```

## Rutas

- `/` portada
- `/fibonacci/` calculadora Fibonacci
- `/login/` formulario de login

## Comando CLI

```bash
python manage.py fibonacci "2026-06-01 00:00:00" "2026-06-30 23:59:59"
python manage.py fibonacci "ts:12345678901234567890" "ts:12345678901234567999"
```

## Tests

```bash
python manage.py test
```
