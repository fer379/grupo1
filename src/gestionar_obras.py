from pathlib import Path
from ftfy import fix_text
from datetime import datetime
import pandas as pd
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

        df = pd.read_csv(archivo, encoding="latin1", sep=";", low_memory=False, dtype=str, keep_default_na=False)
        self.df = df

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
            "cuit_contratista"
        ]

        for c in columnas_texto:
            if c in df.columns:
                df[c] = (
                    df[c]
                    .astype(str)
                    .map(fix_text)
                    .str.normalize("NFC")
                    .str.strip()
                    .replace(
                        {
                            "nan": None,
                            "None": None,
                            "NaN": None,
                            "NO INFORMADO": None,
                            "SIN DATOS": None,
                            "No aplica": None,
                            "no aplica": None,
                            "NO APLICA": None,
                            "-": None,
                            "": None
                        }
                    )
                )

        df = df.where(pd.notnull(df), None)

        columnas_fecha = ["fecha_inicio", "fecha_fin_inicial"]

        for c in columnas_fecha:
            if c in df.columns:

                meses_es = {
                    "ene": "1", "feb": "2", "mar": "3", "abr": "4",
                    "may": "5", "jun": "6", "jul": "7", "ago": "8",
                    "sep": "9", "oct": "10", "nov": "11", "dic": "12"
                }
                col = df[c].astype(str).str.strip().str.lower()
                for m_es, m_num in meses_es.items():
                    col = col.str.replace(fr"^{m_es}-","1/" + m_num + "/" + "20", regex=True)
                #  NOTE se normalizan esas fechas con formato 'mar-23', pasandolas al primer dia del y el mes de texto a numero utiliando los indices del array 'meses_es'

                df[c] = pd.to_datetime(col, dayfirst=True, errors="coerce")
                df[c] = (df[c].astype(str).replace('NaT', None))

        columnas_numericas = [
            "plazo_meses",
            "licitacion_anio",
            "mano_obra",
        ]

        for c in columnas_numericas:
            if c in df.columns:
                df[c] = df[c].astype(str).str.strip().str.replace('.', '').str.replace(",", ".", regex=False).str.replace('$', '').replace('N/A', '').str.strip()
                df[c] = pd.to_numeric(df[c], errors="coerce")

        if "porcentaje_avance" in df.columns:

            # NOTE hay un valor 'mar-34.2%' asi quitamos ese valor usando solo la parte de la derecha del guion
            df["porcentaje_avance"] = df["porcentaje_avance"].astype(str).str.split("-", n=1).str[-1]
            df["porcentaje_avance"] = df["porcentaje_avance"].astype(str).str.strip().str.replace(",", ".", regex=False).str.replace('%', '', regex=False)
            
            df["porcentaje_avance"] = pd.to_numeric(df["porcentaje_avance"], errors="coerce")
            df['porcentaje_avance'] = df['porcentaje_avance'].astype(object)
            df.loc[pd.isna(df['porcentaje_avance']), 'porcentaje_avance'] = None




        if 'monto_contrato' in df.columns:
            df['monto_contrato'] = df['monto_contrato'].replace('.', None, regex=False).replace('', None, regex=False)
            normal = (
                df['monto_contrato']
                .astype(str)
                .str.replace('$', '', regex=False)
                .str.strip()
            )

            # NOTE hay muchos formatos de montos en el csv

            nuevo = normal.copy()
            #  primero se agregan los que tienen un solo punto (ya tienen delimitado el decimal, quiza tengan comas)
            mask_un_punto = normal.str.count(r'\.') == 1
            nuevo.loc[mask_un_punto] = (
                normal.loc[mask_un_punto]
                .str.strip()
            )

            #  luego los que tienen una sola coma (coma en vez de punto para delimitar decimal)
            mask_una_coma = normal.str.count(r'\,') == 1
            nuevo.loc[mask_una_coma] = (
                normal.loc[mask_una_coma]
                .str.replace(',', '.', regex=False)
                .str.strip()
            )

            #  luego los que tienen sus miles separados por comas, si tienen un punto se queda ya que delimita el decimal
            mask_comas = normal.str.count(',') > 1
            nuevo.loc[mask_comas] = (
                normal.loc[mask_comas]
                .str.replace(',', '', regex=False)
                .str.strip()
            )

            #  luego los que tienen sus miles separados por puntos, se quitan y en caso que tengan coma se cambia por punto
            mask_puntos = normal.str.count(r'\.') > 1
            nuevo.loc[mask_puntos] = (
                normal.loc[mask_puntos]
                .str.replace('.', '', regex=False)
                .str.replace(',', '.', regex=False)
                .str.strip()
            )
            
            #  finalmente parseamos a float y pasamos los nan a None para que queden null en la db
            df['monto_contrato'] = pd.to_numeric(nuevo, errors='coerce')

            df['monto_contrato'] = df['monto_contrato'].astype(object)
            df.loc[pd.isna(df['monto_contrato']), 'monto_contrato'] = None




        for c in ["lat", "lng"]:
            if c in df.columns:
                df[c] = (df[c].astype(str)
                .str.replace('.', '')
                .str.replace(",", "", regex=False)
                .str.strip()
                .replace(["N/A", ""], None)
                )

        columnas_booleanas = ["compromiso", "destacada", "ba_elige"]

        for c in columnas_booleanas:
            if c in df.columns:
                df[c] = (df[c]
                    .astype(str)
                    .str.strip()
                    .str.upper()
                    .eq("SI")
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
            ManoObra,
            Financiera,
            Obra,
            EmpresaContratista
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
                ManoObra,
                Financiera,
                Obra,
                EmpresaContratista
            ]
        )
        db.commit()
        db.close()
        print(" Tablas creadas correctamente en la base de datos.")

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
            ManoObra,
            Financiera,
            Obra,
            EmpresaContratista
        )

        self.conectar_db()

        if self.df is None:
            raise RuntimeError("Primero ejecutá extraer_datos() y limpiar_datos()")

        # df = self.df.iloc[::-1].reset_index(drop=True)
        # # NOTE damos vuelta el df para que a la hora de cargarse los datos, en las obras repetidas, se guarde solo la ultima creada y no la primera (que seguramente este desactualizada)
        print(" Iniciando carga de obras...")

        cargadas = 0
        errores = 0

        for i, fila in df.iterrows():
            try:
                # NOTE normalizacion extra por las dudas
                def clean(v):
                    if pd.isna(v) or v == "":
                        return None
                    return v
                fila = fila.map(clean)
                entorno, _ = Entorno.get_or_create(
                    tipo=fila.get("entorno") or None
                )
                etapa, _ = Etapa.get_or_create(tipo=fila.get("etapa") or None)
                tipo, _ = TipoObra.get_or_create(
                    tipo=fila.get("tipo") or None
                )
                area_responsable, _ = AreaResponsable.get_or_create(
                    nombre=fila.get("area_responsable") or None
                )
                barrio, _ = Barrio.get_or_create(
                    nombre=fila.get("barrio") or None,
                    comuna=fila.get("comuna") or None,
                )

                licitacion_oferta_empresa, _ = EmpresaLicitacion.get_or_create(
                    razon_social=fila.get("licitacion_oferta_empresa") or None
                )

                tipo_contratacion, _ = TipoContratacion.get_or_create(
                    tipo=fila.get("tipo") or None
                )

                mano_obra, _ = ManoObra.get_or_create(
                    dato=fila.get("mano_obra") or None
                )

                financiamiento, _ = Financiera.get_or_create(
                    nombre=fila.get("financiamiento") or None
                )

                obra, _ = Obra.get_or_create(
                    nombre=fila.get("nombre"),
                    expediente=fila.get("expediente-numero"),
                    descripcion=fila.get("descripcion"),
                    monto=fila.get("monto_contrato") or None,
                    direccion=fila.get("direccion"),
                    latitud=fila.get("lat"),
                    longitud=fila.get("lng"),
                    fecha_inicio=fila.get("fecha_inicio"),
                    fecha_fin_inicial=fila.get("fecha_fin_inicial"),
                    plazo_meses=fila.get("plazo_meses"),
                    porcentaje_avance=fila.get("porcentaje_avance") or None,
                    imagen_1=fila.get("imagen_1") or None,
                    imagen_2=fila.get("imagen_2") or None,
                    imagen_3=fila.get("imagen_3") or None,
                    imagen_4=fila.get("imagen_4") or None,
                    licitacion_anio=fila.get("licitacion_anio"),
                    nro_contratacion=fila.get("nro_contratacion"),
                    beneficiarios=fila.get("beneficiarios"),
                    mano_obra=mano_obra,
                    compromiso=fila.get("compromiso"),
                    destacada=fila.get("destacada"),
                    ba_elige=fila.get("ba_elige"),
                    link_interno=fila.get("link_interno"),
                    pliego_descarga=fila.get("pliego_descarga"),
                    expediente_numero=fila.get("expediente_numero"),
                    estudio_ambiental_descarga=fila.get("estudio_ambiental_descarga"),
                    financiamiento=financiamiento,
                    entorno=entorno,
                    etapa=etapa,
                    tipo=tipo,
                    area_responsable=area_responsable,
                    barrio=barrio,
                    licitacion_oferta_empresa=licitacion_oferta_empresa,
                    tipo_contratacion=tipo_contratacion,
                )
                cuit_contratista, _ = EmpresaContratista.get_or_create(
                    cuit=fila.get("cuit_contratista") or None,
                    obra = obra
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
