import pandas as pd
import numpy as np  
from abc import ABC, abstractmethod
from modelo_orm import db, AreaResponsable, TipoObra, Barrio, Etapa, Empresa, TipoContratacion, FuenteFinanciamiento, Obra
from peewee import IntegrityError
from dateutil import parser

class GestionarObra(ABC):
    @classmethod
    def limpiar_datos(cls):
        cols_text = ['area_responsable', 'tipo_obra', 'barrio', 'empresa', 'fuente_financiamiento', 'etapa']
        for c in cols_text:
            if c in df.columns:
                df[c] = df[c].astype(str).str.strip().replace({'nan': None, 'None': None})
    