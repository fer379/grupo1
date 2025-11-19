from peewee import *
from modelo_orm import Obra, db
from gestionar_obras import GestionarObra



def ultimasCincoObras():
    GestionarObra.conectar_db()
    print("Obra exists?", Obra.table_exists())
    ultimos_cinco = Obra.select().order_by(Obra.id.desc()).limit(5)

    return ultimos_cinco
