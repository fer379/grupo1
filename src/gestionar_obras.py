from pathlib import Path
import pandas as pd
import numpy as np
from abc import ABC, abstractmethod
from modelo_orm import db


class GestionarObra:
    df = None

    @classmethod
    def conectar_db(self):
        raiz = Path(__file__).resolve().parent.parent
        archivo_db = raiz / "data" / "obras_urbanas.db"

        db.init(str(archivo_db))

        if db.is_closed():
            db.connect()
        print(f" Base de datos conectada en: {archivo_db}")
        return db

    @classmethod
    def extraer_datos(self):
        raiz = Path(__file__).resolve().parent.parent
        archivo = raiz / "data" / "observatorio-de-obras-urbanas.csv"

        self.df = pd.read_csv(archivo, encoding="latin1", sep=";", low_memory=False)
        return self.df

    @classmethod
    def limpiar_datos(self):
        if self.df is None:
            raise RuntimeError("Primero ejecutá extraer_datos()")

        df = self.df.copy()

        columnas_texto = [
            "entorno",
            "nombre",
            "etapa",
            "tipo",
            "area_responsable",
            "descripcion",
            "barrio",
            "direccion",
            "imagen_1",
            "imagen_2",
            "imagen_3",
            "imagen_4",
            "comuna"
            "licitacion_oferta_empresa",
            "contratacion_tipo",
            "nro_contratacion",
            "beneficiarios",
            "compromiso",
            "destacada",
            "ba_elige",
            "link_interno",
            "pliego_descarga",
            "expediente-numero",
            "estudio_ambiental_descarga",
            "financiamiento",
        ]

        for c in columnas_texto:
            if c in df.columns:
                df[c] = (
                    df[c]
                    .astype(str)
                    .str.strip()
                    .replace(
                        {
                            "nan": None,
                            "None": None,
                            "NaN": None,
                            "NO INFORMADO": None,
                            "SIN DATOS": None,
                        }
                    )
                )

        df = df.where(pd.notnull(df), None)

        columnas_fecha = ["fecha_inicio", "fecha_fin"]

        for c in columnas_fecha:
            if c in df.columns:
                df[c] = pd.to_datetime(df[c], format="%d/%m/%Y", errors="coerce")
                df[c] = df[c].dt.strftime("%Y-%m-%d")

        columnas_numericas = [
            "monto_contrato",
            "plazo_meses",
            "porcentaje_avance",
            "licitacion_anio",
            "cuit_contratista",
            "mano_obra",
        ]

        for c in columnas_numericas:
            if c in df.columns:
                df[c] = df[c].astype(str).str.strip().str.replace('.', '').str.replace(",", ".", regex=False).str.replace('$', '').replace('%', '').replace('N/A', '').str.strip()
                print(df[c].values)
                df[c] = pd.to_numeric(df[c], errors="coerce")

        for c in ["lat", "lng"]:
            if c in df.columns:
                df[c] = df[c].astype(str).str.strip().str.replace('.', '').str.replace(",", "", regex=False).str.replace('$', '').str.strip()
                print(df[c].values)
                df[c] = pd.to_numeric(df[c], errors="coerce")


        columnas_booleanas = ["compromiso", "destacada", "ba_elige"]

        for c in columnas_booleanas:
            if c in df.columns:
                df[c] = (df[c]
                    .fillna("")        
                    .astype(str)       
                    .map({
                        "SI": True,
                        "": False,
                        "NO": False,
                        None: False
                    })
                    .fillna(False)
                )
                


        self.df = df
        return df

    @classmethod
    def mapear_orm(self):
        self.conectar_db()

        from modelo_orm import (
            Entorno,
            Etapa,
            TipoObra,
            AreaResponsable,
            Barrio,
            EmpresaLicitacion,
            EmpresaContratista,
            TipoContratacion,
            Obra,
        )

        db.create_tables(
            [
                Entorno,
                Etapa,
                TipoObra,
                AreaResponsable,
                Barrio,
                EmpresaLicitacion,
                EmpresaContratista,
                TipoContratacion,
                Obra,
            ]
        )
        db.commit()
        db.close()
        print(" Tablas creadas correctamente en la base de datos.")

    @classmethod
    def obtenerDf(self):
        df = self.df
        # for i, fila in df.iterrows():
        #     print(fila.get("nombre"))
        #     print(fila.get("monto"))
        #     print(fila.get("compromiso"))
        #     print(fila["compromiso"].apply(type))
        #     print("\n")
        print(df['compromiso'].head(10))
        print(df['compromiso'].apply(type).head(10))

    @classmethod
    def cargar_datos(self):
        from modelo_orm import (
            Entorno,
            Etapa,
            TipoObra,
            AreaResponsable,
            Barrio,
            EmpresaLicitacion,
            EmpresaContratista,
            TipoContratacion,
            Obra,
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

                expediente = fila.get("expediente-numero") or None

                if expediente:
                    existente = (
                        Obra.select().where(Obra.expediente == expediente).first()
                    )
                    if existente:
                        print(
                            f" Fila {i}: Ya existe obra con expediente {expediente} → se omite."
                        )
                        continue
                entorno, _ = Entorno.get_or_create(
                    tipo=fila.get("entorno") or "NO INFORMADO"
                )
                etapa, _ = Etapa.get_or_create(tipo=fila.get("etapa") or "NO INFORMADO")
                tipo, _ = TipoObra.get_or_create(
                    tipo=fila.get("tipo") or "NO INFORMADO"
                )
                area_responsable, _ = AreaResponsable.get_or_create(
                    nombre=fila.get("area_responsable") or "NO INFORMADO"
                )
                barrio, _ = Barrio.get_or_create(
                    nombre=fila.get("barrio") or "NO INFORMADO",
                    comuna=fila.get("comuna") or "NO INFORMADO",
                )

                licitacion_oferta_empresa, _ = EmpresaLicitacion.get_or_create(
                    razon_social=fila.get("licitacion_oferta_empresa") or "NO INFORMADO"
                )
                cuit_contratista, _ = EmpresaContratista.get_or_create(
                    cuit=fila.get("cuit_contratista") or "NO INFORMADO"
                )

                tipo_contratacion, _ = TipoContratacion.get_or_create(
                    tipo=fila.get("tipo_contratacion") or "NO INFORMADO"
                )

                Obra.create(
                    nombre=fila.get("nombre"),
                    expediente=expediente,
                    descripcion=fila.get("descripcion"),
                    monto=fila.get("monto_contrato") or 0,
                    direccion=fila.get("direccion"),
                    latitud=fila.get("lat"),
                    longitud=fila.get("lng"),
                    fecha_inicio=fila.get("fecha_inicio"),
                    fecha_fin_inicial=fila.get("fecha_fin_inicial"),
                    plazo_meses=fila.get("plazo_meses"),
                    porcentaje_avance=fila.get("porcentaje_avance") or 0,
                    imagen_1=fila.get("imagen_1") or None,
                    imagen_2=fila.get("imagen_2") or None,
                    imagen_3=fila.get("imagen_3") or None,
                    imagen_4=fila.get("imagen_4") or None,
                    licitacion_anio=fila.get("licitacion_anio"),
                    nro_contratacion=fila.get("nro_contratacion"),
                    beneficiarios=fila.get("beneficiarios"),
                    mano_obra=fila.get("mano_obra"),
                    compromiso=fila.get("compromiso"),
                    destacada=fila.get("destacada"),
                    ba_elige=fila.get("ba_elige"),
                    link_interno=fila.get("link_interno"),
                    pliego_descarga=fila.get("pliego_descarga"),
                    expediente_numero=fila.get("expediente_numero"),
                    estudio_ambiental_descarga=fila.get("estudio_ambiental_descarga"),
                    financiamiento=fila.get("financiamiento"),
                    entorno=entorno,
                    etapa=etapa,
                    tipo=tipo,
                    area_responsable=area_responsable,
                    barrio=barrio,
                    licitacion_oferta_empresa=licitacion_oferta_empresa,
                    tipo_contratacion=tipo_contratacion,
                    cuit_contratista=cuit_contratista,
                )

                cargadas += 1

            except Exception as e:
                errores += 1
                print(f" Error en fila {i}: {e}")

        db.commit()
        print(f" Obras insertadas: {cargadas}")
        print(f" Filas con error: {errores}")
        db.close()


# def nueva_obra(self):

#     from modelo_orm import (
#         AreaResponsable, TipoObra, Barrio, Etapa,
#         Empresa, TipoContratacion, FuenteFinanciamiento, Obra
#     )

#     self.conectar_db()

#     print("\n=== CREAR NUEVA OBRA ===")


#     expediente = input("Ingrese expediente: ").strip()
#     descripcion = input("Ingrese descripción: ").strip()


#     def pedir_fk(modelo, campo_nombre):

#         while True:
#             valor = input(f"Ingrese {campo_nombre}: ").strip()

#             instancia = modelo.get_or_none(modelo.nombre == valor)

#             if instancia:
#                 return instancia

#             print(f" {campo_nombre} '{valor}' no existe. Intente nuevamente.\n")

#     area = pedir_fk(AreaResponsable, "Área Responsable")
#     tipo = pedir_fk(TipoObra, "Tipo de Obra")
#     barrio = pedir_fk(Barrio, "Barrio")
#     etapa = pedir_fk(Etapa, "Etapa")
#     empresa = pedir_fk(Empresa, "Empresa")
#     tipo_contra = pedir_fk(TipoContratacion, "Tipo de Contratación")
#     fuente = pedir_fk(FuenteFinanciamiento, "Fuente de Financiamiento")


#     try:
#         monto = float(input("Monto del contrato: "))
#     except:
#         monto = None

#     try:
#         avance = int(input("Porcentaje de avance: "))
#     except:
#         avance = 0

#     destacada = input("¿Es destacada? (SI/NO): ").upper() in ["SI", "SÍ", "TRUE"]


#     obra = Obra(
#         expediente=expediente,
#         descripcion=descripcion,
#         area_responsable=area,
#         tipo_obra=tipo,
#         barrio=barrio,
#         etapa=etapa,
#         empresa=empresa,
#         tipo_contratacion=tipo_contra,
#         fuente_financiamiento=fuente,
#         monto=monto,
#         porcentaje_avance=avance,
#         destacada=destacada
#     )

#     obra.save()

#     print("\n Obra creada correctamente!")
#     print(f"ID asignado: {obra.id}")

#     return obra
