from gestionar_obras import GestionarObra
from utils import ultimasCincoObras, obtenerAcumColumna, obtenerRegistro, obtenerValoresTabla
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

def main():

    # print("\n Conectando base de datos ===")
    GestionarObra.conectar_db()

    # print("\n Extrayendo datos del CSV ===")
    # df = GestionarObra.extraer_datos()
    
    # print("\n Limpiando datos ===")
    # df = GestionarObra.limpiar_datos()

    # print("\n Creando tablas ORM ===")
    # GestionarObra.mapear_orm()

    # print("\n Cargando datos en la base ===")
    # GestionarObra.cargar_datos()


    # print("\n Obteniendo un registro ===")
    # print(obtenerRegistro(Obra, compromiso=True))

    # print("\n Obteniendo datos de tabla ===")
    # print(obtenerValoresTabla(Obra, compromiso=True))

    # GestionarObra.obtenerDf()
    # GestionarObra.extraer_datos()

    # print(GestionarObra.nueva_obra())
    # print(obtenerRegistro(Obra, id = 1664))


if __name__ == "__main__":
    main()
