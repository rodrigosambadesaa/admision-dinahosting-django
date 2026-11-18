# Respuestas del PDF y adecuación técnica — Django

El documento **`Prueba Tca_PHP.pdf`** se conserva idéntico al original (SHA de
objeto Git `3fba2fcb5d8dd1fac76a89d6d150f20d44671d04`).
Las respuestas personales del candidato, incluido que empezó con C y que
indicó Java como lenguaje principal, se mantienen como constancia histórica.

## Precisiones sobre las respuestas técnicas originales

- **Regex de etiquetas HTML**: la expresión señalada detecta bloques
  `<script>`, `<style>`, comentarios y etiquetas HTML. No es un
  saneador fiable de HTML arbitrario; debe usarse un parser y/o un sanitizer
  probado si el objetivo es defenderse de XSS.
- **`docker-compose up`**: crea (o recrea cuando corresponda), inicia y
  adjunta servicios; la construcción de imágenes no es incondicional.
  `docker compose up --build` solicita expresamente reconstruirlas.
- **MVC**: Kendo UI es principalmente una biblioteca de componentes de
  interfaz, no un framework MVC completo. Laravel es un ejemplo clásico;
  Django utiliza MTV, análogo por separación de responsabilidades.
- **ORM**: es una técnica/capa de mapeo objeto-relacional, no simplemente
  una práctica genérica. Ejemplos: Eloquent en Laravel y el ORM de Django.
- **`git stash`**: guarda temporalmente cambios del índice y árbol de
  trabajo; no incluye ficheros no rastreados por defecto (se usa `-u`).

El análisis de la función PHP de la página 2 sigue vigente, especialmente
el uso potencial de `$form` sin inicializar y el `catch` redundante.

## Correspondencia con los tres ejercicios del PDF

| Carpeta solicitada | Entrega Django |
| --- | --- |
| `PHP/` | `fibonacci.py`, adaptador CLI al comando Django; servicios Python |
| `JAVASCRIPT/` | HTML y Vanilla JS ES6+ originales, autónomos |
| `CSS/` | Formulario HTML5 sin JS, Bootstrap y fuentes CSS/SCSS |

El enunciado exige `POST https://dinahosting.com/login-usuarios`.
Por fidelidad al contrato, se conserva como destino declarado en los
formularios. **No hay autenticación dentro del proyecto**. La página
advierte de utilizar únicamente datos ficticios; un envío real al pulsar
«Entrar» se dirige al dominio externo de Dinahosting.
