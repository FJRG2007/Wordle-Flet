# Importaciones internas del proyecto.
import models # Módulo con los modelos a utilizar en la base de datos.
import basicsUtils # Módulo con las funciones más habituales en el proyecto.
# Importaciones de librerías externas al proyecto.
import flet as ft # Framework usado para crear el front-end del proyecto.
import bcrypt # Importamos bcrypt para hashear ("encriptar") la contraseña de los usuarios y agregar algo de seguridad aunque sea un proyecto simple.
import db # Módulo con la configuración de conexión a la base de datos.
import os # Módulo para el control del sistema operativo cliente.
from random import choice
from time import sleep
words = [] # Definimos el array para almacenar las palabras.
with open(os.path.join("database", "words.conf"), "r", encoding="utf-8") as f:
    for i in f:
        words.append(i.strip()) # Agregamos todas las palabras al array.

ROWS = [] # Definimos un array vació para los cubos de cada letra.

def store_row_in_list(function):
    def wrapper(*args, **kwargs):
        res = function(*args, **kwargs)
        ROWS.append(res)
        return res

    return wrapper

class GameErrorHandler(ft.UserControl): # Sistema para mostrar un error en la interfaz.
    def __init__(self):
        super().__init__()

    @store_row_in_list
    def set_error_text(self):
        return ft.Text(
            size=11,
            weight="bold",
        )

    def build(self):
        return ft.Row(alignment=ft.MainAxisAlignment.CENTER, controls=[self.set_error_text()])

class Access(ft.UserControl): # Definimos la clase/grupo que contendrá los elementos/componentes de la ventana/interfaz de acceso.
    def __init__(self, page: ft.Page):
        super().__init__()
        self.page = page # Guardamos la página como atributo para poder acceder a ella en el método de construcción.
    def login_btn(self, e): # Definimos la función que permitirá al usuario iniciar sesión si es que su cuenta ya existe.
        if not basicsUtils.checkEmail(self.login_email.value):
            self.login_email.error_text = "Error: Introduce un email inválido." # Generamos un error si el email no es válido.
            self.update() # Usamos esta función para actualizar la interfaz.
            return self.update() # Usamos esta función para actualizar la interfaz.
        user = db.session.query(models.User).filter_by(email=self.login_email.value).first()
        if user and bcrypt.checkpw(self.login_password.value.encode('utf-8'), user.password):
            self.page.session.set("user_session", user.id) # Guardamos la sesión del usuario almacenando su ID.
            self.page.clean() # Limipiamos/eliminamos todos los componentes de la página/interfaz.
            self.page.add(InterfaceBase(self.page)) # Agregamos la interfaz base.
            return self.update() # Actualizamos la página/interfaz.
        else:
            self.login_log.color = "red"
            self.login_log.value = "Error: Credenciales incorrectas." # Si la contraseña no es válida devolvemos un mensaje de error. Nota: No decimos que la contraseña es incorrecta para evitar que un posible atacante confirme que el email ya está registrado o si la cuenta no existe devolvemos un mensaje de error.
            return self.update()
    def register_btn(self, e): # Definimos la función que permitirá al usuario crear una nueva cuenta si es que aún no existe.
        if not basicsUtils.checkEmail(self.register_email.value):
            self.register_email.error_text = "Error: Introduce un email inválido."
            return self.update()
        if db.session.query(models.User).filter_by(email=self.register_email.value).first(): # Verificamos que una cuenta con este email no exista en la base de datos.
            self.register_email.error_text = "Error: El email ya está registrado."
            return self.update()
        if self.register_password.value != self.register_confirm_password.value: # Verificamos que ambas contraseñas son idénticas.
            self.register_confirm_password.error_text = "Error: Las contraseñas no coinciden." # Si las contraseñas no coinciden devolvemos un mensaje de error.
            return self.update()
        db.session.add(models.User(name=self.register_name.value, email=self.register_email.value, password=bcrypt.hashpw(self.register_password.value.encode('utf-8'), bcrypt.gensalt()))) # Agregamos el nuevo usuario a la base de datos. Además hasheamos ("encriptar/proteger") la contraseña del usuario.
        db.session.commit() # Guardamos los cambios en la base de datos.
        self.login_email.autofocus = True
        self.login_log.color = "green"
        self.register_log.value = "Usuario registrado con éxito." # Devolvemos un mensaje de éxito si todo ha sido correcto.
        return self.update()
    def build(self): # En esta función con nombre por defecto de Flet, construimos la interfaz con los componentes.
        # Componentes necesarios para iniciar sesión.
        self.login_email = ft.TextField(label="Email", prefix_icon = ft.icons.EMAIL)
        self.login_password = ft.TextField(label="Contraseña", prefix_icon = ft.icons.LOCK, password = True)
        self.login_log = ft.Text("")
        # Componentes necesarios para registrarse/crear una cuenta.
        self.register_name = ft.TextField(label="Nombre", prefix_icon = ft.icons.PERSON)
        self.register_email = ft.TextField(label="Email", prefix_icon = ft.icons.EMAIL)
        self.register_password = ft.TextField(label="Contraseña", prefix_icon = ft.icons.LOCK, password = True)
        self.register_confirm_password = ft.TextField(label="Contraseña", prefix_icon = ft.icons.LOCK, password = True)
        self.register_log = ft.Text("")
        # Otros parámetros adaptativos.
        if db.session.query(models.User).count() >= 1: # Aquí verificamos si ya existe una cuenta en la base de datos.
            self.login_email.autofocus = True # Si existe hacemos autofocus para iniciar sesión y agilizar el proceso.
        else:
            self.register_name.autofocus = True # Si no existe hacemos autofocus para crear una cuenta y nuevamente agilizar el proceso.
        return ft.Row(
            # width=page.window_width,
            spacing=ft.alignment.center,
            alignment=ft.MainAxisAlignment.SPACE_AROUND,
            controls=[
                ft.Column([
                    ft.Text(value="Iniciar sesión", size=18, weight=ft.FontWeight.W_100),
                    self.login_email,
                    self.login_password,
                    ft.ElevatedButton("Acceder", on_click=self.login_btn),
                    self.login_log
                ]),
                ft.Column([
                ft.Text(value="Crear cuenta", size=18, weight=ft.FontWeight.W_100),
                    self.register_name,
                    self.register_email,
                    self.register_password,
                    self.register_confirm_password,
                    ft.ElevatedButton("Crear cuenta", on_click=self.register_btn),
                    self.register_log
                ])
        ])

class GameInputField(ft.UserControl): # Esta clase/componente hará referencia al input del usuario para que escriba la palabra.
    def __init__(self, word: str, modal):
        self.line = 0
        self.guess = 5
        self.word = word
        self.modal = modal
        super().__init__()

    def get_letters(self, e):
        word = e.control.value
        is_word = e.control.value
        if len(word) == 5:
            if word in words:
                word = [*word]  # Convertimos los caracteres en una lista para poder iterar correctamente sobre ellos.

                if is_word == self.word:
                    ROWS[6].value = f"¡CORRECTO! La palabra es \"{self.word.upper()}\""
                    self.modal.open = True
                    self.modal.update()
                    ROWS[6].update()
                    user = db.session.query(models.User).filter_by(id=self.page.session.get("user_session")).first()
                    if user: # Verificamos que la sesión sea válida.
                        user.wins += 1 # Sumamos una victoria para el juagdor actual.
                        db.session.add(user) # Definimos el usuario a actualizar.
                        db.session.commit() # Guardamos los cambios en la base de datos.

                elif self.line > 5 or self.guess < 1:
                    ROWS[
                        6
                    ].value = f"Te quedaste sin intentos, la palabra era \"{self.word.upper()}\"."
                    self.modal.open = True
                    self.modal.update()
                    ROWS[6].update()

                for index, box in enumerate(ROWS[self.line].controls[:]):
                    if word[index] in self.word:
                        if word[index] == self.word[index]:
                            box.content.value = word[index].upper()
                            box.content.offset = ft.transform.Offset(0, 0)
                            box.content.opacity = 1
                            box.bgcolor = "green900"
                            box.update()
                            sleep(0.4)
                        else:
                            box.content.value = word[index].upper()
                            box.content.offset = ft.transform.Offset(0, 0)
                            box.content.opacity = 1
                            box.bgcolor = "#b59e38"
                            box.update()
                            sleep(0.4)
                    else:
                        box.content.value = word[index].upper()
                        box.content.offset = ft.transform.Offset(0, 0)
                        box.content.opacity = 1
                        box.update()
                        sleep(0.4)

                self.line += 1
                self.guess -= 1

            else: # Si la palabra no existe dentro del diccionario, mostramos un error.
                ROWS[6].value = "Debe ser una palabra válida. Inténtelo de nuevo."
                ROWS[6].update()
        else: # Si la palanbra no tiene 5 letras/caracteres, mostramos un error.
            ROWS[6].value = "La palabra debe tener 5 letras. ¡Inténtalo de nuevo!"
            ROWS[6].update()

        e.control.value = ""
        e.control.update()

    def clear_error(self, e):
        ROWS[6].value = ""
        ROWS[6].update()

    def build(self):
        return ft.Row(
            spacing=20,
            alignment=ft.MainAxisAlignment.CENTER,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Container(
                    height=45,
                    width=250,
                    border=ft.border.all(0.5, ft.colors.WHITE24),
                    border_radius=6,
                    content=ft.Row(
                        alignment=ft.MainAxisAlignment.CENTER,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            ft.TextField(
                                border_color="transparent",
                                bgcolor="transparent",
                                height=20,
                                width=200,
                                text_size=12,
                                content_padding=3,
                                cursor_color="white",
                                cursor_width=1,
                                color="white",
                                hint_text="Escribe una palabra de 5 letras...",
                                text_align="center",
                                hint_style=ft.TextStyle(
                                    size=11,
                                ),
                                on_submit=lambda e: self.get_letters(e),
                                on_focus=lambda e: self.clear_error(e),
                            ),
                        ],
                    ),
                ),
            ],
        )

class GameGrid(ft.UserControl):
    def __init__(self):
        super().__init__()

    @store_row_in_list
    def create_single_row_grid(self):
        row = ft.Row(alignment=ft.MainAxisAlignment.CENTER)
        for __ in range(5):
            row.controls.append(
                ft.Container(
                    width=52,
                    height=52,
                    border=ft.border.all(0.5, "white24"),
                    alignment=ft.alignment.center,
                    clip_behavior=ft.ClipBehavior.HARD_EDGE,
                    animate=ft.animation.Animation(300, "decelerate"),
                    content=ft.Text(
                        size=20,
                        weight="bold",
                        opacity=0,
                        offset=ft.transform.Offset(0, 0.75),
                        animate_opacity=ft.animation.Animation(400, "decelerate"),
                        animate_offset=ft.animation.Animation(400, "decelerate"),
                    ),
                )
            )
        return row

    def build(self):
        return ft.Column(
            controls=[
                self.create_single_row_grid(),
                self.create_single_row_grid(),
                self.create_single_row_grid(),
                self.create_single_row_grid(),
                self.create_single_row_grid(),
                self.create_single_row_grid(),
            ],
        )



class InterfaceBase(ft.UserControl): # Definimos la clase/grupo que contendrá los elementos/componentes de la ventana/interfaz base (al iniciar sesión).
    def __init__(self, page: ft.Page):
        super().__init__()
        self.page = page # Guardamos la página como atributo para poder acceder a ella en el método de construcción.
    def build(self): # En esta función nuevamente con nombre por defecto de Flet, construimos la interfaz con los componentes.
        if not self.page.session.contains_key("user_session"): # Si no hay una sesión almacenada mostraremos la interfaz de acceso.
            self.page.add(Access(self.page)) # Agregamos la interfaz de acceso nuevamente.
            return self.update() # Actualizamos la página/interfaz.
        user = db.session.query(models.User).filter_by(id=self.page.session.get("user_session")).first()
        if user: # Verificamos que la sesión sea válida.
            def new_game(e):
                if hasattr(self, "modal"):
                    self.modal.open = False
                self.page.clean()
                self.page.add(InterfaceBase(self.page))
                return self.update()

            word = words # Obtenemos la lista de palabras en castellano.
            word = list(filter(lambda x: len(x) == 5 and '-' not in x, word)) # Seleccionamos una palabra con 5 letras/caracteres y sin giones ("-"), esto se debe ha que la lista de esta librería incluye palabras como "-ftp-".
            word = choice(word).lower() # Convertimos la palabra a minúscula.
            print(f"[TEST] Palabra seleccionada: {word}") # Mostramos la palabra seleccionada para facilitar el testeo a la administración de Tokio School.
            def exit(e):
                self.modal.open = False
                self.update()
                self.page.clean()
                self.page.add(Access(self.page))
                return self.update()
            self.modal = ft.AlertDialog( # Cuando la partida finaliza le preguntamos al usuario si quiere jugar nuevamente.
                modal=True,
                title=ft.Text("Partida finalizada"),
                content=ft.Text("¿Quiéres jugar de nuevo?"),
                actions=[
                    ft.TextButton("Nueva partida", on_click=new_game), # Reiniciamos la partida.
                    ft.TextButton("Salir", on_click=exit), # Enviamaos al usuario a la pantalla de acceso/login.
                ],
                actions_alignment=ft.MainAxisAlignment.END,
                on_dismiss=exit,
            )
            return [
                ft.Column(
                    alignment=ft.MainAxisAlignment.CENTER,
                    controls=[
                        self.modal,
                        ft.Row(
                            alignment=ft.MainAxisAlignment.CENTER,
                            controls=[ft.Text(basicsUtils.config["app"]["name"], size=25, weight="bold")], # Título.
                        ),
                        ft.Row(
                            alignment=ft.MainAxisAlignment.CENTER,
                            controls=[
                                ft.Text(
                                    f"¡Bienvenido {user.name}!", # Damos la bienvenida al usuario
                                    size=16,
                                    weight="bold",
                                    color=ft.colors.WHITE54,
                                )
                            ],
                        ),
                        ft.Row(
                            alignment=ft.MainAxisAlignment.CENTER,
                            controls=[
                                ft.Text(
                                    f"Victorias: {user.wins}",
                                    size=12,
                                    weight="bold",
                                    color=ft.colors.WHITE54,
                                )
                            ],
                        ),
                        ft.Row(
                            alignment=ft.MainAxisAlignment.CENTER,
                            controls=[
                                ft.Text(
                                    "Reglas del juego\n1. Verde: Letra y posición correctas.\n2. Amarillo: Letra correcta pero posición incorrecta.\n3. Negro: La letra no está en la palabra.",
                                    size=11,
                                    weight="bold",
                                    color=ft.colors.WHITE54,
                                )
                            ],
                        ),
                        ft.Divider(height=20, color="transparent"),
                        GameGrid(),
                        ft.Divider(height=10, color="transparent"),
                        GameInputField(word, self.modal),
                        ft.Divider(height=10, color="transparent"),
                        GameErrorHandler(),
                    ],
                )
            ]