from peewee import *
from datetime import date, datetime

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
    estudio_ambiental_descarga = CharField(null=True)

    entorno = ForeignKeyField(Entorno, backref='obras', null=True)
    etapa = ForeignKeyField(Etapa, backref='obras', null=True)
    tipo = ForeignKeyField(TipoObra, backref='obras', null=True)
    area_responsable = ForeignKeyField(AreaResponsable, backref='obras', null=True)
    barrio = ForeignKeyField(Barrio, backref='obras_barriales', null=True)
    licitacion_oferta_empresa = ForeignKeyField(EmpresaLicitacion, backref='obras', null=True)
    tipo_contratacion = ForeignKeyField(TipoContratacion, backref='obras', null=True)
    mano_obra = ForeignKeyField(ManoObra, backref='obras', null=True)
    financiamiento = ForeignKeyField(Financiera, backref='obras', null=True)

    def pedir_fk(self, modelo, campo, nombre_modelo, texto_campo, obligatorio=True):
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
                    if instancia:
                        return instancia
                    print("ID inválido.")

                print(f"No se encontró {nombre_modelo} con clave '{id}'. Intente nuevamente.\n")

    def input_obligatorio(self,mensaje):
            while True:
                valor = input(mensaje).strip()
                if valor:
                    return valor
                print("Este valor es obligatorio. Intente nuevamente.")

    def input_bool_obligatorio(self, mensaje):
            while True:
                valor = input(mensaje + " [s/n]: ").strip().lower()
                if valor in ("s", "n"):
                    return valor == "s"
                print("Debe ingresar 's' o 'n'.")

    def input_datetime(self, mensaje):
            while True:
                valor = input(mensaje).strip()
                formatos = ("%Y-%m-%d", "%Y-%m-%d %H:%M")
                for fmt in formatos:
                    try:
                        return datetime.strptime(valor, fmt)
                    except ValueError:
                        pass
                print("Formato inválido. Use 'YYYY-MM-DD' o 'YYYY-MM-DD HH:MM' o deje vacío.")

    def input_float(self, mensaje):
            while True:
                valor = input(mensaje).strip()
                try:
                    return float(valor.replace(",", "."))
                except ValueError:
                    print("Debe ser un número (usar . o , para decimales)")
    def input_porcentaje(self, mensaje):
        while True:
                valor = input(mensaje).strip()
                try:
                    num = float(valor.replace(",", "."))
                    if(num <= 100):
                        return num
                    else: return 100
                except ValueError:
                    print("Debe ser un número (usar . o , para decimales)")

    def nuevo_proyecto(self):
        def pedir_barrio(obligatorio=True):
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
        etapa, _ = Etapa.get_or_create(tipo="Proyecto")
        self.etapa = etapa
        self.tipo = self.pedir_fk(TipoObra, TipoObra.tipo, "Tipo de Obra", "tipo", obligatorio=True)
        self.area_responsable = self.pedir_fk(AreaResponsable, AreaResponsable.nombre, "Área Responsable", "nombre", obligatorio=True)
        self.barrio = pedir_barrio()
        self.save()
        db.commit()
        db.close()

    def iniciar_contratacion(self):
        self.tipo_contratacion = self.pedir_fk(TipoContratacion, TipoContratacion.tipo, "Tipo de Contratacion", "tipo", obligatorio=True)
        self.nro_contratacion = self.input_obligatorio("Número de contratación: ")

        self.save()
        db.commit()
        db.close()

    def adjudicar_obra(self):
        self.licitacion_oferta_empresa = self.pedir_fk(EmpresaLicitacion, EmpresaLicitacion.razon_social, "Empresa Licitación", "razón social")
        self.expediente = self.input_obligatorio("Expediente: ")

        self.save()
        db.commit()
        db.close()

    def iniciar_obra(self):

        self.destacada = self.input_bool_obligatorio("¿Es destacada?")
        self.fecha_inicio = self.input_datetime("Fecha de inicio (YYYY-MM-DD o YYYY-MM-DD HH:MM): ")
        self.fecha_fin_inicial = self.input_datetime("Fecha de finalizacion (YYYY-MM-DD o YYYY-MM-DD HH:MM): ")

        self.financiamiento = self.pedir_fk(Financiera, Financiera.nombre, "Financiamiento", "nombre", obligatorio=True)

        mano_obra, _ = ManoObra.get_or_create(dato=(input('Ingrese la mano de obra: \n')))
        self.mano_obra = mano_obra

        etapa, _ = Etapa.get_or_create(tipo="Ejecución")
        self.etapa = etapa

        self.save()
        db.commit()
        db.close()

    def actualizar_porcentaje_avance(self):
        if(isinstance(self.porcentaje_avance, int) or isinstance(self.porcentaje_avance, float)):
            self.porcentaje_avance = int(self.porcentaje_avance) + int(self.input_porcentaje(f"Ingrese el valor a sumar al porcentaje de avance original ({self.porcentaje_avance}): "))
        else:
            self.porcentaje_avance = self.input_porcentaje(f"El valor en la db del porcentaje de avance no es un numero o esta vacio ({self.porcentaje_avance or None}), ingrese un valor numerico para actualizarlo: ")
        self.save()
        db.commit()
        db.close()

    def incrementar_plazo(self):
        if(isinstance(self.plazo_meses, int) or isinstance(self.plazo_meses, float)):
            self.plazo_meses = int(self.plazo_meses) + int(self.input_float(f"Ingrese el valor a sumar al plazo en meses original ({self.plazo_meses}): "))
        else:
            self.plazo_meses = self.input_float(f"El valor en la db del plazo en meses no es un numero o esta vacio ({self.plazo_meses or None}), ingrese un valor numerico para actualizarlo: ")
        self.save()
        db.commit()
        db.close()

    def incrementar_mano_obra(self):
        if(isinstance(self.mano_obra.dato, int) or isinstance(self.mano_obra.dato, float) or (isinstance(self.mano_obra.dato, str) and self.mano_obra.dato.isdigit())):
            mano_obra, _ = ManoObra.get_or_create(dato=int(self.mano_obra.dato) + int(self.input_float(f"Ingrese el valor a sumar a la mano de obra original ({self.mano_obra.dato}): ")))
            self.mano_obra = mano_obra
        else:
            mano_obra, _ = ManoObra.get_or_create(dato=self.input_float(f"El valor en la db de la mano de obra no es un numero ({self.mano_obra or None}), ingrese un valor numerico para actualizarlo: "))
            self.mano_obra = mano_obra
        self.save()
        db.commit()
        db.close()

    def finalizar_obra(self):
        etapa, _ = Etapa.get_or_create(tipo="Finalizada")
        self.etapa = etapa
        self.porcentaje_avance = 100
        self.save()
        db.commit()
        db.close()

    def rescindir_obra(self):
        etapa, _ = Etapa.get_or_create(tipo="Rescindida")
        self.etapa = etapa
        self.save()
        db.commit()
        db.close()

class EmpresaContratista(BaseModel):
        id = AutoField()
        obra = ForeignKeyField(Obra, backref="obra", on_delete="CASCADE")
        cuit = CharField(null=True)
        class Meta:
            indexes = (
                (('obra', 'cuit'), True),
            )
