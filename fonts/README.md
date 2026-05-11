# Fuentes personalizadas

Puedes colocar aquí cualquier archivo de fuente `.ttf` u `.otf` para que el conversor lo registre automáticamente.

## Cómo se detectan

- Cada archivo dentro de `fonts/` se analiza al abrir el menú interactivo o aplicar la configuración del documento.
- El nombre visible de la fuente se deriva del nombre del archivo.
- Si subes varias variantes de una misma familia, el sistema intenta agruparlas automáticamente.

## Variantes reconocidas

El detector reconoce sufijos comunes en el nombre del archivo, por ejemplo:

- `Regular`
- `Bold`
- `Italic`
- `Oblique`
- `BoldItalic`
- `BoldOblique`

## Ejemplos

- `Ryman Eco Regular.ttf`
- `Ryman Eco Bold.ttf`
- `Garamond-Italic.otf`
- `MiFuente-BoldItalic.ttf`

Si una fuente personalizada no puede registrarse, el proyecto mantiene automáticamente las fuentes base de `ReportLab` como fallback.
