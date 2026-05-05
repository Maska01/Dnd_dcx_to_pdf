# Historial de la conversación — Word → PDF estilo Aventura

Proyecto: conversor de Word (`.docx`) → PDF con estilo "Aventura" (inspirado
en un PDF de Stranger Things en español).

Carpeta: `C:\Users\uiv06676\Documents\StrangerThings_PDF`

Archivos:
- `convert.py` — script principal.
- `requirements.txt` — dependencias (`python-docx`, `reportlab`, `Pillow`).
- `README.md` — instrucciones de uso.
- `CHAT.md` — este historial.
- `.gitignore` — ignora `__pycache__/`, `*.pyc`, `.venv/`, `venv/`, `*.pdf`, `*.docx`.

---

## Turno 1 — Usuario
> Crear un script Python que convierta un Word a un PDF como un adjunto de
> aventura. ¿Qué parámetros se necesitan?

### Respuesta
Propuesta usando `python-docx` + `reportlab`. Se preguntaron preferencias:
estilos de Word, color, tipografía, portada, TOC, encabezado/pie, formatos
especiales (Consejo del DM, citas), imágenes.

Archivos iniciales: `convert.py`, `requirements.txt`, `README.md`.

---

## Turno 2 — Usuario
Definió:
1. Color rojo `#8B0000`, fuente Helvetica.
2. Imagen de portada con ruta de ejemplo.
3. Sí, tabla de contenidos.
4. No quiere encabezado/pie.
5. Sí habrá imágenes embebidas en el Word.
6. "Consejo del DM" = recuadro azul + texto azul (respetando negritas).
7. "Cita" = recuadro amarillo + texto negro.

### Respuesta
Reescritura de `convert.py` con:
- Constantes de color editables.
- Portada con imagen opcional (`IMAGEN_PORTADA_DEFAULT`, flag `--portada`).
- TOC automática con `multiBuild` (clase `DocConTOC`).
- Extracción e inserción de imágenes embebidas del docx.
- Detección de `CONSEJO DEL DM` → caja azul.
- Estilo `Cita` (Quote) → caja amarilla.

---

## Turno 3 — Usuario
> ¿Podemos mover este chat y los archivos generados a otra carpeta?

### Respuesta
Carpeta movida a `C:\Users\uiv06676\Documents\StrangerThings_PDF` y
generado este `CHAT.md`.

---

## Turno 4 — Usuario
> Inicia un repositorio de git con un commit inicial.

### Acción
```powershell
git init
# .gitignore con __pycache__/, *.pyc, .venv/, venv/, *.pdf, *.docx
git add .
git commit -m "chore: initial commit - Word to Aventura PDF converter"
```
Commit raíz: `5720e82` (master).

---

## Turno 5 — Usuario
> Selección de archivo de entrada con ventana de Windows (diálogo).

### Cambios en `convert.py`
- Nueva función `_seleccionar_archivo_dialogo()` con `tkinter.filedialog`.
- En `main()` los argumentos `entrada` y `salida` se hicieron opcionales
  (`nargs="?"`).
  - Si falta `entrada` → `askopenfilename` filtrando `*.docx`.
  - Si falta `salida` → `asksaveasfilename` filtrando `*.pdf`,
    prerrellenado con el nombre del docx.
- Ventana forzada a primer plano con `-topmost`.

---

## Turno 6 — Usuario
> El "Consejo del DM" no se aplicó al PDF (en Word el texto era
> `**CONSEJO DEL DM (REGLAS 5.5):**` con asteriscos markdown).

### Causa
- `startswith("consejo del dm")` fallaba por los `**` iniciales.
- Los `**...**` salían literales en el PDF.

### Cambios en `convert.py`
1. `es_consejo_dm()` ahora hace `lstrip(" *_“\"'\t")` antes de comparar.
2. `runs_a_html()` añadió: si Word no marcó negrita/cursiva en los runs,
   convertir markdown inline:
   - `**texto**` → `<b>texto</b>`
   - `*texto*` → `<i>texto</i>`
3. Añadido `import re`.

---

## Turno 7 — Usuario
> Una cita en dos párrafos consecutivos sale en dos cajas. Fusionar citas
> consecutivas si no hay más de 2 saltos de renglón entre ellas.

### Cambios en `convert.py`
- Buffer `citas_pendientes` y contador `vacios_desde_ultima_cita`.
- Constante `MAX_VACIOS_FUSION_CITA = 2`.
- Nueva función `vaciar_citas()` que emite todo el buffer en una sola
  caja amarilla, separando párrafos con `<br/><br/>`.
- Cualquier contenido distinto (texto normal, título, imagen, lista,
  Consejo del DM) cierra el bloque de citas.

---

## Turno 8 — Usuario
> Cambiar la condición de "consejo del dm" por "Consejo para el DM".

### Cambios
- `es_consejo_dm()`: ahora detecta `"consejo para el dm"`.
- Actualizados docstrings, comentarios y `README.md`
  (tabla, sección, ejemplo).

---

## Turno 9 — Usuario
> En Word los Consejos del DM están envueltos entre `#...#`. Hacer que todo
> lo que esté entre dos almohadillas se considere parte del mismo Consejo.

### Cambios en `convert.py`
Primera versión: bloques `#...#` a nivel de párrafo (apertura al inicio,
cierre al final), con buffer `consejo_buffer` y función `emitir_consejo()`.

`README.md`: documentada la nueva sintaxis con dos formas (bloque `#…#` y
párrafo único `CONSEJO PARA EL DM`).

---

## Turno 10 — Usuario
> Los Consejos no se generaron. Ejemplo: `#Consejo para el DM:…#` está
> **dentro** de un párrafo de viñeta (mismo párrafo que `Cultivos Marchitos:`).

### Causa
La detección anterior sólo miraba si el párrafo empezaba/terminaba con `#`,
así que `#` interiores (inline) no disparaban nada.

### Cambios en `convert.py`
Reescrita la lógica para procesar `#` **inline**:
- En cada párrafo, dividir el HTML por `#` y alternar estado
  `dentro_consejo` (toggle).
- Texto **fuera** del consejo se reemite con el estilo original del
  párrafo (viñeta, cuerpo, cita, H1/H2/H3).
- Texto **dentro** se acumula en `consejo_buffer` y se emite como caja
  azul cuando aparece el `#` de cierre.
- Se mantiene compatibilidad con el formato anterior
  (`CONSEJO PARA EL DM` sin `#`).

---

## Turno 11 — Usuario
Error en la ejecución:
```
ValueError: paragraph text '<para><b></para>' caused exception
Parse error: saw </para> instead of expected </b>
```

### Causa
El `#` quedó dentro de un run con negrita en Word, p.ej.
`<b>#Consejo para el DM:</b> ... <b>#</b>`. Al hacer `split("#")` los
segmentos quedaban con HTML desbalanceado (`<b>` sin cierre, `</b>` sin
apertura) y ReportLab fallaba.

### Cambios en `convert.py`
Nuevo helper `_split_html_balanceado(html, sep="#")`:
- Recorre el HTML manteniendo una pila de etiquetas abiertas.
- Al encontrar el separador, **cierra** las etiquetas pendientes antes del
  corte y las **reabre** al inicio del siguiente segmento.
- Garantiza que cada segmento sea HTML válido aunque el `#` esté dentro
  de `<b>`, `<i>`, `<u>`.

El bucle principal ahora usa `_split_html_balanceado(texto_html, "#")` en
lugar de `texto_html.split("#")`.

---

## Turno 12 — Usuario
> Guarda esta conversación para exportarla a otro agente de IA.

### Acción
Regenerado este `CHAT.md` con el historial completo y el estado final del
proyecto.

---

## Estado final del proyecto

### Convención del Word
| En Word | Resultado en PDF |
|---|---|
| Título 1 / 2 / 3 | Encabezados (1 y 2 entran en TOC) |
| Normal | Texto justificado |
| Cita (Quote) | 🟨 caja amarilla + texto negro (citas consecutivas se fusionan si hay ≤ 2 párrafos vacíos entre ellas) |
| Párrafo que empieza con `CONSEJO PARA EL DM` | 🟦 caja azul + texto azul |
| Texto envuelto entre `#...#` (inline o multi-párrafo) | 🟦 caja azul + texto azul |
| Listas con viñetas | Listas |
| Imágenes embebidas | Insertadas en el PDF |
| `**texto**` / `*texto*` (si no hay formato real en Word) | Negrita / cursiva |

### Uso rápido
```powershell
cd C:\Users\uiv06676\Documents\StrangerThings_PDF
pip install -r requirements.txt

# Sin argumentos -> diálogos de Windows para entrada y salida
python convert.py --titulo "Stranger Things" --autor "Tu Nombre"

# Con argumentos
python convert.py mi_aventura.docx salida.pdf `
    --titulo "Stranger Things" `
    --subtitulo "El Otro Lado" `
    --autor "Tu Nombre" `
    --portada "C:\ruta\a\tu\imagen.jpg"
```

### Constantes parametrizables (al inicio de `convert.py`)
- Colores: `COLOR_PRIMARIO`, `COLOR_AZUL_*`, `COLOR_AMA_*`.
- Tipografía: `FUENTE_TITULO`, `FUENTE_TEXTO`.
- Página: `TAMANO_PAGINA`, `MARGEN`.
- Portada: `IMAGEN_PORTADA_DEFAULT`.
- Fusión de citas: `MAX_VACIOS_FUSION_CITA = 2`.

### Funciones clave en `convert.py`
- `construir_estilos()` → estilos de ReportLab.
- `estilo_para_parrafo(p)` → mapea estilo de Word a clave (`H1`/`H2`/`H3`/`CitaCaja`/`Lista`/`Cuerpo`).
- `runs_a_html(parrafo)` → respeta runs de Word + fallback a markdown inline.
- `_markdown_inline_a_html(texto)` → `**bold**` / `*italic*`.
- `extraer_imagenes_de_parrafo(parrafo, doc_word)` → bytes de imágenes embebidas.
- `imagen_flowable(blob, ancho_max)` → `Image` escalada al ancho útil.
- `es_consejo_dm(texto_plano)` → detecta "Consejo para el DM" tolerante a `*`/comillas.
- `_split_html_balanceado(html, sep)` → split conservando balance de etiquetas.
- `DocConTOC` → `BaseDocTemplate` que notifica TOC para H1/H2.
- `construir_pdf(...)` → bucle principal por párrafos del docx.
- `_seleccionar_archivo_dialogo(...)` → diálogo Tk para abrir/guardar.
- `main()` → CLI con `argparse`, args opcionales.

### Git
- Repo inicializado, primer commit: `5720e82` ("chore: initial commit").
- Commit posterior: "Doble cita arreglado".

---

## Actualización posterior del proyecto

Este historial quedó desactualizado respecto al estado real del repositorio.
Los cambios más recientes ya implementados en `convert.py` y documentados en
`README.md` son los siguientes.

### Nuevas capacidades añadidas después de este resumen inicial

1. **Hipervínculos reales en el PDF**
  - Los enlaces insertados en Word se conservan como enlaces clickables.

2. **Índice y marcadores PDF más completos**
  - El documento genera índice y marcadores internos para navegación.

3. **Cajas especiales adicionales**
  - `Información adicional`
  - `Consejo para el DM`
  - `Cita`
  - `NPC`
  - `Enemigo`
  - `Aliado`

4. **Bloques manuales soportados actualmente**
  - `:::info`
  - `:::consejo`
  - `:::cita`
  - `:::npc`
  - `:::enemigo`
  - `:::aliado`

5. **Contenido permitido dentro de bloques manuales**
  - párrafos normales,
  - listas con viñetas,
  - sangrías,
  - imágenes,
  - enlaces,
  - tablas de Word,
  - espacios en blanco moderados entre párrafos.

6. **Consejos del DM por estilo y por prefijo**
  - El estilo de Word `Consejos` sigue funcionando.
  - También se detectan párrafos que empiezan por `CONSEJO PARA EL DM`.

7. **Información adicional por estilo y por prefijo**
  - Se reconoce el estilo `Información adicional`.
  - También se detectan prefijos como `INFORMACIÓN ADICIONAL:`.

8. **Imágenes dentro de recuadros**
  - Las imágenes insertadas dentro de bloques manuales permanecen dentro del
    mismo recuadro en el PDF.

9. **Tablas dentro de recuadros**
  - Las tablas de Word ahora pueden formar parte de un bloque manual y se
    renderizan dentro de la caja correspondiente.

### Armonización reciente del código

En una refactorización posterior se armonizó el proyecto para reducir la
mezcla de nombres en inglés y español.

Cambios destacados:
- `IMAGEN_PORTADA_DEFAULT` → `IMAGEN_PORTADA_PREDETERMINADA`
- `DocConTOC` → `DocumentoConIndice`
- `main()` → `principal()`
- `runs_a_html()` → `parrafo_a_html()`
- `imagen_flowable()` → `crear_flujo_imagen()`
- nombres internos de estilos de caja unificados a español:
  - `CajaCita`
  - `CajaInfoAdicional`
  - `CajaConsejoDm`
  - `CajaNpc`
  - `CajaEnemigo`
  - `CajaAliado`

También se simplificó parte del flujo interno de `construir_pdf()` para evitar
duplicación en la lógica de captura de bloques manuales.

### README reescrito

`README.md` se rehizo para que deje de parecer una acumulación de parches.
Ahora está reorganizado en:
- instalación,
- uso,
- preparación del Word,
- bloques especiales,
- capacidades de bloques manuales,
- imágenes,
- enlaces,
- índice,
- personalización.

### Estado actual recomendado del proyecto

#### Archivos principales
- `convert.py` — script principal actual.
- `README.md` — guía actualizada y armonizada.
- `requirements.txt` — dependencias.
- `CHAT.md` — historial resumido.

#### Punto de entrada actual
- La función principal actual es `principal()`.

#### Constante de portada actual
- `IMAGEN_PORTADA_PREDETERMINADA`

#### Clase principal de documento PDF
- `DocumentoConIndice`

### Commits recientes relevantes

- `5720e82` — commit inicial del proyecto.
- `f402e3d` — soporte para imágenes dentro de contenido en cajas.
- `187d72d` — `feat: add npc, enemy, and ally boxed blocks`
- `117a86e` — `refactor: harmonize Spanish naming and docs`
- `0617441` — `fix: improve boxed image layout and pagination`
- `200b140` — `fix: polish boxed media layout and heading grouping`
- `97dac71` — `feat: add cream page background`

### Última actualización verificada en este chat

Se validó y confirmó un ajuste reciente orientado a mejorar el comportamiento
de las cajas especiales cuando contienen imágenes grandes.

Cambios confirmados:
- `crear_flujo_imagen()` ahora acepta `alto_max` además de `ancho_max` para
  limitar correctamente imágenes altas dentro de recuadros.
- `_renderizar_caja()` calcula un alto máximo útil para imágenes dentro del
  área imprimible.
- El renderizado de cajas dejó de envolver todo en `KeepTogether` y ahora usa
  una tabla por filas con `splitByRow=1`, permitiendo una paginación más
  robusta cuando el contenido no cabe completo en una sola página.
- También se añadió el archivo `docx_to_pdf.code-workspace` al repositorio.

Validación realizada en esta sesión:
- compilación correcta de `convert.py`,
- dependencias presentes,
- prueba funcional con un `.docx` temporal que incluía una imagen grande dentro
  de un bloque `:::npc`, generando el PDF correctamente.

### Actualizaciones posteriores confirmadas

Después de esa validación se aplicaron dos mejoras adicionales ya confirmadas
en el repositorio actual.

#### 1. Pulido visual de cajas con imágenes y tablas

Commit: `200b140` — `fix: polish boxed media layout and heading grouping`

Cambios confirmados:
- las cajas decoradas agrupan mejor la cabecera visual con la primera imagen o
  tabla del bloque,
- las imágenes dentro de cajas se centran de forma más estable,
- se mejoró el espaciado entre cabecera y contenido multimedia,
- se mantuvo la paginación por filas en la caja principal, sin volver al uso
  global de `KeepTogether`.

Validación realizada:
- compilación correcta,
- prueba funcional con un `.docx` temporal que incluía un bloque `:::npc` con
  imagen y un bloque `:::enemigo` con tabla, generando el PDF correctamente.

#### 2. Fondo crema global para todas las páginas

Commit: `97dac71` — `feat: add cream page background`

Cambios confirmados:
- nueva constante configurable `COLOR_FONDO_PAGINA`,
- `DocumentoConIndice` dibuja un fondo crema en cada página mediante
  `onPage=self._dibujar_fondo_pagina`,
- `README.md` actualizado para documentar la nueva constante visual.

Color configurado actualmente:
- `#F7F1E3`

Validación realizada:
- compilación correcta,
- generación satisfactoria de un PDF temporal con texto y caja de cita sobre
  el nuevo fondo crema.

### Nota para futuros traspasos a otro agente

Si se reutiliza este archivo para retomar el contexto en otra sesión o en otro
entorno, conviene tomar como referencia el estado actual del repositorio y no
solo el historial inicial, porque varias funciones y nombres cambiaron durante
la armonización posterior.
