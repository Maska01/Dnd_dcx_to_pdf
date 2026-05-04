# Historial de la conversación

## Contexto
Proyecto: conversor de Word (.docx) → PDF con estilo "Aventura" (inspirado en
un PDF de aventura de Stranger Things en español).

---

## Turno 1 — Usuario
> Me gustaría saber si es posible que crees un script en Python al que pueda
> darle un archivo de Word y me devuelva un PDF como el adjunto, pero partiendo
> de un Word básico con ciertos parámetros. ¿Qué necesitamos y qué parámetros
> debo proporcionar?

### Respuesta
Se propuso un script con `python-docx` + `reportlab`. Se pidió definir:
- Estructura de estilos en Word (Título 1/2/3, Cita, Normal, Listas).
- Color principal y tipografía.
- Si se quería portada, TOC, encabezado/pie e imágenes.
- Formatos especiales (consejos DM, citas).

Se crearon los archivos iniciales:
- `convert.py`
- `requirements.txt`
- `README.md`

---

## Turno 2 — Usuario
Respondió a las preguntas:
1. Color rojo `#8B0000` y Helvetica → OK.
2. Quiere imagen de portada con ruta de ejemplo (aún no decide cuál).
3. Sí quiere tabla de contenidos.
4. No quiere encabezado/pie de página.
5. Sí habrá imágenes embebidas en el Word.
6. Formato "Consejo del DM": texto azul dentro de recuadro azul, respetando
   negritas (referencia visual adjunta).
7. Citas: texto negro dentro de recuadro amarillo (referencia visual adjunta).

### Respuesta
Se reescribió `convert.py` con:
- Constantes de color editables (rojo primario, azul para consejos DM,
  amarillo para citas).
- Portada con imagen opcional (`IMAGEN_PORTADA_DEFAULT` y flag `--portada`).
- Tabla de contenidos automática con `multiBuild` (`DocConTOC`).
- Extracción e inserción de imágenes embebidas del docx.
- Detección automática de párrafos que empiezan por `CONSEJO DEL DM` →
  caja azul redondeada.
- Estilo `Cita` de Word → caja amarilla con texto negro.
- Eliminado encabezado/pie de página.

`README.md` actualizado con la convención de estilos de Word y ejemplos.

---

## Turno 3 — Usuario
> ¿Podemos mover este chat y los archivos generados a otra carpeta?

### Respuesta
Se preguntó la ruta destino y si quería conservar el historial en `CHAT.md`.

---

## Turno 4 — Usuario
Destino: `C:\Users\uiv06676\Documents\StrangerThings_PDF`
Sí quiere `CHAT.md`.

### Acción
- Generado este `CHAT.md`.
- Carpeta movida desde `C:\Users\uiv06676\Downloads\word_to_aventura_pdf` a
  `C:\Users\uiv06676\Documents\StrangerThings_PDF`.

---

## Estado final del proyecto
Carpeta: `C:\Users\uiv06676\Documents\StrangerThings_PDF`

Archivos:
- `convert.py` — script principal.
- `requirements.txt` — dependencias (`python-docx`, `reportlab`).
- `README.md` — instrucciones de uso.
- `CHAT.md` — este historial.

### Uso rápido
```powershell
cd C:\Users\uiv06676\Documents\StrangerThings_PDF
pip install -r requirements.txt
python convert.py mi_aventura.docx salida.pdf `
    --titulo "Stranger Things" `
    --subtitulo "El Otro Lado" `
    --autor "Tu Nombre" `
    --portada "C:\ruta\a\tu\imagen.jpg"
```

### Convención del Word
| En Word | Resultado |
|---|---|
| Título 1 / 2 / 3 | Encabezados (1 y 2 entran en TOC) |
| Normal | Texto justificado |
| Cita (Quote) | 🟨 caja amarilla + texto negro |
| Párrafo que empieza con `CONSEJO DEL DM` | 🟦 caja azul + texto azul |
| Listas con viñetas | Listas |
| Imágenes pegadas en el docx | Insertadas en el PDF |
