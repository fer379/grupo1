Tenés razón en que la consigna es medio contradictoria, así que vamos por partes 😊

## 1. ¿Qué *parece* que quiso el profe?

Te dice:

* *“Crear la clase abstracta GestionarObra…”*
* Pero después: *“Se deben crear nuevas instancias de Obra invocando al método de clase GestionarObra.nueva_obra()”*

Eso suena a que **quiere que llames directamente a los métodos de GestionarObra sin instanciarla**, algo así:

```python
from gestionar_obras import GestionarObra

def main():
    GestionarObra.extraer_datos()
    GestionarObra.conectar_db()
    GestionarObra.mapear_orm()
    GestionarObra.limpiar_datos()
    GestionarObra.cargar_datos()

    obra1 = GestionarObra.nueva_obra()
    obra2 = GestionarObra.nueva_obra()

    GestionarObra.obtener_indicadores()
```

Es decir, se usa como **“clase gestora/utility” con métodos de clase**, no creando objetos de GestionarObra. En muchos trabajos prácticos llaman a eso "clase abstracta" solo porque *no se instancia*, aunque técnicamente en Python no uses `ABC`.

En ese enfoque, podrías hacer algo así:

```python
# gestionar_obras.py
import pandas as pd
from peewee import SqliteDatabase
from modelo_orm import Obra, Etapa, TipoObra, AreaResponsable, Barrio, FuenteFinanciamiento, Empresa, TipoContratacion

class GestionarObra:
    db = SqliteDatabase("obras_urbanas.db")
    df_obras = None

    @classmethod
    def extraer_datos(cls):
        cls.df_obras = pd.read_csv("observatorio-de-obras-urbanas.csv", sep=';')

    @classmethod
    def conectar_db(cls):
        cls.db.connect()

    @classmethod
    def mapear_orm(cls):
        cls.db.create_tables([Obra, Etapa, TipoObra, AreaResponsable, Barrio,
                              FuenteFinanciamiento, Empresa, TipoContratacion])

    @classmethod
    def limpiar_datos(cls):
        cls.df_obras = cls.df_obras.dropna(subset=["columna_importante"])

    @classmethod
    def cargar_datos(cls):
        for _, row in cls.df_obras.iterrows():
            # acá haces los create() de las tablas relacionadas y de Obra
            ...

    @classmethod
    def nueva_obra(cls):
        # pedir datos por input(), buscar FKs en la BD, crear Obra, save() y devolverla
        ...

    @classmethod
    def obtener_indicadores(cls):
        # queries ORM con peewee
        ...
```

Acá **no la instanciás nunca**, solo usás sus métodos de clase. Eso encaja perfecto con la forma en que la consigna dice: *“invocar al método de clase GestionarObra.nueva_obra()”*.

---

## 2. ¿Y qué pasa con que sea “abstracta”?

Si quisieras ser más purista con el concepto de clase abstracta (usando `abc.ABC` y `@abstractmethod`), ahí sí deberías:

1. Declarar `GestionarObra` como abstracta.
2. Hacer una subclase concreta, por ejemplo `GestorObrasBA`, que implemente los métodos.
3. Usar **la subclase** en el `main`, no la clase abstracta.

Algo así:

```python
from abc import ABC, abstractmethod

class GestionarObra(ABC):

    @classmethod
    @abstractmethod
    def extraer_datos(cls):
        ...

    @classmethod
    @abstractmethod
    def conectar_db(cls):
        ...
```

Y luego:

```python
class GestorObrasBA(GestionarObra):
    db = SqliteDatabase("obras_urbanas.db")
    df_obras = None

    @classmethod
    def extraer_datos(cls):
        ...

    @classmethod
    def conectar_db(cls):
        ...
```

Y en tu script principal:

```python
from gestionar_obras import GestorObrasBA

def main():
    GestorObrasBA.extraer_datos()
    ...
```

**Peeero** la consigna nunca menciona una subclase ni un nombre concreto, y sí menciona explícitamente llamar a `GestionarObra.nueva_obra()`. Eso es una pista fuerte de que el/la profe **no espera** que armes una jerarquía de herencia real, sino que:

* Definas `GestionarObra` como “abstracta de facto” (no instanciable en la práctica).
* La uses directamente con métodos de clase.

---

## 3. Entonces… ¿cómo la usaría yo para el TP?

La opción más simple, totalmente alineada con el enunciado:

* **No uses `ABC` ni `@abstractmethod`** (a menos que te lo exijan explícitamente).
* Hacé que `GestionarObra`:

  * Tenga atributos de clase compartidos (`db`, `df_obras`, etc.).
  * Tenga todos esos métodos como `@classmethod`.
* En tu `main.py` o similar:

```python
from gestionar_obras import GestionarObra

if __name__ == "__main__":
    GestionarObra.extraer_datos()
    GestionarObra.conectar_db()
    GestionarObra.mapear_orm()
    GestionarObra.limpiar_datos()
    GestionarObra.cargar_datos()

    obra1 = GestionarObra.nueva_obra()
    obra2 = GestionarObra.nueva_obra()

    # hacer pasar a obra1 y obra2 por las etapas usando los métodos de instancia de Obra
    # obra1.nuevo_proyecto(); obra1.save(); etc.

    GestionarObra.obtener_indicadores()
```

Si querés, en un comentario podés aclarar algo tipo:

```python
# Nota: esta clase se considera "abstracta" en el sentido de que no se instancia,
# sólo se usan sus métodos de clase como interfaz de gestión de obras.
```

---

Si querés, en otro mensaje te puedo ayudar a bosquejar el modelo ORM (`modelo_orm.py`) con las tablas típicas (Obra, TipoObra, Etapa, Empresa, etc.) y cómo engancharlo con `GestionarObra`.
