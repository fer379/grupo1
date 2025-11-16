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
