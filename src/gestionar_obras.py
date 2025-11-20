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
            "comuna",
            "licitacion_oferta_empresa",
            "contratacion_tipo",
            "nro_contratacion",
            "beneficiarios",
            "compromiso",
            "destacada",
            "ba_elige",
            "link_interno",
            "pliego_descarga",
            "estudio_ambiental_descarga",
            "financiamiento",
            "mano_obra",
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
                            "": None,
                            '.': None,
                            'Sin efecto': None
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
            df.loc[pd.isna(df['porcentaje_avance']), 'porcentaje_avance'] = 0




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
        )

        self.conectar_db()

        if self.df is None:
            raise RuntimeError("Primero ejecutá extraer_datos() y limpiar_datos()")

        df = self.df
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
                    tipo=fila.get("contratacion_tipo") or None
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

    @classmethod
    def nueva_obra(self):
        from datetime import datetime

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
            EmpresaContratista,
        )


        def _input_obligatorio(mensaje):
            while True:
                valor = input(mensaje).strip()
                if valor:
                    return valor
                print("Este valor es obligatorio. Intente nuevamente.")

        def _input_opcional(mensaje):
            valor = input(mensaje).strip()
            return valor or None

        def _input_float_opcional(mensaje):
            while True:
                valor = input(mensaje).strip()
                if not valor:
                    return None
                try:
                    return float(valor.replace(",", "."))
                except ValueError:
                    print("Debe ser un número (usar . o , para decimales) o dejar vacío.")

        def _input_int_opcional(mensaje):
            while True:
                valor = input(mensaje).strip()
                if not valor:
                    return None
                try:
                    return int(valor)
                except ValueError:
                    print("Debe ser un número entero o dejar vacío.")

        def _input_bool_obligatorio(mensaje):
            while True:
                valor = input(mensaje + " [s/n]: ").strip().lower()
                if valor in ("s", "n"):
                    return valor == "s"
                print("Debe ingresar 's' o 'n'.")

        def _input_datetime_opcional(mensaje):
            while True:
                valor = input(mensaje).strip()
                formatos = ("%Y-%m-%d", "%Y-%m-%d %H:%M")
                for fmt in formatos:
                    try:
                        return datetime.strptime(valor, fmt)
                    except ValueError:
                        pass
                print("Formato inválido. Use 'YYYY-MM-DD' o 'YYYY-MM-DD HH:MM' o deje vacío.")

        def _pedir_fk(modelo, campo, nombre_modelo, texto_campo, obligatorio=True):
            opciones = modelo.select()

            if not opciones:
                print(f"No hay registros en {nombre_modelo}.")
                return None if not obligatorio else None

            print(f"\n--- Seleccione {nombre_modelo} por ID")
            
            for o in opciones:
                valor = getattr(o, campo.name)
                print(f"ID {o.id}: {valor}")

            while True:
                id = input(f"Ingrese la clave de {nombre_modelo}"
                            f"{' (vacío si no aplica)' if not obligatorio else ''}: ").strip()

                if not id and not obligatorio:
                    return None

                if id.isdigit():
                    instancia = modelo.get(modelo.id == int(id))
                    print(instancia)
                    if instancia:
                        return instancia
                    print("ID inválido.")

                print(f"No se encontró {nombre_modelo} con clave '{id}'. Intente nuevamente.\n")

        def _pedir_barrio(obligatorio=True):
            from modelo_orm import Barrio

            barrios = Barrio.select()
            if not barrios:
                print("No hay registros de Barrio.")
                return None if not obligatorio else None

            print("\n--- Barrios disponibles ---")
            for b in barrios:
                print(f"{b.id}: {b.nombre} (comuna {b.comuna})")

            while True:
                id = input(
                    f"Ingrese la clave del barrio-comuna"
                    f"{' (vacío si no aplica)' if not obligatorio else ''}: "
                ).strip()
            
                if not id and not obligatorio:
                    return None

                barrio = Barrio.get_or_none(
                    (Barrio.id == id)
                )
                if barrio:
                    return barrio

                print(
                    f"Clave barrio-comuna invalida'. "
                    "Verifique los datos e intente nuevamente.\n"
                )

        
        nombre = _input_obligatorio("Nombre de la obra: ")
        # expediente = _input_opcional("Expediente: ")
        descripcion = _input_opcional("Descripción: ")
        monto = _input_float_opcional("Monto del contrato (vacío si no aplica): ")
        direccion = _input_opcional("Dirección: ")

        latitud = _input_opcional("Latitud (texto, vacío si no aplica): ")
        longitud = _input_opcional("Longitud (texto, vacío si no aplica): ")

        # fecha_inicio = _input_datetime_opcional("Fecha de inicio (YYYY-MM-DD o YYYY-MM-DD HH:MM, vacío si no aplica): ")
        # fecha_fin_inicial = _input_datetime_opcional("Fecha fin inicial (YYYY-MM-DD o YYYY-MM-DD HH:MM, vacío si no aplica): ")

        plazo_meses = _input_float_opcional("Plazo en meses (vacío si no aplica): ")
        porcentaje_avance = 0

        imagen_1 = _input_opcional("URL imagen 1 (vacío si no aplica): ")
        imagen_2 = _input_opcional("URL imagen 2 (vacío si no aplica): ")
        imagen_3 = _input_opcional("URL imagen 3 (vacío si no aplica): ")
        imagen_4 = _input_opcional("URL imagen 4 (vacío si no aplica): ")

        licitacion_anio = _input_int_opcional("Año de licitación (entero, vacío si no aplica): ")
        # nro_contratacion = _input_opcional("Número de contratación (vacío si no aplica): ")

        beneficiarios = _input_opcional("Beneficiarios (texto, vacío si no aplica): ")

        compromiso = _input_bool_obligatorio("¿Tiene compromiso?")
        # destacada = _input_bool_obligatorio("¿Es destacada?")
        ba_elige = _input_bool_obligatorio("¿Es BA Elige?")

        link_interno = _input_opcional("Link interno (vacío si no aplica): ")
        pliego_descarga = _input_opcional("URL pliego descarga (vacío si no aplica): ")
        estudio_ambiental_descarga = _input_opcional("URL estudio ambiental (vacío si no aplica): ")

        entorno = _pedir_fk(Entorno, Entorno.tipo, "Entorno", "tipo", obligatorio=True)
        # etapa = _pedir_fk(Etapa, Etapa.tipo, "Etapa", "tipo", obligatorio=False)
        # tipo = _pedir_fk(TipoObra, TipoObra.tipo, "Tipo de Obra", "tipo", obligatorio=True)
        # area_responsable = _pedir_fk(AreaResponsable, AreaResponsable.nombre, "Área Responsable", "nombre")
        # barrio = _pedir_barrio(obligatorio=True)
        # licitacion_oferta_empresa = _pedir_fk(EmpresaLicitacion, EmpresaLicitacion.razon_social,
        #                                         "Empresa Licitación", "razón social")
        # tipo_contratacion = _pedir_fk(TipoContratacion, TipoContratacion.tipo,
        #                                 "Tipo de Contratación", "tipo")
        # mano_obra, _ = ManoObra.get_or_create(dato=(input('Ingrese la mano de obra: \n')))
        # financiamiento = _pedir_fk(Financiera, Financiera.nombre, "Financiamiento", "nombre", obligatorio=False)


        obra = Obra(
            nombre=nombre,
            descripcion=descripcion,
            monto=monto,
            direccion=direccion,
            latitud=latitud,
            longitud=longitud,
            plazo_meses=plazo_meses,
            porcentaje_avance=porcentaje_avance,
            imagen_1=imagen_1,
            imagen_2=imagen_2,
            imagen_3=imagen_3,
            imagen_4=imagen_4,
            licitacion_anio=licitacion_anio,
            beneficiarios=beneficiarios,
            compromiso=compromiso,
            ba_elige=ba_elige,
            link_interno=link_interno,
            pliego_descarga=pliego_descarga,
            estudio_ambiental_descarga=estudio_ambiental_descarga,
            entorno=entorno,
            destacada= False,
            # 1. nuevo_proyecto():
            etapa=None,
            tipo=None,
            area_responsable=None,
            barrio=None,

            # 2. iniciar_contratacion():
            nro_contratacion=None,
            tipo_contratacion=None,

            # 3. adjudicar_obra():
            licitacion_oferta_empresa=None,
            expediente=None,


            # 4. iniciar_obra():
            fecha_inicio=None,
            fecha_fin_inicial=None,
            financiamiento=None,
            mano_obra=None,
        )

        obra.save()
        

        cuit_contratista = _input_opcional("CUIT de la empresa contratista (vacío si no aplica): ")
        if cuit_contratista:
            EmpresaContratista.get_or_create(
                obra=obra,
                cuit=cuit_contratista,
            )

        db.commit()
        return obra


    @classmethod
    def obtener_indicadores(self):
        from modelo_orm import (
            Obra, Etapa, TipoObra, AreaResponsable, Barrio, Entorno, Financiera
        )
        from peewee import fn

        self.conectar_db()

        print("\n===== INDICADORES GENERALES DE OBRAS =====\n")

        # 1) Cantidad total
        total = Obra.select().count()
        print(f"Total de obras cargadas: {total}")

        # 2) Obras por etapa
        print("\nObras por etapa:")
        q_etapas = (
            Obra
            .select(Etapa.tipo, fn.COUNT(Obra.id).alias("cant"))
            .join(Etapa)
            .group_by(Etapa.tipo)
        )
        for e in q_etapas:
            print(f"- {e.etapa.tipo}: {e.cant}")

        # 3) Monto total invertido
        monto_total = Obra.select(fn.SUM(Obra.monto)).scalar() or 0
        print(f"\nMonto total invertido: ${monto_total:,.2f}")

        # 4) Monto promedio
        promedio = Obra.select(fn.AVG(Obra.monto)).scalar() or 0
        print(f"Monto promedio por obra: ${promedio:,.2f}")

        # 5) Top áreas responsables
        print("\nÁreas responsables con más obras:")
        q_area = (
            Obra
            .select(AreaResponsable.nombre, fn.COUNT(Obra.id).alias("cant"))
            .join(AreaResponsable)
            .group_by(AreaResponsable.nombre)
            .order_by(fn.COUNT(Obra.id).desc())
            .limit(5)
        )
        for a in q_area:
            print(f"- {a.area_responsable.nombre}: {a.cant}")

        # 6) Barrios con más obras
        print("\nTop 10 barrios con más obras:")
        q_barrios = (
            Obra
            .select(Barrio.nombre, fn.COUNT(Obra.id).alias("cant"))
            .join(Barrio)
            .group_by(Barrio.nombre)
            .order_by(fn.COUNT(Obra.id).desc())
            .limit(10)
        )
        for b in q_barrios:
            print(f"- {b.barrio.nombre}: {b.cant}")

        print("\n===== FIN DE INDICADORES =====\n")
