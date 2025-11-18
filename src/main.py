from gestionar_obras import Gestion

def main():
    g = Gestion()

    print("\n=== 1) Conectando base de datos ===")
    g.conectar_db()

    print("\n=== 2) Extrayendo datos del CSV ===")
    g.extraer_datos()

    print("\n=== 3) Limpiando datos ===")
    g.limpiar_datos()

    print("\n=== 4) Creando tablas ORM ===")
    g.mapear_orm()

    print("\n=== 5) Cargando datos en la base ===")
    g.cargar_datos()

    print("\n🎉 PROCESO COMPLETO — Todo listo!\n")

if __name__ == "__main__":
    main()
