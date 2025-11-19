from peewee import *
from datetime import date
import uuid

db = SqliteDatabase('obras_urbanas.db')

class BaseModel(Model):
    class Meta:
        database = db

class Entorno(BaseModel):
    id = UUIDField (primary_key=True,default=uuid.uuid4)
    tipo = CharField(null=False, unique=True)

class Etapa(BaseModel):
    id = UUIDField (primary_key=True,default=uuid.uuid4)
    tipo = CharField(null=False, unique=True)

class TipoObra(BaseModel):
    id = UUIDField (primary_key=True,default=uuid.uuid4)
    tipo = CharField(unique=True, null=False)

class AreaResponsable(BaseModel):
    id = UUIDField (primary_key=True,default=uuid.uuid4)
    nombre = CharField(unique=True, null=False)

class Barrio(BaseModel):
    id = UUIDField (primary_key=True,default=uuid.uuid4)
    nombre = CharField(null=True)
    comuna = CharField(null=True)
    class Meta:
        indexes = (
            (('nombre', 'comuna'), True),
        )

class EmpresaLicitacion(BaseModel):
    id = UUIDField (primary_key=True,default=uuid.uuid4)
    razon_social = CharField(unique=True, null=False)

class EmpresaContratista(BaseModel):
    id = UUIDField (primary_key=True,default=uuid.uuid4)
    cuit = CharField(unique=True, null=False)

class TipoContratacion(BaseModel):
    id = UUIDField (primary_key=True,default=uuid.uuid4)
    tipo = CharField(unique=True, null=False)


class Obra(BaseModel):
    id = UUIDField (primary_key=True,default=uuid.uuid4)
    nombre = CharField(null=False)
    expediente = CharField(null=True)
    descripcion = TextField(null=True)
    monto = FloatField(null=False)
    direccion = CharField(null=True)
    latitud = IntegerField(null=True)
    longitud = IntegerField(null=True)
    fecha_inicio = DateTimeField(null=True)
    fecha_fin_inicial = DateTimeField(null=True)
    plazo_meses = FloatField(null=True)
    porcentaje_avance = IntegerField(null=False, default=0)
    imagen_1 = CharField(null=True)
    imagen_2 = CharField(null=True)
    imagen_3 = CharField(null=True)
    imagen_4 = CharField(null=True)
    licitacion_anio = IntegerField(null=True)
    nro_contratacion = CharField(null=True)
    beneficiarios = CharField(null=True)
    mano_obra = FloatField(null=True)
    compromiso = BooleanField(null=False)
    destacada = BooleanField(null=False)
    ba_elige = BooleanField(null=False)
    link_interno = CharField(null=True)
    pliego_descarga = CharField(null=True)
    expediente_numero = CharField(null=True)
    estudio_ambiental_descarga = CharField(null=True)
    financiamiento = CharField(null=True)

    entorno = ForeignKeyField(Entorno, backref='obras', null=False)
    etapa = ForeignKeyField(Etapa, backref='obras', null=True)
    tipo = ForeignKeyField(TipoObra, backref='obras', null=False)
    area_responsable = ForeignKeyField(AreaResponsable, backref='obras', null=False)
    barrio = ForeignKeyField(Barrio, backref='obras_barriales', null=False)
    licitacion_oferta_empresa = ForeignKeyField(EmpresaLicitacion, backref='obras', null=False)
    tipo_contratacion = ForeignKeyField(TipoContratacion, backref='obras', null=False)
    cuit_contratista = ForeignKeyField(EmpresaContratista, backref='obras', null=False)

    class Meta:
        table_name: 'obra'

    @classmethod
    def cargar_csv(cls, ruta_csv: str):
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
