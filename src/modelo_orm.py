from peewee import *
from datetime import date

db = SqliteDatabase('obras_urbanas.db')

class BaseModel(Model):
    class Meta:
        database = db

class AreaResponsable(BaseModel):
    nombre = CharField(unique=True)

class TipoObra(BaseModel):
    nombre = CharField(unique=True)

class Barrio(BaseModel):
    nombre = CharField(unique=True)
    comuna = IntegerField(null=True)

class Etapa(BaseModel):
    nombre = CharField(unique=True)

class Empresa(BaseModel):
    nombre = CharField(unique=True)

class TipoContratacion(BaseModel):
    nombre = CharField(unique=True)

class FuenteFinanciamiento(BaseModel):
    nombre = CharField(unique=True)

class Obra(BaseModel):
    # campos mínimos: adaptar según CSV
    id = UUIDField (unique=True,primary_key=True,null=False)
    expediente = CharField(null=True)
    descripcion = TextField(null=True)
    area_responsable = ForeignKeyField(AreaResponsable, backref='obras', null=True)
    tipo_obra = ForeignKeyField(TipoObra, backref='obras', null=True)
    barrio = ForeignKeyField(Barrio, backref='obras', null=True)
    etapa = ForeignKeyField(Etapa, backref='obras', null=True)
    empresa = ForeignKeyField(Empresa, backref='obras', null=True)
    tipo_contratacion = ForeignKeyField(TipoContratacion, backref='obras', null=True)
    fuente_financiamiento = ForeignKeyField(FuenteFinanciamiento, backref='obras', null=True)

    monto = FloatField(null=True)
    fecha_inicio = DateField(null=True)
    fecha_fin_inicial = DateField(null=True)
    porcentaje_avance = IntegerField(default=0)
    plazo_meses = IntegerField(null=True)
    mano_obra = IntegerField(null=True)
    destacada = BooleanField(default=False)

    @classmethod
    def cargar_csv(cls, ruta_csv: str):
        """
        Carga todas las filas del CSV y las convierte en instancias Obra,
        creando automáticamente las FK necesarias (área, empresa, barrio, etc.)
        """
        import pandas as pd

        df = pd.read_csv(ruta_csv, encoding="latin1", sep=";", low_memory=False)

        obras_creadas = []

        for _, fila in df.iterrows():

            # Obtener o crear claves foráneas
            area, _ = AreaResponsable.get_or_create(
                nombre=str(fila.get("area_responsable")).strip()
            ) if fila.get("area_responsable") else (None, False)

            tipo, _ = TipoObra.get_or_create(
                nombre=str(fila.get("tipo_obra")).strip()
            ) if fila.get("tipo_obra") else (None, False)

            barrio, _ = Barrio.get_or_create(
                nombre=str(fila.get("barrio")).strip(),
                defaults={"comuna": fila.get("comuna")}
            ) if fila.get("barrio") else (None, False)

            etapa, _ = Etapa.get_or_create(
                nombre=str(fila.get("etapa")).strip()
            ) if fila.get("etapa") else (None, False)

            empresa, _ = Empresa.get_or_create(
                nombre=str(fila.get("empresa")).strip()
            ) if fila.get("empresa") else (None, False)

            tipo_contra, _ = TipoContratacion.get_or_create(
                nombre=str(fila.get("tipo_contratacion")).strip()
            ) if fila.get("tipo_contratacion") else (None, False)

            fuente, _ = FuenteFinanciamiento.get_or_create(
                nombre=str(fila.get("fuente_financiamiento")).strip()
            ) if fila.get("fuente_financiamiento") else (None, False)

            # Crear obra
            obra = cls.create(
                expediente=fila.get("expediente"),
                descripcion=fila.get("descripcion"),

                area_responsable=area,
                tipo_obra=tipo,
                barrio=barrio,
                etapa=etapa,
                empresa=empresa,
                tipo_contratacion=tipo_contra,
                fuente_financiamiento=fuente,

                monto=fila.get("monto_contrato"),
                fecha_inicio=fila.get("fecha_inicio"),
                fecha_fin_inicial=fila.get("fecha_fin"),
                porcentaje_avance=fila.get("avance_fisico") or 0,
                plazo_meses=fila.get("plazo_actualizado"),
                mano_obra=fila.get("mano_obra"),
                destacada=fila.get("destacada") is True
            )

            obras_creadas.append(obra)

        return obras_creadas

    # Métodos de instancia para etapas (se implementan en este archivo o en otro)
    def nuevo_proyecto(self):
        etapa, _ = Etapa.get_or_create(nombre="Proyecto")
        self.etapa = etapa
        self.save()

    def iniciar_contratacion(self, tipo_contratacion, nro_contratacion):
        tc = TipoContratacion.get(TipoContratacion.nombre == tipo_contratacion)
        self.tipo_contratacion = tc
        # guardamos nro_contratacion en expediente o campo similar
        self.expediente = nro_contratacion
        self.save()

    def adjudicar_obra(self, empresa_nombre, nro_expediente):
        emp = Empresa.get(Empresa.nombre == empresa_nombre)
        self.empresa = emp
        self.expediente = nro_expediente
        self.save()

    def iniciar_obra(self, destacada, fecha_inicio, fecha_fin_inicial, fuente_fin, mano_obra):
        self.destacada = destacada
        self.fecha_inicio = fecha_inicio
        self.fecha_fin_inicial = fecha_fin_inicial
        self.fuente_financiamiento = FuenteFinanciamiento.get(FuenteFinanciamiento.nombre == fuente_fin)
        self.mano_obra = mano_obra
        etapa, _ = Etapa.get_or_create(nombre="Ejecución")
        self.etapa = etapa
        self.save()

    def actualizar_porcentaje_avance(self, porcentaje):
        self.porcentaje_avance = porcentaje
        self.save()

    def incrementar_plazo(self, meses):
        if self.plazo_meses is None: self.plazo_meses = 0
        self.plazo_meses += meses
        self.save()

    def incrementar_mano_obra(self, cantidad):
        if self.mano_obra is None: self.mano_obra = 0
        self.mano_obra += cantidad
        self.save()

    def finalizar_obra(self):
        etapa, _ = Etapa.get_or_create(nombre="Finalizada")
        self.etapa = etapa
        self.porcentaje_avance = 100
        self.save()

    def rescindir_obra(self):
        etapa, _ = Etapa.get_or_create(nombre="Rescindida")
        self.etapa = etapa
        self.save()
