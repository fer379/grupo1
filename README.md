# Comandos para instalar librerias necesarias:
```
pip install pandas numpy peewee python-dateutil
```  
o  
```
python -m pip install pandas numpy peewee python-dateutil
```  

# Puntos clave  
 Se anotaron puntos clave del codigo con comentarios que comienzan en ``` NOTE ```, para luego incluirlos en la presentacion.

# To Do

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
