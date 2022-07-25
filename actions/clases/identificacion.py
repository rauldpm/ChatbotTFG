from typing import Text, List, Any, Dict, Optional
from rasa_sdk.events import SlotSet
from rasa_sdk.interfaces import Action
from rasa_sdk.types import DomainDict
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk import Tracker, FormValidationAction
from actions.clases.auxiliar import *

# -----------------------------------------
auxiliar = Auxiliar()
names = auxiliar.get_names()
malsonantes = auxiliar.get_malsonantes()
# -----------------------------------------

class IdentificarBorrarUsername(Action):
    def name(self):
        return 'IdentificarBorrarUsername'

    def run(self, dispatcher, tracker, domain):
        print("IdentificarBorrarUsername")
        dispatcher.utter_message(
            text=f'He borrado tu nombre de usuario, recuerda que es necesario identificarte para terminar el proceso de reserva.')
        return [SlotSet("first_name", None), SlotSet("first_name_save", None), SlotSet("first_name_set", None), SlotSet("name_spelled_correctly", None), SlotSet("reserva_completa", False)]


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
        first_name_set = tracker.get_slot("first_name_set")
        if first_name_set:
          return {}
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

        first_name_set = tracker.get_slot("first_name_set")
        if first_name_set:
          return {}

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
                reserva_dia = tracker.get_slot("reserva_dia")
                reserva_hora = tracker.get_slot("reserva_hora")
                reserva_comensales = tracker.get_slot("reserva_comensales")
                if reserva_dia is not None and reserva_hora is not None and reserva_comensales is not None:
                  return {"first_name": slot_value, "first_name_set": True, "reserva_completa": True}

                return {"first_name": slot_value, "first_name_set": True, "reserva_completa": False}
        return {"first_name": None, "name_spelled_correctly": False}
