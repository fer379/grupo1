from peewee import *
from modelo_orm import Obra
from gestionar_obras import GestionarObra

def obtenerAcumColumna(nombreColumna: str):
    GestionarObra.conectar_db()
    campo = getattr(Obra, nombreColumna)

    # Crear la consulta
    query = (
        Obra
            .select(campo, fn.COUNT(Obra.id).alias('total'))
            .group_by(campo)
            .order_by(fn.COUNT(Obra.id).desc())
    )

    # Retornar resultados en forma de lista de tuplas
    return([(fila.__data__[nombreColumna], fila.total) for fila in query])


def ultimasCincoObras():
    GestionarObra.conectar_db()
    print("Obra exists?", Obra.table_exists())
    ultimos_cinco = Obra.select().order_by(Obra.id.desc()).limit(5)

    return ultimos_cinco
