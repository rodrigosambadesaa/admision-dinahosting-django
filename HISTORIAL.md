# Entrega verificada e historial normalizado

Reimplementación: **Django/Python**.
Fecha de normalización: **18 de noviembre de 2026**.

Se aplicó `git filter-repo` en GitHub Actions, creando un nuevo historial
limpio que conserva el árbol de archivos exacto de la entrega final.
Antes de publicar el nuevo historial se comprobó que el identificador
Git del árbol original y el del resultado eran idénticos. Se retiró
del snapshot el workflow temporal de limpieza.

El PDF `Prueba Tca_PHP.pdf` está copiado byte a byte del repositorio original
(SHA de blob Git: `3fba2fcb5d8dd1fac76a89d6d150f20d44671d04`).
Las carpetas de entrega `PHP/`, `JAVASCRIPT/` y `CSS/` corresponden
a los apartados del enunciado. Las aclaraciones de respuestas se
incluyen en `RESPUESTAS_Y_ADECUACION.md`, sin modificar el PDF.

El historial previo de `main` y los punteros de ramas antiguas de
PR ya fusionadas se sustituyeron por el snapshot correcto. GitHub
puede conservar referencias internas de PR, registros de Actions,
cachés u objetos inaccesibles por ramas normales: la reescritura de
Git no garantiza su purga inmediata de todos los sistemas de GitHub.

Las suites GitHub Actions verifican el contrato del PDF, las pruebas
del framework, la equivalencia del algoritmo y el contenedor HTTP.
