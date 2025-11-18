from pathlib import Path
import pandas as pd
import numpy as np
from abc import ABC, abstractmethod
from modelo_orm import db



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

    def conectar_db(self):
        """Conecta a la base SQLite en /data."""
        raiz = Path(__file__).resolve().parent.parent
        archivo_db = raiz / "data" / "obras_urbanas.db"

        db.init(str(archivo_db))

        if db.is_closed():
            db.connect()

        print(f" Base de datos conectada en: {archivo_db}")
        return db



    def extraer_datos(self):
        raiz = Path(__file__).resolve().parent.parent
        archivo = raiz / "data" / "observatorio-de-obras-urbanas.csv"

        self.df = pd.read_csv(
            archivo,
            encoding="latin1",
            sep=";",
            low_memory=False
        )
        return self.df



    def limpiar_datos(self):
        """Normaliza texto, fechas, números y NaN."""
        if self.df is None:
            raise RuntimeError("Primero ejecutá extraer_datos()")

        df = self.df.copy()

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

        df = df.where(pd.notnull(df), None)

        columnas_fecha = [
            'fecha_inicio', 'fecha_fin', 'plazo_actualizado',
            'fecha_ultima_muestra'
        ]

        for c in columnas_fecha:
            if c in df.columns:
                df[c] = pd.to_datetime(df[c], errors="coerce")

        columnas_numericas = [
            'monto_contrato', 'avance_financiero', 'avance_fisico'
        ]

        for c in columnas_numericas:
            if c in df.columns:
                df[c] = df[c].astype(str).str.replace(",", ".", regex=False)
                df[c] = pd.to_numeric(df[c], errors="coerce")

        columnas_booleanas = ['tiene_impacto_ambiental', 'posee_proyecto']

        for c in columnas_booleanas:
            if c in df.columns:
                df[c] = df[c].astype(str).str.upper().map({
                    'SI': True,
                    'SÍ': True,
                    'NO': False
                })

        self.df = df
        return df


    def mapear_orm(self):
        self.conectar_db()

        from modelo_orm import (
            AreaResponsable, TipoObra, Barrio, Etapa,
            Empresa, TipoContratacion, FuenteFinanciamiento, Obra
        )

        db.create_tables([
            AreaResponsable, TipoObra, Barrio, Etapa,
            Empresa, TipoContratacion, FuenteFinanciamiento, Obra
        ])

        print(" Tablas creadas correctamente en la base de datos.")


    def cargar_datos(self):
        from modelo_orm import (
            AreaResponsable, TipoObra, Barrio, Etapa,
            Empresa, TipoContratacion, FuenteFinanciamiento, Obra
        )

        self.conectar_db()

        if self.df is None:
            raise RuntimeError("Primero ejecutá extraer_datos() y limpiar_datos()")

        df = self.df
        print(" Iniciando carga de obras...")

        cargadas = 0
        errores = 0

        for i, fila in df.iterrows():
            try:
                clean = lambda v: None if pd.isna(v) or v == "" else v
                fila = fila.map(clean)

                expediente = fila.get("expediente")

                if expediente:
                    existente = Obra.select().where(Obra.expediente == expediente).first()
                    if existente:
                        print(f" Fila {i}: Ya existe obra con expediente {expediente} → se omite.")
                        continue

                area, _ = AreaResponsable.get_or_create(
                    nombre=fila.get("area_responsable") or "NO INFORMADO"
                )

                tipo, _ = TipoObra.get_or_create(
                    nombre=fila.get("tipo_obra") or "NO INFORMADO"
                )

                barrio, _ = Barrio.get_or_create(
                    nombre=fila.get("barrio") or "DESCONOCIDO",
                    defaults={"comuna": fila.get("comuna")}
                )

                etapa, _ = Etapa.get_or_create(
                    nombre=fila.get("etapa") or "Sin etapa"
                )

                empresa, _ = Empresa.get_or_create(
                    nombre=fila.get("empresa") or "NO INFORMADA"
                )

                tipo_contra, _ = TipoContratacion.get_or_create(
                    nombre=fila.get("tipo_contratacion") or "Sin dato"
                )

                fuente, _ = FuenteFinanciamiento.get_or_create(
                    nombre=fila.get("fuente_financiamiento") or "Sin dato"
                )

                Obra.create(
                    expediente=expediente,
                    descripcion=fila.get("descripcion"),

                    area_responsable=area,
                    tipo_obra=tipo,
                    barrio=barrio,
                    etapa=etapa,
                    empresa=empresa,
                    tipo_contratacion=tipo_contra,
                    fuente_financiamiento=fuente,

                    monto=fila.get("monto_contrato"),
                    porcentaje_avance=fila.get("avance_fisico") or 0,
                    mano_obra=fila.get("mano_obra"),
                    fecha_inicio=fila.get("fecha_inicio"),
                    fecha_fin_inicial=fila.get("fecha_fin"),
                    plazo_meses=fila.get("plazo_actualizado"),

                    destacada=str(fila.get("destacada")).upper() in ["SI", "SÍ", "TRUE"]
                )

                cargadas += 1

            except Exception as e:
                errores += 1
                print(f" Error en fila {i}: {e}")


        print(f" Obras insertadas: {cargadas}")
        print(f" Filas con error: {errores}")
def nueva_obra(self):

    from modelo_orm import (
        AreaResponsable, TipoObra, Barrio, Etapa,
        Empresa, TipoContratacion, FuenteFinanciamiento, Obra
    )

    self.conectar_db()

    print("\n=== CREAR NUEVA OBRA ===")


    expediente = input("Ingrese expediente: ").strip()
    descripcion = input("Ingrese descripción: ").strip()



    def pedir_fk(modelo, campo_nombre):

        while True:
            valor = input(f"Ingrese {campo_nombre}: ").strip()

            instancia = modelo.get_or_none(modelo.nombre == valor)

            if instancia:
                return instancia

            print(f" {campo_nombre} '{valor}' no existe. Intente nuevamente.\n")

    area = pedir_fk(AreaResponsable, "Área Responsable")
    tipo = pedir_fk(TipoObra, "Tipo de Obra")
    barrio = pedir_fk(Barrio, "Barrio")
    etapa = pedir_fk(Etapa, "Etapa")
    empresa = pedir_fk(Empresa, "Empresa")
    tipo_contra = pedir_fk(TipoContratacion, "Tipo de Contratación")
    fuente = pedir_fk(FuenteFinanciamiento, "Fuente de Financiamiento")


    try:
        monto = float(input("Monto del contrato: "))
    except:
        monto = None

    try:
        avance = int(input("Porcentaje de avance: "))
    except:
        avance = 0

    destacada = input("¿Es destacada? (SI/NO): ").upper() in ["SI", "SÍ", "TRUE"]


    obra = Obra(
        expediente=expediente,
        descripcion=descripcion,
        area_responsable=area,
        tipo_obra=tipo,
        barrio=barrio,
        etapa=etapa,
        empresa=empresa,
        tipo_contratacion=tipo_contra,
        fuente_financiamiento=fuente,
        monto=monto,
        porcentaje_avance=avance,
        destacada=destacada
    )

    obra.save()

    print("\n Obra creada correctamente!")
    print(f"ID asignado: {obra.id}")

    return obra
