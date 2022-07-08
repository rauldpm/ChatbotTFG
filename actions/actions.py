import pathlib
import json

from rasa_sdk import Tracker, FormValidationAction
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.types import DomainDict
from rasa_sdk.interfaces import Action
from rasa_sdk.events import SlotSet
from typing import Text, List, Any, Dict, Optional

names = pathlib.Path("data/diccionarios/nombres.txt").read_text().split("\n")
malsonantes = pathlib.Path(
    "data/diccionarios/malsonante.txt").read_text().split("\n")

DIAS_SEMANA = ["lunes", "martes", "miercoles",
               "jueves", "viernes", "sabado", "domingo"]
CATEGORIA_MENU = ["entrantes", "carnes", "pescados", "postres", "bebidas"]

f = open(pathlib.Path("data/menu/horario.json"))
horario = json.load(f)
f.close()

f = open(pathlib.Path("data/tables/mesas.json"))
mesas = json.load(f)
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
            return [SlotSet("cantidad", None), SlotSet("categoria", categoria)]
        elif categoria in CATEGORIA_MENU:
            dispatcher.utter_message(self.getSubmenu(categoria))
            return [SlotSet("cantidad", None), SlotSet("categoria", categoria)]

        dispatcher.utter_message(text=f'No se ha validado la la categoria.')
        return [SlotSet("cantidad", None), SlotSet("categoria", None)]


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
                    SlotSet("bebida_id", None), SlotSet(
                        "entrante_nombre", None), SlotSet("entrante_precio", None),
                    SlotSet("plato_establecido", False), SlotSet("cantidad", None)]
        elif intent == "deny":
            dispatcher.utter_message(
                text=f'El menu que tienes establecido es el siguiente:')
            GetUserMenu.run(self, dispatcher, tracker, domain)
            return ''
        elif intent in ["borrar_entrante", "borrar_carne", "borrar_pescado", "borrar_postre", "borrar_bebida"]:
            tipo = intent.split("_", 1)[1]
            dispatcher.utter_message(
                text=f'Se ha eliminado el plato seleccionado.')
            entrante_id = tracker.get_slot("entrante_id")
            carne_id = tracker.get_slot("carne_id")
            pescado_id = tracker.get_slot("pescado_id")
            postre_id = tracker.get_slot("postre_id")
            bebida_id = tracker.get_slot("bebida_id")
            if entrante_id is None and carne_id is None and pescado_id is None and postre_id is None and bebida_id is None:
                return [SlotSet(tipo+"_id", None), SlotSet(tipo+"_nombre", None), SlotSet(tipo+"_precio", None), SlotSet("plato_establecido", False), SlotSet("cantidad", None)]
            else:
                return [SlotSet(tipo+"_id", None), SlotSet(tipo+"_nombre", None), SlotSet(tipo+"_precio", None), SlotSet("cantidad", None)]
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


class ValidateCantidadForm(FormValidationAction):
    def name(self) -> Text:
        return 'validate_cantidad_form'

    async def required_slots(
        self, slots_mapped_in_domain: List[Text],
        dispatcher: CollectingDispatcher,
        tracker: Tracker, domain: DomainDict,
    ) -> Optional[List[Text]]:
        return slots_mapped_in_domain

    def validate_cantidad(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        print("validate_cantidad")

        intent = tracker.get_intent_of_latest_message()
        if intent == "stop":
            return {"requested_slot": None, "cantidad": None, "categoria": None}

        categoria = tracker.get_slot("categoria")
        if categoria is not None:
            categoria = categoria.lower()
        cantidad = tracker.get_slot("cantidad")

        if categoria is not None:
            for it in CATEGORIA_MENU:
                if categoria in it:
                    categoria = it
                    break

            if intent in ["establecer_plato_entrante", "establecer_plato_carne", "establecer_plato_pescado", "establecer_plato_postre", "establecer_plato_bebida"]:
                return {"categoria": categoria, "cantidad": None}

            f = open(pathlib.Path("data/menu/"+str(categoria)+".json"))
            data = json.load(f)
            f.close()

            for it in data[categoria]:
                if str(it['id']) == cantidad:
                    if categoria == "entrantes":
                        dispatcher.utter_message(
                            response="utter_entrante_seleccionado", entrante_nombre=it['nombre'], entrante_precio=it['precio'])
                        dispatcher.utter_message(
                            response="utter_change_plato_info")
                        return {"categoria": None, "cantidad": cantidad, "entrante_id": cantidad, "entrante_nombre": it['nombre'], "entrante_precio": it['precio'], "plato_establecido": True}
                    elif categoria == "carnes":
                        dispatcher.utter_message(
                            response="utter_carne_seleccionado", carne_nombre=it['nombre'], carne_precio=it['precio'])
                        dispatcher.utter_message(
                            response="utter_change_plato_info")
                        return {"categoria": None, "cantidad": cantidad, "carne_id": cantidad, "carne_nombre": it['nombre'], "carne_precio": it['precio'], "plato_establecido": True}
                    elif categoria == "pescados":
                        dispatcher.utter_message(
                            response="utter_pescado_seleccionado", pescado_nombre=it['nombre'], pescado_precio=it['precio'])
                        dispatcher.utter_message(
                            response="utter_change_plato_info")
                        return {"categoria": None, "cantidad": cantidad, "pescado_id": cantidad, "pescado_nombre": it['nombre'], "pescado_precio": it['precio'], "plato_establecido": True}
                    elif categoria == "postres":
                        dispatcher.utter_message(
                            response="utter_postre_seleccionado", postre_nombre=it['nombre'], postre_precio=it['precio'])
                        dispatcher.utter_message(
                            response="utter_change_plato_info")
                        return {"categoria": None, "cantidad": cantidad, "postre_id": cantidad, "postre_nombre": it['nombre'], "postre_precio": it['precio'], "plato_establecido": True}
                    elif categoria == "bebidas":
                        dispatcher.utter_message(
                            response="utter_bebida_seleccionado", bebida_nombre=it['nombre'], bebida_precio=it['precio'])
                        dispatcher.utter_message(
                            response="utter_change_plato_info")
                        return {"categoria": None, "cantidad": cantidad, "bebida_id": cantidad, "bebida_nombre": it['nombre'], "bebida_precio": it['precio'], "plato_establecido": True}

            dispatcher.utter_message(
                text=f'El plato elegido no esta en la lista de la categoria, selecciona otro o escribe "stop" para parar el proceso.')
            return {"cantidad": None}


class ValidateComensales(Action):
    def name(self):
        return 'ValidateComensales'

    def run(self, dispatcher, tracker, domain):
        print("ValidateComensales")

        intent = tracker.get_intent_of_latest_message()
        if intent == "stop":
            dispatcher.utter_message(response="utter_stop")
            return {"requested_slot": None, "comensales": None}

        comensales = tracker.get_slot("comensales")

        if comensales is not None:

            if not comensales.isnumeric():
                dispatcher.utter_message(
                    text='No se ha podido validar el numero de comensales. Introducelo de nuevo <Reserva para X persona>.')
                return [SlotSet("comensales", None)]

            if int(comensales) <= 0:
                dispatcher.utter_message(
                    text=f'El numero de comensales debe ser superior a 0, si quieres parar escribe "stop".')
                return [SlotSet("comensales", None)]

            disponibles = len(
                GetMesasLibres.get_mesas_libres_numero_comensal(self, comensales))
            if disponibles <= 0:
                dispatcher.utter_message(
                    text=f'No disponemos de mesas libres en este momento para ' + comensales + ' comensales.')
                return [SlotSet("comensales", None), SlotSet("mesa_disponible", False)]
            message = 'Para ' + comensales + ' comensales disponemos de ' + \
                str(disponibles) + ' mesas libres.'
            dispatcher.utter_message(text=message)
            return [SlotSet("comensales", comensales), SlotSet("mesa_disponible", True)]


class ReservarMesa(Action):
    def name(self):
        return 'ReservarMesa'

    def updateMesasJsonFile(Action, mesa):
        jsonFile = open("data/tables/mesas.json", "w")
        jsonFile.write(json.dumps(mesas))
        jsonFile.close()
        return ''

    def run(self, dispatcher, tracker, domain):
        print("ReservarMesa")
        intent = tracker.get_intent_of_latest_message()

        mesa_reservada = tracker.get_slot("mesa_reservada")
        if mesa_reservada is not None:
            dispatcher.utter_message(
                text='Ya tienes realizada una reserva, si quieres cambiarla, eliminala primero introduciendo <Borrar reserva>.')
            return ''

        if intent == "affirm":
            comensales = tracker.get_slot("comensales")
            mesas_disponibles = GetMesasLibres.get_mesas_libres_numero_comensal(
                self, comensales)
            if len(mesas_disponibles) > 0:
                id = mesas['mesas'][mesas_disponibles[0]]['id']
                mesas['mesas'][mesas_disponibles[0]]['comensales'] = comensales
                mesas['mesas'][mesas_disponibles[0]]['ocupada'] = "True"
                self.updateMesasJsonFile(mesas)
                dispatcher.utter_message(text=f'Mesa reservada.')
                return [SlotSet("mesa_reservada", id)]
            else:
                dispatcher.utter_message(
                    text=f'No he encontrado mesas libres.')
                return [SlotSet("comensales", None), SlotSet("mesa_reservada", None), SlotSet("mesa_disponible", False)]
        elif intent == "deny":
            dispatcher.utter_message(text=f'Cancelando reserva de mesa.')
        return [SlotSet("comensales", None), SlotSet("mesa_reservada", None), SlotSet("mesa_disponible", None)]


class RemoveMesa(Action):
    def name(self):
        return 'RemoveMesa'

    def updateMesasJsonFile(Action, mesa):
        jsonFile = open("data/tables/mesas.json", "w")
        jsonFile.write(json.dumps(mesas))
        jsonFile.close()
        return ''

    def run(self, dispatcher, tracker, domain):
        print('RemoveMesa')

        intent = tracker.get_intent_of_latest_message()
        comensales = tracker.get_slot("comensales")
        mesa_reservada = tracker.get_slot("mesa_reservada")

        if mesa_reservada is None:
            dispatcher.utter_message(
                text=f'Antes de eliminar debes realizar una reserva.')
            return ''

        if intent in ["affirm", "deny"]:
            if comensales is None:
                dispatcher.utter_message(
                    text=f'No se ha establecido el numero de comensales, para hacerlo, establece una reserva antes.')
                return ''
            elif mesa_reservada is None:
                dispatcher.utter_message(
                    text=f'No se ha establecido una mesa reservada, para hacerlo, establece una reserva antes.')
                return ''

        if intent == "affirm":
            mesas['mesas'][mesa_reservada]['comensales'] = "0"
            mesas['mesas'][mesa_reservada]['ocupada'] = "False"
            self.updateMesasJsonFile(mesas)
            dispatcher.utter_message(
                text=f'Se ha cancelado la reserva con exito.')
            return [SlotSet("comensales", None), SlotSet("mesa_reservada", None)]
        elif intent == "deny":
            dispatcher.utter_message(text=f'Operacion cancelada. La reserva se mantiene para ' +
                                     str(comensales) + ' comensales en la mesa ' + str(mesa_reservada) + '.')
            return ''
        return ''


class MostrarReserva(Action):
    def name(self):
        return 'MostrarReserva'

    def run(self, dispatcher, tracker, domain):
        print('MostrarReserva')

        mesa_reservada = tracker.get_slot("mesa_reservada")
        if mesa_reservada is not None:
            comensales = tracker.get_slot("comensales")
            dispatcher.utter_message(text=f'Tienes una reserva para ' +
                                     str(comensales) + ' comensales en la mesa ' + str(mesa_reservada) + '.')
            return ''
        else:
            dispatcher.utter_message(
                text=f'No se ha establecido una mesa reservada, para hacerlo, establece una reserva antes.')
            return ''


class GetMesasLibres(Action):
    def name(self):
        return 'GetMesasLibres'

    def get_mesas_libres(Action):
        disponibles = []
        for it in mesas['mesas']:
            if it['ocupada'] == "False":
                disponibles.append(it['id'])
        return disponibles

    def get_mesas_libres_numero_comensal(Action, numero):
        disponibles = []
        for it in mesas['mesas']:
            if it['ocupada'] == "False" and int(it['max_comensales']) >= int(numero):
                disponibles.append(it['id'])
        return disponibles

    def run(self, dispatcher, tracker, domain):
        print("GetMesasLibres")

        intent = tracker.get_intent_of_latest_message()
        disponibles = self.get_mesas_libres()
        if intent == "mostrar_cantidad_mesas_libres" or intent == "hacer_reserva":

            if len(disponibles) > 0:
                message = "Tenemos disponibles: " + "\n"
                m = []
                n = {}
                for id in disponibles:
                    m.append(mesas['mesas'][id]['max_comensales'])
                ini = m[0]
                contador = 0
                for it in m:
                    if ini != it:
                        ini = it
                        contador = 0
                    contador += 1
                    n[ini] = contador
                for it in n:
                    message += "- " + \
                        str(n[it]) + " mesas de " + it + " comensales." + "\n"

                message = message[:-2] + " comensales."
                dispatcher.utter_message(text=message)

            return [SlotSet("cantidad", None), SlotSet("mesa_disponible", True)]

        return [SlotSet("cantidad", None), SlotSet("mesa_disponible", False)]
