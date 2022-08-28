from rasa_sdk.interfaces import Action
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


class Opciones(Action):
    def name(self):
        return "Opciones"

    def run(self, dispatcher, tracker, domain):
        print("Opciones")

        buttons = []
        buttons = [
            {'title': 'Opciones', 'payload': '/opciones'},
            {'title': 'Horario', 'payload': '/horario'},
            {'title': 'Consultar carta', 'payload': '/menu_completo'}
        ]

        if tracker.get_slot("first_name_set"):
            buttons.append(
                {"title": "Olvida mi nombre", "payload": "/identificar_borrar"})
        else:
            buttons.append({"title": "Identificarme",
                           "payload": "/identificar"})

        if tracker.get_slot("menu_establecido") or tracker.get_slot("menu_hay_plato"):
            if tracker.get_slot("menu_plato_1_id") is None or tracker.get_slot("menu_plato_2_id") is None or tracker.get_slot("menu_plato_3_id") is None or tracker.get_slot("menu_bebida_id") is None:
                buttons.append(
                    {"title": "Elegir plato", "payload": "/establecer_menu"})
            buttons.append(
                {"title": "Borrar todo el menu", "payload": "/menu_borra_todo"})
            buttons.append(
                {"title": "Borrar plato", "payload": "/menu_borra_plato"})
            buttons.append({"title": "Consultar mi menu",
                           "payload": "/menu_usuario"})
            buttons.append({"title": "Guardar mi menu",
                           "payload": "/menu_finalizar"})
        else:
            buttons.append({"title": "Establecer menu",
                           "payload": "/establecer_menu"})

        if tracker.get_slot("reserva_dia") or tracker.get_slot("reserva_hora") or tracker.get_slot("reserva_comensales") or tracker.get_slot("reserva_completa") or tracker.get_slot("reserva_realizada"):
            buttons.append({"title": "Borrar reserva",
                           "payload": "/reserva_borrar_mesa"})
            buttons.append({"title": "Guardar mi reserva",
                           "payload": "/reserva_finalizar"})
            buttons.append({"title": "Consultar mi reserva",
                           "payload": "/reserva_usuario"})
        else:
            buttons.append(
                {"title": "Realizar reserva de mesa", "payload": "/reservar"})

        dispatcher.utter_message(
            text=f'Estas son las opciones que puedes realizar ahora', buttons=buttons, button_type="vertical")
        return ""
