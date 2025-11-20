from peewee import *
from gestionar_obras import GestionarObra
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

def obtenerAcumColumna(nombreColumna: str):
    GestionarObra.conectar_db()
    campo = getattr(Obra, nombreColumna)

    query = (
        Obra
            .select(campo, fn.COUNT(Obra.id).alias('total'))
            .group_by(campo)
            .order_by(fn.COUNT(Obra.id).desc())
    )

    return([(fila.__data__[nombreColumna], fila.total) for fila in query])


def ultimasCincoObras():
    GestionarObra.conectar_db()
    print("Obra exists?", Obra.table_exists())
    ultimos_cinco = Obra.select().order_by(Obra.id.desc()).limit(5)

    return ultimos_cinco

def obtenerRegistro(model, **filters):
    GestionarObra.conectar_db()
    obra = Obra.get_or_none(**filters)
    if obra is None:
        return None

    data = {
        "id": str(obra.id),
        "nombre": obra.nombre,
        "expediente": obra.expediente,
        "descripcion": obra.descripcion,
        "monto": obra.monto,
        "direccion": obra.direccion,
        "latitud": obra.latitud,
        "longitud": obra.longitud,
        "fecha_inicio": obra.fecha_inicio,
        "fecha_fin_inicial": obra.fecha_fin_inicial,
        "plazo_meses": obra.plazo_meses,
        "porcentaje_avance": obra.porcentaje_avance,
        "imagen_1": obra.imagen_1,
        "imagen_2": obra.imagen_2,
        "imagen_3": obra.imagen_3,
        "imagen_4": obra.imagen_4,
        "licitacion_anio": obra.licitacion_anio,
        "nro_contratacion": obra.nro_contratacion,
        "beneficiarios": obra.beneficiarios,
        "compromiso": obra.compromiso,
        "destacada": obra.destacada,
        "ba_elige": obra.ba_elige,
        "link_interno": obra.link_interno,
        "pliego_descarga": obra.pliego_descarga,
        "estudio_ambiental_descarga": obra.estudio_ambiental_descarga,
    }

    data["entorno"] = {
        "id": str(obra.entorno.id),
        "tipo": obra.entorno.tipo,
    } if obra.entorno is not None else {}

    data["etapa"] = {
        "id": str(obra.etapa.id),
        "tipo": obra.etapa.tipo,
    } if obra.etapa is not None else {}

    data["tipo"] = {
        "id": str(obra.tipo.id),
        "tipo": obra.tipo.tipo,
    } if obra.tipo is not None else {}

    data["area_responsable"] = {
        "id": str(obra.area_responsable.id),
        "nombre": obra.area_responsable.nombre,
    } if obra.area_responsable is not None else {}

    data["barrio"] = {
        "id": str(obra.barrio.id),
        "nombre": obra.barrio.nombre,
        "comuna": obra.barrio.comuna,
    } if obra.barrio is not None else {}

    data["licitacion_oferta_empresa"] = {
        "id": str(obra.licitacion_oferta_empresa.id),
        "razon_social": obra.licitacion_oferta_empresa.razon_social,
    } if obra.licitacion_oferta_empresa is not None else {}

    data["tipo_contratacion"] = {
        "id": str(obra.tipo_contratacion.id),
        "tipo": obra.tipo_contratacion.tipo,
    } if obra.tipo_contratacion is not None else {}

    data["mano_obra"] = {
        "id": str(obra.mano_obra.id),
        "dato": obra.mano_obra.dato,
    } if obra.mano_obra is not None else {}

    data["financiamiento"] = {
        "id": str(obra.financiamiento.id),
        "nombre": obra.financiamiento.nombre,
    } if obra.financiamiento is not None else {}

    data["empresas_contratistas"] = [
        {
            "id": str(ec.id),
            "cuit": ec.cuit,
        }
        for ec in obra.obra
    ]

    # ------------------------------
    # 🔄 Convertir todos los None a texto ("")
    # ------------------------------
    def reemplazar_none(valor):
        if isinstance(valor, dict):
            return {k: ("" if v is None else reemplazar_none(v)) for k, v in valor.items()}
        if isinstance(valor, list):
            return [reemplazar_none(v) for v in valor]
        return "" if valor is None else valor

    data = reemplazar_none(data)

    return data



def obtenerValoresTabla(modelo, **filters):
    GestionarObra.conectar_db()

    res = modelo.get_or_none(**filters)
    return res.descripcion

    # resultados = {}
    
    # for campo in modelo._meta.fields.values():
    #     query = (
    #         modelo
    #         .select(campo, fn.COUNT(modelo.id).alias("total"))
    #         .group_by(campo)
    #     )
    #     resultados[campo.name] = list(query)
    
    # return resultados
