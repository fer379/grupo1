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
            EmpresaContratista,
            db
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

    Obra.delete().where(Obra.nombre == 'nueva obra 1').execute()
    Obra.delete().where(Obra.nombre == 'nueva obra 2').execute()
    db.commit()

    print("\n Crea una instancia de obra ===")
    obra1 = GestionarObra.nueva_obra()
    print("\n Resultado: \n ===")
    print(obtenerRegistro(Obra, nombre = 'nueva obra 1'))


    # print("\n Nuevo proyecto ===")
    # obra1.nuevo_proyecto()
    # print("\n Resultado: \n ===")
    # print(obtenerRegistro(Obra, nombre = 'nueva obra 1'))

    # print("\n Iniciar contratacion ===")
    # obra1.iniciar_contratacion()
    # print("\n Resultado: \n ===")
    # print(obtenerRegistro(Obra, nombre = 'nueva obra 1'))

    # print("\n Adjudicar obra ===")
    # obra1.adjudicar_obra()
    # print("\n Resultado: \n ===")
    # print(obtenerRegistro(Obra, nombre = 'nueva obra 1'))

    print("\n Iniciar obra ===")
    obra1.iniciar_obra()
    print("\n Resultado: \n ===")
    print(obtenerRegistro(Obra, nombre = 'nueva obra 1'))

    print("\n Actualizar porcentaje de avance de la obra ===")
    obra1.actualizar_porcentaje_avance()
    print("\n Resultado: \n ===")
    print(obtenerRegistro(Obra, nombre = 'nueva obra 1'))
    
    print("\n Incrementar plazo de obra ===")
    obra1.incrementar_plazo()
    print("\n Resultado: \n ===")
    print(obtenerRegistro(Obra, nombre = 'nueva obra 1'))

    print("\n Incrementar mano de obra de obra ===")
    obra1.incrementar_mano_obra()
    print("\n Resultado: \n ===")
    print(obtenerRegistro(Obra, nombre = 'nueva obra 1'))

    print("\n Finalizar obra resultado: ===")
    obra1.finalizar_obra()
    print("\n Resultado: \n ===")
    print(obtenerRegistro(Obra, nombre = 'nueva obra 1'))

    print("\n Rescindir obra resultado: ===")
    obra1.rescindir_obra()
    print(obtenerRegistro(Obra, nombre = 'nueva obra 1'))    


    print("\n Crea una instancia de obra ===")
    obra2 = GestionarObra.nueva_obra()
    print("\n Resultado: \n ===")
    print(obtenerRegistro(Obra, nombre = 'nueva obra 2'))


    print("\n Nuevo proyecto ===")
    obra2.nuevo_proyecto()
    print("\n Resultado: \n ===")
    print(obtenerRegistro(Obra, nombre = 'nueva obra 2'))

    print("\n Iniciar contratacion ===")
    obra2.iniciar_contratacion()
    print("\n Resultado: \n ===")
    print(obtenerRegistro(Obra, nombre = 'nueva obra 2'))

    print("\n Adjudicar obra ===")
    obra2.adjudicar_obra()
    print("\n Resultado: \n ===")
    print(obtenerRegistro(Obra, nombre = 'nueva obra 2'))

    print("\n Iniciar obra ===")
    obra2.iniciar_obra()
    print("\n Resultado: \n ===")
    print(obtenerRegistro(Obra, nombre = 'nueva obra 2'))

    print("\n Actualizar porcentaje de avance de la obra ===")
    obra2.actualizar_porcentaje_avance()
    print("\n Resultado: \n ===")
    print(obtenerRegistro(Obra, nombre = 'nueva obra 2'))
    
    print("\n Incrementar plazo de obra ===")
    obra2.incrementar_plazo()
    print("\n Resultado: \n ===")
    print(obtenerRegistro(Obra, nombre = 'nueva obra 2'))

    print("\n Incrementar mano de obra de obra ===")
    obra2.incrementar_mano_obra()
    print("\n Resultado: \n ===")
    print(obtenerRegistro(Obra, nombre = 'nueva obra 2'))

    print("\n Finalizar obra resultado: ===")
    obra2.finalizar_obra()
    print("\n Resultado: \n ===")
    print(obtenerRegistro(Obra, nombre = 'nueva obra 2'))

    print("\n Rescindir obra resultado: ===")
    obra2.rescindir_obra()
    print(obtenerRegistro(Obra, nombre = 'nueva obra 2'))    


if __name__ == "__main__":
    main()
