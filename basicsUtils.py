import re
import os # Módulo para el control del sistema operativo cliente.
import json # Importamos esta librería para poder obtener los datos de configuración de config.json.

with open("config.json", "r") as jsonfile: # Importamos los datos generales de configuración. Con esto cambiando los datos en un único lugar se adaptará en todo el proyecto.
    config = json.load(jsonfile)

def checkEmail(email):
    return re.compile(r'^[\w\.-]+@[a-zA-Z0-9\.-]+\.[a-zA-Z]{2,}$').match(email)

class StorageValuesConstructor: # Usaremos este sistema de caché/storage ya que el nativo de flet se resetea al reiniciar la app. Este lo usaremos para guardar configuraciones.
    def __init__(self):
        self.file_path = os.path.join(os.getenv('APPDATA'), f"{config["app"]["name"].replace(" ", "_")}_storage_values.json")
        self.data = {}
        # Cargar datos desde el archivo si existe.
        if os.path.exists(self.file_path):
            with open(self.file_path, 'r') as file:
                self.data = json.load(file)
    def set(self, key, value):
        self.data[key] = value
        self.save_data()
    def get(self, key):
        return self.data.get(key)
    def contains_key(self, key):
        return key in self.data
    def remove(self, key):
        if key in self.data:
            del self.data[key]
            self.save_data()
    def save_data(self):
        with open(self.file_path, 'w') as file:
            json.dump(self.data, file)
StorageValues = StorageValuesConstructor()