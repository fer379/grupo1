from peewee import *
from datetime import date
import uuid

db = SqliteDatabase('obras_urbanas.db')

class BaseModel(Model):
    class Meta:
        database = db


class Entorno(BaseModel):
    id = AutoField()
    tipo = CharField(null=False, unique=True)

class Etapa(BaseModel):
    id = AutoField()
    tipo = CharField(null=False, unique=True)

class TipoObra(BaseModel):
    id = AutoField()
    tipo = CharField(unique=True, null=True)

class AreaResponsable(BaseModel):
    id = AutoField()
    nombre = CharField(unique=True, null=False)

class Barrio(BaseModel):
    id = AutoField()
    nombre = CharField(null=True)
    comuna = CharField(null=True)
    class Meta:
        indexes = (
            (('nombre', 'comuna'), True),
        )

class EmpresaLicitacion(BaseModel):
    id = AutoField()
    razon_social = CharField(unique=True, null=True)

class TipoContratacion(BaseModel):
    id = AutoField()
    tipo = CharField(unique=True, null=True)

class ManoObra(BaseModel):
    id = AutoField()
    dato = CharField(unique=True, null=True)

class Financiera(BaseModel):
    id = AutoField()
    nombre = CharField(unique=True, null=True)

class Obra(BaseModel):
    id = AutoField()
    nombre = CharField(null=False)
    expediente = CharField(null=True)
    descripcion = TextField(null=True)
    monto = FloatField(null=True)
    direccion = CharField(null=True)
    latitud = CharField(null=True)
    longitud = CharField(null=True)
    fecha_inicio = DateTimeField(null=True)
    fecha_fin_inicial = DateTimeField(null=True)
    plazo_meses = FloatField(null=True)
    porcentaje_avance = IntegerField(null=True, default=0)
    imagen_1 = CharField(null=True)
    imagen_2 = CharField(null=True)
    imagen_3 = CharField(null=True)
    imagen_4 = CharField(null=True)
    licitacion_anio = IntegerField(null=True)
    nro_contratacion = CharField(null=True)
    beneficiarios = CharField(null=True)
    compromiso = BooleanField(null=False)
    destacada = BooleanField(null=False)
    ba_elige = BooleanField(null=False)
    link_interno = CharField(null=True)
    pliego_descarga = CharField(null=True)
    expediente_numero = CharField(null=True)
    estudio_ambiental_descarga = CharField(null=True)

    entorno = ForeignKeyField(Entorno, backref='obras', null=False)
    etapa = ForeignKeyField(Etapa, backref='obras', null=True)
    tipo = ForeignKeyField(TipoObra, backref='obras', null=False)
    area_responsable = ForeignKeyField(AreaResponsable, backref='obras', null=False)
    barrio = ForeignKeyField(Barrio, backref='obras_barriales', null=False)
    licitacion_oferta_empresa = ForeignKeyField(EmpresaLicitacion, backref='obras', null=False)
    tipo_contratacion = ForeignKeyField(TipoContratacion, backref='obras', null=False)
    mano_obra = ForeignKeyField(ManoObra, backref='obras', null=True)
    financiamiento = ForeignKeyField(Financiera, backref='obras', null=True)


class EmpresaContratista(BaseModel):
    id = AutoField()
    obra = ForeignKeyField(Obra, backref="obra", on_delete="CASCADE")
    cuit = CharField(null=True)
    class Meta:
        indexes = (
            (('obra', 'cuit'), True),
        )


    def nuevo_proyecto(self):
        etapa, _ = Etapa.get_or_create(nombre="Proyecto")
        self.etapa = etapa
        self.save()

    # def iniciar_contratacion(self, tipo_contratacion, nro_contratacion):
    #     tc = TipoContratacion.get(TipoContratacion.nombre == tipo_contratacion)
    #     self.tipo_contratacion = tc
    #     # guardamos nro_contratacion en expediente o campo similar
    #     self.expediente = nro_contratacion
    #     self.save()

    # def adjudicar_obra(self, empresa_nombre, nro_expediente):
    #     emp = Empresa.get(Empresa.nombre == empresa_nombre)
    #     self.empresa = emp
    #     self.expediente = nro_expediente
    #     self.save()

    # def iniciar_obra(self, destacada, fecha_inicio, fecha_fin_inicial, fuente_fin, mano_obra):
    #     self.destacada = destacada
    #     self.fecha_inicio = fecha_inicio
    #     self.fecha_fin_inicial = fecha_fin_inicial
    #     self.fuente_financiamiento = FuenteFinanciamiento.get(FuenteFinanciamiento.nombre == fuente_fin)
    #     self.mano_obra = mano_obra
    #     etapa, _ = Etapa.get_or_create(nombre="Ejecución")
    #     self.etapa = etapa
    #     self.save()

    # def actualizar_porcentaje_avance(self, porcentaje):
    #     self.porcentaje_avance = porcentaje
    #     self.save()

    # def incrementar_plazo(self, meses):
    #     if self.plazo_meses is None: self.plazo_meses = 0
    #     self.plazo_meses += meses
    #     self.save()

    # def incrementar_mano_obra(self, cantidad):
    #     if self.mano_obra is None: self.mano_obra = 0
    #     self.mano_obra += cantidad
    #     self.save()

    # def finalizar_obra(self):
    #     etapa, _ = Etapa.get_or_create(nombre="Finalizada")
    #     self.etapa = etapa
    #     self.porcentaje_avance = 100
    #     self.save()

    # def rescindir_obra(self):
    #     etapa, _ = Etapa.get_or_create(nombre="Rescindida")
    #     self.etapa = etapa
    #     self.save()


