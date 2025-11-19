from gestionar_obras import GestionarObra
from utils import ultimasCincoObras, obtenerAcumColumna

def main():

    print("\n Conectando base de datos ===")
    GestionarObra.conectar_db()

    # print("\n Extrayendo datos del CSV ===")
    df = GestionarObra.extraer_datos()

    # print(df['lat'].dtype)
    # print(df.loc[444,"lat"])
    # print(type(df.loc[444,"lat"]))


    print("\n Limpiando datos ===")
    df = GestionarObra.limpiar_datos()

    # print(df.loc[445,"lat"])
    # print(df['lat'].dtype)


    # print("\n Creando tablas ORM ===")
    # GestionarObra.mapear_orm()

    # print("\n Cargando datos en la base ===")
    # GestionarObra.cargar_datos()

    # GestionarObra.obtenerDf()
    # GestionarObra.extraer_datos()

    # res = obtenerAcumColumna('expediente')
    # for exp in res:
    #     if exp[1] != 1:
    #         print(exp)

if __name__ == "__main__":
    main()
