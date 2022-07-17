
import pathlib
from os import path
import json


class Auxiliar():

    def __init__(self):
        self.CATEGORIA_MENU = ["entrantes", "carnes",
                               "pescados", "postres", "bebidas"]
        self.DIAS_SEMANA = ["lunes", "martes", "miercoles",
                            "jueves", "viernes", "sabado", "domingo"]

        data_path = "/app/actions"
        if not path.exists(data_path):
            data_path = "./actions"
        self.data_path = data_path

        self.NAMES = pathlib.Path(
            data_path+"/data/diccionarios/nombres.txt").read_text().split("\n")
        self.MALSONANTES = pathlib.Path(
            data_path+"/data/diccionarios/malsonante.txt").read_text().split("\n")

        self.horario = self.get_data_generic(
            data_path+"/data/menu/horario.json")
        self.mesas = self.get_data_generic(data_path+"/data/tables/mesas.json")
        self.horas = self.get_data_generic(data_path+"/data/tables/horas.json")

    def get_data_generic(self, path):
        f = open(pathlib.Path(path))
        data = json.load(f)
        f.close()
        return data

    def get_dias_semana(self):
        return self.DIAS_SEMANA

    def get_categorias_menu(self):
        return self.CATEGORIA_MENU

    def get_names(self):
        return self.NAMES

    def get_malsonantes(self):
        return self.MALSONANTES

    def get_horario(self):
        return self.horario

    def get_mesas(self):
        return self.mesas

    def get_horas(self):
        return self.horas

    def get_data_path(self):
        return self.data_path
