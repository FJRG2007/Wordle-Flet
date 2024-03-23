"""
* Curso: Curso de Programación con Python.
* Copyright: Libre de copyright con uso limitado a la institución certificadora: TOKIO NEW TECHNOLOGY SCHOOL.
* Autor: Javier Romero González (FJRG2007)
* Portafolio: https://tpeoficial.com/fjrg2007/
* Más información: ./README.md
"""

# Este proyecto estará comentado en castellano para facilitar su lectura a Tokio School.
# Todo en el proyecto estará muy detallado, por lo que no se medirá un rendimiento alto para este programa.
# En la versión ejecutable para sistemas Windows, el proyecto ya se encuentra optimiziado al ser compilado.

# Importaciones internas del proyecto.
import db # Módulo con la configuración de conexión a la base de datos.
import components # Importamos los componentes que mostraremos en el front-end.
import basicsUtils # Módulo con las funciones más habituales en el proyecto.
# Importaciones de librerías externas al proyecto.
import flet as ft # Framework usado para crear el front-end del proyecto.

def main(page: ft.Page): # Definimos la función que mostrará la interfaz al usuario usando Flet.
    page.title = f"{basicsUtils.config["app"]["name"]} — A Tokio School by {basicsUtils.config["app"]["author"]}" # Definimos el título de la ventana para el usuario.
    page.vertical_alignment = ft.MainAxisAlignment.CENTER # Centramos los elementos en la ventana verticalmente.
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER # Centramos los elementos en la ventana horizontalmente.
    page.theme_mode = ft.ThemeMode.DARK # Por defecto se adapta al color del sistema operativo, pero lo estableceremos en oscuro.
    page.window_resizable = False # Establecemos la configuración de la ventana para que no se pueda reescalar.
    page.window_maximized = True # Al establecer esta propiedad forzamos la ventana a maximizarse.
    page.add(
        components.Access(page)
    )

# Acciones a ejecutar al iniciar el script.
if __name__ == "__main__":
    db.Base.metadata.create_all(db.engine) # Creación de la base de datos.
    ft.app(target=main) # Inicialización del la app generada con Flet.