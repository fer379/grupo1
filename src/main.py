from gestionar_obras import GestionarObra
from utils import ultimasCincoObras, obtenerAcumColumna

def main():

    print("\n Conectando base de datos ===")
    GestionarObra.conectar_db()

    # print("\n Extrayendo datos del CSV ===")
    df = GestionarObra.extraer_datos()

    # print(df.loc[1211,"comuna"])
    # print(type(df.loc[1211,"comuna"]))


    print("\n Limpiando datos ===")
    df = GestionarObra.limpiar_datos()

    # print(df['monto_contrato'].value_counts(dropna=False)) 
    # print(df.loc[1211,"comuna"])
    # print(type(df.loc[1211,"comuna"]))


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
