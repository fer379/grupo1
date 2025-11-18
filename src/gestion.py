from pathlib import Path
import pandas as pd
from gestionar_obras import GestionarObra
from modelo_orm import db


class gestion(GestionarObra):

    def __init__(self):
        super().__init__()


    def conectar_db(self):
        """Conecta a la base de datos SQLite obras_urbanas.db."""
        raiz = Path(__file__).resolve().parent.parent
        archivo_db = raiz / "data" / "obras_urbanas.db"

        db.init(str(archivo_db))

        if db.is_closed():
            db.connect()

        print(f"📌 Base de datos conectada en: {archivo_db}")
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

        self.df = df
        return df


def mapear_orm(self):
    """Crea la estructura de tablas de la base de datos usando Peewee ORM"""

    # conexión
    self.conectar_db()

    #  Importar modelos del ORM
    from modelo_orm import (
        AreaResponsable, TipoObra, Barrio, Etapa,
        Empresa, TipoContratacion, FuenteFinanciamiento, Obra
    )

    #  Crear tablas
    db.create_tables([
        AreaResponsable, TipoObra, Barrio, Etapa,
        Empresa, TipoContratacion, FuenteFinanciamiento, Obra
    ])

    print("📌 Tablas ORM creadas correctamente en la base de datos.")


 
    
    def cargar_datos(self):
        """
        Carga el contenido del DataFrame limpio a la base de datos.
        Usa get_or_create para claves foráneas.
        Evita duplicados por expediente.
        No detiene la carga por errores.
        """
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
                # -------------------------
                # Limpieza rápida
                # -------------------------
                clean = lambda v: None if pd.isna(v) or v == "" else v
                fila = fila.map(clean)

                # -------------------------
                # Evitar duplicados por expediente
                # -------------------------
                expediente = fila.get("expediente")

                if expediente:
                    existente = Obra.select().where(Obra.expediente == expediente).first()
                    if existente:
                        print(f"⚠️ Fila {i}: Ya existe obra con expediente {expediente} → se omite.")
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

        print("===================================")
        print(f" Obras insertadas: {cargadas}")
        print(f" Filas con error: {errores}")
        print("===================================")
def nueva_obra(self):
    """
    Carga manualmente una nueva obra desde la consola.
    Crea o usa claves foráneas según corresponda.
    """
    from modelo_orm import (
        AreaResponsable, TipoObra, Barrio, Etapa,
        Empresa, TipoContratacion, FuenteFinanciamiento, Obra
    )

    print("\n=== Crear nueva obra ===")

    # -------- Entrada de datos --------
    expediente = input("Expediente (obligatorio, único): ").strip()
    if expediente == "":
        print(" El expediente no puede estar vacío.")
        return

    # Verificar duplicado
    duplicado = Obra.select().where(Obra.expediente == expediente).first()
    if duplicado:
        print(f" Ya existe una obra con expediente {expediente}.")
        return

    descripcion = input("Descripción: ").strip() or None

    area = input("Área responsable: ").strip() or "NO INFORMADO"
    tipo = input("Tipo de obra: ").strip() or "NO INFORMADO"
    barrio_nombre = input("Barrio: ").strip() or "DESCONOCIDO"
    comuna_input = input("Comuna (número): ").strip()
    empresa_nombre = input("Empresa: ").strip() or "NO INFORMADA"
    etapa_nombre = input("Etapa (Planificada / Ejecución / Finalizada): ").strip() or "Sin etapa"
    tipo_contra_nombre = input("Tipo de contratación: ").strip() or "Sin dato"
    fuente_fin = input("Fuente de financiamiento: ").strip() or "Sin dato"

    monto = input("Monto del contrato: ").replace(",", ".").strip()
    monto = float(monto) if monto not in ["", None] else None

    fecha_ini = input("Fecha inicio (YYYY-MM-DD): ").strip()
    fecha_fin = input("Fecha fin inicial (YYYY-MM-DD): ").strip()

    try:
        fecha_ini = pd.to_datetime(fecha_ini).date() if fecha_ini else None
        fecha_fin = pd.to_datetime(fecha_fin).date() if fecha_fin else None
    except:
        print(" Error: formato de fecha inválido.")
        return

    avance = input("Avance físico (%): ").strip()
    avance = int(avance) if avance.isdigit() else 0

    plazo = input("Plazo (meses): ").strip()
    plazo = int(plazo) if plazo.isdigit() else None

    mano_obra = input("Mano de obra asignada: ").strip()
    mano_obra = int(mano_obra) if mano_obra.isdigit() else None

    destacada = input("¿Es destacada? (si/no): ").strip().lower()
    destacada = True if destacada in ["si", "sí", "true"] else False

    # -------- Claves foráneas --------
    area_obj, _ = AreaResponsable.get_or_create(nombre=area)
    tipo_obj, _ = TipoObra.get_or_create(nombre=tipo)
    barrio_obj, _ = Barrio.get_or_create(nombre=barrio_nombre,
                                         defaults={"comuna": comuna_input or None})
    etapa_obj, _ = Etapa.get_or_create(nombre=etapa_nombre)
    empresa_obj, _ = Empresa.get_or_create(nombre=empresa_nombre)
    contra_obj, _ = TipoContratacion.get_or_create(nombre=tipo_contra_nombre)
    fuente_obj, _ = FuenteFinanciamiento.get_or_create(nombre=fuente_fin)

    # -------- Crear obra --------
    obra = Obra.create(
        expediente=expediente,
        descripcion=descripcion,

        area_responsable=area_obj,
        tipo_obra=tipo_obj,
        barrio=barrio_obj,
        etapa=etapa_obj,
        empresa=empresa_obj,
        tipo_contratacion=contra_obj,
        fuente_financiamiento=fuente_obj,

        monto=monto,
        porcentaje_avance=avance,
        mano_obra=mano_obra,
        fecha_inicio=fecha_ini,
        fecha_fin_inicial=fecha_fin,
        plazo_meses=plazo,
        destacada=destacada
    )

    print("\n Obra creada correctamente:")
    print(f"   Expediente: {obra.expediente}")
    print(f"   Descripción: {obra.descripcion}")

    return obra

    def obtener_indicadores(self):
        pass
