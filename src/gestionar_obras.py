from pathlib import Path
import pandas as pd
from abc import ABC, abstractmethod

class GestionarObra(ABC):

    def __init__(self):
        self.df = None   # atributo común para todas las subclases

    @abstractmethod
    def extraer_datos(self):
        pass

    @abstractmethod
    def limpiar_datos(self):
        pass


class Gestion(GestionarObra):

    def __init__(self):
        super().__init__()   # inicializa self.df = None

    def extraer_datos(self):
        # Acá deberías cargar el CSV real
        raiz = Path (__file__).resolve().parent.parent
        archivo = raiz / "data" / "observatorio-de-obras-urbanas.csv"
        datos = pd.read_csv (archivo, encoding="latin1", sep = ";")
        self.df = pd.DataFrame (datos         
        )
        print (self.df)
        return self.df

    def limpiar_datos(self):
        if self.df is None:
            raise RuntimeError("Primero ejecutá extraer_datos()")

        df = self.df.copy()

        cols_text = ['area_responsable', 'tipo_obra', 'barrio']
        for c in cols_text:
            if c in df.columns:
                df[c] = (
                    df[c].astype(str)
                    .str.strip()
                    .replace({'nan': None, 'None': None,'NaN': None })
                )

        self.df = df
        return df
    def imprimir (self):
        print (self.df.iloc [28:35]["estudio_ambiental_descarga"])

gestion = Gestion()

gestion.extraer_datos()
gestion.limpiar_datos()

"""gestion.imprimir ()"""
