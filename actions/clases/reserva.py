from typing import Text, List, Any, Dict, Optional
from rasa_sdk.events import SlotSet
from rasa_sdk.interfaces import Action
from rasa_sdk.types import DomainDict
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk import Tracker, FormValidationAction
import unidecode  # acentos
import datetime
import re
from actions.Clases.auxiliar import *
from actions.Clases.menu import MenuGetUser

# -----------------------------------------
auxiliar = Auxiliar()
DIAS_SEMANA = auxiliar.get_dias_semana()
HORAS = auxiliar.get_horas()
HORARIO = auxiliar.get_horario()
# -----------------------------------------

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
        for it in HORAS['horas'][dia]:
            if it['ocupada'] == "False":
                hay_mesa = True
                break
        return hay_mesa

    def run(self, dispatcher, tracker, domain):
        print("ReservaGetMesasLibres")
        reserva_dia = tracker.get_slot("reserva_dia")
        if reserva_dia is not None:
            if HORARIO['horario'][reserva_dia][0] == "cerrado":
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
        for it in HORAS['horas'][dia]:
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
        for it in HORAS['horas'][dia][0]['time']:
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
