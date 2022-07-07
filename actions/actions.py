from asyncore import dispatcher
from code import interact
from copyreg import dispatch_table
import pathlib
from sre_constants import CATEGORY_SPACE
from typing import Text, List, Any, Dict, Optional
import json

from rasa_sdk import Tracker, FormValidationAction
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.types import DomainDict
from rasa_sdk.interfaces import Action
from rasa_sdk.events import SlotSet

names = pathlib.Path("data/diccionarios/nombres.txt").read_text().split("\n")
malsonantes = pathlib.Path(
    "data/diccionarios/malsonante.txt").read_text().split("\n")

DIAS_SEMANA = ["lunes", "martes", "miercoles",
               "jueves", "viernes", "sabado", "domingo"]
CATEGORIA_MENU = ["entrantes", "carnes", "pescados", "postres", "bebidas"]

f = open(pathlib.Path("data/menu/horario.json"))
horario = json.load(f)
f.close()


class ValidateNameForm(FormValidationAction):

    def name(self) -> Text:
        return "validate_name_form"

    async def required_slots(
        self, slots_mapped_in_domain: List[Text],
        dispatcher: CollectingDispatcher,
        tracker: Tracker, domain: DomainDict,
    ) -> Optional[List[Text]]:
        print("Required slots")

        first_name = tracker.slots.get("first_name")
        if first_name is not None:
            if first_name.lower() not in names:
                return ["name_spelled_correctly"] + slots_mapped_in_domain
        return slots_mapped_in_domain

    async def extract_name_spelled_correctly(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> Dict[Text, Any]:
        print("extract_name_spelled_correctly")

        first_name = tracker.slots.get("first_name")
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
                buttons = [{'title': 'Yes', 'payload': '/affirm'},
                           {'title': 'No', 'payload': '/repetir_nombre'}]
                dispatcher.utter_message(
                    "Mmm esta bien escrito tu nombre? Si no, escribe tu nombre de nuevo", buttons=buttons)
                return {"first_name": None, "name_spelled_correctly": None, "first_name_save": latest_message}
            return {"first_name": None, "name_spelled_correctly": False, "first_name_save": latest_message}

        if tracker.get_intent_of_latest_message() != "repetir_nombre" or intent == "repetir_nombre":
            if latest_message is not None and latest_message != tracker.get_slot("first_name") and intent != "affirm":
                return {"first_name": latest_message, "name_spelled_correctly": None}
            buttons = [{'title': 'Yes', 'payload': '/affirm'},
                       {'title': 'No', 'payload': '/repetir_nombre'}]
            dispatcher.utter_message(
                "Mmm esta bien escrito tu nombre? Si no, escribe tu nombre de nuevo", buttons=buttons)
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


class GetHorario(Action):
    def name(self):
        return 'GetHorario'

    def run(self, dispatcher, tracker, domain):

        intent = tracker.get_intent_of_latest_message()
        if intent == "horario" or intent == "apertura" or intent == "cierre":
            dispatcher.utter_message(response="utter_horario")
        message = ""
        if intent == "horario":
            for dia in DIAS_SEMANA:
                message += dia.capitalize() + ": " + \
                    horario["horario"][dia][0] + " - " + \
                    horario["horario"][dia][1] + "." + "\n"
        elif intent == "apertura" or intent == "cierre":
            value = 0 if intent == "apertura" else 1
            for dia in DIAS_SEMANA:
                message += dia.capitalize() + ": " + \
                    horario["horario"][dia][value] + "." + "\n"
        elif intent == "horario_concreto":
            dia = tracker.get_slot("dia").lower()
            if dia not in DIAS_SEMANA:
                message = "Ese dia de la semana es incorrecto."
                dispatcher.utter_message(message)
                return [SlotSet("dia", None)]
            elif horario["horario"][dia][0] == "Cerrado":
                message = "El " + dia + " estamos cerrados por descanso del personal."
            else:
                message = "El " + dia + " abrimos a las " + \
                    horario["horario"][dia][0] + " y cerramos a las " + \
                    horario["horario"][dia][1] + "."
        dispatcher.utter_message(message)
        return ''


class GetMenu(Action):
    def name(self):
        return 'GetMenu'

    def getSubmenu(Action, tipo):
        f = open(pathlib.Path("data/menu/"+tipo+".json"))
        data = json.load(f)
        f.close()
        message = tipo.capitalize() + ":" + "\n"
        for it in data[tipo]:
            message += str(it['id']) + ": " + it['nombre'] + \
                " - (" + it['precio'] + ")\n"
        return message

    def run(self, dispatcher, tracker, domain):
        print("GetMenu")
        intent = tracker.get_intent_of_latest_message()
        categoria = tracker.get_slot("categoria")
        if categoria is not None:
            categoria = categoria.lower()

        if categoria is not None:
            for it in CATEGORIA_MENU:
                if categoria in it:
                    categoria = it
                    break

        if intent == "menu" or intent == "establecer_menu":
            for item in CATEGORIA_MENU:
                dispatcher.utter_message(self.getSubmenu(item))
            return [SlotSet("plato_id", None), SlotSet("categoria", categoria)]
        elif categoria in CATEGORIA_MENU:
            dispatcher.utter_message(self.getSubmenu(categoria))
            return [SlotSet("plato_id", None), SlotSet("categoria", categoria)]

        dispatcher.utter_message(text=f'No se ha validado la la categoria.')
        return [SlotSet("plato_id", None), SlotSet("categoria", None)]


class ResetMenu(Action):
    def name(self):
        return 'ResetMenu'

    def run(self, dispatcher, tracker, domain):
        print("ResetMenu")
        intent = tracker.get_intent_of_latest_message()
        if intent == "affirm":
            dispatcher.utter_message(text=f'Menu restablecido.')
            return [SlotSet("entrante_id", None), SlotSet("entrante_nombre", None), SlotSet("entrante_precio", None),
                    SlotSet("carne_id", None), SlotSet(
                        "carne_nombre", None), SlotSet("carne_precio", None),
                    SlotSet("pescado_id", None), SlotSet(
                        "pescado_nombre", None), SlotSet("pescado_precio", None),
                    SlotSet("postre_id", None), SlotSet(
                        "postre_nombre", None), SlotSet("postre_precio", None),
                    SlotSet("bebida_id", None), SlotSet("entrante_nombre", None), SlotSet("entrante_precio", None)]
        elif intent == "deny":
            dispatcher.utter_message(
                text=f'El menu que tienes establecido es el siguiente:')
            GetUserMenu.run(self, dispatcher, tracker, domain)
            return ''
        elif intent in ["borrar_entrante", "borrar_carne", "borrar_pescado", "borrar_postre", "borrar_bebida"]:
            tipo = intent.split("_", 1)[1]
            dispatcher.utter_message(text=f'Se ha eliminado el plato seleccionado.')
            return [SlotSet(tipo+"_id", None), SlotSet(tipo+"_nombre", None), SlotSet(tipo+"_precio", None)]
        else:
            return ''


class ValidateCategoriaForm(FormValidationAction):
    def name(self) -> Text:
        return 'validate_categoria_form'

    async def required_slots(
        self, slots_mapped_in_domain: List[Text],
        dispatcher: CollectingDispatcher,
        tracker: Tracker, domain: DomainDict,
    ) -> Optional[List[Text]]:
        return slots_mapped_in_domain

    def validate_categoria(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        print("validate_categoria")

        categoria = tracker.get_slot("categoria")
        if categoria is not None:
            categoria = categoria.lower()

        if categoria is not None:
            for it in CATEGORIA_MENU:
                if categoria in it:
                    categoria = it
                    break

            if categoria not in CATEGORIA_MENU:
                dispatcher.utter_message(
                    text=f'No he podido validar esa categoria, por favor selecciona una categoria valida.')
                dispatcher.utter_message(response="utter_show_menu")
                return {"categoria": None}

            dispatcher.utter_message(
                text=f'Categoria establecida: ' + categoria.capitalize() + '.')
            return {"categoria": categoria}

        dispatcher.utter_message(
            text=f'No se ha intentado establecer una categoria. Parando el formulario.')
        return {"requested_slot": None, "categoria": None}


class GetUserMenu(Action):
    def name(self):
        return 'GetUserMenu'

    def run(self, dispatcher, tracker, domain):
        print("GetUserMenu")

        entrante_id = tracker.get_slot("entrante_id")
        carne_id = tracker.get_slot("carne_id")
        pescado_id = tracker.get_slot("pescado_id")
        postre_id = tracker.get_slot("postre_id")
        bebida_id = tracker.get_slot("bebida_id")

        message = ''
        if entrante_id is not None:
            message += "Entrante:\n- " + \
                tracker.get_slot("entrante_nombre") + " - (" + \
                tracker.get_slot("entrante_precio") + ")\n"
        if carne_id is not None:
            message += "Carne:\n- " + \
                tracker.get_slot("carne_nombre") + " - (" + \
                tracker.get_slot("carne_precio") + ")\n"
        if pescado_id is not None:
            message += "Pescado:\n- " + \
                tracker.get_slot("pescado_nombre") + " - (" + \
                tracker.get_slot("pescado_precio") + ")\n"
        if postre_id is not None:
            message += "Postre:\n- " + \
                tracker.get_slot("postre_nombre") + " - (" + \
                tracker.get_slot("postre_precio") + ")\n"
        if bebida_id is not None:
            message += "Bebida:\n- " + \
                tracker.get_slot("bebida_nombre") + " - (" + \
                tracker.get_slot("bebida_precio") + ")\n"

        if message == '':
            dispatcher.utter_message(
                text=f"No se ha establecido ningun plato aun. Introduce \"Establecer plato <categoria>\" para añadir un plato.")
            dispatcher.utter_message(response="utter_show_menu")
        else:
            dispatcher.utter_message(text=message)
        return ''


class ValidatePlatoForm(FormValidationAction):
    def name(self) -> Text:
        return 'validate_plato_form'

    async def required_slots(
        self, slots_mapped_in_domain: List[Text],
        dispatcher: CollectingDispatcher,
        tracker: Tracker, domain: DomainDict,
    ) -> Optional[List[Text]]:
        return slots_mapped_in_domain

    def validate_plato_id(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        print("validate_plato_id")

        categoria = tracker.get_slot("categoria")
        categoria = categoria.lower()
        plato_id = tracker.get_slot("plato_id")
        intent = tracker.get_intent_of_latest_message()

        if intent == "stop":
            return {"requested_slot": None, "first_name": None}

        if categoria is not None:
            for it in CATEGORIA_MENU:
                if categoria in it:
                    categoria = it
                    break

            if intent in ["establecer_plato_entrante", "establecer_plato_carne", "establecer_plato_pescado", "establecer_plato_postre", "establecer_plato_bebida"]:
                return {"categoria": categoria, "plato_id": None}

            f = open(pathlib.Path("data/menu/"+str(categoria)+".json"))
            data = json.load(f)
            f.close()

            for it in data[categoria]:
                if str(it['id']) == plato_id:
                    if categoria == "entrantes":
                        dispatcher.utter_message(
                            response="utter_entrante_seleccionado", entrante_nombre=it['nombre'], entrante_precio=it['precio'])
                        dispatcher.utter_message(
                            response="utter_change_plato_info")
                        return {"categoria": None, "plato_id": plato_id, "entrante_id": plato_id, "entrante_nombre": it['nombre'], "entrante_precio": it['precio']}
                    elif categoria == "carnes":
                        dispatcher.utter_message(
                            response="utter_carne_seleccionado", carne_nombre=it['nombre'], carne_precio=it['precio'])
                        dispatcher.utter_message(
                            response="utter_change_plato_info")
                        return {"categoria": None, "plato_id": plato_id, "carne_id": plato_id, "carne_nombre": it['nombre'], "carne_precio": it['precio']}
                    elif categoria == "pescados":
                        dispatcher.utter_message(
                            response="utter_pescado_seleccionado", pescado_nombre=it['nombre'], pescado_precio=it['precio'])
                        dispatcher.utter_message(
                            response="utter_change_plato_info")
                        return {"categoria": None, "plato_id": plato_id, "pescado_id": plato_id, "pescado_nombre": it['nombre'], "pescado_precio": it['precio']}
                    elif categoria == "postres":
                        dispatcher.utter_message(
                            response="utter_postre_seleccionado", postre_nombre=it['nombre'], postre_precio=it['precio'])
                        dispatcher.utter_message(
                            response="utter_change_plato_info")
                        return {"categoria": None, "plato_id": plato_id, "postre_id": plato_id, "postre_nombre": it['nombre'], "postre_precio": it['precio']}
                    elif categoria == "bebidas":
                        dispatcher.utter_message(
                            response="utter_bebida_seleccionado", bebida_nombre=it['nombre'], bebida_precio=it['precio'])
                        dispatcher.utter_message(
                            response="utter_change_plato_info")
                        return {"categoria": None, "plato_id": plato_id, "bebida_id": plato_id, "bebida_nombre": it['nombre'], "bebida_precio": it['precio']}

        dispatcher.utter_message(
            text=f'El plato elegido no esta en la lista de la categoria, selecciona otro o escribe "stop" para parar el proceso.')
        return {"plato_id": None}
