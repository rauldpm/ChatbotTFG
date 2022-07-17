from typing import Text, List, Any, Dict, Optional
from rasa_sdk.events import SlotSet
from rasa_sdk.interfaces import Action
from rasa_sdk.types import DomainDict
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk import Tracker, FormValidationAction
from os import path
import unidecode  # acentos
import datetime
import pathlib
import json
import re
import locale  # dias español
locale.setlocale(locale.LC_ALL, 'es_ES.utf8')


data_path = "/app/actions"
if not path.exists(data_path):
    data_path = "./actions"
names = pathlib.Path(
    data_path+"/data/diccionarios/nombres.txt").read_text().split("\n")
malsonantes = pathlib.Path(
    data_path+"/data/diccionarios/malsonante.txt").read_text().split("\n")

DIAS_SEMANA = ["lunes", "martes", "miercoles",
               "jueves", "viernes", "sabado", "domingo"]
CATEGORIA_MENU = ["entrantes", "carnes", "pescados", "postres", "bebidas"]


def get_data_generic(path):
    f = open(pathlib.Path(path))
    data = json.load(f)
    f.close()
    return data


horario = get_data_generic(data_path+"/data/menu/horario.json")
mesas = get_data_generic(data_path+"/data/tables/mesas.json")
horas = get_data_generic(data_path+"/data/tables/horas.json")


# ---------------------------------------------------------------------
# Identificacion Class
# ---------------------------------------------------------------------

class IdentificarBorrarUsername(Action):
    def name(self):
        return 'IdentificarBorrarUsername'

    def run(self, dispatcher, tracker, domain):
        print("IdentificarBorrarUsername")
        dispatcher.utter_message(
            text=f'He borrado tu nombre de usuario, recuerda que es necesario identificarte para terminar el proceso de reserva.')
        return [SlotSet("first_name", None), SlotSet("first_name_save", None), SlotSet("first_name_set", None), SlotSet("name_spelled_correctly", None)]


class ValidateNameForm(FormValidationAction):

    def name(self) -> Text:
        return "validate_name_form"

    async def required_slots(
        self, slots_mapped_in_domain: List[Text],
        dispatcher: CollectingDispatcher,
        tracker: Tracker, domain: DomainDict,
    ) -> Optional[List[Text]]:
        print("Required slots")

        first_name = tracker.get_slot("first_name")
        if first_name is not None:
            if first_name.lower() not in names:
                return ["name_spelled_correctly"] + slots_mapped_in_domain
        return slots_mapped_in_domain

    async def extract_name_spelled_correctly(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> Dict[Text, Any]:
        print("extract_name_spelled_correctly")
        first_name = tracker.get_slot("first_name")
        intent = tracker.get_intent_of_latest_message()
        if intent == "affirm":
            first_name = tracker.get_slot("first_name_save")
        if first_name != "/repetir_nombre":
            if len(first_name) < 3 or len(first_name) > 11:
                dispatcher.utter_message(
                    text=f"El nombre no cumple con los requisitos (minimo 3 letras y maximo 11)")
                return {"first_name": None, "name_spelled_correctly": False, "first_name_save": None}
        return {"name_spelled_correctly": tracker.get_intent_of_latest_message() == "affirm"}

    def validate_name_spelled_correctly(
        self, slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker, domain: DomainDict,
    ) -> Dict[Text, Any]:
        print("validate_name_spelled_correctly")

        if tracker.get_intent_of_latest_message() == "stop":
            return {"requested_slot": None, "first_name": None, "name_spelled_correctly": None, "first_name_set": None}

        intent = tracker.get_intent_of_latest_message()
        first_name = tracker.slots.get("first_name")
        first_name_save = tracker.slots.get("first_name_save")
        latest_message = tracker.latest_message['text']

        if first_name is not None:
            for string in malsonantes:
                if string in first_name:
                    dispatcher.utter_message(
                        "El nombre contiene una palabra no admitida: " + string + ". Por favor, utiliza otro nombre.")
                    return {"first_name": None, "name_spelled_correctly": None, "first_name_save": None}

        if (first_name_save is not None and intent == "affirm" and first_name_save != "/repetir_nombre"):
            names.append(first_name_save.lower())
            return {"first_name": first_name_save, "first_name_set": True, "first_name_save": None}

        elif (first_name_save is not None) and ((intent == "repetir_nombre") or (first_name == "/repetir_nombre")):
            if (first_name_save is not None and latest_message is not None and latest_message != first_name):
                return {"first_name": latest_message, "name_spelled_correctly": None, "first_name_save": None}
            if (first_name_save.lower() not in names and intent == "repetir_nombre" and first_name != "/repetir_nombre") or (intent == "deny"):
                buttons = [{'title': 'Si', 'payload': '/affirm'},
                           {'title': 'No', 'payload': '/repetir_nombre'}]
                dispatcher.utter_message(
                    "Mmm esta bien escrito tu nombre? Si no, escribe tu nombre de nuevo", buttons=buttons, button_type="vertical")
                return {"first_name": None, "name_spelled_correctly": None, "first_name_save": latest_message}
            return {"first_name": None, "name_spelled_correctly": False, "first_name_save": latest_message}
        if tracker.get_intent_of_latest_message() != "repetir_nombre" or intent == "repetir_nombre":
            if latest_message is not None and latest_message != tracker.get_slot("first_name") and intent != "affirm":
                return {"first_name": latest_message, "name_spelled_correctly": None}
            buttons = [{'title': 'Si', 'payload': '/affirm'},
                       {'title': 'No', 'payload': '/repetir_nombre'}]
            dispatcher.utter_message(
                "Mmm esta bien escrito tu nombre? Si no, escribe tu nombre de nuevo", buttons=buttons, button_type="vertical")

            return {"first_name": None, "name_spelled_correctly": None, "first_name_save": tracker.get_slot("first_name")}
        return {"first_name": tracker.get_slot("first_name"), "name_spelled_correctly": None}

    def validate_first_name(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        print("Validate first_name value")

        if tracker.get_intent_of_latest_message() == "stop":
            return {"requested_slot": None, "first_name": None, "name_spelled_correctly": None, "first_name_set": None}
        if slot_value is not None:
            if (len(slot_value) < 3 or len(slot_value) > 11) and (slot_value != "/repetir_nombre"):
                dispatcher.utter_message(
                    text=f"El nombre no cumple con los requisitos (minimo 3 letras y maximo 11)")
                return {"first_name": None, "name_spelled_correctly": False}
            else:
                return {"first_name": slot_value, "first_name_set": True}
        return {"first_name": None, "name_spelled_correctly": False}


# ---------------------------------------------------------------------
# Otros Class
# ---------------------------------------------------------------------


class HorarioGet(Action):
    def name(self):
        return 'HorarioGet'

    def run(self, dispatcher, tracker, domain):
        print("HorarioGet")
        intent = tracker.get_intent_of_latest_message()
        if intent == "horario" or intent == "apertura" or intent == "cierre":
            dispatcher.utter_message(response="utter_horario")
        message = ""
        if intent == "horario":
            for dia in DIAS_SEMANA:
                if horario["horario"][dia][0] == "cerrado" and horario["horario"][dia][1] == "cerrado":
                    message += dia.capitalize() + ": " + \
                        (horario["horario"][dia][0]).capitalize() + "." + "\n"
                else:
                    message += dia.capitalize() + ": " + \
                        horario["horario"][dia][0] + " - " + \
                        horario["horario"][dia][1] + "." + "\n"
        elif intent == "apertura" or intent == "cierre":
            value = 0 if intent == "apertura" else 1
            for dia in DIAS_SEMANA:
                if horario["horario"][dia][0] == "cerrado" and horario["horario"][dia][1] == "cerrado":
                    message += dia.capitalize() + ": " + \
                        (horario["horario"][dia][0]).capitalize() + "." + "\n"
                else:
                    message += dia.capitalize() + ": " + \
                        horario["horario"][dia][value] + "." + "\n"
        elif intent == "horario_concreto":
            dia = tracker.get_slot("dia")
            if dia is not None:
                dia = dia.lower()

                if dia == "hoy":
                    now = datetime.datetime.now()
                    dia = now.strftime("%A")
                elif dia == "mañana":
                    now = (datetime.datetime.now() +
                           datetime.timedelta(1)).strftime("%A")
                    dia = now
                elif dia == "pasado mañana":
                    now = (datetime.datetime.now() +
                           datetime.timedelta(2)).strftime("%A")
                    dia = now
                dia = unidecode.unidecode(dia)

            if dia not in DIAS_SEMANA:
                message = "Ese dia de la semana es incorrecto."
                dispatcher.utter_message(message)
            elif horario["horario"][dia][0] == "cerrado":
                message = "El " + dia + " estamos cerrados por descanso del personal."
            else:
                message = "El " + dia + " abrimos a las " + \
                    horario["horario"][dia][0] + " y cerramos a las " + \
                    horario["horario"][dia][1] + "."
        dispatcher.utter_message(message)
        return [SlotSet("dia", None)]


# ---------------------------------------------------------------------
# Menu Class
# ---------------------------------------------------------------------


class MenuBorrarPlato(Action):
    def name(self):
        return 'MenuBorrarPlato'

    def run(self, dispatcher, tracker, domain):
        print("MenuBorrarPlato")

        menu_plato_id = tracker.get_slot("menu_plato_id")
        menu_entrante_id = tracker.get_slot("menu_entrante_id")
        menu_carne_id = tracker.get_slot("menu_carne_id")
        menu_pescado_id = tracker.get_slot("menu_pescado_id")
        menu_postre_id = tracker.get_slot("menu_postre_id")
        menu_bebida_id = tracker.get_slot("menu_bebida_id")

        if menu_entrante_id is None and menu_carne_id is None and menu_pescado_id is None and menu_postre_id is None and menu_bebida_id is None:
            dispatcher.utter_message(text=f'')
            return ""

        if menu_plato_id is not None:
            menu_plato_id = menu_plato_id.upper()
            if menu_plato_id == menu_entrante_id:
                dispatcher.utter_message(
                    text=f'Se ha eliminado el plato entrante.')
                if menu_carne_id is None and menu_pescado_id is None and menu_postre_id is None and menu_bebida_id is None:
                    return [SlotSet("menu_establecido", False), SlotSet("menu_plato_categoria", None), SlotSet("menu_plato_id", None), SlotSet("menu_entrante_id", None), SlotSet("menu_entrante_nombre", None), SlotSet("menu_entrante_precio", None)]
                return [SlotSet("menu_plato_id", None), SlotSet("menu_plato_categoria", None), SlotSet("menu_entrante_id", None), SlotSet("menu_entrante_nombre", None), SlotSet("menu_entrante_precio", None)]
            elif menu_plato_id == menu_carne_id:
                dispatcher.utter_message(
                    text=f'Se ha eliminado el plato de carne.')
                if menu_entrante_id is None and menu_pescado_id is None and menu_postre_id is None and menu_bebida_id is None:
                    return [SlotSet("menu_establecido", False), SlotSet("menu_plato_categoria", None), SlotSet("menu_plato_id", None), SlotSet("menu_carne_id", None), SlotSet("menu_carne_nombre", None), SlotSet("menu_carne_precio", None)]
                return [SlotSet("menu_plato_id", None), SlotSet("menu_plato_categoria", None), SlotSet("menu_carne_id", None), SlotSet("menu_carne_nombre", None), SlotSet("menu_carne_precio", None)]
            elif menu_plato_id == menu_pescado_id:
                dispatcher.utter_message(
                    text=f'Se ha eliminado el plato de pescado.')
                if menu_carne_id is None and menu_entrante_id is None and menu_postre_id is None and menu_bebida_id is None:
                    return [SlotSet("menu_establecido", False), SlotSet("menu_plato_categoria", None), SlotSet("menu_plato_id", None), SlotSet("menu_pescado_id", None), SlotSet("menu_pescado_nombre", None), SlotSet("menu_pescado_precio", None)]
                return [SlotSet("menu_plato_id", None), SlotSet("menu_plato_categoria", None), SlotSet("menu_pescado_id", None), SlotSet("menu_pescado_nombre", None), SlotSet("menu_pescado_precio", None)]
            elif menu_plato_id == menu_postre_id:
                dispatcher.utter_message(text=f'Se ha eliminado el postre.')
                if menu_carne_id is None and menu_pescado_id is None and menu_entrante_id is None and menu_bebida_id is None:
                    return [SlotSet("menu_establecido", False), SlotSet("menu_plato_categoria", None), SlotSet("menu_plato_id", None), SlotSet("menu_postre_id", None), SlotSet("menu_postre_nombre", None), SlotSet("menu_postre_precio", None)]
                return [SlotSet("menu_plato_id", None), SlotSet("menu_plato_categoria", None), SlotSet("menu_postre_id", None), SlotSet("menu_postre_nombre", None), SlotSet("menu_postre_precio", None)]
            elif menu_plato_id == menu_bebida_id:
                dispatcher.utter_message(text=f'Se ha eliminado la bebida.')
                if menu_carne_id is None and menu_pescado_id is None and menu_postre_id is None and menu_entrante_id is None:
                    return [SlotSet("menu_establecido", False), SlotSet("menu_plato_categoria", None), SlotSet("menu_plato_id", None), SlotSet("menu_bebida_id", None), SlotSet("menu_bebida_nombre", None), SlotSet("menu_bebida_precio", None)]
                return [SlotSet("menu_plato_id", None), SlotSet("menu_plato_categoria", None), SlotSet("menu_bebida_id", None), SlotSet("menu_bebida_nombre", None), SlotSet("menu_bebida_precio", None)]
            else:
                dispatcher.utter_message(
                    text=f'Ese plato no esta establecido no esta guardado, comprueba el ID.')
                return [SlotSet("menu_plato_id", None)]
        else:
            dispatcher.utter_message(
                text=f'No se ha establecido un ID de plato.')
            return [SlotSet("menu_plato_id", None)]


class MenuBorrarTodo(Action):
    def name(self):
        return 'MenuBorrarTodo'

    def run(self, dispatcher, tracker, domain):
        print("MenuBorrarTodo")

        dispatcher.utter_message(text=f'Menu restablecido.')
        return [SlotSet("menu_entrante_id", None),
                SlotSet("menu_entrante_nombre", None),
                SlotSet("menu_entrante_precio", None),
                SlotSet("menu_carne_id", None),
                SlotSet("menu_carne_nombre", None),
                SlotSet("menu_carne_precio", None),
                SlotSet("menu_pescado_id", None),
                SlotSet("menu_pescado_nombre", None),
                SlotSet("menu_pescado_precio", None),
                SlotSet("menu_postre_id", None),
                SlotSet("menu_postre_nombre", None),
                SlotSet("menu_postre_precio", None),
                SlotSet("menu_bebida_id", None),
                SlotSet("menu_bebida_nombre", None),
                SlotSet("menu_bebida_precio", None),
                SlotSet("menu_establecido", False),
                SlotSet("menu_plato_id", None),
                SlotSet("menu_plato_categoria", None)]


class MenuGet(Action):
    def name(self):
        return 'MenuGet'

    def get_menu_plato(Action, tipo):
        data = get_data_generic(data_path+"/data/menu/"+tipo+".json")
        message = tipo.capitalize() + ":" + "\n"
        for it in data[tipo]:
            message += str(it['id']) + ": " + it['nombre'] + \
                " - (" + it['precio'] + ")\n"
        return message

    def get_submenu_botones(Action, tipo):
        data = get_data_generic(data_path+"/data/menu/"+tipo+".json")
        buttons = []
        for it in data[tipo]:
            buttons.append({"title": "{}".format(
                it['nombre'] + " (" + it['id'] + ")"), "payload": "{}".format(it['id'])})
        return buttons

    def run(self, dispatcher, tracker, domain):
        print("MenuGet")
        menu_plato_categoria = tracker.get_slot("menu_plato_categoria")
        intent = tracker.get_intent_of_latest_message()

        if intent == "menu_completo":
            message = ""
            for it in CATEGORIA_MENU:
                data = get_data_generic(data_path+"/data/menu/"+it+".json")
                message += it.capitalize() + ":\n"
                for d in data[it]:
                    message += "- " + d['nombre'] + \
                        " - (" + d['precio'] + ")\n"
            dispatcher.utter_message(text=message)
            return ""

        if menu_plato_categoria is not None:

            menu_plato_categoria = menu_plato_categoria.lower()
            for it in CATEGORIA_MENU:
                if menu_plato_categoria in it:
                    menu_plato_categoria = it
                    break
            if menu_plato_categoria in CATEGORIA_MENU:
                message = self.get_menu_plato(menu_plato_categoria)
                dispatcher.utter_message(text=message)
                return [SlotSet("menu_plato_categoria", menu_plato_categoria)]
            else:
                dispatcher.utter_message(text=f'Esa categoria no existe.')
                return [SlotSet("menu_plato_categoria", None)]
        else:
            dispatcher.utter_message(
                text=f'No se ha establecido una categoria')


class MenuGetCategoriasButtons(Action):
    def name(self):
        return 'MenuGetCategoriasButtons'

    def get_categorias_botones(Action):
        buttons = []
        for it in CATEGORIA_MENU:
            buttons.append({"title": "{}".format(
                it.capitalize()), "payload": "{}".format(it)})
        return buttons

    def run(self, dispatcher, tracker, domain):
        print("MenuGetCategoriasButtons")

        buttons = self.get_categorias_botones()
        dispatcher.utter_message(
            "Selecciona una categoria:", buttons=buttons, button_type="vertical")
        return ""


class MenuGetUser(Action):
    def name(self):
        return 'MenuGetUser'

    def run(self, dispatcher, tracker, domain):
        print("MenuGetUser")

        menu_entrante_id = tracker.get_slot("menu_entrante_id")
        menu_carne_id = tracker.get_slot("menu_carne_id")
        menu_pescado_id = tracker.get_slot("menu_pescado_id")
        menu_postre_id = tracker.get_slot("menu_postre_id")
        menu_bebida_id = tracker.get_slot("menu_bebida_id")

        message = ''
        if menu_entrante_id is not None:
            message += "Entrante:\n- " + \
                tracker.get_slot("menu_entrante_id") + ": " + \
                tracker.get_slot("menu_entrante_nombre") + " - (" + \
                tracker.get_slot("menu_entrante_precio") + ")\n"
        if menu_carne_id is not None:
            message += "Carne:\n- " + \
                tracker.get_slot("menu_carne_id") + ": " + \
                tracker.get_slot("menu_carne_nombre") + " - (" + \
                tracker.get_slot("menu_carne_precio") + ")\n"
        if menu_pescado_id is not None:
            message += "Pescado:\n- " + \
                tracker.get_slot("menu_pescado_id") + ": " + \
                tracker.get_slot("menu_pescado_nombre") + " - (" + \
                tracker.get_slot("menu_pescado_precio") + ")\n"
        if menu_postre_id is not None:
            message += "Postre:\n- " + \
                tracker.get_slot("menu_postre_id") + ": " + \
                tracker.get_slot("menu_postre_nombre") + " - (" + \
                tracker.get_slot("menu_postre_precio") + ")\n"
        if menu_bebida_id is not None:
            message += "Bebida:\n- " + \
                tracker.get_slot("menu_bebida_id") + ": " + \
                tracker.get_slot("menu_bebida_nombre") + " - (" + \
                tracker.get_slot("menu_bebida_precio") + ")\n"

        if message == '':
            dispatcher.utter_message(
                text=f"No se ha establecido ningun plato aun. Introduce \"Establecer menu\" para añadir un plato.")
        else:
            dispatcher.utter_message(text=message)
        return ''


class MenuResetPlatoID(Action):
    def name(self):
        return 'MenuResetPlatoID'

    def run(self, dispatcher, tracker, domain):
        print("MenuResetPlatoID")
        return [SlotSet("menu_plato_id", None)]


class ValidateMenuPlatoCategoriaForm(FormValidationAction):
    def name(self) -> Text:
        return 'validate_menu_plato_categoria_form'

    async def required_slots(
        self, slots_mapped_in_domain: List[Text],
        dispatcher: CollectingDispatcher,
        tracker: Tracker, domain: DomainDict,
    ) -> Optional[List[Text]]:
        return slots_mapped_in_domain

    async def extract_menu_plato_categoria(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> Dict[Text, Any]:
        print("extract_menu_plato_categoria")

        menu_plato_categoria = tracker.get_slot("menu_plato_categoria")
        if menu_plato_categoria is not None:
            menu_plato_categoria = menu_plato_categoria.lower()
            if menu_plato_categoria in CATEGORIA_MENU:
                return {"menu_plato_categoria": menu_plato_categoria}
        return {"menu_plato_categoria": None}

    def validate_menu_plato_categoria(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        print("validate_menu_plato_categoria")

        menu_plato_categoria = tracker.get_slot("menu_plato_categoria")
        if menu_plato_categoria is not None:
            menu_plato_categoria = menu_plato_categoria.lower()
        else:
            return {"menu_plato_categoria": None}

        if menu_plato_categoria not in CATEGORIA_MENU:
            buttons = []
            for it in CATEGORIA_MENU:
                buttons.append({"title": "{}".format(
                    it.capitalize()), "payload": "{}".format(it)})
            dispatcher.utter_message(
                "No reconozco esa categoria, elige una de las siguientes:", buttons=buttons, button_type="vertical")
            return {"menu_plato_categoria": None}
        else:
            return {"menu_plato_categoria": menu_plato_categoria}


class ValidateMenuPlatoIDForm(FormValidationAction):
    def name(self) -> Text:
        return 'validate_menu_plato_id_form'

    async def required_slots(
        self, slots_mapped_in_domain: List[Text],
        dispatcher: CollectingDispatcher,
        tracker: Tracker, domain: DomainDict,
    ) -> Optional[List[Text]]:
        print("Required slots menu_plato_id")
        return slots_mapped_in_domain

    async def extract_menu_plato_id(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> Dict[Text, Any]:
        print("extract_menu_plato_id")

        intent = tracker.get_intent_of_latest_message()
        if intent == "stop":
            return {"requested_slot": None, "menu_plato_id": None, "menu_plato_categoria": None}

        menu_plato_id = tracker.get_slot("menu_plato_id")
        menu_plato_categoria = tracker.get_slot("menu_plato_categoria")

        if menu_plato_categoria is None:
            dispatcher.utter_message(
                text=f'No se ha introducido una categoria, parando el proceso.')
            return {"requested_slot": None, "menu_plato_id": None}

        if menu_plato_id is not None:
            for it in CATEGORIA_MENU:
                if menu_plato_categoria in it:
                    menu_plato_categoria = it
                    break

            data = get_data_generic(
                data_path+"/data/menu/"+menu_plato_categoria+".json")
            for it in data[menu_plato_categoria]:
                if it['id'] == str(menu_plato_id):
                    return {"menu_plato_id": menu_plato_id}
            buttons = MenuGet.get_submenu_botones(self, menu_plato_categoria)
            dispatcher.utter_message(
                text=f'No se ha encontrado ese identificador, selecciona uno de los siguientes:', buttons=buttons, button_type="vertical")
            return {"menu_plato_categoria": menu_plato_categoria, "menu_plato_id": None}
        else:
            return {"menu_plato_id": None}

    def validate_menu_plato_id(
        self, slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker, domain: DomainDict,
    ) -> Dict[Text, Any]:
        print("validate_menu_plato_id")
        intent = tracker.get_intent_of_latest_message()
        if intent == "stop":
            return {"requested_slot": None, "menu_plato_id": None, "menu_plato_categoria": None}
        menu_plato_id = tracker.get_slot("menu_plato_id")
        menu_plato_categoria = tracker.get_slot("menu_plato_categoria")
        if menu_plato_id is not None:
            for it in CATEGORIA_MENU:
                if menu_plato_categoria in it:
                    menu_plato_categoria = it
                    break

            data = get_data_generic(
                data_path+"/data/menu/"+menu_plato_categoria+".json")
            for it in data[menu_plato_categoria]:
                if it['id'] == str(menu_plato_id):
                    message = "Guardado plato " + menu_plato_categoria + \
                        ":\n- " + it['nombre'] + " (" + it['precio'] + ")"
                    dispatcher.utter_message(text=message)
                    if menu_plato_categoria == "entrantes":
                        return {"menu_plato_id": menu_plato_id, "menu_entrante_id": menu_plato_id, "menu_entrante_nombre": it['nombre'], "menu_entrante_precio": it['precio'], "menu_establecido": True}
                    elif menu_plato_categoria == "carnes":
                        return {"menu_plato_id": menu_plato_id, "menu_carne_id": menu_plato_id, "menu_carne_nombre": it['nombre'], "menu_carne_precio": it['precio'], "menu_establecido": True}
                    elif menu_plato_categoria == "pescados":
                        return {"menu_plato_id": menu_plato_id, "menu_pescado_id": menu_plato_id, "menu_pescado_nombre": it['nombre'], "menu_pescado_precio": it['precio'], "menu_establecido": True}
                    elif menu_plato_categoria == "postres":
                        return {"menu_plato_id": menu_plato_id, "menu_postre_id": menu_plato_id, "menu_postre_nombre": it['nombre'], "menu_postre_precio": it['precio'], "menu_establecido": True}
                    elif menu_plato_categoria == "bebidas":
                        return {"menu_plato_id": menu_plato_id, "menu_bebida_id": menu_plato_id, "menu_bebida_nombre": it['nombre'], "menu_bebida_precio": it['precio'], "menu_establecido": True}
        return {"menu_plato_id": None}


# ---------------------------------------------------------------------
# Reserva Class
# ---------------------------------------------------------------------


class ReservaBorrar(Action):
    def name(self):
        return 'ReservaBorrar'

    def run(self, dispatcher, tracker, domain):
        print("ReservaBorrar")
        dispatcher.utter_message(
            text=f'Se ha eliminado los datos de reserva introducidos.')
        return [SlotSet("reserva_dia", None), SlotSet("reserva_hora", None), SlotSet("reserva_comensales", None), SlotSet("reserva_mesa_id", None)]


class ReservaGetMesasLibres(Action):
    def name(self):
        return 'ReservaGetMesasLibres'

    def check_mesas_libres_dia(Action, dia):
        hay_mesa = False
        for it in horas['horas'][dia]:
            if it['ocupada'] == "False":
                hay_mesa = True
                break
        return hay_mesa

    def run(self, dispatcher, tracker, domain):
        print("ReservaGetMesasLibres")
        reserva_dia = tracker.get_slot("reserva_dia")
        if reserva_dia is not None:
            if horario['horario'][reserva_dia][0] == "cerrado":
                dispatcher.utter_message(
                    text=f'El ' + reserva_dia + ' estamos cerrados.')
                return [SlotSet("reserva_dia", None)]
        else:
            dispatcher.utter_message(
                text=f'No se ha establecido un dia para la reserva.')
            return []

        if self.check_mesas_libres_dia(reserva_dia):
            dispatcher.utter_message(
                text=f'Anotado el ' + reserva_dia + ' para reserva.')
            return [SlotSet("reserva_dia", reserva_dia)]
        else:
            dispatcher.utter_message(
                text=f'El ' + reserva_dia + ' no tenemos mesas disponibles.')
            return [SlotSet("reserva_dia", None)]


class ReservaGetUser(Action):
    def name(self):
        return "ReservaGetUser"

    def run(self, dispatcher, tracker, domain):
        print("ReservaGetUser")

        reserva_dia = tracker.get_slot("reserva_dia")
        reserva_hora = tracker.get_slot("reserva_hora")
        reserva_comensales = tracker.get_slot("reserva_comensales")
        reserva_mesa_id = tracker.get_slot("reserva_mesa_id")

        message = "No se ha establecido una reserva aun."
        if reserva_dia is not None or reserva_hora is not None or reserva_comensales is not None or reserva_mesa_id is not None:
            message = "Tu reserva tiene los siguientes datos:\n"

        if reserva_dia is not None:
            message += "- Dia: " + reserva_dia + ".\n"
        if reserva_hora is not None:
            message += "- Hora: " + reserva_hora + ".\n"
        if reserva_mesa_id is not None:
            message += "- Mesa: " + str(reserva_mesa_id) + ".\n"
        if reserva_comensales is not None:
            message += "- Comensales: " + reserva_comensales + ".\n"

        dispatcher.utter_message(text=message)

        if tracker.get_slot("menu_establecido"):
            dispatcher.utter_message(text=f'Tu menu esta compuesto por:')
            MenuGetUser.run(self, dispatcher, tracker, domain)

        return ""


class ValidateReservaComensalesForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_reserva_comensales_form"

    def get_mesa_libre(Action, dia, hora):
        for it in horas['horas'][dia]:
            if it['time'][hora] == "False":
                return it['id']
        return False

    async def required_slots(
        self, slots_mapped_in_domain: List[Text],
        dispatcher: CollectingDispatcher,
        tracker: Tracker, domain: DomainDict,
    ) -> Optional[List[Text]]:
        print("Required slots comensales")
        return slots_mapped_in_domain

    async def extract_reserva_comensales(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> Dict[Text, Any]:
        print("extract_reserva_comensales")

        reserva_comensales = tracker.get_slot("reserva_comensales")
        if reserva_comensales is not None:
            return {"reserva_comensales": reserva_comensales}
        else:
            dispatcher.utter_message(
                text=f'No se han establecido los comensales.')
            return {"reserva_comensales": None}

    def validate_reserva_comensales(
        self, slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker, domain: DomainDict,
    ) -> Dict[Text, Any]:
        print("validate_reserva_comensales")
        if tracker.get_intent_of_latest_message() == "stop":
            return {"requested_slot": None, "reserva_hora": None, "reserva_dia": None, "reserva_comensales": None}
        reserva_comensales = tracker.get_slot("reserva_comensales")
        if not reserva_comensales.isnumeric():
            dispatcher.utter_message(
                text=f'Por favor, indica los comensales con formato numerico.')
            return {"reserva_comensales": None}
        reserva_dia = tracker.get_slot("reserva_dia")
        reserva_hora = tracker.get_slot("reserva_hora")
        reserva_mesa_id = self.get_mesa_libre(reserva_dia, reserva_hora)
        if reserva_mesa_id is not None:
            dispatcher.utter_message(
                text=f'Anotado ' + reserva_comensales + ' comensales.')
            return {"reserva_comensales": reserva_comensales, "reserva_mesa_id": reserva_mesa_id}
        dispatcher.utter_message(text=f'No hay mesa disponible en esa hora.')
        return {}


class ValidateReservaDiaForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_reserva_dia_form"

    async def required_slots(
        self, slots_mapped_in_domain: List[Text],
        dispatcher: CollectingDispatcher,
        tracker: Tracker, domain: DomainDict,
    ) -> Optional[List[Text]]:
        print("Required slots reserva_dia")
        return slots_mapped_in_domain

    async def extract_reserva_dia(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> Dict[Text, Any]:
        print("extract_reserva_dia")
        reserva_dia = tracker.get_slot("reserva_dia")
        if reserva_dia is not None:
            reserva_dia = reserva_dia.lower()
            if reserva_dia == "hoy":
                now = datetime.datetime.now()
                reserva_dia = now.strftime("%A")
            elif reserva_dia == "mañana":
                now = (datetime.datetime.now() +
                       datetime.timedelta(1)).strftime("%A")
                reserva_dia = now
            elif reserva_dia == "pasado mañana":
                now = (datetime.datetime.now() +
                       datetime.timedelta(2)).strftime("%A")
                reserva_dia = now
            reserva_dia = unidecode.unidecode(reserva_dia)

            if reserva_dia not in DIAS_SEMANA:
                buttons = [
                    {'title': 'Lunes',     'payload': 'lunes'},
                    {'title': 'Martes',    'payload': 'martes'},
                    {'title': 'Miercoles', 'payload': 'miercoles'},
                    {'title': 'Jueves',    'payload': 'jueves'},
                    {'title': 'Viernes',   'payload': 'viernes'},
                    {'title': 'Sabado',    'payload': 'sabado'},
                    {'title': 'Domingo',   'payload': 'domingo'}]
                dispatcher.utter_message(
                    "No se ha reconocido el dia, pulsa sobre el dia que quieras", buttons=buttons, button_type="vertical")
                return {"reserva_dia": None}
            return {"reserva_dia": reserva_dia}
        return {"reserva_dia": None}

    def validate_reserva_dia(
        self, slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker, domain: DomainDict,
    ) -> Dict[Text, Any]:
        print("validate_reserva_dia")
        if tracker.get_intent_of_latest_message() == "stop":
            return {"requested_slot": None, "reserva_dia": None}
        reserva_dia = tracker.get_slot("reserva_dia")
        if reserva_dia is not None and reserva_dia not in DIAS_SEMANA:
            dispatcher.utter_message(
                text=f'No reconozco ese dia.')
            return {"reserva_dia": None}
        if tracker.get_slot("menu_establecido") is None:
            return {"reserva_dia": reserva_dia, "menu_establecido": False}
        return {"reserva_dia": reserva_dia}


class ValidateReservaHoraForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_reserva_hora_form"

    def get_horas_mesas(Action, dia):
        horas_mesas = []
        for it in horas['horas'][dia][0]['time']:
            horas_mesas.append(it)
        return horas_mesas

    def validate_regex(Action, hora):
        return bool(re.search('[0-9][0-9]:[0-9][0-9]', hora))

    async def required_slots(
        self, slots_mapped_in_domain: List[Text],
        dispatcher: CollectingDispatcher,
        tracker: Tracker, domain: DomainDict,
    ) -> Optional[List[Text]]:
        print("Required slots reserva_hora")
        return slots_mapped_in_domain

    async def extract_reserva_hora(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> Dict[Text, Any]:
        print("extract_reserva_hora")
        reserva_dia = tracker.get_slot("reserva_dia")
        reserva_hora = tracker.get_slot("reserva_hora")
        horas_mesas = self.get_horas_mesas(reserva_dia)
        if reserva_hora in horas_mesas:
            return {"reserva_hora": reserva_hora}
        if reserva_dia is not None:
            reserva_dia = reserva_dia.lower()
            if self.validate_regex(reserva_dia):
                return {"reserva_hora": tracker.get_slot("reserva_hora")}
        if reserva_dia is not None:
            buttons = []
            for it in horas_mesas:
                buttons.append({"title": "{}".format(
                    it), "payload": "{}".format(it)})
            dispatcher.utter_message(
                "Estas son las horas disponibles el " + reserva_dia + ":", buttons=buttons, button_type="vertical")
            return {"reserva_hora": None}
        return {"reserva_hora": None}

    def validate_reserva_hora(
        self, slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker, domain: DomainDict,
    ) -> Dict[Text, Any]:
        print("validate_reserva_hora")
        if tracker.get_intent_of_latest_message() == "stop":
            return {"requested_slot": None, "reserva_hora": None, "reserva_dia": None}
        reserva_hora = tracker.get_slot("reserva_hora")
        reserva_dia = tracker.get_slot("reserva_dia")
        horas_mesas = self.get_horas_mesas(reserva_dia)
        if reserva_hora in horas_mesas:
            dispatcher.utter_message(
                text=f'Anotada la hora de reserva: ' + reserva_hora)
            return {"reserva_hora": reserva_hora}
        else:
            return {"reserva_hora": None}
