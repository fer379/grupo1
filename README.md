# Comandos para instalar librerias necesarias:
```
pip install pandas numpy peewee python-dateutil
```  
o  
```
python -m pip install pandas numpy peewee python-dateutil
```  

# To Do

- [ ] Terminar la normalizacion:
    - [ ] Las fecha_inicio y fecha_fin_inicial tienen valores "N/A" y con el formato "mar-23" "2024-04-31" en vez de con barras
    - [ ] Algunas valores de comunas/barrios incluyen varios, separados por comas o por "y".
    - [ ] Algunos porcentajes de avance de obra estan como 100, otros 100%, otros 42.6, otros 73,64, otros como Mayo 2024 - 89,84%.
    - [ ] Algunas imagenes tienen '-' en vez de nada
    - [ ] Algunos cuit_contratista incluyen varios cuits, deberia guardarse como un array
    - [ ] Algunos mano_obra tienen links(?
    - [ ] Algunos pliego_descarga tienen 'No aplica', deberia ser None
    - [ ] Algunos estudio_ambiental_descarga tienen 'No aplica', deberia ser None
    - [ ] Algunos licitacion_oferta_empresa tienen varias empresas separadas por un 'y' (indefinido como se deberia normalizar esto)
