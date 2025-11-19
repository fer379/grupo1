from gestionar_obras import GestionarObra
from utils import ultimasCincoObras

def main():

    print("\n Conectando base de datos ===")
    GestionarObra.conectar_db()

    print("\n Extrayendo datos del CSV ===")
    GestionarObra.extraer_datos()

    print("\n Limpiando datos ===")
    df = GestionarObra.limpiar_datos()

    print(df["monto_contrato"].unique)


    print("\n Creando tablas ORM ===")
    GestionarObra.mapear_orm()

    print("\n Cargando datos en la base ===")
    GestionarObra.cargar_datos()

    # GestionarObra.obtenerDf()
    # GestionarObra.extraer_datos()

    # print("Ultimos 5 filas de la base de datos:\n")
    
    # cinco = ultimasCincoObras()
    # for row in cinco:
    #     print(row.expediente)

if __name__ == "__main__":
    main()
