# Comandos para instalar librerias necesarias:
```
pip install pandas numpy peewee python-dateutil ftfy
```  
o  
```
python -m pip install pandas numpy peewee python-dateutil ftfy
```  
para correr la aplicacion ejecutar el codigo en el archivo main.py, o mediante el comando en consola sobre /src/:
```
python main.py
```  

# Puntos clave  
 Se anotaron puntos clave del codigo con comentarios que comienzan en ``` NOTE ```, para luego incluirlos en la presentacion.

# To-Do List – Trabajo Práctico Final Integrador (DSOO)

## 1. Preparación del proyecto
- [X] Crear carpeta del proyecto con apellidos de los integrantes separados por guiones.
- [X] Descargar el archivo `observatorio-de-obras-urbanas.csv` desde los enlaces proporcionados.
- [X] Ubicar el CSV en la carpeta del proyecto.
- [X] Analizar la estructura de datos del CSV.

## 2. Crear módulo `modelo_orm.py`
- [X] Crear archivo `modelo_orm.py`.
- [X] Definir clase `BaseModel` heredando de `peewee.Model`.
- [X] Definir todas las clases necesarias del modelo ORM (tablas y relaciones).
- [X] Configurar conexión a la base de datos SQLite `obras_urbanas.db`.

## 3. Crear módulo `gestionar_obras.py`
- [X] Crear archivo `gestionar_obras.py`.
- [X] Definir clase abstracta `GestionarObra` con métodos de clase.

### Métodos obligatorios
- [X] `extraer_datos()` → cargar dataset con pandas en un DataFrame.
- [X] `conectar_db()` → conectar con la base SQLite `obras_urbanas.db`.
- [X] `mapear_orm()` → crear tablas con `create_tables(list)`.
- [X] `limpiar_datos()` → limpieza de nulos y datos incorrectos del DataFrame.
- [ ] `cargar_datos()` → persistir registros limpios en la BD usando `Model.create()`.
- [ ] `nueva_obra()` → crear nuevas instancias de Obra con datos ingresados por teclado.
    - [ ] Validar claves foráneas mediante búsqueda ORM.
    - [ ] Informar y pedir reingreso si el valor no existe.
    - [ ] Persistir con `save()`.
    - [ ] Retornar la nueva instancia.
- [ ] `obtener_indicadores()` → consultas ORM para obtener estadísticas.

- [X] Terminar la normalizacion:
    - [X] Verificar columnas booleanas.
    - [X] Verificar columnas lat y lon.
    - [X] Ahora se chequea que las obras no tengan el mismo nombre (guarda la mas reciente)
    - [X] Antes de la normalizacion, que empiece de abajo hacia arriba. (de mas nuevo a mas viejo, por las obras repetidas)
    - [X] Las fecha_inicio y fecha_fin_inicial tienen valores "N/A" y con el formato "mar-23" "2024-04-31" en vez de con barras
    - [X] Algunos valores de comunas/barrios incluyen varios, separados por comas o por "y". (se guardo todo como string)
    - [X] Algunos porcentajes de avance de obra estan como 100, otros 100%, otros 42.6, otros 73,64, otros como Mayo 2024 - 89,84%.
    - [X] Algunas imagenes tienen '-' en vez de nada
    - [X] Algunos cuit_contratista incluyen varios cuits, deberia guardarse como un array
    - [X] Algunos mano_obra tienen links(?
    - [X] Algunos pliego_descarga tienen 'No aplica', deberia ser None
    - [X] Algunos estudio_ambiental_descarga tienen 'No aplica', deberia ser None
    - [ ] Algunos licitacion_oferta_empresa tienen varias empresas separadas por un 'y' (indefinido como se deberia normalizar esto)

## 4. Clase `Obra` (modelo ORM)
Incluir métodos de instancia:
- [ ] `nuevo_proyecto()`
- [ ] `iniciar_contratacion()`
- [ ] `adjudicar_obra()`
- [ ] `iniciar_obra()`
- [ ] `actualizar_porcentaje_avance()`
- [ ] `incrementar_plazo()` (opcional)
- [ ] `incrementar_mano_obra()` (opcional)
- [ ] `finalizar_obra()`
- [ ] `rescindir_obra()`

## 5. Creación y manejo de obras
- [ ] Crear al menos dos instancias de Obra usando `GestionarObra.nueva_obra()`.
- [ ] Pasar cada obra por todas las etapas definidas, excepto las opcionales.
- [ ] Luego de cada etapa, persistir cambios con `save()`.

## 6. Reglas específicas por etapa
- [ ] `nuevo_proyecto()`:
    - [ ] Asignar etapa inicial “Proyecto”.
    - [ ] Crear etapa si no existe en BD.
    - [ ] Usar valores existentes de tipo_obra, area_responsable y barrio.
- [ ] `iniciar_contratacion()`:
    - [ ] Asignar TipoContratacion existente en BD.
    - [ ] Ingresar nro_contratacion.
- [ ] `adjudicar_obra()`:
    - [ ] Asignar Empresa existente en BD.
    - [ ] Ingresar nro_expediente.
- [ ] `iniciar_obra()`:
    - [ ] Asignar: destacada, fecha_inicio, fecha_fin_inicial, fuente_financiamiento (existente), mano_obra.
- [ ] `actualizar_porcentaje_avance()` → actualizar porcentaje.
- [ ] `incrementar_plazo()` → actualizar plazo_meses (opcional).
- [ ] `incrementar_mano_obra()` → actualizar mano_obra (opcional).
- [ ] `finalizar_obra()`:
    - [ ] etapa = "Finalizada"
    - [ ] porcentaje_avance = 100
- [ ] `rescindir_obra()`:
    - [ ] etapa = "Rescindida"

## 7. Obtener indicadores antes de finalizar
Ejecutar `GestionarObra.obtener_indicadores()` para mostrar:
- [ ] Listado de áreas responsables.
- [ ] Listado de tipos de obra.
- [ ] Cantidad de obras por etapa.
- [ ] Cantidad de obras y monto total por tipo de obra.
- [ ] Listado de barrios de comunas 1, 2 y 3.
- [ ] Cantidad de obras finalizadas en ≤ 24 meses.
- [ ] Monto total de inversión.

## 8. Aclaraciones
- [ ] Todos los métodos de `GestionarObra` deben ser métodos de clase.
- [ ] Atributos de clase cuando corresponda.
- [ ] Incluir manejo de excepciones donde sea pertinente.

