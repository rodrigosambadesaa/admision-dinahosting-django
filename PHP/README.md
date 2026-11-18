# Ejercicio 1 — Fibonacci CLI (versión Django)

Esta carpeta mantiene la estructura de entrega del PDF original. La implementación
es **Django/Python**, no una copia del PHP: el comando real se encuentra en
`challenge/management/commands/fibonacci.py` y la lógica en `challenge/services.py`.

```bash
python PHP/fibonacci.py "ts:0" "ts:21"
# También:
python manage.py fibonacci "2026-01-01 00:00:00" "2026-12-31 23:59:59"
```

Se procesan el mes y el año actuales (UTC) y el intervalo personalizado,
con salida JSON y valores Fibonacci exactos. Las otras carpetas de entrega,
`JAVASCRIPT/` y `CSS/`, contienen los ejercicios autónomos del navegador.
