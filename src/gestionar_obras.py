from pathlib import Path
import pandas as pd
import numpy as np
from abc import ABC, abstractmethod


class GestionarObra(ABC):

    def __init__(self):
        self.df = None

    @abstractmethod
    def extraer_datos(self):
        pass

    @abstractmethod
    def limpiar_datos(self):
        pass


class Gestion(GestionarObra):

    def __init__(self):
        super().__init__()

    def extraer_datos(self):
        """Carga el CSV desde la carpeta data."""
        raiz = Path(__file__).resolve().parent.parent
        archivo = raiz / "data" / "observatorio-de-obras-urbanas.csv"

        self.df = pd.read_csv(
            archivo,
            encoding="latin1",
            sep=";",
            low_memory=False
        )

        return self.df
    
    """        super().__init__()   # inicializa self.df = None

    def extraer_datos(self):
        
        raiz = Path (__file__).resolve().parent.parent
        archivo = raiz / "data" / "observatorio-de-obras-urbanas.csv"
        datos = pd.read_csv (archivo, encoding="latin1", sep = ";")
        self.df = pd.DataFrame (datos         
        )
        print (self.df)
        return self.df
"""

    def limpiar_datos(self):
        """Normaliza texto, fechas, números y NaN."""
        if self.df is None:
            raise RuntimeError("Primero ejecutá extraer_datos()")

        df = self.df.copy()

        # ---------------------------
        # 1) NORMALIZACIÓN DE TEXTO
        # ---------------------------

        columnas_texto = [
            'area_responsable', 'tipo_obra', 'barrio', 'empresa',
            'fuente_financiamiento', 'etapa', 'descripcion', 'comuna'
        ]

        for c in columnas_texto:
            if c in df.columns:
                df[c] = (
                    df[c].astype(str)
                    .str.strip()
                    .replace({
                        'nan': None, 'None': None, 'NaN': None,
                        'NO INFORMADO': None, 'SIN DATOS': None
                    })
                )

        # ---------------------------
        # 2) REEMPLAZAR NaN REALES POR None
        # ---------------------------

        df = df.where(pd.notnull(df), None)

        # ---------------------------
        # 3) CONVERSIÓN DE FECHAS
        # ---------------------------

        columnas_fecha = [
            'fecha_inicio', 'fecha_fin', 'plazo_actualizado',
            'fecha_ultima_muestra'
        ]

        for c in columnas_fecha:
            if c in df.columns:
                df[c] = pd.to_datetime(df[c], errors="coerce")
        
        # ---------------------------
        # 4) CONVERSIÓN DE NÚMEROS
        # ---------------------------

        columnas_numericas = [
            'monto_contrato', 'avance_financiero', 'avance_fisico'
        ]

        for c in columnas_numericas:
            if c in df.columns:
                df[c] = (
                    df[c].astype(str)
                    .str.replace(",", ".", regex=False)
                )
                df[c] = pd.to_numeric(df[c], errors="coerce")

        # ---------------------------
        # 5) CONVERSIÓN SI/NO A BOOL
        # ---------------------------

        columnas_booleanas = [
            'tiene_impacto_ambiental', 'posee_proyecto'
        ]

        for c in columnas_booleanas:
            if c in df.columns:
                df[c] = df[c].astype(str).str.upper().map({
                    'SI': True,
                    'SÍ': True,
                    'NO': False
                })

        # ---------------------------
        # GUARDAR RESULTADO
        # ---------------------------

        self.df = df
        return df


    def imprimir(self):
        print(self.df.iloc[28:35]["estudio_ambiental_descarga"])


gestion = Gestion()

"""gestion.extraer_datos()
gestion.limpiar_datos()"""
gestion.extraer_datos()
gestion.limpiar_datos()
print(gestion.df.iloc[28:35]["estudio_ambiental_descarga"])

