# Word → PDF estilo Aventura

Conversor de `.docx` a PDF pensado para aventuras y material de rol. Genera un documento con portada opcional, índice, marcadores de navegación, estilos jerárquicos, cajas temáticas, enlaces, imágenes y tablas dentro de bloques especiales.

## Estructura del proyecto

La lógica principal ya no vive en un único archivo. El proyecto quedó dividido así:

- `convert.py`: fachada principal y CLI; mantiene compatibilidad como punto de entrada.
- `configuracion_pdf.py`: constantes visuales, configuración mutable y construcción de estilos.
- `procesamiento_word.py`: parsing de Word, HTML intermedio, detectores de bloques y helpers de imágenes/tablas.
- `renderizado_cajas.py`: render de cajas, imágenes, tablas y flowables personalizados para paginación.
- `constructor_pdf.py`: ensamblado del PDF, TOC, portada y estado del recorrido del documento.
- `interfaz_usuario.py`: diálogos de archivo, avisos y menú interactivo.

La modularización también eliminó el uso de funciones anidadas en el flujo principal para dejar responsabilidades más claras y facilitar cambios futuros.

## Instalación

```powershell
pip install -r requirements.txt
```

## Uso básico

```powershell
python convert.py mi_aventura.docx mi_aventura.pdf `
    --titulo "Stranger Things" `
    --subtitulo "El Otro Lado" `
    --autor "Tu Nombre" `
    --portada "C:\ruta\a\tu\imagen.jpg"
```

Si ejecutas `python convert.py` sin indicar entrada y salida, se abrirá directamente el menú interactivo unificado. Primero verás una pantalla compacta para elegir el `.docx` de entrada y la ruta `.pdf` de salida. Cuando ambas rutas sean válidas, podrás pulsar `Continuar` para pasar a la personalización.

## Menú interactivo

El menú interactivo ahora funciona como un asistente de dos pasos dentro de una sola ventana:

- una primera pantalla para seleccionar el archivo Word de entrada y la ruta PDF de salida,
- una segunda pantalla para metadatos, portada, tamaño de página, fuentes, márgenes y colores.

Cuando las rutas son válidas, el botón `Continuar` habilita la segunda pantalla. Desde ahí puedes usar `Regresar` para cambiar entrada o salida sin perder la configuración que ya hayas escrito.

Desde el menú inicial puedes:

- ajustar colores de títulos, texto general y fondo de página,
- personalizar texto, borde y fondo de cada caja especial,
- modificar tamaño de página, márgenes y fuentes,
- activar adornos de margen con preview, presets o un PNG transparente personalizado,
- indicar título, subtítulo y autor,
- activar una portada y elegir su imagen,
- cambiar también los colores de `Tesoro/Premio` y `Objeto`.

Además de las fuentes estándar de `ReportLab`, el menú detecta automáticamente cualquier archivo `.ttf` u `.otf` que coloques dentro de `fonts/` y lo expone como opción seleccionable. El nombre visible se deriva del nombre del archivo y el conversor intenta enlazar variantes comunes como `Regular`, `Bold`, `Italic`, `Oblique` y `BoldItalic` cuando las encuentra.

Si la fuente personalizada no está disponible o no puede registrarse, el conversor mantiene el fallback actual a `Helvetica`/`Helvetica-Bold`.

## Adornos de margen

La pestaña `General` permite activar adornos decorativos para los márgenes del PDF.

- Puedes desactivarlos por completo con una casilla.
- Puedes elegir entre presets `Clásico`, `Floral` y `Geométrico`.
- También puedes usar `Personalizado (PNG)` y seleccionar un archivo `.png` con transparencia.
- El menú muestra un preview pequeño del estilo actual antes de generar el PDF.

Para un adorno personalizado, lo ideal es preparar un PNG vertical del tamaño de la página o con una proporción parecida al papel final, dejando transparente el centro para que el contenido siga siendo legible.

Si dejas título, subtítulo o autor en blanco, esos datos no se agregan al PDF.

Puedes forzar u omitir el menú desde la línea de comandos:

```powershell
python convert.py --menu-interactivo
python convert.py mi_aventura.docx salida.pdf --sin-menu
```

Si usas `--sin-menu` y omites alguna ruta, el conversor conserva el flujo alternativo de diálogos simples solo para seleccionar los archivos faltantes.

Si omites `--portada`, el script intenta usar la ruta configurada en `IMAGEN_PORTADA_PREDETERMINADA`. Si no encuentra esa imagen, la ignora sin fallar.

## Cómo preparar el Word

El conversor se apoya principalmente en los estilos de Word.

| En Word | Resultado en PDF |
|---|---|
| **Título 1** | Capítulo en rojo, incluido en el índice |
| **Título 2** | Sección en rojo, incluida en el índice |
| **Título 3** | Subsección |
| **Normal** | Texto justificado |
| **Cita** o **Quote** | Caja amarilla |
| **Información adicional** | Caja verde-azulada |
| **Consejos** | Caja azul de consejo para el DM |
| Lista con viñetas | Lista con viñetas |
| Hipervínculo real | Enlace clickable en el PDF |

También se respetan negrita, cursiva y subrayado, incluso dentro de las cajas.

## Cajas y bloques especiales

### Consejo para el DM

Puedes generarlo de tres maneras:

1. Con el estilo `Consejos`
2. Con un párrafo que empiece por `CONSEJO PARA EL DM`
3. Con un bloque manual

```text
:::consejo
Consejo para el DM: Usa esta escena para subir la tensión.

- Puedes introducir una pista falsa.
- También puedes acelerar el ritmo si la mesa ya entendió la idea.
:::
```

Si el contenido ya empieza por `Consejo para el DM`, el encabezado se separa y no se duplica. También se conservan subtítulos como `Consejo para el DM (Motivación Adicional):`.

### Información adicional

También admite tres entradas:

1. Estilo `Información adicional`
2. Prefijo automático, por ejemplo `INFORMACIÓN ADICIONAL:`
3. Bloque manual

```text
:::info
Este detalle añade contexto opcional para enriquecer la escena.

- Puedes usarlo como pista secundaria.
- También puedes omitirlo si quieres ir al grano.
:::
```

### Cita

Se puede crear con el estilo `Cita` o con bloque manual:

```text
:::cita
Este texto irá dentro de una sola caja amarilla.

- Puedes mezclar varios párrafos.
- También listas y enlaces.
:::
```

### NPC, enemigo, aliado, tesoro, premio y objeto

Estas cajas se activan mediante bloques manuales.

#### NPC

```text
:::npc
Nombre: Jim Hopper

- Sheriff de Hawkins
- Protector y desconfiado
:::
```

#### Enemigo

```text
:::enemigo
Demogorgon

- Acecha desde el Otro Lado.
- Ataca cuando detecta sangre.
:::
```

#### Aliado

```text
:::aliado
Once

- Puede ayudarte en escenas críticas.
- Funciona muy bien como apoyo narrativo.
:::
```

#### Tesoro

```text
:::tesoro
Contenido del tesoro
:::
```

#### Premio

```text
:::premio
Contenido del premio
:::
```

#### Objeto

```text
:::objeto
Contenido del objeto
:::
```

`Tesoro` y `Premio` comparten estilo y restricciones; solo cambia el encabezado visible. `Objeto` usa su propia caja y admite el mismo contenido compuesto que los demás bloques manuales.

## Qué admite un bloque manual

Los bloques manuales comparten la misma lógica base de renderizado. Dentro de ellos puedes mezclar:

- párrafos normales,
- listas con viñetas,
- sangrías,
- enlaces,
- imágenes,
- tablas de Word,
- espacios en blanco moderados entre fragmentos.

El motor de paginación intenta partir solo el texto cuando hace falta y mantener juntas imágenes, tablas y cabeceras visuales siempre que sea posible.

## Imágenes

Las imágenes insertadas en Word se extraen y se colocan en el PDF ajustadas al ancho útil de la página.

- Si una imagen aparece sola, se respeta su tamaño visible original del `.docx` siempre que quepa.
- Si una imagen aparece dentro de un bloque manual, permanece dentro del mismo recuadro.
- Si varias imágenes pueden agruparse en una fila, el conversor intenta mantenerlas equilibradas visualmente.

## Enlaces

Los hipervínculos reales de Word se conservan como enlaces clickables en el PDF y mantienen su estilo visual azul y subrayado.

## Índice y navegación

El índice se genera automáticamente a partir de `Título 1` y `Título 2`.

El script usa `multiBuild` para recalcular la paginación y dejar los números correctos en una segunda pasada.

Además:

- el texto de cada entrada del índice es clickable,
- el número de página del índice también es clickable,
- el propio `Índice` aparece como marcador visible en el panel lateral del PDF,
- los `Título 1`, `Título 2` y `Título 3` generan marcadores de navegación.

Esto permite navegar tanto desde la tabla de contenidos como desde el panel de marcadores del visor PDF.

## Personalización

Si quieres ajustar el estilo visual desde código, revisa principalmente `configuracion_pdf.py`:

- `COLOR_PRIMARIO`
- `COLOR_FONDO_PAGINA`
- `COLOR_AZUL_*`
- `COLOR_AMA_*`
- `COLOR_INFO_*`
- `COLOR_NPC_*`
- `COLOR_ENEMIGO_*`
- `COLOR_ALIADO_*`
- `COLOR_TESORO_*`
- `COLOR_OBJETO_*`
- `FUENTE_TITULO`
- `FUENTE_TEXTO`
- `MARGEN`
- `TAMANO_PAGINA`
- `IMAGEN_PORTADA_PREDETERMINADA`

`convert.py` sigue reexportando la configuración principal por compatibilidad, pero la fuente de verdad ahora está centralizada en `configuracion_pdf.py`.

## Observaciones

El código del conversor sigue una convención de nombres en español para helpers y funciones auxiliares propias del proyecto, con el objetivo de mantener una base más coherente y fácil de leer.

La refactorización reciente preserva el comportamiento existente de cajas, imágenes, tablas, índice y menú interactivo, pero deja el mantenimiento mucho más atomizado.
