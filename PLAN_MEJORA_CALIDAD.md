# Plan de Mejora de Calidad

## Objetivo

Convertir el proyecto en una base más mantenible, testeable y predecible sin romper el comportamiento actual de conversión Word/TXT a PDF.

Este plan está escrito para que otro agente de IA pueda ejecutarlo de forma incremental.

## Estado actual resumido

- El proyecto compila correctamente.
- No hay errores de editor reportados.
- No existe suite de tests automática.
- Los principales focos de complejidad están en:
  - la configuración global mutable,
  - la máquina de estados del constructor de PDF,
  - la clase UI principal demasiado grande.

## Restricciones de ejecución

- No cambiar el comportamiento funcional sin antes capturarlo con tests de caracterización.
- Hacer cambios por fases pequeñas.
- Validar cada fase con checks ejecutables.
- No mezclar cambio de arquitectura con cambio masivo de naming en la misma fase.
- Mantener español como idioma interno por defecto salvo que el usuario pida migración a inglés.

## Orden recomendado

1. Crear baseline de tests.
2. Introducir modelos de configuración tipados.
3. Reducir acoplamiento entre CLI y configuración.
4. Extraer la lógica de bloques del constructor de PDF.
5. Terminar la descomposición de la UI.
6. Normalizar naming y cerrar deuda técnica.
7. Añadir quality gates de lint y test.

## Fase 0 - Baseline y red de seguridad

### Objetivo

Capturar el comportamiento actual antes de tocar arquitectura.

### Archivos a tocar

- requirements.txt
- README.md
- Nuevo directorio tests/
- docx_to_pdf_app/core/configuracion_pdf.py
- docx_to_pdf_app/core/procesamiento_word.py
- docx_to_pdf_app/pdf/constructor_pdf.py
- docx_to_pdf_app/ui/interfaz_usuario.py

### Tareas

1. Añadir pytest como dependencia de desarrollo.
2. Crear tests de caracterización para funciones puras o casi puras.
3. Evitar empezar por tests de Tk completos; priorizar helpers sin UI real.
4. Añadir fixtures mínimas para configuraciones de documento y colores.

### Tests mínimos a crear

1. Configuración visual por defecto:
   - verificar claves devueltas por obtener_configuracion_visual_predeterminada.
   - verificar normalización de hex válidos e inválidos.

2. Configuración de documento:
   - verificar normalización de margen con y sin adornos.
   - verificar normalización de tamaño personalizado.

3. Parsing Word/TXT:
   - estilo_para_parrafo.
   - es_consejo_dm.
   - es_info_adicional.
   - es_inicio_bloque_*.
   - _dividir_html_en_salto.
   - _extraer_bloque_prefijo_embebido.

4. UI helpers sin Tk real:
   - _normalizar_ruta_salida.
   - _es_ruta_entrada_valida.
   - _es_ruta_salida_valida.
   - _estado_tamano_personalizado.

5. Constructor PDF, comportamiento mínimo:
   - tests sobre EstadoConstruccionPdf para aperturas y cierres de bloques.
   - no intentar al principio tests completos de layout PDF página a página.

### Criterio de aceptación

- Existe suite pytest ejecutable.
- Los helpers críticos tienen cobertura básica.
- El comportamiento actual queda protegido antes de refactorizar.

### Validación

1. Ejecutar compilación Python.
2. Ejecutar pytest.

## Fase 1 - Configuración explícita y tipada

### Objetivo

Eliminar la dependencia de globals mutables como mecanismo principal de configuración.

### Archivos a tocar

- docx_to_pdf_app/core/configuracion_pdf.py
- docx_to_pdf_app/cli/convert.py
- docx_to_pdf_app/pdf/constructor_pdf.py
- docx_to_pdf_app/pdf/renderizado_cajas.py
- docx_to_pdf_app/ui/interfaz_usuario.py

### Problema actual

- configuracion_pdf.py mezcla:
  - constantes por defecto,
  - estado mutable global,
  - normalización,
  - construcción de estilos,
  - registro de fuentes.
- convert.py sincroniza globals entre módulos en lugar de pasar configuración explícita.

### Tareas

1. Crear dataclasses o estructuras tipadas:
   - ConfiguracionVisual
   - ConfiguracionDocumento

2. Separar claramente:
   - valores por defecto,
   - normalización,
   - conversión desde diccionarios de UI/CLI,
   - construcción de estilos ReportLab.

3. Hacer que construir_estilos reciba configuración explícita.
4. Hacer que constructor_pdf reciba configuración explícita en lugar de leer cfg global en la mayor parte de los casos.
5. Reducir convert.py a capa de orquestación.

### Subtareas sugeridas

1. Mantener compatibilidad temporal con wrappers para no romper todo en un solo commit.
2. Introducir funciones tipo:
   - construir_configuracion_visual_desde_dict
   - construir_configuracion_documento_desde_dict
3. Migrar primero el camino CLI directo.
4. Migrar luego el camino UI.

### Criterio de aceptación

- convert.py deja de sincronizar globals manualmente.
- constructor_pdf puede ejecutarse con objetos de configuración explícitos.
- los tests de fase 0 siguen pasando.

### Validación

1. pytest
2. py_compile

## Fase 2 - Reorganizar el parser y la máquina de estados de bloques

### Objetivo

Reducir la complejidad de EstadoConstruccionPdf y hacer extensible la lógica de bloques especiales.

### Archivos a tocar

- docx_to_pdf_app/pdf/constructor_pdf.py
- docx_to_pdf_app/core/procesamiento_word.py
- Nuevo archivo sugerido: docx_to_pdf_app/core/bloques_especiales.py
- Nuevo archivo sugerido: docx_to_pdf_app/core/tipos_bloque.py

### Problema actual

- constructor_pdf.py contiene demasiada lógica de parsing y control de estado.
- cada tipo de bloque añade más buffers, flags y métodos repetidos.

### Tareas

1. Introducir un modelo común para bloques especiales.
2. Crear una tabla o registro de tipos de bloque con:
   - identificador,
   - detector de apertura,
   - detector de cierre,
   - estilo destino,
   - decorador HTML,
   - política de fusión.

3. Reemplazar flags duplicados por una estructura de estado genérica.
4. Extraer la lógica repetida de vaciado y cierre.
5. Mantener compatibilidad de comportamiento para:
   - consejo,
   - info,
   - cita,
   - npc,
   - enemigo,
   - aliado,
   - tesoro/premio,
   - puzzle/acertijo/rompecabezas,
   - objeto.

### Implementación sugerida

1. Crear un contenedor de estado por bloque activo.
2. Crear funciones genéricas:
   - abrir_bloque
   - cerrar_bloque
   - agregar_item_a_bloque_activo
   - vaciar_bloques_pendientes
3. Dejar en constructor_pdf solo la orquestación de alto nivel del documento.

### Criterio de aceptación

- el número de métodos específicos por bloque en EstadoConstruccionPdf baja de forma clara;
- añadir un nuevo tipo de bloque requiere cambiar un registro central, no replicar ramas enteras;
- los tests de parsing y de estado siguen pasando.

### Validación

1. pytest
2. generación manual de 1 o 2 PDFs de muestra si el usuario los aporta;
3. py_compile

## Fase 3 - Terminar la separación de responsabilidades en UI

### Objetivo

Convertir la UI en una composición de módulos coordinados por una clase pequeña, no en una clase contenedor de todo.

### Archivos a tocar

- docx_to_pdf_app/ui/interfaz_usuario.py
- docx_to_pdf_app/ui/form_blocks.py
- docx_to_pdf_app/ui/preview_rendering.py
- docx_to_pdf_app/ui/tab_building.py
- docx_to_pdf_app/ui/dialog_state.py
- Nuevos archivos sugeridos:
  - docx_to_pdf_app/ui/validation_logic.py
  - docx_to_pdf_app/ui/navigation_logic.py
  - docx_to_pdf_app/ui/submission_logic.py

### Problema actual

- interfaz_usuario.py sigue siendo demasiado grande.
- contiene lógica de layout, validación, navegación, lectura de configuración, previews y aceptación.
- además mantiene muchos wrappers finos hacia otros módulos.

### Tareas

1. Mover helpers de validación a un módulo dedicado.
2. Mover navegación entre páginas y estado de botones a un módulo dedicado.
3. Mover la construcción del payload final de configuración a un módulo dedicado.
4. Eliminar wrappers triviales cuando no aporten encapsulación real.
5. Mantener dialog_state.py como agrupador de estado, pero tiparlo mejor.

### Tipado sugerido

1. Sustituir object por tipos más informativos cuando sea práctico.
2. Si Tk complica el tipado exacto, usar Protocol o alias de tipos parciales.
3. Tipar al menos:
   - payload de aceptación,
   - configuraciones leídas,
   - valores de validación.

### Criterio de aceptación

- interfaz_usuario.py baja claramente de tamaño y de número de métodos;
- la clase principal queda centrada en ciclo de vida y composición;
- las validaciones pueden probarse sin levantar la UI completa.

### Validación

1. pytest
2. py_compile de módulos UI
3. smoke test manual del diálogo

## Fase 4 - Normalización de naming

### Objetivo

Eliminar inconsistencias de naming sin mezclarlo con refactors estructurales profundos.

### Archivos a tocar

- docx_to_pdf_app/core/configuracion_pdf.py
- docx_to_pdf_app/ui/interfaz_usuario.py
- docx_to_pdf_app/ui/form_blocks.py
- tests/
- README.md

### Problema actual

- coexisten claves tipo COLOR_CONSEJO_TEXTO y color_info_texto.
- eso hace más difícil automatizar, tipar y refactorizar.

### Tareas

1. Elegir una convención única para claves externas e internas.
2. Recomendación: snake_case en minúsculas para datos de configuración.
3. Mantener MAYÚSCULAS solo para verdaderas constantes de módulo si siguen existiendo.
4. Crear capa de compatibilidad temporal si la UI aún emite claves antiguas.
5. Eliminar compatibilidad heredada solo cuando tests y llamadas internas estén migrados.

### Criterio de aceptación

- no quedan diccionarios de configuración con mezcla arbitraria de mayúsculas y minúsculas;
- la UI, el core y los tests usan la misma convención.

### Validación

1. pytest
2. búsqueda de claves antiguas en el workspace

## Fase 5 - Calidad continua y documentación técnica

### Objetivo

Dejar el proyecto con una base de validación repetible.

### Archivos a tocar

- requirements.txt o archivo de dev-deps si se introduce
- README.md
- Nuevo archivo sugerido: CONTRIBUTING.md
- Nuevo archivo sugerido: pytest.ini si hace falta
- Nuevo archivo sugerido: ruff.toml o configuración equivalente

### Tareas

1. Añadir lint con ruff.
2. Documentar comandos de validación.
3. Documentar la arquitectura resultante.
4. Añadir guía breve para incorporar nuevos tipos de caja/bloque.

### Comandos objetivo

1. Compilación Python.
2. Suite pytest.
3. Ruff check.

### Criterio de aceptación

- existe una secuencia de validación estándar documentada;
- un nuevo colaborador o IA puede ejecutar checks sin reconstruir el contexto desde cero.

## Backlog priorizado

### Prioridad alta

1. Crear suite de tests de baseline.
2. Sustituir configuración global mutable por configuración explícita.
3. Reducir complejidad de EstadoConstruccionPdf.

### Prioridad media

1. Completar la separación de la UI.
2. Normalizar naming de configuración.

### Prioridad baja

1. Mejorar tipado de widgets Tk.
2. Añadir documentación para colaboradores.
3. Añadir lint y polish adicional.

## Dependencias entre tareas

1. No empezar renombrados masivos antes de tener tests.
2. No refactorizar constructor_pdf sin fijar primero la configuración explícita o, como mínimo, su interfaz.
3. No hacer limpieza masiva de UI antes de separar validación y payload de aceptación.

## Estrategia de commits recomendada

1. test: añadir baseline de caracterización
2. refactor: introducir modelos de configuración
3. refactor: simplificar convert.py y flujo de configuración
4. refactor: extraer estado de bloques especiales
5. refactor: separar validación y payload de UI
6. chore: normalizar naming de configuración
7. chore: añadir lint y documentación técnica

## Prompt sugerido para otro agente de IA

Trabaja por fases pequeñas sobre PLAN_MEJORA_CALIDAD.md.
Empieza por Fase 0.
No cambies comportamiento sin antes crear tests de caracterización.
Después de cada cambio, ejecuta py_compile y pytest.
Cuando completes una fase, resume:
1. qué cambió,
2. qué riesgos quedan,
3. qué fase sigue,
4. qué validación ejecutaste.
