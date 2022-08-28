from dis import dis
from typing import Text, List, Any, Dict, Optional
from rasa_sdk.events import SlotSet
from rasa_sdk.interfaces import Action
from rasa_sdk.types import DomainDict
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk import Tracker, FormValidationAction
from sqlalchemy import null
from actions.clases.auxiliar import *
from actions.clases.email import *
from actions.clases.menu import MenuGetUser
import unidecode  # acentos
import datetime
import re
import random

# -----------------------------------------
auxiliar = Auxiliar()
email = Email()
DIAS_SEMANA = auxiliar.get_dias_semana()
HORAS = auxiliar.get_horas()
HORARIO = auxiliar.get_horario()
# -----------------------------------------


class ReservaBorrar(Action):
    def name(self):
        return 'ReservaBorrar'

    def run(self, dispatcher, tracker, domain):
        print("ReservaBorrar")

        reserva_realizada = tracker.get_slot("reserva_realizada")
        if reserva_realizada is not None:
            if reserva_realizada == "True":
                email.send_email_message(tracker.get_slot(
                    "reserva_email"), null, null, "borrar")

        dispatcher.utter_message(
            text=f'Se ha eliminado los datos de reserva introducidos.')
        return [SlotSet("reserva_realizada", False), SlotSet("reserva_email", None), SlotSet("reserva_codigo", None), SlotSet("reserva_codigo_tmp", None), SlotSet("reserva_email_set", None), SlotSet("reserva_dia", None), SlotSet("reserva_hora", None), SlotSet("reserva_comensales", None), SlotSet("reserva_mesa_id", None), SlotSet("reserva_completa", False)]


class ReservaFinalizarBorrar(Action):
    def name(self):
        return 'ReservaFinalizarBorrar'

    def run(self, dispatcher, tracker, domain):
        print("ReservaFinalizarBorrar")
        dispatcher.utter_message(
            text=f'Se ha cancelado la finalizacion de la reserva. Aun recuerdo tu reserva, si quieres borrarla escribe: Borrar reserva, si quieres volver a formalizar la reserva escribe: Finalizar reserva.')
        return [SlotSet("reserva_email", None), SlotSet("reserva_codigo", None), SlotSet("reserva_codigo_tmp", None), SlotSet("reserva_email_set", None)]


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
            reserva_hora = tracker.get_slot("reserva_hora")
            reserva_comensales = tracker.get_slot("reserva_comensales")
            reserva_mesa_id = tracker.get_slot("reserva_mesa_id")
            name = tracker.get_slot("first_name_set")
            if name is not None and name == True and reserva_dia is not None and reserva_hora is not None and reserva_comensales is not None and reserva_mesa_id is not None and tracker.get_slot("menu_establecido") is None:
                return [SlotSet("reserva_dia", reserva_dia), SlotSet("reserva_completa", True), SlotSet("menu_establecido", False)]
            if name is not None and name == True and reserva_dia is not None and reserva_hora is not None and reserva_comensales is not None and reserva_mesa_id is not None:
                return [SlotSet("reserva_dia", reserva_dia), SlotSet("reserva_completa", True)]
            return [SlotSet("reserva_dia", reserva_dia), SlotSet("reserva_completa", False)]
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
        name = tracker.get_slot("first_name")
        message = "No se ha establecido una reserva aun.\n"
        if reserva_dia is not None or reserva_hora is not None or reserva_comensales is not None or reserva_mesa_id is not None:
            message = "Tu reserva tiene los siguientes datos:\n"

        if reserva_dia is not None:
            message += "- Dia: " + reserva_dia + ".\n"
        if reserva_hora is not None:
            message += "- Hora: " + reserva_hora + ".\n"
        if reserva_mesa_id is not None:
            message += "- Mesa: " + str(reserva_mesa_id) + ".\n"
        if name is not None:
            message += "- Nombre de reserva: " + name + ".\n"
        if reserva_comensales is not None:
            message += "- Comensales: " + reserva_comensales + ".\n"

        dispatcher.utter_message(text=message)

        if tracker.get_slot("menu_establecido") or tracker.get_slot("menu_hay_plato"):
            dispatcher.utter_message(text=f'Tu menu esta compuesto por:')
            MenuGetUser.run(self, dispatcher, tracker, domain)
            dispatcher.utter_message(response="utter_menu_no_guardado")
        else:
            dispatcher.utter_message(response="utter_menu_aviso")

        return ""


class SendCodeEmail(Action):
    def name(self):
        return "SendCodeEmail"

    def run(self, dispatcher, tracker, domain):
        print("SendCodeEmail")

        reserva_email = tracker.get_slot("reserva_email")
        if reserva_email is not None:
            code = str(random.randint(100000, 999999))
            name = tracker.get_slot("first_name")
            email.send_email_code(reserva_email, code, name)
            dispatcher.utter_message(
                "Se ha enviado un codigo a la direccion " + reserva_email)
            return [SlotSet("reserva_codigo_tmp", code)]

        dispatcher.utter_message(text=f'No se ha establecido un email.')
        return ""


class ValidateReservaComensalesForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_reserva_comensales_form"

    def get_mesa_libre(Action, dia, hora):
        for it in HORAS['horas'][dia]:
            if len(it['time']) == 0:
                return it['id']
            else:
                h = int(hora[:2])
                for it2 in it['time']:
                    h2 = int(it2[:2])
                    if (h == h2) or (h > h2 and h < int(h2+2)) or (int(h+2) > h2 and int(h+2) < int(h2+2)):
                        return False
                return it['id']

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
        if tracker.get_intent_of_latest_message() == "stop":
            return {"requested_slot": None, "reserva_comensales": None}
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
            return {"requested_slot": None, "reserva_comensales": None}
        reserva_comensales = tracker.get_slot("reserva_comensales")
        if not reserva_comensales.isnumeric():
            dispatcher.utter_message(
                text=f'Por favor, indica los comensales con formato numerico.')
            return {"reserva_comensales": None}
        reserva_dia = tracker.get_slot("reserva_dia")
        reserva_hora = tracker.get_slot("reserva_hora")
        reserva_mesa_id = self.get_mesa_libre(reserva_dia, reserva_hora)
        name = tracker.get_slot("first_name_set")
        if reserva_mesa_id is not None:
            dispatcher.utter_message(
                text=f'Anotado ' + reserva_comensales + ' comensales.')

            if name is not None and name == True and reserva_dia is not None and reserva_hora is not None and reserva_comensales is not None and tracker.get_slot("menu_establecido") is None:
                return {"reserva_comensales": reserva_comensales, "reserva_mesa_id": reserva_mesa_id, "reserva_completa": True, "menu_establecido": False}
            if name is not None and name == True and reserva_dia is not None and reserva_hora is not None and reserva_comensales is not None:
                return {"reserva_comensales": reserva_comensales, "reserva_mesa_id": reserva_mesa_id, "reserva_completa": True}
            return {"reserva_comensales": reserva_comensales, "reserva_mesa_id": reserva_mesa_id, "reserva_completa": False}
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
        if tracker.get_intent_of_latest_message() == "stop":
            return {"requested_slot": None, "reserva_dia": None}
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
        reserva_hora = tracker.get_slot("reserva_hora")
        reserva_comensales = tracker.get_slot("reserva_comensales")
        reserva_mesa_id = tracker.get_slot("reserva_mesa_id")
        name = tracker.get_slot("first_name_set")
        if reserva_dia is not None and reserva_dia not in DIAS_SEMANA:
            dispatcher.utter_message(
                text=f'No reconozco ese dia.')
            return {"reserva_dia": None}

        if name is not None and name == True and reserva_dia is not None and reserva_hora is not None and reserva_comensales is not None and reserva_mesa_id is not None and tracker.get_slot("menu_establecido") is None:
            return {"reserva_dia": reserva_dia, "reserva_completa": True, "menu_establecido": False}

        if name is not None and name == True and reserva_dia is not None and reserva_hora is not None and reserva_comensales is not None and reserva_mesa_id is not None:
            return {"reserva_dia": reserva_dia, "reserva_completa": True}
        return {"reserva_dia": reserva_dia, "reserva_completa": False}


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
        reserva_dia = reserva_dia.lower()
        reserva_hora = tracker.get_slot("reserva_hora")
        horas_mesas = self.get_horas_mesas(reserva_dia)
        if tracker.get_intent_of_latest_message() == "stop":
            return {"requested_slot": None, "reserva_hora": None}
        if reserva_hora in horas_mesas:
            dispatcher.utter_message(
                "La hora elegida no esta disponible o terminaria dentro del periodo de una reserva ya realizada.")
            dispatcher.utter_message(
                "Las reservas tienen una duracion de 2 horas.")
            message = "Las horas ocupadas son: \n"
            for h in horas_mesas:
                message += "- {} hasta {}{}\n".format(
                    str(h), str(int(h[:2])+2), str(h[2:]))
            dispatcher.utter_message(message)
            dispatcher.utter_message("Selecciona otra hora.")
            return {"reserva_hora": None}

        for t in HORAS['horas'][reserva_dia][0]['time']:
            h = int(reserva_hora[:2])
            h2 = int(t[:2])
            if (h == h2) or (h > h2 and h < (h2+2)) or ((h+2) > h2 and (h+2) < (h2+2)):
                dispatcher.utter_message(
                    "La hora elegida no esta disponible o terminaria dentro del periodo de una reserva ya realizada.")
                dispatcher.utter_message(
                    "Las reservas tienen una duracion de 2 horas.")
                message = "Las horas ocupadas son: \n"
                for h in horas_mesas:
                    message += "- {} hasta {}{}\n".format(
                        str(h), str(int(h[:2])+2), str(h[2:]))
                dispatcher.utter_message(message)
                dispatcher.utter_message("Selecciona otra hora.")
                return {"reserva_hora": None}

        if reserva_hora is not None:
            if self.validate_regex(reserva_hora):
                return {"reserva_hora": tracker.get_slot("reserva_hora")}
        dispatcher.utter_message("Selecciona otra hora")
        return {"reserva_hora": None}

    def validate_reserva_hora(
        self, slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker, domain: DomainDict,
    ) -> Dict[Text, Any]:
        print("validate_reserva_hora")
        if tracker.get_intent_of_latest_message() == "stop":
            return {"requested_slot": None, "reserva_hora": None}
        reserva_hora = tracker.get_slot("reserva_hora")
        reserva_dia = tracker.get_slot("reserva_dia")
        reserva_comensales = tracker.get_slot("reserva_comensales")
        reserva_mesa_id = tracker.get_slot("reserva_mesa_id")
        horas_mesas = self.get_horas_mesas(reserva_dia)
        name = tracker.get_slot("first_name_set")
        if reserva_hora is not None and self.validate_regex(reserva_hora):
            dispatcher.utter_message(
                text=f'Anotada la hora de reserva: ' + reserva_hora)
            if name is not None and name == True and reserva_dia is not None and reserva_hora is not None and reserva_comensales is not None and reserva_mesa_id is not None and tracker.get_slot("menu_establecido") is None:
                return {"reserva_hora": reserva_hora, "reserva_completa": True, "menu_establecido": False}
            if name is not None and name == True and reserva_dia is not None and reserva_hora is not None and reserva_comensales is not None and reserva_mesa_id is not None:
                return {"reserva_hora": reserva_hora, "reserva_completa": True}
            return {"reserva_hora": reserva_hora, "reserva_completa": False}
        else:
            return {"reserva_hora": None}


class ValidateReservaEmailForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_reserva_email_form"

    async def required_slots(
        self, slots_mapped_in_domain: List[Text],
        dispatcher: CollectingDispatcher,
        tracker: Tracker, domain: DomainDict,
    ) -> Optional[List[Text]]:
        print("Required slots reserva_email")
        return slots_mapped_in_domain

    async def extract_reserva_email(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> Dict[Text, Any]:
        print("extract_reserva_email")
        reserva_email = tracker.get_slot("reserva_email")
        if tracker.get_intent_of_latest_message() == "stop":
            return {"requested_slot": None, "reserva_email": None}
        if reserva_email is not None:
            return {"reserva_email": reserva_email}
        dispatcher.utter_message(text=f'No se ha establecido un email.')
        return {}

    def validate_reserva_email(
        self, slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker, domain: DomainDict,
    ) -> Dict[Text, Any]:
        print("validate_reserva_email")

        if tracker.get_intent_of_latest_message() == "stop":
            dispatcher.utter_message(text=f'Parando el proceso.')
            return {"requested_slot": None, "reserva_email": None}

        reserva_email = tracker.get_slot("reserva_email")
        reserva_completa = tracker.get_slot("reserva_completa")

        if reserva_completa is not None:
            if reserva_completa:
                if reserva_email is not None:
                    regex = '^[a-z0-9]+[._]?[a-z0-9]+[@][a-z]+[.][a-z]{2,3}$'
                    if(re.search(regex, reserva_email)):
                        dispatcher.utter_message(
                            text="Anotado email " + reserva_email)
                        return {"reserva_email": reserva_email, "reserva_email_set": True, "reserva_realizada": False}
                    else:
                        dispatcher.utter_message(
                            text="El email " + reserva_email + " no ha podido ser validado, comprueba que esta bien escrito.")
                        return {"reserva_email": None, "reserva_email_set": False, "reserva_realizada": False}
                else:
                    dispatcher.utter_message(
                        text=f'No se ha establecido un email.')
                    return {"reserva_email_set": False, "reserva_realizada": False}
            else:
                dispatcher.utter_message(
                    text=f'Es necesario especificar una reserva antes de guardar la reserva.')
                return {"reserva_email": None, "reserva_email_set": False, "reserva_realizada": False}
        else:
            dispatcher.utter_message(
                text=f'Es necesario especificar una reserva antes de guardar la reserva.')
            return {"reserva_email": None, "reserva_email_set": False, "reserva_realizada": False}


class ValidateReservaCodigoForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_reserva_codigo_form"

    async def required_slots(
        self, slots_mapped_in_domain: List[Text],
        dispatcher: CollectingDispatcher,
        tracker: Tracker, domain: DomainDict,
    ) -> Optional[List[Text]]:
        print("Required slots reserva_codigo")
        return slots_mapped_in_domain

    async def extract_reserva_codigo(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> Dict[Text, Any]:
        print("extract_reserva_codigo")
        if tracker.get_intent_of_latest_message() == "stop":
            return {"requested_slot": None, "reserva_codigo": None}
        reserva_codigo = tracker.get_slot("reserva_codigo")
        if reserva_codigo is not None:
            return {"reserva_codigo": reserva_codigo}
        else:
            return {"reserva_codigo": None}

    def validate_reserva_codigo(
        self, slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker, domain: DomainDict,
    ) -> Dict[Text, Any]:
        print("validate_reserva_codigo")
        if tracker.get_intent_of_latest_message() == "stop":
            dispatcher.utter_message(text=f'Parando el proceso.')
            return {"requested_slot": None, "reserva_codigo": None}
        reserva_codigo = tracker.get_slot("reserva_codigo")
        if reserva_codigo is not None:
            if len(reserva_codigo) == 6:
                if reserva_codigo.isdigit():
                    reserva_codigo_tmp = tracker.get_slot("reserva_codigo_tmp")
                    if reserva_codigo == reserva_codigo_tmp:
                        dispatcher.utter_message(
                            text=f'Codigo aceptado. Se ha enviado un correo con un resumen de tu reserva.')
                        reserva_dia = tracker.get_slot("reserva_dia")
                        reserva_hora = tracker.get_slot("reserva_hora")
                        reserva_comensales = tracker.get_slot(
                            "reserva_comensales")
                        reserva_mesa_id = tracker.get_slot("reserva_mesa_id")
                        name = tracker.get_slot("first_name")
                        reserva_array = [reserva_dia, reserva_hora,
                                         reserva_mesa_id, reserva_comensales, name]
                        menu_array = []
                        if tracker.get_slot("menu_establecido"):
                            menu_array.append(
                                tracker.get_slot("menu_plato_1_nombre"))
                            menu_array.append(
                                tracker.get_slot("menu_plato_2_nombre"))
                            menu_array.append(
                                tracker.get_slot("menu_plato_3_nombre"))
                            menu_array.append(
                                tracker.get_slot("menu_bebida_nombre"))
                        email.send_email_message(tracker.get_slot(
                            "reserva_email"), reserva_array, menu_array)
                        return {"reserva_codigo": reserva_codigo, "reserva_realizada": True}
                    else:
                        dispatcher.utter_message(
                            text=f'El codigo es incorrecto. ¿Lo has copiado bien?')
                        return {"reserva_codigo": None, "reserva_realizada": False}
                else:
                    dispatcher.utter_message(
                        text=f'El codigo debe estar compuesto por 6 digitos.')
                    return {"reserva_codigo": None, "reserva_realizada": False}
            else:
                dispatcher.utter_message(
                    text=f'El codigo debe tener 6 digitos.')
                return {"reserva_codigo": None, "reserva_realizada": False}

        else:
            dispatcher.utter_message(
                "No se ha establecido un codigo de confirmacion.")
            return {"reserva_codigo": None, "reserva_realizada": False}
