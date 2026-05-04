# Word → PDF estilo Aventura

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

Si no pasas `--portada`, usa la ruta de ejemplo definida en `convert.py`
(`IMAGEN_PORTADA_DEFAULT`). Si la imagen no existe, se omite sin error.

## Cómo escribir el Word

Usa los **estilos de Word** para que el script reconozca cada parte:

| En Word | Resultado en PDF |
|---|---|
| **Título 1** | Capítulo (rojo, entra en el índice) |
| **Título 2** | Sección (rojo, entra en el índice) |
| **Título 3** | Subsección |
| **Normal** | Texto justificado |
| **Cita** (Quote) | 🟨 Caja amarilla con texto negro |
| Párrafo que empieza con `CONSEJO PARA EL DM` | 🟦 Caja azul con texto azul |
| Lista con viñetas | Lista con viñetas |

Dentro de cualquier párrafo puedes usar **negrita**, *cursiva* o subrayado y se
respetan en el PDF, también dentro de las cajas.

### Consejo para el DM
Tienes **dos formas** de marcar un Consejo del DM:

**1) Bloque delimitado por `#` (recomendado para varios párrafos / listas):**
Pon una `#` al principio del primer párrafo y otra `#` al final del último.
Todo lo que esté entre las dos almohadillas (texto, listas, negritas…) entrará
en la misma caja azul.

```
#Consejo para el DM (Interacción Social): Wesley es escurridizo. Pide a los
jugadores una Prueba de Sabiduría (Perspicacia) CD 14...

- Si venden la estatua: ...
- Si rompen la estatua: ...#
```

**2) Párrafo único que empieza por `CONSEJO PARA EL DM`:**
Escribe un párrafo Normal que empiece exactamente así:

> **CONSEJO PARA EL DM (REGLAS 5.5):** Entrega a tus jugadores el "Cartel de Persona Desaparecida"...

El script lo detecta automáticamente y lo encierra en la caja azul.

### Citas
Aplica el estilo **Cita** al párrafo en Word → saldrá en caja amarilla.

### Imágenes
Pega las imágenes en el Word donde quieras. El script las extrae y las coloca
en el PDF en el mismo punto, escaladas al ancho útil de la página.

## Tabla de contenidos
Se genera automáticamente desde los Título 1 y Título 2.
El script hace doble pasada (`multiBuild`) para que los números de página sean correctos.

## Personalización
Edita las constantes al inicio de `convert.py`:
- `COLOR_PRIMARIO`, `COLOR_AZUL_*`, `COLOR_AMA_*`
- `FUENTE_TITULO`, `FUENTE_TEXTO`
- `MARGEN`, `TAMANO_PAGINA`
- `IMAGEN_PORTADA_DEFAULT`
