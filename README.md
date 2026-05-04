# Word → PDF estilo Aventura

Conversor de `.docx` a PDF pensado para aventuras: portada, índice, títulos jerárquicos, cajas temáticas, enlaces, imágenes y tablas dentro de bloques especiales.

## Instalación

```powershell
pip install -r requirements.txt
```

## Uso

```powershell
python convert.py mi_aventura.docx mi_aventura.pdf `
    --titulo "Stranger Things" `
    --subtitulo "El Otro Lado" `
    --autor "Tu Nombre" `
    --portada "C:\ruta\a\tu\imagen.jpg"
```

Si omites `--portada`, el script usa la ruta configurada en `convert.py` en `IMAGEN_PORTADA_PREDETERMINADA`. Si no encuentra esa imagen, la ignora sin fallar.

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

También se respetan la negrita, la cursiva y el subrayado, incluso dentro de las cajas.

## Bloques y estilos especiales

### Consejo para el DM

Puedes generarlo de tres maneras:

1. **Con el estilo `Consejos`**
2. **Con un párrafo que empiece por `CONSEJO PARA EL DM`**
3. **Con un bloque manual**

```text
:::consejo
Consejo para el DM: Usa esta escena para subir la tensión.

- Puedes introducir una pista falsa.
- También puedes acelerar el ritmo si la mesa ya entendió la idea.
:::
```

Si el contenido empieza por `Consejo para el DM`, el encabezado se separa y no se duplica. También se conservan subtítulos como `Consejo para el DM (Motivación Adicional):`.

### Información adicional

También admite tres entradas:

1. **Estilo `Información adicional`**
2. **Prefijo automático**, por ejemplo `INFORMACIÓN ADICIONAL:`
3. **Bloque manual**

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

### NPC, enemigo y aliado

Estos tres cuadros especiales solo se activan con bloques manuales.

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

## Qué admite cada bloque manual

Los bloques `:::info`, `:::consejo`, `:::cita`, `:::npc`, `:::enemigo` y `:::aliado` comparten la misma lógica de renderizado. Dentro de ellos puedes mezclar:

- párrafos normales,
- listas con viñetas,
- sangrías,
- enlaces,
- imágenes,
- tablas de Word,
- espacios en blanco moderados entre fragmentos.

Esto permite mantener dentro del mismo recuadro contenido compuesto, sin partirlo artificialmente.

## Imágenes

Las imágenes insertadas en Word se extraen y se colocan en el PDF ajustadas al ancho útil de la página.

Si una imagen aparece dentro de un bloque manual, permanece dentro del mismo recuadro.

## Enlaces

Los hipervínculos reales de Word se conservan como enlaces clickables en el PDF y mantienen su estilo visual azul y subrayado.

## Índice

El índice se genera automáticamente a partir de `Título 1` y `Título 2`.

El script usa `multiBuild` para recalcular la paginación y dejar los números correctos en la segunda pasada.

## Personalización

Si quieres ajustar el estilo visual, revisa estas constantes al inicio de `convert.py`:

- `COLOR_PRIMARIO`
- `COLOR_AZUL_*`
- `COLOR_AMA_*`
- `COLOR_INFO_*`
- `COLOR_NPC_*`
- `COLOR_ENEMIGO_*`
- `COLOR_ALIADO_*`
- `FUENTE_TITULO`
- `FUENTE_TEXTO`
- `MARGEN`
- `TAMANO_PAGINA`
- `IMAGEN_PORTADA_PREDETERMINADA`
